#!/usr/bin/env python3
"""Capture immutable local source identity for real Pilot task binding.

This is a pre-init, read-only probe. Its output is deliberately NOT a Material
Manifest, Pilot result, Verification report, Review report, release approval, or
phase-3 evidence. It only records Git source identity and optional evidence-file
digests so operators can bind a real task without inventing immutable facts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def git(repo_root: Path, *args: str, allow_missing: bool = False) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode == 0:
        return completed.stdout.strip()
    if allow_missing:
        return None
    detail = (completed.stderr or completed.stdout or "git command failed").strip()
    raise ValueError(f"git {' '.join(args)} failed: {detail}")


def parse_evidence(values: list[str]) -> list[tuple[str, Path]]:
    parsed: list[tuple[str, Path]] = []
    seen: set[str] = set()
    for value in values:
        if "=" not in value:
            raise ValueError(f"--evidence must be KIND=PATH: {value}")
        kind, raw_path = value.split("=", 1)
        if re.fullmatch(r"[A-Za-z0-9_.-]+", kind) is None:
            raise ValueError(f"invalid evidence kind: {kind}")
        if kind in seen:
            raise ValueError(f"duplicate evidence kind: {kind}")
        seen.add(kind)
        parsed.append((kind, Path(raw_path)))
    return parsed


def build_report(repo_root: Path, evidence: list[tuple[str, Path]]) -> dict:
    requested_root = repo_root.expanduser().resolve()
    if not requested_root.exists():
        raise ValueError(f"repo root does not exist: {requested_root}")

    top_level_raw = git(requested_root, "rev-parse", "--show-toplevel")
    assert top_level_raw is not None
    top_level = Path(top_level_raw).resolve()

    head = git(requested_root, "rev-parse", "--verify", "HEAD")
    assert head is not None
    if re.fullmatch(r"[0-9a-fA-F]{40}", head) is None:
        raise ValueError(f"git HEAD is not a full 40-hex SHA: {head}")
    head = head.lower()

    remote_origin = git(requested_root, "config", "--get", "remote.origin.url", allow_missing=True)
    status = git(requested_root, "status", "--porcelain=v1", "--untracked-files=all")
    assert status is not None
    dirty_lines = [line for line in status.splitlines() if line.strip()]
    clean = not dirty_lines

    evidence_files = []
    for kind, raw_path in evidence:
        path = raw_path.expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"evidence file missing: {path}")
        evidence_files.append(
            {
                "kind": kind,
                "path": str(path),
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    return {
        "schema_version": 1,
        "report_type": "real-pilot-source-probe",
        "generated_at": now_iso(),
        "promotion_eligible": False,
        "source_identity": {
            "requested_root": str(requested_root),
            "git_top_level": str(top_level),
            "head_sha": head,
            "remote_origin": remote_origin,
            "working_tree_clean": clean,
            "dirty_entry_count": len(dirty_lines),
            "dirty_status_sha256": sha256_text(status) if dirty_lines else None,
        },
        "evidence_files": evidence_files,
        "source_identity_ready": clean,
        "not_authoritative_for": [
            "material_readiness",
            "verification",
            "independent_review",
            "release_approval",
            "pilot_outcome",
            "phase3_evidence",
            "canonical_routing_switch",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument(
        "--evidence",
        action="append",
        default=[],
        help="Optional evidence identity to hash, expressed as KIND=PATH. May repeat.",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--require-clean",
        action="store_true",
        help="Exit 2 when the Git worktree is dirty; report is still emitted.",
    )
    args = parser.parse_args()

    report = build_report(args.repo_root, parse_evidence(args.evidence))
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    if args.require_clean and not report["source_identity_ready"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
