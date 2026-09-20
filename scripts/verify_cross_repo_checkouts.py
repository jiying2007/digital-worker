#!/usr/bin/env python3
"""Verify exact cross-repo pins against real provider checkouts.

By default this verifies repositories already present below --root. With --fetch it
creates detached, depth-1 checkouts from the exact SHAs in cross-repo-lock.json for public providers. Private providers may instead use a signed Git object proof that is verified offline against a pinned trust key. The report is deterministic evidence that a lock points to an exact provider identity and the contracts at that identity still have the expected canonical JSON digests/versions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from private_provider_proof import ProofError, verify_proof

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "config" / "integrations" / "cross-repo-lock.json"
EXPECTED_REPOS = {
    "knowledge_control_plane": "jiying2007/knowledge-hub",
    "agent_asset_control_plane": "jiying2007/agent-dev-kit",
    "runtime_practice_eval": "jiying2007/llm_agent",
    "codex": "jiying2007/codex",
    "claude-code": "jiying2007/claude",
    "codex_review_safe": "jiying2007/codex-review",
}
READY_RUNTIME_BINDING_STATUSES = {"source-set-bound", "ready", "active"}


def fail(message: str) -> None:
    raise RuntimeError(message)


def run(*args: str, cwd: Path | None = None) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.STDOUT).strip()


def canonical_digest(path: Path) -> str:
    doc = json.loads(path.read_text(encoding="utf-8"))
    payload = json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def checkout(repo: str, commit: str, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    run("git", "init", "--quiet", str(destination))
    run("git", "-C", str(destination), "remote", "add", "origin", f"https://github.com/{repo}.git")
    run("git", "-C", str(destination), "fetch", "--quiet", "--depth=1", "origin", commit)
    run("git", "-C", str(destination), "checkout", "--quiet", "--detach", "FETCH_HEAD")


def fetch_exact_tag(destination: Path, tag: str) -> None:
    """Fetch exactly one tag ref without relying on Git's positional `tag` syntax."""
    if not re_full_tag(tag):
        fail(f"invalid release tag name: {tag}")
    tag_ref = f"refs/tags/{tag}"
    run("git", "-C", str(destination), "fetch", "--quiet", "origin", f"{tag_ref}:{tag_ref}")


def re_full_tag(tag: str) -> bool:
    # Release tags are intentionally simple and must never be interpreted as refspec fragments.
    import re

    return re.fullmatch(r"v[0-9]+(?:\.[0-9]+){2}(?:[-+][0-9A-Za-z.-]+)?", tag) is not None


def verify_contract(
    *,
    name: str,
    destination: Path,
    contract_rel: str,
    expected_version: str,
    expected_digest: str,
) -> dict:
    contract = destination / contract_rel
    if not contract.is_file():
        fail(f"{name}: contract missing at locked commit: {contract_rel}")
    doc = json.loads(contract.read_text(encoding="utf-8"))
    actual_version = str(doc.get("contract_version"))
    if actual_version != str(expected_version):
        fail(f"{name}: contract version mismatch: {actual_version} != {expected_version}")
    actual_digest = canonical_digest(contract)
    if actual_digest != expected_digest:
        fail(f"{name}: contract canonical SHA256 mismatch: {actual_digest} != {expected_digest}")
    return {
        "contract": contract_rel,
        "contract_version": actual_version,
        "contract_canonical_sha256": actual_digest,
    }


