#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import tempfile
from typing import Any

SCRIPTS_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from runtime_r2_intake import IntakeError, safe_extract_tar
from runtime_r2_local_verify import (
    VerificationError,
    _run_native_host_verification,
    _verify_frozen_artifact_identity,
    load_json,
    sha256_file,
)


class PostflightError(RuntimeError):
    pass


def _write_json(path: pathlib.Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def run_postflight(
    frozen_plan: pathlib.Path,
    result_archive: pathlib.Path,
    out: pathlib.Path,
) -> dict[str, Any]:
    frozen_plan = frozen_plan.resolve()
    result_archive = result_archive.resolve()
    out = out.resolve()
    if not frozen_plan.is_file():
        raise PostflightError(f"frozen plan missing: {frozen_plan}")
    if not result_archive.is_file():
        raise PostflightError(f"result archive missing: {result_archive}")

    plan = load_json(frozen_plan)
    controlled = plan.get("controlled_task")
    if not isinstance(controlled, dict):
        raise PostflightError("frozen plan controlled task is missing")
    contract = controlled.get("host_verifier_contract")
    if not isinstance(contract, dict):
        raise PostflightError("frozen host verifier contract is missing")

    out.mkdir(parents=True, exist_ok=True)
    host_log = out / "result-postflight-host.log"
    ota_log = out / "result-postflight-ota.log"

    try:
        with tempfile.TemporaryDirectory(prefix="runtime-r2-postflight-") as tmp_value:
            tree = pathlib.Path(tmp_value) / "result-tree"
            safe_extract_tar(result_archive, tree)

            forbidden = [
                path
                for path in tree.rglob("*")
                if ".git" in path.relative_to(tree).parts
            ]
            if forbidden:
                raise PostflightError(
                    "replay result tree contains forbidden .git metadata: "
                    + ", ".join(path.relative_to(tree).as_posix() for path in forbidden[:5])
                )

            _verify_frozen_artifact_identity(tree, plan, ota_log)
            _run_native_host_verification(tree, host_log, plan)
    except (IntakeError, VerificationError, OSError, json.JSONDecodeError) as exc:
        raise PostflightError(str(exc)) from exc

    receipt = {
        "schema": "digital-worker-runtime-r2-result-postflight/v1",
        "status": "pass",
        "replay_self_contained": True,
        "git_metadata_present": False,
        "descriptor_path": contract.get("descriptor_path"),
        "descriptor_schema": contract.get("schema"),
        "result_archive_sha256": sha256_file(result_archive),
        "host_log_sha256": sha256_file(host_log),
        "ota_log_sha256": sha256_file(ota_log),
        "verification_pass_claimed": False,
        "domain_verification_pass_claimed": False,
        "r2_qualified": False,
    }
    _write_json(out / "result-postflight.json", receipt)
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Replay an R2 result archive without Git metadata and fail closed unless its declared host verifier contract passes."
    )
    parser.add_argument("--frozen-plan", type=pathlib.Path, required=True)
    parser.add_argument("--result-archive", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    parser.add_argument("--summary-json", action="store_true")
    args = parser.parse_args(argv)

    try:
        receipt = run_postflight(args.frozen_plan, args.result_archive, args.out)
    except (PostflightError, OSError, json.JSONDecodeError) as exc:
        failure = {
            "schema": "digital-worker-runtime-r2-result-postflight/v1",
            "status": "blocked",
            "error": str(exc),
            "verification_pass_claimed": False,
            "domain_verification_pass_claimed": False,
            "r2_qualified": False,
        }
        print(json.dumps(failure, ensure_ascii=False, sort_keys=True))
        return 2

    if args.summary_json:
        print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    else:
        print("R2 result postflight: PASS")
        print(args.out / "result-postflight.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
