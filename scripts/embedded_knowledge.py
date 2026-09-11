#!/usr/bin/env python3
"""Embedded knowledge adapter.

The local registry is a bootstrap/internal-seed catalog only. Long-term knowledge
context, evidence packs and proposal lifecycle are delegated to Knowledge Hub.
This adapter never upgrades a candidate into a verified fact and never bypasses
source authority/version/ACL/provenance checks.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "expert-groups" / "embedded-system" / "knowledge" / "registry.yaml"
LOCK = ROOT / "config" / "integrations" / "cross-repo-lock.json"


def load_registry():
    doc = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    defaults = doc.get("defaults", {})
    entries = []
    for raw in doc.get("entries", []):
        item = dict(defaults)
        item.update(raw)
        entries.append(item)
    return doc, entries


def load_lock() -> dict:
    return json.loads(LOCK.read_text(encoding="utf-8"))


def terms(text: str) -> set[str]:
    return {part.lower() for part in re.findall(r"[A-Za-z0-9_+.-]+|[\u4e00-\u9fff]{2,}", text or "")}


def searchable(entry: dict) -> str:
    values = [
        entry.get("knowledge_id", ""), entry.get("title", ""), entry.get("domain", ""),
        entry.get("knowledge_type", ""), entry.get("authority", ""), entry.get("owner", ""),
        entry.get("source_provider", ""), entry.get("source_ref", ""),
        " ".join(entry.get("tags", []) or []),
        " ".join(entry.get("product_scope", []) or []),
        " ".join(entry.get("platform_scope", []) or []),
    ]
    return " ".join(str(v) for v in values).lower()


def score(entry: dict, query_terms: set[str]) -> int:
    if not query_terms:
        return 1
    haystack = searchable(entry)
    total = 0
    for token in query_terms:
        if token in haystack:
            total += 2
        if token in {str(x).lower() for x in (entry.get("tags") or [])}:
            total += 2
        if token == str(entry.get("domain", "")).lower():
            total += 3
    return total


def filter_entries(entries: list[dict], args) -> list[tuple[int, dict]]:
    query_terms = terms(args.text)
    result = []
    for entry in entries:
        if args.domain and entry.get("domain") != args.domain:
            continue
        if args.type and entry.get("knowledge_type") != args.type:
            continue
        if args.tag and args.tag not in (entry.get("tags") or []):
            continue
        item_score = score(entry, query_terms)
        if args.text and item_score == 0:
            continue
        result.append((item_score, entry))
    result.sort(key=lambda pair: (-pair[0], pair[1].get("knowledge_id", "")))
    return result[: args.limit]


def print_markdown(result: list[tuple[int, dict]]):
    print("| ID | Title | Domain | Authority | Source | Score |")
    print("|---|---|---|---|---|---:|")
    for item_score, entry in result:
        title = str(entry.get("title", "")).replace("|", "\\|")
        source = str(entry.get("source_ref", "")).replace("|", "\\|")
        print(f"| {entry['knowledge_id']} | {title} | {entry.get('domain','')} | {entry.get('authority','')} | `{source}` | {item_score} |")


def cmd_query(args):
    """Bootstrap-only local catalog query."""
    doc, entries = load_registry()
    result = filter_entries(entries, args)
    if args.format == "json":
        print(json.dumps({
            "mode": "bootstrap-local-catalog",
            "registry_id": doc.get("registry_id"),
            "registry_status": doc.get("status"),
            "query": args.text,
            "results": [{"score": item_score, **entry} for item_score, entry in result],
            "warning": "Candidate list only; prefer Knowledge Hub context/evidence-pack for task use.",
        }, ensure_ascii=False, indent=2))
    else:
        print(f"Bootstrap Registry: {doc.get('registry_id')} / {doc.get('status')} / provider={doc.get('provider_binding')}")
        print_markdown(result)
        print("\nCandidate list only. Prefer `context` / `evidence-pack`; source ACL/version/provenance must still be checked.")


def cmd_verify(_args):
    doc, entries = load_registry()
    missing = []
    duplicate = []
    seen = set()
    for entry in entries:
        kid = entry.get("knowledge_id")
        if kid in seen:
            duplicate.append(kid)
        seen.add(kid)
        if entry.get("source_provider") == "git":
            ref = entry.get("source_ref")
            if not ref or not (ROOT / ref).exists():
                missing.append({"knowledge_id": kid, "source_ref": ref})
    lock = load_lock()
    provider = lock.get("providers", {}).get("knowledge_control_plane", {})
    report = {
        "registry_id": doc.get("registry_id"),
        "status": doc.get("status"),
        "entry_count": len(entries),
        "duplicate_ids": duplicate,
        "missing_git_sources": missing,
        "knowledge_control_plane": provider,
        "valid": not duplicate and not missing and bool(provider.get("commit")),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["valid"]:
        raise SystemExit(2)


def hub_root(args) -> Path:
    raw = getattr(args, "hub_root", None) or os.environ.get("KNOWLEDGE_HUB_ROOT")
    if not raw:
        print(json.dumps({"status": "BLOCKED", "reason": "KNOWLEDGE_HUB_ROOT not configured"}, ensure_ascii=False))
        raise SystemExit(2)
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        print(json.dumps({"status": "BLOCKED", "reason": f"knowledge-hub root not found: {root}"}, ensure_ascii=False))
        raise SystemExit(2)
    return root


def run_hub(args, wrapper: str, wrapper_args: list[str]):
    root = hub_root(args)
    tool = root / "tools" / wrapper
    if not tool.is_file():
        print(json.dumps({"status": "BLOCKED", "reason": f"Knowledge Hub surface missing: {wrapper}"}, ensure_ascii=False))
        raise SystemExit(2)
    completed = subprocess.run(["bash", str(tool), *wrapper_args], cwd=root, text=True, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def cmd_adapter_status(args):
    lock = load_lock()
    provider = lock["providers"]["knowledge_control_plane"]
    raw = args.hub_root or os.environ.get("KNOWLEDGE_HUB_ROOT")
    root = Path(raw).expanduser().resolve() if raw else None
    surfaces = ["knowledge-context.sh", "knowledge-evidence-pack.sh", "knowledge-action-check.sh", "knowledge-proposal-route.sh"]
    available = bool(root and root.is_dir() and all((root / "tools" / name).is_file() for name in surfaces))
    print(json.dumps({
        "status": "READY" if available else "BLOCKED",
        "provider": provider,
        "configured_root": str(root) if root else None,
        "required_surfaces": surfaces,
        "available": available,
    }, ensure_ascii=False, indent=2))
    if not available:
        raise SystemExit(2)


def cmd_context(args):
    command = ["--cwd", args.cwd, "--query", args.query, "--task-type", args.task_type,
               "--context-budget", args.context_budget, "--limit", str(args.limit), "--summary-json"]
    if args.telemetry:
        command.append("--telemetry")
    run_hub(args, "knowledge-context.sh", command)


def cmd_evidence_pack(args):
    run_hub(args, "knowledge-evidence-pack.sh", [args.query, "--scope-ref", args.scope_ref, "--json"])


def cmd_action_check(args):
    run_hub(args, "knowledge-action-check.sh", ["--task", args.task, "--candidate", args.candidate, "--scope-ref", args.scope_ref, "--json"])


def cmd_proposal_route(args):
    proposal = Path(args.proposal).expanduser().resolve()
    if not proposal.is_file():
        raise SystemExit(f"proposal file missing: {proposal}")
    run_hub(args, "knowledge-proposal-route.sh", ["--proposal", str(proposal), "--json"])


def add_hub_root(parser):
    parser.add_argument("--hub-root", help="Knowledge Hub checkout; alternatively set KNOWLEDGE_HUB_ROOT")


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    query = sub.add_parser("query", help="Bootstrap-only local internal-seed query")
    query.add_argument("--text", default="")
    query.add_argument("--domain")
    query.add_argument("--type")
    query.add_argument("--tag")
    query.add_argument("--limit", type=int, default=10)
    query.add_argument("--format", choices=["markdown", "json"], default="markdown")
    query.set_defaults(func=cmd_query)

    verify = sub.add_parser("verify")
    verify.set_defaults(func=cmd_verify)

    status = sub.add_parser("adapter-status")
    add_hub_root(status)
    status.set_defaults(func=cmd_adapter_status)

    context = sub.add_parser("context")
    add_hub_root(context)
    context.add_argument("--cwd", required=True)
    context.add_argument("--query", required=True)
    context.add_argument("--task-type", default="general")
    context.add_argument("--context-budget", choices=["small", "normal", "deep"], default="small")
    context.add_argument("--limit", type=int, default=3)
    context.add_argument("--telemetry", action="store_true")
    context.set_defaults(func=cmd_context)

    evidence = sub.add_parser("evidence-pack")
    add_hub_root(evidence)
    evidence.add_argument("--query", required=True)
    evidence.add_argument("--scope-ref", required=True)
    evidence.set_defaults(func=cmd_evidence_pack)

    action = sub.add_parser("action-check")
    add_hub_root(action)
    action.add_argument("--task", required=True)
    action.add_argument("--candidate", required=True)
    action.add_argument("--scope-ref", required=True)
    action.set_defaults(func=cmd_action_check)

    proposal = sub.add_parser("proposal-route")
    add_hub_root(proposal)
    proposal.add_argument("--proposal", required=True)
    proposal.set_defaults(func=cmd_proposal_route)
    return parser


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