def verify_second_runtime_candidate(candidates: dict, approved_binding: dict | None = None) -> str:
    candidate = candidates.get("claude-code")
    if not isinstance(candidate, dict):
        fail("runtime_practice_eval: claude-code comparison candidate is missing")
    if candidate.get("target") != "claude-code":
        fail("runtime_practice_eval: claude-code comparison target drift")

    status = candidate.get("status")
    if status == "future-binding":
        if candidate.get("repository") is not None or candidate.get("source_identity_mode") is not None:
            fail("runtime_practice_eval: future-binding must not claim repository/source-set identity")
        return status

    if status == "binding-candidate-blocked":
        expected = {
            "repository": "jiying2007/claude",
            "source_identity_mode": "exact-release-source-blobs",
            "candidate_pr": "jiying2007/claude#1",
            "blocker_ref": "jiying2007/claude#2",
            "blocker": "github-hosted-runner-admission-before-step-execution",
        }
        for key, value in expected.items():
            if candidate.get(key) != value:
                fail(f"runtime_practice_eval: blocked claude-code candidate {key} drift")
        return status

    if status in READY_RUNTIME_BINDING_STATUSES:
        if not isinstance(approved_binding, dict):
            fail("runtime_practice_eval: claude-code is R1-ready upstream but is not yet an approved Digital Worker runtime binding")
        approved_expected = {
            "repository": "jiying2007/claude",
            "runtime_target": "claude-code",
            "source_identity_mode": "exact-release-source-blobs",
            "runtime_readiness": "SOURCE_SET_READY_R1",
            "verified_runtime_execution_receipt": "PENDING",
            "r2_real_provider_substitution": "PENDING",
        }
        for key, expected in approved_expected.items():
            if approved_binding.get(key) != expected:
                fail(f"runtime_practice_eval: approved claude-code binding {key} drift")
        upstream_expected = {
            "repository": "https://github.com/jiying2007/claude.git",
            "source_identity_mode": "exact-release-source-blobs",
            "binding_commit": approved_binding.get("commit"),
            "r1_binding_conformance": "passed",
            "verified_runtime_execution_receipt": "pending",
            "r2_real_provider_substitution": "pending",
        }
        for key, expected in upstream_expected.items():
            if candidate.get(key) != expected:
                fail(f"runtime_practice_eval: ready claude-code candidate {key} drift")
        return status

    fail(f"runtime_practice_eval: unsupported claude-code candidate status: {status!r}")


