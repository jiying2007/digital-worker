#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Any, Mapping

FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
FREEZE_SCHEMA = "digital-worker-runtime-r2-campaign/v1"
INTAKE_SCHEMA = "digital-worker-runtime-r2-local-intake/v1"
RUNTIMES = {
    "codex": {
        "native_candidates": ("codex-native.json",),
        "portable_name": "codex-portable.json",
        "provider_outputs": ("codex-events.jsonl", "codex-final.txt"),
    },
    "claude-code": {
        "native_candidates": ("claude-native-validated.json", "claude-native.json"),
        "portable_name": "claude-portable.json",
        "provider_outputs": ("claude-execution.json",),
    },
}


class IntakeError(RuntimeError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise IntakeError(message)


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IntakeError(f"invalid {label}: {path}") from exc
    require(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def git_head(root: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise IntakeError(completed.stderr.strip() or f"cannot resolve git HEAD: {root}")
    return completed.stdout.strip()


def safe_extract_tar(archive: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    try:
        with tarfile.open(archive, "r:gz") as tf:
            members = tf.getmembers()
            require(bool(members), f"empty result archive: {archive}")
            for member in members:
                rel = Path(member.name)
                require(
                    not rel.is_absolute() and ".." not in rel.parts,
                    f"archive path escapes root: {member.name}",
                )
                require(
                    not member.issym() and not member.islnk(),
                    f"archive links are forbidden: {member.name}",
                )
            tf.extractall(destination, members=members, filter="data")
    except tarfile.TarError as exc:
        raise IntakeError(f"invalid result archive: {archive}") from exc


def tree_digest(root: Path) -> str:
    rows: list[tuple[str, str]] = []
    for path in sorted(x for x in root.rglob("*") if x.is_file() and ".git" not in x.parts):
        rows.append((path.relative_to(root).as_posix(), sha256_file(path)))
    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


def expected_tree_digest(native: Mapping[str, Any], runtime: str) -> str:
    refs = native.get("evidence_refs")
    require(isinstance(refs, list), f"{runtime} native receipt evidence_refs missing")
    matches = [
        item.split("worktree-result:sha256:", 1)[1]
        for item in refs
        if isinstance(item, str) and item.startswith("worktree-result:sha256:")
    ]
    require(len(matches) == 1 and SHA256.fullmatch(matches[0]) is not None, f"{runtime} worktree-result digest missing")
    return matches[0]


def validate_freeze(root: Path, freeze_dir: Path) -> tuple[dict[str, Any], dict[str, Any], Path, str]:
    freeze_dir = freeze_dir.resolve()
    campaign_path = freeze_dir / "campaign.json"
    plan_path = freeze_dir / "frozen-plan.json"
    require(campaign_path.is_file(), f"freeze campaign missing: {campaign_path}")
    require(plan_path.is_file(), f"frozen plan missing: {plan_path}")
    campaign = load_json(campaign_path, "freeze campaign")
    plan = load_json(plan_path, "frozen plan")
    require(campaign.get("schema") == FREEZE_SCHEMA, "unsupported freeze campaign schema")
    require(plan.get("schema") == "digital-worker-runtime-r2-plan/v1", "unsupported frozen plan schema")

    frozen = campaign.get("frozen_inputs_sha256")
    dw_commit = campaign.get("digital_worker_commit")
    target_base = campaign.get("target_base_commit")
    require(isinstance(frozen, str) and SHA256.fullmatch(frozen) is not None, "freeze digest invalid")
    require(isinstance(dw_commit, str) and FULL_SHA.fullmatch(dw_commit) is not None, "Digital Worker commit invalid")
    require(isinstance(target_base, str) and FULL_SHA.fullmatch(target_base) is not None, "target base invalid")
    verification_tool_commit = git_head(root.resolve())

    controlled = plan.get("controlled_task")
    require(isinstance(controlled, dict), "frozen controlled_task missing")
    require(plan.get("frozen_inputs_sha256") == frozen, "freeze campaign/frozen plan digest mismatch")
    require(canonical_digest(controlled) == frozen, "frozen controlled_task content digest mismatch")
    require(controlled.get("run_id") == campaign.get("campaign_id"), "freeze campaign id does not match plan")
    require(controlled.get("exact_base_commit") == target_base, "freeze target base does not match plan")
    governance = plan.get("digital_worker_governance")
    require(
        isinstance(governance, dict) and governance.get("provider_commit") == dw_commit,
        "Digital Worker governance identity mismatch",
    )

    runtime_execution = campaign.get("runtime_execution")
    require(isinstance(runtime_execution, dict), "freeze runtime_execution boundary missing")
    require(runtime_execution.get("mode") == "runtime-owned-local-terminal", "freeze is not local-terminal R2")
    require(runtime_execution.get("runtime_home_mode") == "shared-user-home", "freeze runtime home mode is not shared-user-home")
    require(runtime_execution.get("credential_state_in_evidence") is False, "freeze must exclude credential state from evidence")
    require(runtime_execution.get("github_provider_credentials_required") is False, "GitHub provider credentials must not be required")
    require(runtime_execution.get("provider_credentials_must_not_enter_github") is True, "provider credential boundary missing")
    return campaign, plan, plan_path, verification_tool_commit


def choose_native(evidence_dir: Path, runtime: str) -> Path:
    for name in RUNTIMES[runtime]["native_candidates"]:
        path = evidence_dir / name
        if path.is_file():
            return path
    raise IntakeError(f"{runtime} native receipt missing from {evidence_dir}")


def project_portable(root: Path, runtime: str, native: Path, frozen: Path, output: Path) -> None:
    command = [
        sys.executable,
        str(root / "scripts/runtime_r2_evidence.py"),
        "project-receipt",
        "--root",
        str(root),
        "--runtime",
        runtime,
        "--native-receipt",
        str(native),
        "--frozen-plan",
        str(frozen),
        "--output",
        str(output),
    ]
    completed = subprocess.run(command, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if completed.returncode != 0:
        raise IntakeError(f"{runtime} native-to-portable projection failed: {completed.stdout.strip()}")


def validate_runtime(
    root: Path,
    runtime: str,
    evidence_dir: Path,
    plan: Mapping[str, Any],
    frozen_plan: Path,
    runtime_out: Path,
) -> dict[str, Any]:
    evidence_dir = evidence_dir.resolve()
    require(evidence_dir.is_dir(), f"{runtime} evidence directory missing: {evidence_dir}")
    runtime_out.mkdir(parents=True, exist_ok=True)
    evidence_out = runtime_out / "evidence"
    evidence_out.mkdir(parents=True, exist_ok=True)

    auth_path = evidence_dir / "provider-authorization.json"
    result_archive = evidence_dir / "result-tree.tar.gz"
    require(auth_path.is_file(), f"{runtime} provider authorization missing")
    require(result_archive.is_file(), f"{runtime} result-tree.tar.gz missing")
    auth = load_json(auth_path, f"{runtime} provider authorization")
    require(auth.get("authorized") is True, f"{runtime} provider execution not authorized")
    require(auth.get("verification_or_release_authority") is False, f"{runtime} provider receipt overclaims authority")
    require(auth.get("frozen_inputs_sha256") == plan.get("frozen_inputs_sha256"), f"{runtime} provider authorization freeze mismatch")
    require(auth.get("github_provider_credential_used") is False, f"{runtime} local evidence must not use GitHub provider credentials")
    require(auth.get("runtime_home_mode") == "shared-user-home", f"{runtime} runtime home must be shared-user-home")
    require(auth.get("credential_state_in_evidence") is False, f"{runtime} credential state must not enter evidence")
    actor = auth.get("actor")
    require(isinstance(actor, str) and actor, f"{runtime} provider actor missing")

    native_path = choose_native(evidence_dir, runtime)
    native = load_json(native_path, f"{runtime} native receipt")
    portable_path = runtime_out / "portable-receipt.json"
    project_portable(root, runtime, native_path, frozen_plan, portable_path)
    portable = load_json(portable_path, f"{runtime} portable receipt")
    require(portable.get("status") == "completed", f"{runtime} portable receipt must be completed")
    require(portable.get("frozen_inputs_sha256") == plan.get("frozen_inputs_sha256"), f"{runtime} portable receipt freeze mismatch")
    require(portable.get("verification_pass_claimed") is False, f"{runtime} portable receipt must disclaim Verification PASS")

    identity = portable.get("runtime_identity")
    require(isinstance(identity, dict), f"{runtime} portable runtime identity missing")
    require(identity.get("runtime_host") is not None, f"{runtime} runtime host missing")
    expected_binding = plan.get("runtime_bindings", {}).get(runtime)
    require(isinstance(expected_binding, dict), f"{runtime} frozen binding missing")
    require(identity.get("runtime_binding_commit") == expected_binding.get("commit"), f"{runtime} binding commit mismatch")

    result_tree = runtime_out / "result-tree"
    safe_extract_tar(result_archive, result_tree)
    actual_tree = tree_digest(result_tree)
    require(actual_tree == expected_tree_digest(native, runtime), f"{runtime} result tree digest mismatch")

    copied: dict[str, str] = {}
    for source in (auth_path, native_path, result_archive):
        destination = evidence_out / source.name
        shutil.copyfile(source, destination)
        copied[source.name] = sha256_file(destination)
    for name in RUNTIMES[runtime]["provider_outputs"]:
        source = evidence_dir / name
        require(source.is_file(), f"{runtime} provider output evidence missing: {name}")
        destination = evidence_out / name
        shutil.copyfile(source, destination)
        copied[name] = sha256_file(destination)

    return {
        "execution_venue": "local-terminal",
        "runtime_home_mode": "shared-user-home",
        "credential_state_in_evidence": False,
        "provider_actor": actor,
        "runtime_binding_commit": identity.get("runtime_binding_commit"),
        "native_receipt_sha256": sha256_file(native_path),
        "portable_receipt_sha256": sha256_file(portable_path),
        "result_archive_sha256": sha256_file(result_archive),
        "result_tree_sha256": actual_tree,
        "evidence_files": copied,
    }


def intake(
    root: Path,
    freeze_dir: Path,
    codex_evidence_dir: Path,
    claude_evidence_dir: Path,
    out: Path,
) -> dict[str, Any]:
    root = root.resolve()
    out = out.resolve()
    campaign, plan, frozen_plan, verification_tool_commit = validate_freeze(root, freeze_dir)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    runtime_dirs = {
        "codex": codex_evidence_dir,
        "claude-code": claude_evidence_dir,
    }
    execution_receipts: dict[str, str] = {}
    actors: dict[str, str] = {}
    runtime_evidence: dict[str, dict[str, Any]] = {}
    for runtime in ("codex", "claude-code"):
        descriptor = validate_runtime(
            root,
            runtime,
            runtime_dirs[runtime],
            plan,
            frozen_plan,
            out / runtime,
        )
        runtime_evidence[runtime] = descriptor
        actors[runtime] = descriptor["provider_actor"]
        execution_receipts[runtime] = descriptor["portable_receipt_sha256"]

    collection = {
        "schema": INTAKE_SCHEMA,
        "status": "provider-executions-collected-pending-digital-worker-verification-review",
        "campaign_id": campaign["campaign_id"],
        "freeze_workflow_run_id": str(campaign.get("freeze_workflow_run_id") or ""),
        "frozen_inputs_sha256": campaign["frozen_inputs_sha256"],
        "digital_worker_commit": campaign["digital_worker_commit"],
        "verification_tool_commit": verification_tool_commit,
        "target_base_commit": campaign["target_base_commit"],
        "execution_venue": "local-terminal",
        "runtime_home_mode": "shared-user-home",
        "credential_state_in_evidence": False,
        "github_provider_credentials_required": False,
        "verification_pass_claimed": False,
        "r2_qualified": False,
        "execution_receipts": execution_receipts,
        "provider_execution_actors": actors,
        "provider_execution_evidence": runtime_evidence,
    }
    (out / "intake-collection.json").write_text(
        json.dumps(collection, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return collection


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate local-terminal R2 runtime evidence before Digital Worker Verification")
    parser.add_argument("--root", default=".", type=Path)
    parser.add_argument("--freeze-dir", required=True, type=Path)
    parser.add_argument("--codex-evidence-dir", required=True, type=Path)
    parser.add_argument("--claude-evidence-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--summary-json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = intake(
            args.root,
            args.freeze_dir,
            args.codex_evidence_dir,
            args.claude_evidence_dir,
            args.out,
        )
    except (OSError, IntakeError, json.JSONDecodeError, tarfile.TarError) as exc:
        print(json.dumps({"schema": INTAKE_SCHEMA, "status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    if args.summary_json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"R2 local intake: {result['status']} campaign={result['campaign_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
