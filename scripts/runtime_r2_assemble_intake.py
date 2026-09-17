#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tarfile
from pathlib import Path
from typing import Any

FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
FREEZE_SCHEMA = "digital-worker-runtime-r2-campaign/v1"
INTAKE_SCHEMA = "digital-worker-runtime-r2-intake/v1"
EXPECTED = {
    "codex": {
        "repository": "jiying2007/codex",
        "signer_workflow": "jiying2007/codex/.github/workflows/runtime-r2-provider-execution.yml",
        "subject_name": "codex-evidence.tar.gz",
        "attestation_name": "codex-attestation.json",
    },
    "claude-code": {
        "repository": "jiying2007/claude",
        "signer_workflow": "jiying2007/claude/.github/workflows/runtime-r2-provider-execution.yml",
        "subject_name": "claude-code-evidence.tar.gz",
        "attestation_name": "claude-code-attestation.json",
    },
}


class AssembleError(RuntimeError):
    pass


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssembleError(message)


def load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AssembleError(f"invalid {label}: {path}") from exc


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def regular(path: Path, label: str) -> Path:
    path = path.resolve()
    require(path.is_file() and not path.is_symlink(), f"{label} must be a regular file: {path}")
    return path


def tar_member_bytes(archive: Path, wanted: str, label: str) -> bytes:
    matches: list[tarfile.TarInfo] = []
    try:
        with tarfile.open(archive, "r:gz") as tf:
            for member in tf.getmembers():
                rel = Path(member.name)
                require(not rel.is_absolute() and ".." not in rel.parts, f"{label} archive path escapes root: {member.name}")
                require(not member.issym() and not member.islnk(), f"{label} archive links are forbidden: {member.name}")
                normalized = member.name.removeprefix("./")
                if normalized == wanted:
                    matches.append(member)
            require(len(matches) == 1, f"{label} archive must contain exactly one {wanted}")
            stream = tf.extractfile(matches[0])
            require(stream is not None, f"{label} archive member is unreadable: {wanted}")
            return stream.read()
    except tarfile.TarError as exc:
        raise AssembleError(f"invalid {label} archive: {archive}") from exc


def load_subject_manifest(archive: Path, runtime: str) -> dict[str, Any]:
    raw = tar_member_bytes(archive, "bundle-manifest.json", runtime)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AssembleError(f"{runtime} bundle-manifest.json is invalid") from exc
    require(isinstance(value, dict), f"{runtime} bundle manifest must be an object")
    spec = EXPECTED[runtime]
    require(value.get("runtime") == runtime, f"{runtime} bundle runtime mismatch")
    require(
        value.get("status") == "provider-execution-completed-pending-digital-worker-verification",
        f"{runtime} bundle status is not pending Digital Worker Verification",
    )
    require(value.get("verification_pass_claimed") is False, f"{runtime} bundle must disclaim Verification PASS")
    require(value.get("r2_qualified") is False, f"{runtime} bundle must not self-qualify R2")
    require(value.get("workflow_repository") == spec["repository"], f"{runtime} workflow repository mismatch")
    workflow_sha = value.get("workflow_sha")
    workflow_run_id = str(value.get("workflow_run_id") or "")
    require(isinstance(workflow_sha, str) and FULL_SHA.fullmatch(workflow_sha) is not None, f"{runtime} workflow SHA invalid")
    require(workflow_run_id.isdigit(), f"{runtime} workflow run id invalid")
    return value


def validate_freeze(freeze_dir: Path) -> tuple[dict[str, Any], dict[str, Any], Path]:
    freeze_dir = freeze_dir.resolve()
    campaign_path = regular(freeze_dir / "campaign.json", "freeze campaign")
    plan_path = regular(freeze_dir / "frozen-plan.json", "frozen plan")
    campaign = load_json(campaign_path, "freeze campaign")
    plan = load_json(plan_path, "frozen plan")
    require(isinstance(campaign, dict) and campaign.get("schema") == FREEZE_SCHEMA, "unsupported freeze campaign schema")
    require(isinstance(plan, dict) and plan.get("schema") == "digital-worker-runtime-r2-plan/v1", "unsupported frozen plan schema")
    campaign_id = campaign.get("campaign_id")
    frozen = campaign.get("frozen_inputs_sha256")
    dw_commit = campaign.get("digital_worker_commit")
    target_base = campaign.get("target_base_commit")
    require(isinstance(campaign_id, str) and campaign_id, "freeze campaign_id missing")
    require(isinstance(frozen, str) and SHA256.fullmatch(frozen) is not None, "freeze frozen_inputs_sha256 invalid")
    require(isinstance(dw_commit, str) and FULL_SHA.fullmatch(dw_commit) is not None, "freeze Digital Worker commit invalid")
    require(isinstance(target_base, str) and FULL_SHA.fullmatch(target_base) is not None, "freeze target base invalid")
    controlled = plan.get("controlled_task")
    require(isinstance(controlled, dict), "frozen controlled_task missing")
    require(plan.get("frozen_inputs_sha256") == frozen, "freeze campaign/frozen plan digest mismatch")
    require(canonical_digest(controlled) == frozen, "frozen controlled_task content digest mismatch")
    require(controlled.get("run_id") == campaign_id, "freeze campaign id does not match frozen plan")
    require(controlled.get("exact_base_commit") == target_base, "freeze target base does not match frozen plan")
    governance = plan.get("digital_worker_governance")
    require(isinstance(governance, dict) and governance.get("provider_commit") == dw_commit, "freeze Digital Worker identity mismatch")
    workflows = campaign.get("runtime_execution_workflows")
    require(isinstance(workflows, dict), "freeze runtime execution workflows missing")
    for runtime, spec in EXPECTED.items():
        require(workflows.get(runtime) == spec["signer_workflow"], f"freeze signer workflow drift: {runtime}")
    return campaign, plan, plan_path


