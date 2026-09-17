#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tarfile
from pathlib import Path
from typing import Any

FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
CAMPAIGN_SCHEMA = "digital-worker-runtime-r2-intake/v1"
RUNTIMES = {
    "codex": {
        "repository": "jiying2007/codex",
        "signer_workflow": "jiying2007/codex/.github/workflows/runtime-r2-provider-execution.yml",
        "native": "codex-native.json",
    },
    "claude-code": {
        "repository": "jiying2007/claude",
        "signer_workflow": "jiying2007/claude/.github/workflows/runtime-r2-provider-execution.yml",
        "native": "claude-native-validated.json",
    },
}


class IntakeError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IntakeError(f"invalid {label}: {path}") from exc
    if not isinstance(value, dict):
        raise IntakeError(f"{label} must be a JSON object")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise IntakeError(message)


def regular_under(root: Path, value: Any, label: str) -> Path:
    require(isinstance(value, str) and value, f"{label} must be a non-empty relative path")
    rel = Path(value)
    require(not rel.is_absolute() and ".." not in rel.parts, f"{label} must stay inside the campaign directory")
    path = (root / rel).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise IntakeError(f"{label} escapes campaign directory") from exc
    require(path.is_file() and not path.is_symlink(), f"{label} must be a regular file: {value}")
    return path


