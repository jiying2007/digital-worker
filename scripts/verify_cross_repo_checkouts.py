#!/usr/bin/env python3
"""Verify exact cross-repo pins against real provider checkouts.

By default this verifies repositories already present below --root. With --fetch it
creates detached, depth-1 checkouts from the exact SHAs in cross-repo-lock.json.
The report is deterministic evidence that a lock points to a real commit and the
contracts at that commit still have the expected canonical JSON digests/versions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "config" / "integrations" / "cross-repo-lock.json"
EXPECTED_REPOS = {
    "knowledge_control_plane": "jiying2007/knowledge-hub",
    "agent_asset_control_plane": "jiying2007/agent-dev-kit",
    "runtime_practice_eval": "jiying2007/llm_agent",
    "codex": "jiying2007/codex",
    "codex_review_safe": "jiying2007/codex-review",
}


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


def verify_runtime_practice_eval(entry: dict, destination: Path) -> dict:
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
    if candidates.get("codex", {}).get("status") != "source-set-bound":
        fail("runtime_practice_eval: pinned Codex comparison binding is not source-set-bound")
    if candidates.get("claude-code", {}).get("status") != "future-binding":
        fail("runtime_practice_eval: second runtime blocker must remain future-binding until real provider evidence exists")

    certifier_text = paths["certifier"].read_text(encoding="utf-8")
    for marker in [
        'TERMINAL_EVIDENCE_LEVEL = "R2-real-provider-substitution"',
        'DEFAULT_EVIDENCE = "reports/long-term-assets/runtime-portability-current.json"',
        "class PortabilityBlocked",
        "LTA-02 requires at least two real runtime execution receipts",
        "execution receipt contains a forbidden verification PASS claim",
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
    requirements = {
        item.get("id"): item
        for item in qualification.get("blocking_requirements", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    lta02 = requirements.get("LTA-02")
    if not isinstance(lta02, dict):
        fail("runtime_practice_eval: LTA-02 qualification requirement missing")
    expected_lta02 = {
        "status": "blocked_external_evidence",
        "implementation_status": "certifier-ready",
        "required_evidence_level": evidence_level,
        "certifier": "tools.control_plane.runtime_portability",
        "default_evidence_path": "reports/long-term-assets/runtime-portability-current.json",
        "remaining_external_blocker": "second-real-runtime-provider-binding-and-R2-comparison-evidence",
    }
    for key, expected in expected_lta02.items():
        if lta02.get(key) != expected:
            fail(f"runtime_practice_eval: LTA-02 {key} drift: {lta02.get(key)!r} != {expected!r}")
    if lta02.get("required_healthy_runtime_bindings", 0) < 2:
        fail("runtime_practice_eval: LTA-02 must require at least two healthy runtime bindings")
    if lta02.get("r1_binding_conformance_is_terminal_evidence") is not False:
        fail("runtime_practice_eval: R1 binding conformance must remain non-terminal")

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
        "remaining_external_blocker": lta02["remaining_external_blocker"],
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


def verify_one(name: str, entry: dict, destination: Path, fetch: bool) -> dict:
    repo = entry["repository"]
    expected_repo = EXPECTED_REPOS[name]
    if repo != expected_repo:
        fail(f"{name}: repository is not approved: {repo}")
    commit = entry["commit"]
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
        report["runtime_portability"] = verify_runtime_practice_eval(entry, destination)

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

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="directory containing provider checkouts")
    parser.add_argument("--fetch", action="store_true", help="fetch exact locked SHAs from approved public GitHub repositories")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    if lock.get("schema_version") != 4:
        fail("cross-repo checkout verifier requires source-set lock schema v4")
    entries = {
        "knowledge_control_plane": lock["providers"]["knowledge_control_plane"],
        "agent_asset_control_plane": lock["providers"]["agent_asset_control_plane"],
        "runtime_practice_eval": lock["providers"]["runtime_practice_eval"],
        "codex": lock["runtime_bindings"]["codex"],
    }
    args.root.mkdir(parents=True, exist_ok=True)
    results = []
    for name, entry in entries.items():
        destination = args.root / name
        results.append(verify_one(name, entry, destination, args.fetch))
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