def validate_subject(runtime: str, subject: Path, attestation: Path, frozen_plan: Path) -> dict[str, Any]:
    subject = regular(subject, f"{runtime} subject")
    attestation = regular(attestation, f"{runtime} attestation")
    manifest = load_subject_manifest(subject, runtime)
    embedded_plan = tar_member_bytes(subject, "frozen-plan.json", runtime)
    require(embedded_plan == frozen_plan.read_bytes(), f"{runtime} embedded frozen plan is not byte-identical to freeze artifact")
    parsed_attestation = load_json(attestation, f"{runtime} attestation")
    require(isinstance(parsed_attestation, (dict, list)) and bool(parsed_attestation), f"{runtime} attestation JSON is empty")
    return manifest


def assemble(
    root: Path,
    freeze_dir: Path,
    codex_subject: Path,
    codex_attestation: Path,
    claude_subject: Path,
    claude_attestation: Path,
    output_dir: Path,
) -> dict[str, Any]:
    root = root.resolve()
    intake_root = (root / "reports/runtime-r2/intake").resolve()
    output_dir = output_dir.resolve()
    try:
        output_dir.relative_to(intake_root)
    except ValueError as exc:
        raise AssembleError("output directory must stay under reports/runtime-r2/intake") from exc
    require(output_dir != intake_root, "output directory must be a campaign subdirectory")
    if output_dir.exists():
        require(not any(output_dir.iterdir()), f"output directory must be empty: {output_dir}")
    else:
        output_dir.mkdir(parents=True)

    freeze, plan, plan_path = validate_freeze(freeze_dir)
    runtime_inputs = {
        "codex": (codex_subject, codex_attestation),
        "claude-code": (claude_subject, claude_attestation),
    }
    descriptors: dict[str, dict[str, Any]] = {}
    copied: list[Path] = []
    try:
        shutil.copyfile(plan_path, output_dir / "frozen-plan.json")
        copied.append(output_dir / "frozen-plan.json")
        for runtime, (subject, attestation) in runtime_inputs.items():
            spec = EXPECTED[runtime]
            manifest = validate_subject(runtime, subject, attestation, plan_path)
            subject_dst = output_dir / spec["subject_name"]
            attestation_dst = output_dir / spec["attestation_name"]
            shutil.copyfile(subject, subject_dst)
            shutil.copyfile(attestation, attestation_dst)
            copied.extend([subject_dst, attestation_dst])
            descriptors[runtime] = {
                "repository": spec["repository"],
                "signer_workflow": spec["signer_workflow"],
                "workflow_sha": manifest["workflow_sha"],
                "workflow_run_id": str(manifest["workflow_run_id"]),
                "subject": subject_dst.name,
                "subject_sha256": sha256_file(subject_dst),
                "attestation": attestation_dst.name,
                "attestation_sha256": sha256_file(attestation_dst),
            }

        campaign = {
            "schema": INTAKE_SCHEMA,
            "campaign_id": freeze["campaign_id"],
            "frozen_inputs_sha256": freeze["frozen_inputs_sha256"],
            "digital_worker_commit": freeze["digital_worker_commit"],
            "target_base_commit": freeze["target_base_commit"],
            "frozen_plan": "frozen-plan.json",
            "freeze_workflow_run_id": str(freeze.get("freeze_workflow_run_id") or ""),
            "freeze_campaign_sha256": sha256_file((freeze_dir / "campaign.json").resolve()),
            "runtime_evidence": descriptors,
            "verification_status": "pending",
            "independent_review_status": "pending",
            "r2_qualified": False,
        }
        campaign_path = output_dir / "campaign.json"
        campaign_path.write_text(json.dumps(campaign, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        copied.append(campaign_path)
        return campaign
    except Exception:
        for path in copied:
            path.unlink(missing_ok=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assemble a tracked Digital Worker R2 intake campaign from one freeze artifact and two runtime-owned attested subjects")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--freeze-dir", type=Path, required=True)
    parser.add_argument("--codex-subject", type=Path, required=True)
    parser.add_argument("--codex-attestation", type=Path, required=True)
    parser.add_argument("--claude-subject", type=Path, required=True)
    parser.add_argument("--claude-attestation", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--summary-json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = assemble(
            args.root,
            args.freeze_dir,
            args.codex_subject,
            args.codex_attestation,
            args.claude_subject,
            args.claude_attestation,
            args.output_dir,
        )
    except (OSError, AssembleError, json.JSONDecodeError, tarfile.TarError) as exc:
        print(json.dumps({"schema": INTAKE_SCHEMA, "status": "blocked", "error": str(exc)}, sort_keys=True))
        return 2
    if args.summary_json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"R2 intake campaign assembled: {result['campaign_id']} -> {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
