#!/usr/bin/env python3
"""Verify exact cross-repo pins against real provider checkouts.

By default this verifies repositories already present below --root. With --fetch it
creates detached, depth-1 checkouts from the exact SHAs in cross-repo-lock.json.
The report is deterministic evidence that a lock points to a real commit and the
contract at that commit still has the expected canonical JSON digest/version.
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
    contract_rel = entry["contract"]
    contract = destination / contract_rel
    if not contract.is_file():
        fail(f"{name}: contract missing at locked commit: {contract_rel}")
    doc = json.loads(contract.read_text(encoding="utf-8"))
    actual_version = str(doc.get("contract_version"))
    if actual_version != str(entry["contract_version"]):
        fail(f"{name}: contract version mismatch: {actual_version} != {entry['contract_version']}")
    actual_digest = canonical_digest(contract)
    expected_digest = entry["contract_canonical_sha256"]
    if actual_digest != expected_digest:
        fail(f"{name}: contract canonical SHA256 mismatch: {actual_digest} != {expected_digest}")
    report = {
        "name": name,
        "repository": repo,
        "commit": actual_commit,
        "contract": contract_rel,
        "contract_version": actual_version,
        "contract_canonical_sha256": actual_digest,
        "status": "PASS",
    }
    if name == "agent_asset_control_plane":
        second_rel = entry["runtime_binding_contract"]
        second = destination / second_rel
        if not second.is_file():
            fail(f"{name}: runtime binding contract missing: {second_rel}")
        second_digest = canonical_digest(second)
        if second_digest != entry["runtime_binding_contract_canonical_sha256"]:
            fail(f"{name}: runtime binding contract digest mismatch")
        report["runtime_binding_contract"] = second_rel
        report["runtime_binding_contract_canonical_sha256"] = second_digest
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="directory containing provider checkouts")
    parser.add_argument("--fetch", action="store_true", help="fetch exact locked SHAs from approved public GitHub repositories")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    lock = json.loads(LOCK.read_text(encoding="utf-8"))
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
        "schema_version": 1,
        "lock_schema_version": lock["schema_version"],
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
