#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "domains/edge-foundation/pilot/evidence/FEATURE-PCR02-OTA-001"
TASK_BRIEF = EVIDENCE_ROOT / "task-brief.json"
ENGINEERING_PACKAGE = EVIDENCE_ROOT / "engineering-task-package.json"
PILOT_RESULT = EVIDENCE_ROOT / "pilot-result.json"
MATERIAL_MANIFEST = EVIDENCE_ROOT / "extras/material_manifest.json"
CROSS_REPO_LOCK = ROOT / "config/integrations/cross-repo-lock.json"
CONTRACT_CATALOG = ROOT / "contracts/catalog.json"
R2_ADK_RELEASE_LOCK = ROOT / "manifests/r2_frozen_adk_release.lock.json"
DOMAIN_REF = "domains/edge-foundation/runtime/workflow.yaml"
ROUTING_REF = "domains/edge-foundation/routing.yaml"
PORTABLE_SCHEMA = "digital-worker-runtime-portability-receipt/v1"
R2_RUN_ID = "R2-FEATURE-PCR02-OTA-001"
R2_PACKAGE_ID = "ETP-PCR02-OTA-R2-001"
FULL_SHA = __import__("re").compile(r"^[0-9a-f]{40}$")
SHA256 = __import__("re").compile(r"^[0-9a-f]{64}$")


class R2EvidenceError(RuntimeError):
    pass


