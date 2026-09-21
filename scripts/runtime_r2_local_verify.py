#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
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



def _expected_artifact(plan: dict[str, Any]) -> tuple[str, int, str, str]:
    controlled = plan.get("controlled_task")
    package = plan.get("engineering_task_package")
    if not isinstance(controlled, dict) or not isinstance(package, dict):
        raise VerificationError("frozen plan artifact identity inputs are missing")

    expected_size: int | None = None
    for criterion in controlled.get("acceptance_criteria", []):
        if not isinstance(criterion, str):
            continue
        match = re.search(r"([0-9][0-9,]*)-byte package", criterion)
        if match:
            expected_size = int(match.group(1).replace(",", ""))
            break

    package_path: str | None = None
    expected_sha: str | None = None
    for ref in package.get("evidence_refs", []):
        if not isinstance(ref, str):
            continue
        match = re.fullmatch(r"(\S+)\s+sha256:([0-9a-f]{64})", ref)
        if match:
            package_path, expected_sha = match.groups()
            break

    base_commit = controlled.get("exact_base_commit")
    if (
        expected_size is None
        or package_path is None
        or expected_sha is None
        or not isinstance(base_commit, str)
        or re.fullmatch(r"[0-9a-f]{40}", base_commit) is None
    ):
        raise VerificationError("frozen plan does not expose exact OTA path/size/SHA/source identity")

    rel = pathlib.PurePosixPath(package_path)
    if rel.is_absolute() or ".." in rel.parts:
        raise VerificationError("frozen OTA package path is unsafe")
    return package_path, expected_size, expected_sha, base_commit


def _json_leaf_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        rows: list[str] = []
        for item in value.values():
            rows.extend(_json_leaf_values(item))
        return rows
    if isinstance(value, list):
        rows = []
        for item in value:
            rows.extend(_json_leaf_values(item))
        return rows
    if value is None:
        return []
    return [str(value)]


def _verify_checksum_list(result_tree: pathlib.Path, package_path: str, expected_sha: str) -> str:
    checksum_path = result_tree / "SHA256SUMS.txt"
    if not checksum_path.is_file():
        raise VerificationError("result tree missing SHA256SUMS.txt")

    entries: list[tuple[str, str]] = []
    seen_paths: set[str] = set()
    for lineno, raw in enumerate(checksum_path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        match = re.fullmatch(r"([0-9a-f]{64})\s+[* ]?(.+)", line)
        if match is None:
            raise VerificationError(f"malformed SHA256SUMS.txt entry at line {lineno}")
        digest, path = match.groups()
        path = path.strip()
        if path in seen_paths:
            raise VerificationError(f"duplicate checksum entry: {path}")
        seen_paths.add(path)
        entries.append((path, digest))

    matches = [digest for path, digest in entries if path == package_path]
    if len(matches) != 1:
        raise VerificationError(f"expected exactly one checksum entry for {package_path}")
    if matches[0] != expected_sha:
        raise VerificationError("checksum list SHA-256 does not match frozen artifact identity")
    return sha256_file(checksum_path)


def _find_identity_manifest(
    result_tree: pathlib.Path,
    package_path: str,
    expected_size: int,
    expected_sha: str,
    base_commit: str,
) -> pathlib.Path:
    for path in sorted(result_tree.rglob("*.json")):
        if ".git" in path.parts or not path.is_file():
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        leaves = set(_json_leaf_values(value))
        if (
            package_path in leaves
            and str(expected_size) in leaves
            and expected_sha in leaves
            and base_commit in leaves
        ):
            return path
    raise VerificationError(
        "no machine-readable identity JSON binds frozen package path/size/SHA/source identity"
    )


def _verify_frozen_artifact_identity(
    result_tree: pathlib.Path,
    plan: dict[str, Any],
    log: pathlib.Path,
) -> None:
    package_path, expected_size, expected_sha, base_commit = _expected_artifact(plan)
    package = result_tree.joinpath(*pathlib.PurePosixPath(package_path).parts)
    if not package.is_file():
        raise VerificationError(f"result tree missing frozen OTA package: {package_path}")
    actual_size = package.stat().st_size
    if actual_size != expected_size:
        raise VerificationError(
            f"OTA package size mismatch: expected {expected_size}, got {actual_size}"
        )
    actual_sha = sha256_file(package)
    if actual_sha != expected_sha:
        raise VerificationError("OTA package SHA-256 mismatch against frozen task")

    checksum_sha = _verify_checksum_list(result_tree, package_path, expected_sha)
    identity = _find_identity_manifest(
        result_tree,
        package_path,
        expected_size,
        expected_sha,
        base_commit,
    )
    rows = [
        f"package={package_path}",
        f"size={actual_size}",
        f"sha256={actual_sha}",
        f"base_commit={base_commit}",
        f"identity_manifest={identity.relative_to(result_tree).as_posix()}",
        f"identity_manifest_sha256={sha256_file(identity)}",
        f"checksum_list_sha256={checksum_sha}",
        "status=pass",
        "",
    ]
    log.write_text("\n".join(rows), encoding="utf-8")


def _run_native_host_verification(
    result_tree: pathlib.Path,
    log: pathlib.Path,
) -> None:
    commands: list[list[str]] = []

    tests = result_tree / "tests"
    if tests.is_dir() and any(tests.rglob("test*.py")):
        commands.append([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])

    shell_verifiers = sorted(
        {
            *result_tree.glob("verify*.sh"),
            *(result_tree / "scripts").glob("verify*.sh") if (result_tree / "scripts").is_dir() else [],
        }
    )
    commands.extend([["bash", path.relative_to(result_tree).as_posix()] for path in shell_verifiers])

    legacy = result_tree / "verify_ota_manifest.py"
    manifest = result_tree / "ota-manifest.v1.json"
    if legacy.is_file() and manifest.is_file():
        commands.append([sys.executable, legacy.name, "--manifest", manifest.name])

    if not commands:
        raise VerificationError("result tree exposes no runnable host verifier")

    chunks: list[str] = []
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=result_tree,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        chunks.append("$ " + " ".join(command))
        chunks.append(completed.stdout)
        chunks.append(f"[exit={completed.returncode}]")
        if completed.returncode != 0:
            log.write_text("\n".join(chunks) + "\n", encoding="utf-8")
            raise VerificationError(
                f"verification command failed ({completed.returncode}): {' '.join(command)}"
            )
    log.write_text("\n".join(chunks) + "\n", encoding="utf-8")


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
    if collection.get("runtime_home_mode") != "shared-user-home":
        raise VerificationError("R2 local verification requires shared-user-home runtime mode")
    if collection.get("credential_state_in_evidence") is not False:
        raise VerificationError("R2 local verification forbids credential state in evidence")

    plan = load_json(freeze_dir.resolve() / "frozen-plan.json")
    test_evidence: dict[str, str] = {}
    for runtime, prefix in (("codex", "codex"), ("claude-code", "claude")):
        result_tree = intake_out / runtime / "result-tree"
        if not result_tree.is_dir():
            raise VerificationError(f"missing replay-complete result tree: {runtime}")
        unit_log = out / f"{prefix}-domain-host-tests.log"
        ota_log = out / f"{prefix}-domain-ota-verify.log"
        _verify_frozen_artifact_identity(result_tree, plan, ota_log)
        _run_native_host_verification(result_tree, unit_log)
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
        "runtime_home_mode": "shared-user-home",
        "credential_state_in_evidence": False,
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
            "runtime-native-host-verifier",
            "independent-ota-artifact-identity",
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