def verify_runtime_practice_eval(
    entry: dict,
    destination: Path,
    approved_runtime_bindings: dict | None = None,
) -> dict:
    certifier_rel = entry["runtime_portability_certifier"]
    test_rel = entry["runtime_portability_certifier_test"]
    qualification_rel = entry["runtime_portability_qualification_manifest"]
    cli_rel = entry["runtime_portability_cli_contract"]
    paths = {
        "certifier": destination / certifier_rel,
        "test": destination / test_rel,
        "qualification": destination / qualification_rel,
        "cli": destination / cli_rel,
    }
    for label, path in paths.items():
        if not path.is_file() or path.is_symlink():
            fail(f"runtime_practice_eval: {label} missing or not a regular file at locked commit: {path.relative_to(destination)}")

    contract = json.loads((destination / entry["contract"]).read_text(encoding="utf-8"))
    evidence_level = entry["runtime_portability_evidence_level"]
    if contract.get("terminal_replaceability_evidence_level") != evidence_level:
        fail("runtime_practice_eval: terminal R2 evidence level does not match pinned runtime pilot contract")
    candidates = {item.get("runtime"): item for item in contract.get("candidate_runtime_bindings", []) if isinstance(item, dict)}
    if set(candidates) != {"codex", "claude-code"}:
        fail("runtime_practice_eval: runtime candidate set must be exactly codex + claude-code")
    if candidates.get("codex", {}).get("status") != "source-set-bound":
        fail("runtime_practice_eval: pinned Codex comparison binding is not source-set-bound")
    approved_runtime_bindings = approved_runtime_bindings or {}
    approved_codex = approved_runtime_bindings.get("codex")
    if not isinstance(approved_codex, dict):
        fail("runtime_practice_eval: Codex is R1-ready upstream but is not an approved Digital Worker runtime binding")
    codex_expected = {
        "repository": "https://github.com/jiying2007/codex.git",
        "target": "codex-cli",
        "source_identity_mode": "exact-release-source-blobs",
        "binding_commit": approved_codex.get("commit"),
        "status": "source-set-bound",
    }
    for key, expected in codex_expected.items():
        if candidates["codex"].get(key) != expected:
            fail(f"runtime_practice_eval: ready codex candidate {key} drift")
    second_runtime_status = verify_second_runtime_candidate(
        candidates,
        approved_runtime_bindings.get("claude-code"),
    )

    ownership = contract.get("execution_ownership")
    expected_ownership = {
        "model": "runtime-owned-local-provider-execution+digital-worker-local-verification",
        "provider_credentials_owner": "runtime-local-auth-state",
        "runtime_execution_evidence_transport": "local-terminal-digest-bound-runtime-evidence",
        "digital_worker_holds_provider_credentials": False,
        "local_execution_receipt_is_not_r2_pass": True,
        "runtime_home_mode": "shared-user-home",
        "runtime_local_state_policy": "reuse-local-auth-and-provider-config-exclude-from-evidence",
    }
    if not isinstance(ownership, dict):
        fail("runtime_practice_eval: local-terminal execution ownership missing")
    for key, expected in expected_ownership.items():
        if ownership.get(key) != expected:
            fail(f"runtime_practice_eval: local-terminal execution ownership {key} drift")

    planes = contract.get("execution_plane_evidence")
    if not isinstance(planes, dict):
        fail("runtime_practice_eval: execution plane evidence missing")
    adapter_expected = {
        "codex": ("jiying2007/codex", "scripts/runtime-r2-local.sh", approved_codex.get("commit")),
        "claude-code": (
            "jiying2007/claude",
            "control/scripts/runtime-r2-local.sh",
            (approved_runtime_bindings.get("claude-code") or {}).get("commit"),
        ),
    }
    for runtime, (repository, adapter, commit) in adapter_expected.items():
        plane = planes.get(runtime)
        if not isinstance(plane, dict):
            fail(f"runtime_practice_eval: execution plane missing: {runtime}")
        for key, expected in {
            "repository": repository,
            "execution_plane_commit": commit,
            "frozen_binding_commit": commit,
            "provider_execution_adapter": adapter,
            "execution_venue": "local-terminal",
            "runtime_home_mode": "shared-user-home",
            "credential_state_in_evidence": False,
            "credential_owner": "runtime-local-auth-state",
        }.items():
            if plane.get(key) != expected:
                fail(f"runtime_practice_eval: {runtime} execution plane {key} drift")
        if "provider_execution_workflow" in plane:
            fail(f"runtime_practice_eval: retired provider workflow resurfaced: {runtime}")
    dw_plane = planes.get("digital-worker")
    if not isinstance(dw_plane, dict):
        fail("runtime_practice_eval: digital-worker verification plane missing")
    for key, expected in {
        "repository": "jiying2007/digital-worker",
        "provider_credentials_held": False,
        "combined_provider_workflow_present": False,
        "freeze_workflow": ".github/workflows/runtime-r2-freeze.yml",
        "local_intake": "scripts/runtime_r2_intake.py",
        "local_verifier": "scripts/runtime_r2_local_verify.py",
        "verifier_identity_mode": "receipt-bound-tool-commit",
        "independent_review_workflow": ".github/workflows/runtime-r2-independent-review.yml",
    }.items():
        if dw_plane.get(key) != expected:
            fail(f"runtime_practice_eval: digital-worker verification plane {key} drift")

    certifier_text = paths["certifier"].read_text(encoding="utf-8")
    for marker in [
        'TERMINAL_EVIDENCE_LEVEL = "R2-real-provider-substitution"',
        'DEFAULT_EVIDENCE = "reports/long-term-assets/runtime-portability-current.json"',
        "class PortabilityBlocked",
        "LTA-02 requires at least two real runtime execution receipts",
        "execution receipt contains a forbidden verification PASS claim",
        "provider runtime home mode drift",
        "provider credential state entered evidence",
    ]:
        if marker not in certifier_text:
            fail(f"runtime_practice_eval: portability certifier marker missing: {marker}")

    test_text = paths["test"].read_text(encoding="utf-8")
    for marker in [
        "Missing real comparison evidence is a BLOCKED external-evidence state, never PASS.",
        "self-test-only two-runtime fixture",
        "R1 binding conformance must never qualify terminal portability.",
        "runtime binding is not source-set-bound/ready: claude-code",
    ]:
        if marker not in test_text:
            fail(f"runtime_practice_eval: portability certifier regression marker missing: {marker}")

    qualification = json.loads(paths["qualification"].read_text(encoding="utf-8"))
    if qualification.get("schema") != "llm-agent-long-term-asset-qualification/v2":
        fail("runtime_practice_eval: long-term qualification schema drift")
    requirements = {
        item.get("id"): item
        for item in qualification.get("qualification_requirements", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    lta02 = requirements.get("LTA-02")
    if not isinstance(lta02, dict):
        fail("runtime_practice_eval: LTA-02 qualification requirement missing")
    expected_lta02 = {
        "status": "evidence_collection_in_progress",
        "implementation_status": "certifier-ready",
        "required_evidence_level": evidence_level,
        "certifier": "tools.control_plane.runtime_portability",
        "default_evidence_path": "reports/long-term-assets/runtime-portability-current.json",
        "pending_evidence": "real-codex-and-claude-runtime-execution-receipts-and-same-frozen-task-R2-comparison-evidence",
    }
    for key, expected in expected_lta02.items():
        if lta02.get(key) != expected:
            fail(f"runtime_practice_eval: LTA-02 {key} drift: {lta02.get(key)!r} != {expected!r}")
    if lta02.get("required_healthy_runtime_bindings", 0) < 2:
        fail("runtime_practice_eval: LTA-02 must require at least two healthy runtime bindings")
    if lta02.get("r1_binding_conformance_is_terminal_evidence") is not False:
        fail("runtime_practice_eval: R1 binding conformance must remain non-terminal")
    terminal = qualification.get("terminal")
    if not isinstance(terminal, dict):
        fail("runtime_practice_eval: long-term terminal projection missing")
    if terminal.get("qualified") is not False or terminal.get("status") != "qualification_pending":
        fail("runtime_practice_eval: long-term terminal qualification must remain pending")
    pending = terminal.get("pending_requirements")
    if not isinstance(pending, list) or "LTA-02" not in pending:
        fail("runtime_practice_eval: LTA-02 must remain a terminal pending requirement")

    cli_text = paths["cli"].read_text(encoding="utf-8")
    if '"runtime-portability": "tools.control_plane.runtime_portability"' not in cli_text:
        fail("runtime_practice_eval: runtime-portability CLI surface missing")

    return {
        "status": entry["runtime_portability_status"],
        "certifier": certifier_rel,
        "certifier_test": test_rel,
        "qualification_manifest": qualification_rel,
        "cli_contract": cli_rel,
        "evidence_level": evidence_level,
        "second_runtime_candidate_status": second_runtime_status,
        "pending_evidence": lta02["pending_evidence"],
    }


def verify_signed_provider(name: str, entry: dict) -> dict:
    repo = entry["repository"]
    commit = entry["commit"]
    verification_mode = entry.get("verification_mode")
    if verification_mode != "signed-git-object-proof":
        fail(f"{name}: unsupported verification_mode: {verification_mode}")
    proof_rel = entry.get("verification_proof")
    trust_rel = entry.get("verification_trust_key")
    if not isinstance(proof_rel, str) or not proof_rel or not isinstance(trust_rel, str) or not trust_rel:
        fail(f"{name}: signed private-provider verification metadata is incomplete")
    proof_path = ROOT / proof_rel
    trust_path = ROOT / trust_rel
    if not proof_path.is_file() or not trust_path.is_file():
        fail(f"{name}: signed private-provider proof/trust key is missing")
    try:
        proof_result = verify_proof(
            root=ROOT,
            proof_path=proof_path,
            expected_repository=repo,
            expected_commit=commit,
            expected_contract_path=entry["contract"],
            expected_contract_version=str(entry["contract_version"]),
            expected_contract_digest=entry["contract_canonical_sha256"],
        )
    except ProofError as exc:
        fail(f"{name}: signed private-provider proof failed: {exc}")
    return {
        "name": name,
        "repository": repo,
        "commit": commit,
        "contract": entry["contract"],
        "contract_version": str(entry["contract_version"]),
        "contract_canonical_sha256": entry["contract_canonical_sha256"],
        "verification_mode": verification_mode,
        "proof": proof_rel,
        "proof_root_tree_sha": proof_result["root_tree_sha"],
        "proof_contract_blob_sha": proof_result["contract_blob_sha"],
        "signer_key_fingerprint": proof_result["signer_key_fingerprint"],
        "provider_network_accessed": False,
        "status": "PASS",
    }


def verify_assurance_binding(name: str, entry: dict, destination: Path, fetch: bool) -> dict:
    repo = entry["repository"]
    if repo != EXPECTED_REPOS[name]:
        fail(f"{name}: repository is not approved: {repo}")
    commit = entry["commit"]
    if fetch:
        checkout(repo, commit, destination)
        fetch_exact_tag(destination, entry["release_tag"])
    if not destination.is_dir():
        fail(f"{name}: checkout missing: {destination}")
    actual_commit = run("git", "-C", str(destination), "rev-parse", "HEAD").lower()
    if actual_commit != commit:
        fail(f"{name}: checkout HEAD mismatch: expected {commit}, got {actual_commit}")
    if entry["ref"] != entry["release_tag"]:
        fail(f"{name}: assurance ref must equal immutable release tag")
    actual_tag_commit = run("git", "-C", str(destination), "rev-parse", f"{entry['release_tag']}^{{}}")
    if actual_tag_commit != commit:
        fail(f"{name}: immutable release tag does not peel to locked commit")

    contract_path = destination / entry["product_contract"]
    if not contract_path.is_file():
        fail(f"{name}: product contract missing")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    actual_digest = canonical_digest(contract_path)
    if actual_digest != entry["product_contract_canonical_sha256"]:
        fail(f"{name}: product contract canonical digest mismatch")
    checks = {
        "productContractVersion": entry["product_contract_version"],
        "productId": entry["product_id"],
        "productVersion": entry["product_version"],
        "safeCoreCommit": entry["safe_core_commit"],
        "safeCoreVersion": entry["safe_core_version"],
        "safeCoreRuntimeDigest": entry["safe_core_runtime_digest"],
        "safeCoreGovernanceDigest": entry["safe_core_governance_digest"],
        "reviewReceiptVersion": entry["review_receipt_schema_version"],
    }
    for field, expected in checks.items():
        if contract.get(field) != expected:
            fail(f"{name}: product contract {field} mismatch")
    actual_core_pin = run("git", "-C", str(destination), "rev-parse", "HEAD:src/codex-safe-core")
    if actual_core_pin != entry["safe_core_commit"]:
        fail(f"{name}: Safe Core gitlink mismatch")
    if entry.get("release_immutable") is not True:
        fail(f"{name}: assurance release must be declared immutable")
    if entry.get("validation") != "PINNED_IMMUTABLE_RELEASE_PRODUCT_CONTRACT_VERIFIED_REAL_RUN_USAGE_PENDING":
        fail(f"{name}: real-run usage pending boundary drift")
    return {
        "name": name,
        "repository": repo,
        "commit": actual_commit,
        "release_tag": entry["release_tag"],
        "product_contract": entry["product_contract"],
        "product_contract_version": contract["productContractVersion"],
        "product_contract_canonical_sha256": actual_digest,
        "review_receipt_schema_version": contract["reviewReceiptVersion"],
        "safe_core_commit": actual_core_pin,
        "real_run_usage": "PENDING",
        "status": "PASS",
    }


def verify_one(
    name: str,
    entry: dict,
    destination: Path,
    fetch: bool,
    approved_runtime_bindings: dict | None = None,
) -> dict:
    repo = entry["repository"]
    expected_repo = EXPECTED_REPOS[name]
    if repo != expected_repo:
        fail(f"{name}: repository is not approved: {repo}")
    commit = entry["commit"]
    verification_mode = entry.get("verification_mode")
    if verification_mode == "signed-git-object-proof":
        return verify_signed_provider(name, entry)
    if verification_mode not in (None, "live-checkout"):
        fail(f"{name}: unsupported verification_mode: {verification_mode}")
    if fetch:
        checkout(repo, commit, destination)
    if not destination.is_dir():
        fail(f"{name}: checkout missing: {destination}")
    actual_commit = run("git", "-C", str(destination), "rev-parse", "HEAD").lower()
    if actual_commit != commit:
        fail(f"{name}: checkout HEAD mismatch: expected {commit}, got {actual_commit}")

    primary = verify_contract(
        name=name,
        destination=destination,
        contract_rel=entry["contract"],
        expected_version=str(entry["contract_version"]),
        expected_digest=entry["contract_canonical_sha256"],
    )
    report = {
        "name": name,
        "repository": repo,
        "commit": actual_commit,
        **primary,
        "status": "PASS",
    }

    if name == "agent_asset_control_plane":
        secondary = verify_contract(
            name=f"{name}:runtime-binding",
            destination=destination,
            contract_rel=entry["runtime_binding_contract"],
            expected_version=str(entry["runtime_binding_contract_version"]),
            expected_digest=entry["runtime_binding_contract_canonical_sha256"],
        )
        report["runtime_binding_contract"] = secondary
        baseline = entry["release_baseline"]
        if fetch:
            run("git", "-C", str(destination), "fetch", "--quiet", "--depth=1", "origin", baseline["commit"])
            fetch_exact_tag(destination, baseline["tag"])
        actual_tree = run("git", "-C", str(destination), "rev-parse", f"{baseline['commit']}^{{tree}}")
        actual_manifest_blob = run("git", "-C", str(destination), "rev-parse", f"{baseline['commit']}:manifest.json")
        actual_tag_commit = run("git", "-C", str(destination), "rev-parse", f"{baseline['tag']}^{{}}")
        if actual_tree != baseline["tree"]:
            fail(f"{name}: immutable release tree mismatch")
        if actual_manifest_blob != baseline["manifest_blob"]:
            fail(f"{name}: immutable release manifest blob mismatch")
        if actual_tag_commit != baseline["commit"]:
            fail(f"{name}: immutable release tag does not peel to release commit")
        report["release_baseline"] = baseline

    if name == "runtime_practice_eval":
        report["runtime_portability"] = verify_runtime_practice_eval(
            entry,
            destination,
            approved_runtime_bindings,
        )

    if name == "codex":
        bootstrap = verify_contract(
            name=f"{name}:session-bootstrap",
            destination=destination,
            contract_rel=entry["session_bootstrap_contract"],
            expected_version=str(entry["session_bootstrap_contract_version"]),
            expected_digest=entry["session_bootstrap_contract_canonical_sha256"],
        )
        report["session_bootstrap_contract"] = bootstrap
        binding_doc = json.loads((destination / entry["contract"]).read_text(encoding="utf-8"))
        if binding_doc.get("readiness") != entry["runtime_readiness"]:
            fail(f"{name}: runtime readiness mismatch")
        if binding_doc.get("source_binding", {}).get("identity_mode") != entry["source_identity_mode"]:
            fail(f"{name}: source identity mode mismatch")
        bootstrap_doc = json.loads((destination / entry["session_bootstrap_contract"]).read_text(encoding="utf-8"))
        if bootstrap_doc.get("role") != "thin-session-bootstrap":
            fail(f"{name}: Session Bootstrap role drift")
        for mode in ("L0", "L1", "L2"):
            if mode not in bootstrap_doc.get("modes", {}):
                fail(f"{name}: Session Bootstrap missing mode {mode}")

    if name == "claude-code":
        binding_doc = json.loads((destination / entry["contract"]).read_text(encoding="utf-8"))
        expected_binding = {
            "status": entry["runtime_readiness"],
            "repository": entry["repository"],
            "runtime_target": entry["runtime_target"],
            "source_identity_mode": entry["source_identity_mode"],
            "maturity_level": "R1-binding-conformance",
            "terminal_replaceability_qualified": False,
        }
        for key, expected in expected_binding.items():
            if binding_doc.get(key) != expected:
                fail(f"{name}: binding contract {key} drift")
        if binding_doc.get("agent_dev_kit", {}).get("asset_profile") != entry["required_asset_profile"]:
            fail(f"{name}: required ADK asset profile drift")
        hard_rules = binding_doc.get("hard_rules", {})
        for rule in ("runtime_output_is_not_verification_pass", "r1_is_not_r2", "r2_requires_real_same_task_execution_receipt"):
            if hard_rules.get(rule) is not True:
                fail(f"{name}: R1/R2 hard rule weakened: {rule}")

        bootstrap = verify_contract(
            name=f"{name}:session-bootstrap",
            destination=destination,
            contract_rel=entry["session_bootstrap_contract"],
            expected_version=str(entry["session_bootstrap_contract_version"]),
            expected_digest=entry["session_bootstrap_contract_canonical_sha256"],
        )
        report["session_bootstrap_contract"] = bootstrap
        bootstrap_doc = json.loads((destination / entry["session_bootstrap_contract"]).read_text(encoding="utf-8"))
        if bootstrap_doc.get("role") != "thin-session-bootstrap" or bootstrap_doc.get("runtime_target") != "claude-code":
            fail(f"{name}: Session Bootstrap identity drift")
        for mode in ("L0", "L1", "L2"):
            if mode not in bootstrap_doc.get("modes", {}):
                fail(f"{name}: Session Bootstrap missing mode {mode}")

        receipt_schema_path = destination / entry["execution_receipt_schema"]
        if not receipt_schema_path.is_file() or receipt_schema_path.is_symlink():
            fail(f"{name}: execution receipt schema missing")
        receipt_schema = json.loads(receipt_schema_path.read_text(encoding="utf-8"))
        props = receipt_schema.get("properties", {})
        if props.get("schema_version", {}).get("const") != entry["execution_receipt_schema_version"]:
            fail(f"{name}: execution receipt schema version drift")
        if props.get("runtime", {}).get("const") != "claude-code":
            fail(f"{name}: execution receipt runtime identity drift")
        if props.get("verification_pass_claimed", {}).get("const") is not False:
            fail(f"{name}: execution receipt must forbid verification PASS claims")
        if entry.get("verified_runtime_execution_receipt") != "PENDING":
            fail(f"{name}: verified runtime execution receipt boundary drift")
        if entry.get("r2_real_provider_substitution") != "PENDING":
            fail(f"{name}: R2 boundary drift")
        report["maturity_level"] = "R1-binding-conformance"
        report["verified_runtime_execution_receipt"] = "PENDING"
        report["r2_real_provider_substitution"] = "PENDING"

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="directory containing provider checkouts")
    parser.add_argument("--fetch", action="store_true", help="fetch exact locked SHAs for public providers; signed proofs remain offline")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    if lock.get("schema_version") != 4:
        fail("cross-repo checkout verifier requires source-set lock schema v4")
    runtime_bindings = lock.get("runtime_bindings", {})
    if not isinstance(runtime_bindings, dict):
        fail("cross-repo runtime_bindings must be an object")
    entries = {
        "knowledge_control_plane": lock["providers"]["knowledge_control_plane"],
        "agent_asset_control_plane": lock["providers"]["agent_asset_control_plane"],
        "runtime_practice_eval": lock["providers"]["runtime_practice_eval"],
        "codex": runtime_bindings["codex"],
        "claude-code": runtime_bindings["claude-code"],
    }
    args.root.mkdir(parents=True, exist_ok=True)
    results = []
    for name, entry in entries.items():
        destination = args.root / name
        results.append(verify_one(name, entry, destination, args.fetch, runtime_bindings))
    assurance = lock.get("assurance_bindings", {}).get("codex_review_safe")
    if not isinstance(assurance, dict):
        fail("codex_review_safe assurance binding missing")
    results.append(verify_assurance_binding("codex_review_safe", assurance, args.root / "codex_review_safe", args.fetch))
    report = {
        "schema_version": 2,
        "lock_schema_version": lock["schema_version"],
        "identity_model": "immutable-release-plus-exact-source-set",
        "status": "PASS",
        "verified": results,
    }
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
