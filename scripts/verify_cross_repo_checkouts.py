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