def safe_extract_tar(archive: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    with tarfile.open(archive, "r:gz") as tf:
        members = tf.getmembers()
        require(bool(members), f"empty evidence archive: {archive}")
        for member in members:
            rel = Path(member.name)
            require(not rel.is_absolute() and ".." not in rel.parts, f"archive path escapes root: {member.name}")
            require(not member.issym() and not member.islnk(), f"archive links are forbidden: {member.name}")
        tf.extractall(destination, members=members, filter="data")


def validate_bundle_manifest(root: Path, runtime: str, expected: dict[str, Any]) -> dict[str, Any]:
    manifest = load_json(root / "bundle-manifest.json", f"{runtime} bundle manifest")
    require(manifest.get("runtime") == runtime, f"{runtime} bundle runtime mismatch")
    require(manifest.get("status") == "provider-execution-completed-pending-digital-worker-verification", f"{runtime} bundle status is not pending verification")
    require(manifest.get("verification_pass_claimed") is False, f"{runtime} bundle must disclaim Verification PASS")
    require(manifest.get("r2_qualified") is False, f"{runtime} bundle must not self-qualify R2")
    require(manifest.get("workflow_repository") == expected["repository"], f"{runtime} workflow repository mismatch")
    require(manifest.get("workflow_sha") == expected["workflow_sha"], f"{runtime} workflow SHA mismatch")
    require(str(manifest.get("workflow_run_id")) == str(expected["workflow_run_id"]), f"{runtime} workflow run id mismatch")
    listed = manifest.get("files")
    require(isinstance(listed, list) and listed, f"{runtime} bundle manifest files missing")
    declared: set[str] = set()
    for item in listed:
        require(isinstance(item, dict), f"{runtime} bundle file entry must be object")
        name = item.get("path")
        digest = item.get("sha256")
        require(isinstance(name, str) and name and "/" not in name and name != "bundle-manifest.json", f"{runtime} bundle file name invalid")
        require(isinstance(digest, str) and SHA256.fullmatch(digest) is not None, f"{runtime} bundle digest invalid: {name}")
        file_path = root / name
        require(file_path.is_file() and not file_path.is_symlink(), f"{runtime} bundle file missing: {name}")
        require(sha256_file(file_path) == digest, f"{runtime} bundle file digest mismatch: {name}")
        declared.add(name)
    actual = {p.name for p in root.iterdir() if p.is_file() and p.name != "bundle-manifest.json"}
    require(actual == declared, f"{runtime} bundle contains undeclared or missing files")
    return manifest


def verify_attestation(subject: Path, bundle: Path, runtime: str, expected: dict[str, Any]) -> None:
    spec = RUNTIMES[runtime]
    command = [
        "gh", "attestation", "verify", str(subject),
        "--repo", spec["repository"],
        "--bundle", str(bundle),
        "--signer-workflow", spec["signer_workflow"],
        "--source-ref", "refs/heads/main",
        "--source-digest", expected["workflow_sha"],
        "--format", "json",
    ]
    completed = subprocess.run(command, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode != 0:
        raise IntakeError(f"{runtime} GitHub OIDC attestation verification failed: {completed.stderr.strip()}")
    try:
        parsed = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise IntakeError(f"{runtime} attestation verification did not return JSON") from exc
    require(isinstance(parsed, list) and parsed, f"{runtime} attestation verification result is empty")


def project_portable(root: Path, runtime: str, native: Path, frozen: Path, output: Path) -> None:
    command = [
        "python", str(root / "scripts/runtime_r2_evidence.py"), "project-receipt",
        "--root", str(root), "--runtime", runtime,
        "--native-receipt", str(native), "--frozen-plan", str(frozen), "--output", str(output),
    ]
    completed = subprocess.run(command, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if completed.returncode != 0:
        raise IntakeError(f"{runtime} native-to-portable projection failed: {completed.stdout.strip()}")


def intake(root: Path, campaign_dir: Path, out: Path) -> dict[str, Any]:
    root = root.resolve()
    campaign_dir = campaign_dir.resolve()
    out = out.resolve()
    try:
        campaign_dir.relative_to(root)
    except ValueError as exc:
        raise IntakeError("campaign directory must stay inside Digital Worker repository") from exc
    campaign = load_json(campaign_dir / "campaign.json", "R2 intake campaign")
    require(campaign.get("schema") == CAMPAIGN_SCHEMA, "unsupported R2 intake campaign schema")
    campaign_id = campaign.get("campaign_id")
    frozen_digest = campaign.get("frozen_inputs_sha256")
    dw_commit = campaign.get("digital_worker_commit")
    target_base = campaign.get("target_base_commit")
    require(isinstance(campaign_id, str) and campaign_id, "campaign_id is missing")
    require(isinstance(frozen_digest, str) and SHA256.fullmatch(frozen_digest) is not None, "frozen_inputs_sha256 is invalid")
    require(isinstance(dw_commit, str) and FULL_SHA.fullmatch(dw_commit) is not None, "digital_worker_commit is invalid")
    require(isinstance(target_base, str) and FULL_SHA.fullmatch(target_base) is not None, "target_base_commit is invalid")
    canonical_plan = regular_under(campaign_dir, campaign.get("frozen_plan"), "frozen_plan")
    plan = load_json(canonical_plan, "canonical frozen plan")
    require(plan.get("schema") == "digital-worker-runtime-r2-plan/v1", "frozen plan schema mismatch")
    require(plan.get("frozen_inputs_sha256") == frozen_digest, "campaign/frozen-plan digest mismatch")
    controlled = plan.get("controlled_task")
    require(isinstance(controlled, dict), "frozen controlled task missing")
    require(controlled.get("run_id") == campaign_id, "campaign id does not match frozen plan")
    require(controlled.get("exact_base_commit") == target_base, "campaign target base does not match frozen plan")
    governance = plan.get("digital_worker_governance")
    require(isinstance(governance, dict) and governance.get("provider_commit") == dw_commit, "campaign Digital Worker identity does not match frozen plan")

    evidence = campaign.get("runtime_evidence")
    require(isinstance(evidence, dict) and set(evidence) == set(RUNTIMES), "runtime_evidence must contain exactly codex + claude-code")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    portable_digests: dict[str, str] = {}
    provider_actors: dict[str, str] = {}
    workflow_runs: dict[str, str] = {}
    result_archives: dict[str, dict[str, str]] = {}

    for runtime, spec in RUNTIMES.items():
        item = evidence[runtime]
        require(isinstance(item, dict), f"{runtime} evidence descriptor must be an object")
        require(item.get("repository") == spec["repository"], f"{runtime} evidence repository mismatch")
        require(item.get("signer_workflow") == spec["signer_workflow"], f"{runtime} signer workflow mismatch")
        workflow_sha = item.get("workflow_sha")
        run_id = str(item.get("workflow_run_id") or "")
        require(isinstance(workflow_sha, str) and FULL_SHA.fullmatch(workflow_sha) is not None, f"{runtime} workflow_sha invalid")
        require(run_id.isdigit(), f"{runtime} workflow_run_id invalid")
        item = dict(item, workflow_sha=workflow_sha, workflow_run_id=run_id)
        subject = regular_under(campaign_dir, item.get("subject"), f"{runtime}.subject")
        attestation = regular_under(campaign_dir, item.get("attestation"), f"{runtime}.attestation")
        verify_attestation(subject, attestation, runtime, item)
        runtime_out = out / runtime
        extracted = runtime_out / "evidence"
        safe_extract_tar(subject, extracted)
        validate_bundle_manifest(extracted, runtime, item)
        embedded_plan = extracted / "frozen-plan.json"
        require(embedded_plan.is_file(), f"{runtime} bundle missing frozen-plan.json")
        require(sha256_file(embedded_plan) == sha256_file(canonical_plan), f"{runtime} frozen plan is not byte-identical to canonical campaign plan")
        native = extracted / spec["native"]
        require(native.is_file(), f"{runtime} native receipt missing")
        portable = runtime_out / "portable-receipt.json"
        runtime_out.mkdir(parents=True, exist_ok=True)
        project_portable(root, runtime, native, canonical_plan, portable)
        portable_doc = load_json(portable, f"{runtime} portable receipt")
        require(portable_doc.get("status") == "completed", f"{runtime} portable receipt must be completed")
        require(portable_doc.get("frozen_inputs_sha256") == frozen_digest, f"{runtime} portable receipt frozen digest mismatch")
        require(portable_doc.get("verification_pass_claimed") is False, f"{runtime} portable receipt must disclaim Verification PASS")
        auth = load_json(extracted / "provider-authorization.json", f"{runtime} provider authorization")
        require(auth.get("authorized") is True and auth.get("verification_or_release_authority") is False, f"{runtime} provider authorization boundary invalid")
        require(auth.get("frozen_inputs_sha256") == frozen_digest, f"{runtime} provider authorization frozen digest mismatch")
        actor = auth.get("actor")
        require(isinstance(actor, str) and actor, f"{runtime} provider actor missing")
        result_archive = extracted / "result-tree.tar.gz"
        require(result_archive.is_file(), f"{runtime} replay result archive missing")
        result_tree = runtime_out / "result-tree"
        safe_extract_tar(result_archive, result_tree)
        portable_digests[runtime] = sha256_file(portable)
        provider_actors[runtime] = actor
        workflow_runs[runtime] = run_id
        result_archives[runtime] = {"path": str(result_archive), "sha256": sha256_file(result_archive)}

    collection = {
        "schema": "digital-worker-runtime-r2-attested-intake/v1",
        "status": "provider-executions-collected-pending-digital-worker-verification-review",
        "campaign_id": campaign_id,
        "frozen_inputs_sha256": frozen_digest,
        "digital_worker_commit": dw_commit,
        "verification_pass_claimed": False,
        "r2_qualified": False,
        "execution_receipts": portable_digests,
        "provider_execution_actors": provider_actors,
        "provider_workflow_runs": workflow_runs,
        "result_archives": result_archives,
    }
    (out / "intake-collection.json").write_text(json.dumps(collection, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return collection


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify attested runtime-owned R2 evidence before Digital Worker Verification")
    parser.add_argument("--root", default=".", type=Path)
    parser.add_argument("--campaign-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--summary-json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = intake(args.root, args.campaign_dir, args.out)
    except (OSError, IntakeError, json.JSONDecodeError, tarfile.TarError) as exc:
        print(json.dumps({"schema":"digital-worker-runtime-r2-attested-intake/v1","status":"blocked","error":str(exc)}, sort_keys=True))
        return 2
    if args.summary_json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(f"R2 attested intake: {result['status']} campaign={result['campaign_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
