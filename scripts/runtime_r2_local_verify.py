#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]


class VerificationError(RuntimeError):
    pass


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise VerificationError(f"expected JSON object: {path}")
    return value


def run_logged(command: list[str], cwd: pathlib.Path, log: pathlib.Path) -> None:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise VerificationError(f"verification command failed ({completed.returncode}): {' '.join(command)}")


def verify_local_r2(
    root: pathlib.Path,
    freeze_dir: pathlib.Path,
    codex_evidence_dir: pathlib.Path,
    claude_evidence_dir: pathlib.Path,
    out: pathlib.Path,
    verification_actor: str,
) -> dict[str, Any]:
    root = root.resolve()
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    intake_out = out / "intake"

    command = [
        sys.executable,
        str(root / "scripts/runtime_r2_intake.py"),
        "--root",
        str(root),
        "--freeze-dir",
        str(freeze_dir),
        "--codex-evidence-dir",
        str(codex_evidence_dir),
        "--claude-evidence-dir",
        str(claude_evidence_dir),
        "--out",
        str(intake_out),
        "--summary-json",
    ]
    completed = subprocess.run(command, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if completed.returncode != 0:
        raise VerificationError(f"R2 local intake failed: {completed.stdout.strip()}")

    collection = load_json(intake_out / "intake-collection.json")
    if collection.get("status") != "provider-executions-collected-pending-digital-worker-verification-review":
        raise VerificationError("local intake did not produce a completed provider evidence collection")
    if collection.get("verification_pass_claimed") is not False or collection.get("r2_qualified") is not False:
        raise VerificationError("runtime intake overclaimed verification or qualification authority")
    if collection.get("execution_venue") != "local-terminal":
        raise VerificationError("R2 local verification requires local-terminal execution venue")

    test_evidence: dict[str, str] = {}
    for runtime, prefix in (("codex", "codex"), ("claude-code", "claude")):
        result_tree = intake_out / runtime / "result-tree"
        if not result_tree.is_dir():
            raise VerificationError(f"missing replay-complete result tree: {runtime}")
        unit_log = out / f"{prefix}-domain-host-tests.log"
        ota_log = out / f"{prefix}-domain-ota-verify.log"
        run_logged([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], result_tree, unit_log)
        run_logged([sys.executable, "verify_ota_manifest.py", "--manifest", "ota-manifest.v1.json"], result_tree, ota_log)
        test_evidence[f"{prefix}_host_tests_sha256"] = sha256_file(unit_log)
        test_evidence[f"{prefix}_ota_verify_sha256"] = sha256_file(ota_log)

    collection_path = intake_out / "intake-collection.json"
    report = {
        "schema": "digital-worker-runtime-r2-domain-verification/v1",
        "status": "pass",
        "comparison_id": collection["campaign_id"],
        "freeze_workflow_run_id": collection["freeze_workflow_run_id"],
        "frozen_inputs_sha256": collection["frozen_inputs_sha256"],
        "standard_id": "digital-worker-runtime-r2-host-verification/v2-local-terminal",
        "source_repository": "jiying2007/digital-worker",
        "source_commit": collection["digital_worker_commit"],
        "verification_tool_commit": collection["verification_tool_commit"],
        "verification_execution_venue": "local-terminal",
        "github_provider_credentials_required": False,
        "provider_execution_actors": collection["provider_execution_actors"],
        "provider_execution_evidence": collection["provider_execution_evidence"],
        "execution_receipts": collection["execution_receipts"],
        "verification_scope": [
            "local-evidence-integrity",
            "exact-frozen-task",
            "native-to-portable-receipt",
            "replay-complete-result-tree",
            "provider-result-identity",
            "host-unit-tests",
            "ota-manifest-verifier",
        ],
        "verification_actor": verification_actor,
        "verification_pass_claimed_by_runtime": False,
        "independent_review_status": "pending",
        "intake_collection_sha256": sha256_file(collection_path),
        "test_evidence": test_evidence,
    }
    report_path = out / "runtime-r2-domain-verification.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Digital Worker R2 domain verification locally against two runtime evidence directories")
    parser.add_argument("--root", type=pathlib.Path, default=ROOT)
    parser.add_argument("--freeze-dir", type=pathlib.Path, required=True)
    parser.add_argument("--codex-evidence-dir", type=pathlib.Path, required=True)
    parser.add_argument("--claude-evidence-dir", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    parser.add_argument("--verification-actor", required=True)
    parser.add_argument("--summary-json", action="store_true")
    args = parser.parse_args(argv)

    try:
        report = verify_local_r2(
            args.root,
            args.freeze_dir,
            args.codex_evidence_dir,
            args.claude_evidence_dir,
            args.out,
            args.verification_actor,
        )
    except (OSError, VerificationError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema": "digital-worker-runtime-r2-domain-verification/v1", "status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2

    if args.summary_json:
        print(json.dumps(report, sort_keys=True))
    else:
        print(f"R2 local verification: PASS comparison={report['comparison_id']}")
        print(args.out / "runtime-r2-domain-verification.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