def _load(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise R2EvidenceError(f"invalid {label}: {path}") from exc
    if not isinstance(value, dict):
        raise R2EvidenceError(f"{label} must be a JSON object")
    return value


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise R2EvidenceError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout.strip()


def _require_full_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or FULL_SHA.fullmatch(value) is None:
        raise R2EvidenceError(f"{label} must be an exact 40-hex commit")
    return value


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256.fullmatch(value) is None:
        raise R2EvidenceError(f"{label} must be a lowercase SHA-256")
    return value


def _contains_forbidden_decision_claim(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in {
                "verification_pass",
                "verification_status",
                "domain_verification_status",
                "release_ready",
                "domain_gate_pass",
            }:
                if item is True or (
                    isinstance(item, str)
                    and item.lower() in {"pass", "passed", "success", "ready"}
                ):
                    return True
            if _contains_forbidden_decision_claim(item):
                return True
    elif isinstance(value, list):
        return any(_contains_forbidden_decision_claim(item) for item in value)
    return False


def _repo_url(owner_repo: str) -> str:
    if not isinstance(owner_repo, str) or owner_repo.count("/") != 1 or owner_repo.startswith("http"):
        raise R2EvidenceError(f"invalid canonical owner/repo identity: {owner_repo!r}")
    return f"https://github.com/{owner_repo}.git"


def _runtime_binding_snapshot(lock: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    bindings = lock.get("runtime_bindings")
    if not isinstance(bindings, Mapping):
        raise R2EvidenceError("cross-repo runtime bindings are missing")
    result: dict[str, dict[str, Any]] = {}
    for runtime, target in (("codex", "codex-cli"), ("claude-code", "claude-code")):
        raw = bindings.get(runtime)
        if not isinstance(raw, Mapping):
            raise R2EvidenceError(f"direct runtime binding is missing: {runtime}")
        repository = raw.get("repository")
        if not isinstance(repository, str) or repository != f"jiying2007/{'codex' if runtime == 'codex' else 'claude'}":
            raise R2EvidenceError(f"direct runtime binding repository drift: {runtime}")
        if raw.get("runtime_target") != target:
            raise R2EvidenceError(f"direct runtime binding target drift: {runtime}")
        if raw.get("source_identity_mode") != "exact-release-source-blobs":
            raise R2EvidenceError(f"direct runtime source identity drift: {runtime}")
        readiness = raw.get("runtime_readiness")
        if readiness not in {"SOURCE_SET_BOUND", "SOURCE_SET_READY_R1"}:
            raise R2EvidenceError(f"direct runtime binding is not R1-ready: {runtime}")
        result[runtime] = {
            "repository": repository,
            "ref": raw.get("ref"),
            "commit": _require_full_sha(raw.get("commit"), f"{runtime} binding commit"),
            "runtime_target": target,
            "source_identity_mode": "exact-release-source-blobs",
            "runtime_readiness": readiness,
            "contract": raw.get("contract"),
            "contract_version": raw.get("contract_version"),
            "contract_canonical_sha256": _require_sha256(
                raw.get("contract_canonical_sha256"), f"{runtime} binding contract digest"
            ),
            "execution_receipt_schema": raw.get("execution_receipt_schema"),
            "execution_receipt_schema_version": raw.get("execution_receipt_schema_version"),
        }
    return result


def build_plan(
    root: Path,
    *,
    digital_worker_commit: str,
    target_head: str,
    target_clean: bool,
) -> dict[str, Any]:
    root = root.resolve()
    task = _load(root / TASK_BRIEF.relative_to(ROOT), "task brief")
    package = _load(root / ENGINEERING_PACKAGE.relative_to(ROOT), "engineering task package")
    pilot = _load(root / PILOT_RESULT.relative_to(ROOT), "pilot result")
    material = _load(root / MATERIAL_MANIFEST.relative_to(ROOT), "material manifest")
    lock = _load(root / CROSS_REPO_LOCK.relative_to(ROOT), "cross-repo lock")
    r2_adk_lock = _load(
        root / R2_ADK_RELEASE_LOCK.relative_to(ROOT),
        "R2 frozen ADK release lock",
    )
    catalog_path = root / CONTRACT_CATALOG.relative_to(ROOT)
    if not catalog_path.is_file():
        raise R2EvidenceError("contract catalog is missing")
    for ref in (DOMAIN_REF, ROUTING_REF):
        if not (root / ref).is_file():
            raise R2EvidenceError(f"required governance ref is missing: {ref}")

    base = _require_full_sha(task.get("base_branch_or_commit"), "task brief base")
    if package.get("base_commit") != base:
        raise R2EvidenceError("engineering package base commit does not match task brief")
    if target_head != base:
        raise R2EvidenceError(f"target checkout HEAD mismatch: expected {base}, got {target_head}")
    if target_clean is not True:
        raise R2EvidenceError("R2 frozen task requires a clean exact-base target checkout")
    dw_commit = _require_full_sha(digital_worker_commit, "digital-worker commit")
    if task.get("work_item_id") != "PCR02-OTA-ARTIFACT-IDENTITY-V1.1.21":
        raise R2EvidenceError("unexpected work item identity")
    if pilot.get("source_type") != "real" or pilot.get("run_id") != "FEATURE-PCR02-OTA-001":
        raise R2EvidenceError("candidate task is not the expected real Feature Pilot")
    route = pilot.get("route")
    if not isinstance(route, dict) or not route.get("actual_mode"):
        raise R2EvidenceError("pilot workflow mode is missing")
    if material.get("readiness") != "READY" or material.get("missing_critical") != []:
        raise R2EvidenceError("material manifest is not READY")

    knowledge = lock.get("providers", {}).get("knowledge_control_plane")
    assets = lock.get("providers", {}).get("agent_asset_control_plane")
    if not isinstance(knowledge, dict) or not isinstance(assets, dict):
        raise R2EvidenceError("cross-repo knowledge/asset providers are missing")
    runtime_bindings = _runtime_binding_snapshot(lock)
    knowledge_commit = _require_full_sha(knowledge.get("commit"), "knowledge provider commit")
    knowledge_digest = _require_sha256(
        knowledge.get("contract_canonical_sha256"), "knowledge contract digest"
    )
    if r2_adk_lock.get("schema") != "digital-worker-r2-frozen-adk-release-lock/v1":
        raise R2EvidenceError("R2 frozen ADK release lock schema is unsupported")
    if r2_adk_lock.get("status") != "immutable-release":
        raise R2EvidenceError("R2 frozen ADK release lock must describe an immutable release")
    if r2_adk_lock.get("scope") != "runtime-r2-freeze-only":
        raise R2EvidenceError("R2 frozen ADK release lock scope drifted")
    if r2_adk_lock.get("repository") != assets.get("repository"):
        raise R2EvidenceError("R2 frozen ADK release repository does not match the ADK provider")
    release_meta = r2_adk_lock.get("release")
    if not isinstance(release_meta, Mapping) or release_meta.get("immutable") is not True:
        raise R2EvidenceError("R2 frozen ADK release must be remotely immutable")
    promotion_meta = r2_adk_lock.get("promotion")
    if not isinstance(promotion_meta, Mapping) or promotion_meta.get("release_eligible") is not True:
        raise R2EvidenceError("R2 frozen ADK release must be promotion-eligible")
    boundary = r2_adk_lock.get("boundary")
    if (
        not isinstance(boundary, Mapping)
        or boundary.get("generic_cross_repo_provider_contract_is_not_r2_release_authority") is not True
        or boundary.get("release_identity_must_not_follow_agent_dev_kit_main") is not True
        or boundary.get("provider_execution_authorized") is not False
    ):
        raise R2EvidenceError("R2 frozen ADK release authority boundary is incomplete")
    version = r2_adk_lock.get("version")
    tag = r2_adk_lock.get("tag")
    if not isinstance(version, str) or not version or tag != f"v{version}":
        raise R2EvidenceError("R2 frozen ADK release version/tag identity is invalid")
    adk_release = {
        "repository": r2_adk_lock.get("repository"),
        "version": version,
        "tag": tag,
        "commit": _require_full_sha(r2_adk_lock.get("commit"), "ADK release commit"),
        "tree": _require_full_sha(r2_adk_lock.get("tree"), "ADK release tree"),
        "manifest_blob": _require_full_sha(r2_adk_lock.get("manifest_blob"), "ADK manifest blob"),
        "artifact_sha256": _require_sha256(
            r2_adk_lock.get("artifact_sha256"), "ADK release artifact digest"
        ),
    }

    governance = {
        "provider": "digital-worker",
        "repository": "jiying2007/digital-worker",
        "provider_commit": dw_commit,
        "contract_catalog_ref": CONTRACT_CATALOG.relative_to(ROOT).as_posix(),
        "contract_catalog_digest": _file_digest(catalog_path),
        "selected_domain_refs": [DOMAIN_REF],
        "selected_routing_refs": [ROUTING_REF],
        "materially_used_domain_skills": [],
    }
    governance_ref = f"sha256:{_digest(governance)}"

    knowledge_material = {
        "provider": "knowledge-hub",
        "repository": knowledge.get("repository"),
        "provider_commit": knowledge_commit,
        "contract": knowledge.get("contract"),
        "contract_canonical_sha256": knowledge_digest,
        "knowledge_refs": task.get("knowledge_refs", []),
    }
    knowledge_fingerprint = f"sha256:{_digest(knowledge_material)}"

    material_ref = MATERIAL_MANIFEST.relative_to(ROOT).as_posix()
    package_ref = ENGINEERING_PACKAGE.relative_to(ROOT).as_posix()
    material_sha = _file_digest(root / material_ref)
    package_sha = _file_digest(root / package_ref)
    r2_package = dict(package)
    r2_package.update(
        {
            "package_id": R2_PACKAGE_ID,
            "work_item_id": task["work_item_id"],
            "run_id": R2_RUN_ID,
            "task_type": task.get("type"),
            "workflow_mode": route["actual_mode"],
            "acceptance_criteria": task.get("acceptance_criteria", []),
            "required_verification": task.get("required_verification", {}),
            "material_manifest_ref": material_ref,
            "material_manifest_sha256": material_sha,
            "source_feature_pilot_run_id": pilot["run_id"],
            "source_engineering_task_package_ref": package_ref,
            "source_engineering_task_package_sha256": package_sha,
        }
    )
    r2_package_sha = _digest(r2_package)

    comparison_source_set = {
        "digital_worker_governance_identity_ref": governance_ref,
        "knowledge_context_fingerprint": knowledge_fingerprint,
        "adk_release": adk_release,
        "runtime_bindings": runtime_bindings,
        "engineering_task_package_sha256": r2_package_sha,
        "material_manifest_sha256": material_sha,
        "target_repository": package.get("repo_root"),
        "exact_base_commit": base,
    }
    comparison_source_set_ref = f"sha256:{_digest(comparison_source_set)}"

    controlled_task = {
        "work_item_id": task["work_item_id"],
        "run_id": R2_RUN_ID,
        "task_type": task.get("type"),
        "workflow_mode": route["actual_mode"],
        "repo_root": package.get("repo_root"),
        "exact_base_commit": base,
        "dirty_baseline": False,
        "digital_worker_governance_identity_ref": governance_ref,
        "material_manifest": {"ref": material_ref, "sha256": material_sha},
        "knowledge_context_fingerprint": knowledge_fingerprint,
        "engineering_task_package": {
            "package_id": R2_PACKAGE_ID,
            "sha256": r2_package_sha,
            "source_ref": package_ref,
            "source_sha256": package_sha,
        },
        "acceptance_criteria": task.get("acceptance_criteria", []),
        "required_verification": task.get("required_verification", {}),
        "adk_release_identity_ref": "manifests/r2_frozen_adk_release.lock.json",
        "adk_asset_profile": assets.get("required_asset_profile"),
        "runtime_source_set_identity_ref": comparison_source_set_ref,
    }
    frozen_digest = _digest(controlled_task)
    prompt = (
        "Execute the frozen PCR02 OTA artifact-identity engineering task from the exact base commit. "
        "Use only the supplied frozen task/package/material inputs. Do not read or reuse another runtime's output or patch. "
        "Implement the acceptance criteria in the target worktree, run the required host verification, and do not push, release, "
        "write devices, or claim Verification PASS/Product Ready/Release Ready. Leave the resulting patch only in the local worktree."
    )
    return {
        "schema": "digital-worker-runtime-r2-plan/v1",
        "status": "ready-for-manual-provider-execution",
        "source_feature_pilot": "FEATURE-PCR02-OTA-001",
        "controlled_task": controlled_task,
        "frozen_inputs_sha256": frozen_digest,
        "digital_worker_governance": governance,
        "knowledge_context": knowledge_material,
        "adk_release_identity": adk_release,
        "runtime_bindings": runtime_bindings,
        "comparison_source_set": comparison_source_set,
        "engineering_task_package": r2_package,
        "prompt": prompt,
        "provider_execution_authorized": False,
        "automatic_execution_enabled": False,
    }


def prepare(root: Path, target_root: Path) -> dict[str, Any]:
    target_root = target_root.resolve()
    target_head = _git(target_root, "rev-parse", "HEAD")
    clean = _git(target_root, "status", "--porcelain=v1", "--untracked-files=all") == ""
    dw_commit = _git(root.resolve(), "rev-parse", "HEAD")
    return build_plan(root, digital_worker_commit=dw_commit, target_head=target_head, target_clean=clean)


def _portable_identity_from_codex(native: Mapping[str, Any]) -> dict[str, Any]:
    binding = native.get("runtime_binding")
    runtime = native.get("runtime")
    if not isinstance(binding, Mapping) or not isinstance(runtime, Mapping):
        raise R2EvidenceError("Codex native receipt runtime binding/runtime identity is missing")
    return {
        "runtime_binding_repository": _repo_url(str(binding.get("repository"))),
        "runtime_binding_commit": _require_full_sha(
            binding.get("commit"), "Codex runtime binding commit"
        ),
        "runtime_target": binding.get("target"),
        "runtime_profile": binding.get("runtime_profile"),
        "runtime_host": binding.get("runtime_host"),
        "runtime_provider": runtime.get("provider"),
        "runtime_version": runtime.get("cli_version"),
        "runtime_source_set_identity_ref": binding.get("source_set_identity_ref"),
        "runtime_distribution_identity_ref": binding.get("runtime_distribution_identity_ref"),
    }


def _portable_identity_from_claude(native: Mapping[str, Any]) -> dict[str, Any]:
    identity = native.get("runtime_identity")
    if not isinstance(identity, Mapping):
        raise R2EvidenceError("Claude native receipt runtime_identity is missing")
    result = dict(identity)
    repository = str(result.get("runtime_binding_repository") or "")
    if repository == "jiying2007/claude":
        result["runtime_binding_repository"] = _repo_url(repository)
    return result


def _validate_identity_against_frozen_binding(
    runtime: str,
    identity: Mapping[str, Any],
    plan: Mapping[str, Any],
) -> None:
    bindings = plan.get("runtime_bindings")
    if not isinstance(bindings, Mapping):
        raise R2EvidenceError("R2 frozen plan runtime bindings are missing")
    expected = bindings.get(runtime)
    if not isinstance(expected, Mapping):
        raise R2EvidenceError(f"R2 frozen plan direct binding is missing: {runtime}")
    comparisons = {
        "runtime_binding_repository": _repo_url(str(expected.get("repository"))),
        "runtime_binding_commit": expected.get("commit"),
        "runtime_target": expected.get("runtime_target"),
    }
    for field, value in comparisons.items():
        if identity.get(field) != value:
            raise R2EvidenceError(f"{runtime} native receipt does not match frozen direct binding: {field}")


def _validate_codex_agent_assets(native: Mapping[str, Any], plan: Mapping[str, Any]) -> None:
    assets = native.get("agent_assets")
    release = plan.get("adk_release_identity")
    if not isinstance(assets, Mapping) or not isinstance(release, Mapping):
        raise R2EvidenceError("Codex native receipt ADK identity is missing")
    expected = {
        "provider_repository": release.get("repository"),
        "release_version": release.get("version"),
        "release_tag": release.get("tag"),
        "release_commit": release.get("commit"),
        "asset_profile": plan.get("controlled_task", {}).get("adk_asset_profile")
        if isinstance(plan.get("controlled_task"), Mapping)
        else None,
    }
    for field, value in expected.items():
        if assets.get(field) != value:
            raise R2EvidenceError(f"Codex native receipt ADK identity drift: {field}")


def project_receipt(
    root: Path,
    *,
    runtime: str,
    native_receipt: Path,
    frozen_plan: Path,
) -> dict[str, Any]:
    native = _load(native_receipt, f"{runtime} native receipt")
    plan = _load(frozen_plan, "R2 frozen plan")
    if plan.get("schema") != "digital-worker-runtime-r2-plan/v1":
        raise R2EvidenceError("unsupported R2 frozen plan")
    frozen_digest = _require_sha256(plan.get("frozen_inputs_sha256"), "frozen inputs digest")
    controlled = plan.get("controlled_task")
    if not isinstance(controlled, Mapping) or _digest(controlled) != frozen_digest:
        raise R2EvidenceError("frozen plan controlled_task digest mismatch")
    if _contains_forbidden_decision_claim(native):
        raise R2EvidenceError(
            "native runtime receipt contains a forbidden Verification/Release decision claim"
        )

    if runtime == "codex":
        if native.get("schema_version") != 2:
            raise R2EvidenceError("Codex native receipt schema_version must be 2")
        execution = native.get("execution")
        repository = native.get("repository")
        if not isinstance(execution, Mapping) or execution.get("status") != "completed":
            raise R2EvidenceError("Codex native execution must be completed")
        if (
            native.get("work_item_id") != controlled.get("work_item_id")
            or native.get("run_id") != controlled.get("run_id")
        ):
            raise R2EvidenceError(
                "Codex native receipt work/run identity does not match frozen task"
            )
        if (
            not isinstance(repository, Mapping)
            or repository.get("base_commit") != controlled.get("exact_base_commit")
        ):
            raise R2EvidenceError(
                "Codex native receipt base commit does not match frozen task"
            )
        _validate_codex_agent_assets(native, plan)
        identity = _portable_identity_from_codex(native)
    elif runtime == "claude-code":
        if (
            native.get("schema_version") != 2
            or native.get("status") != "completed"
            or native.get("runtime") != "claude-code"
        ):
            raise R2EvidenceError("Claude native receipt is not a completed v2 receipt")
        if native.get("frozen_inputs_sha256") != frozen_digest:
            raise R2EvidenceError("Claude native receipt frozen task digest mismatch")
        if native.get("verification_pass_claimed") is not False:
            raise R2EvidenceError("Claude native receipt must disclaim Verification PASS")
        identity = _portable_identity_from_claude(native)
    else:
        raise R2EvidenceError(f"unsupported runtime: {runtime}")

    required = (
        "runtime_binding_repository",
        "runtime_binding_commit",
        "runtime_target",
        "runtime_profile",
        "runtime_host",
        "runtime_provider",
        "runtime_version",
        "runtime_source_set_identity_ref",
        "runtime_distribution_identity_ref",
    )
    missing = [key for key in required if not identity.get(key)]
    if missing:
        raise R2EvidenceError(
            "portable runtime identity is incomplete: " + ", ".join(missing)
        )
    _validate_identity_against_frozen_binding(runtime, identity, plan)
    native_sha = _file_digest(native_receipt)
    return {
        "schema": PORTABLE_SCHEMA,
        "status": "completed",
        "runtime": runtime,
        "frozen_inputs_sha256": frozen_digest,
        "verification_pass_claimed": False,
        "runtime_identity": identity,
        "native_receipt": {
            "ref": native_receipt.name,
            "sha256": native_sha,
        },
        "evidence_refs": [f"native-receipt:sha256:{native_sha}"],
    }


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepare and project fail-closed real R2 runtime portability evidence."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("prepare")
    p.add_argument("--root", default=".")
    p.add_argument("--target-root", required=True)
    p.add_argument("--output", required=True)

    r = sub.add_parser("project-receipt")
    r.add_argument("--root", default=".")
    r.add_argument("--runtime", choices=("codex", "claude-code"), required=True)
    r.add_argument("--native-receipt", required=True)
    r.add_argument("--frozen-plan", required=True)
    r.add_argument("--output", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            value = prepare(Path(args.root), Path(args.target_root))
        else:
            value = project_receipt(
                Path(args.root),
                runtime=args.runtime,
                native_receipt=Path(args.native_receipt),
                frozen_plan=Path(args.frozen_plan),
            )
        _write_json(Path(args.output), value)
        print(
            json.dumps(
                {"status": "pass", "command": args.command, "output": args.output},
                sort_keys=True,
            )
        )
        return 0
    except R2EvidenceError as exc:
        print(
            json.dumps(
                {"status": "blocked", "command": args.command, "reason": str(exc)},
                sort_keys=True,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
