#!/usr/bin/env python3
"""Query the provider-neutral Embedded Knowledge Registry.

This tool returns Registry candidates only. It does not fetch external knowledge,
bypass source ACLs, or upgrade a Registry entry into a verified task fact.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "expert-groups" / "embedded-system" / "knowledge" / "registry.yaml"


def load_registry():
    doc = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    defaults = doc.get("defaults", {})
    entries = []
    for raw in doc.get("entries", []):
        item = dict(defaults)
        item.update(raw)
        entries.append(item)
    return doc, entries


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
        s = score(entry, query_terms)
        if args.text and s == 0:
            continue
        result.append((s, entry))
    result.sort(key=lambda pair: (-pair[0], pair[1].get("knowledge_id", "")))
    return result[: args.limit]


def print_markdown(result: list[tuple[int, dict]]):
    print("| ID | Title | Domain | Authority | Source | Score |")
    print("|---|---|---|---|---|---:|")
    for s, entry in result:
        title = str(entry.get("title", "")).replace("|", "\\|")
        source = str(entry.get("source_ref", "")).replace("|", "\\|")
        print(f"| {entry['knowledge_id']} | {title} | {entry.get('domain','')} | {entry.get('authority','')} | `{source}` | {s} |")


def cmd_query(args):
    doc, entries = load_registry()
    result = filter_entries(entries, args)
    if args.format == "json":
        print(json.dumps({
            "registry_id": doc.get("registry_id"),
            "registry_status": doc.get("status"),
            "query": args.text,
            "results": [{"score": s, **entry} for s, entry in result],
        }, ensure_ascii=False, indent=2))
    else:
        print(f"Registry: {doc.get('registry_id')} / {doc.get('status')} / provider={doc.get('provider_binding')}")
        print_markdown(result)
        print("\nCandidate list only: source ACL/version/provenance must still be checked at task use time.")


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
    report = {
        "registry_id": doc.get("registry_id"),
        "status": doc.get("status"),
        "entry_count": len(entries),
        "duplicate_ids": duplicate,
        "missing_git_sources": missing,
        "valid": not duplicate and not missing,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["valid"]:
        raise SystemExit(2)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    query = sub.add_parser("query")
    query.add_argument("--text", default="")
    query.add_argument("--domain")
    query.add_argument("--type")
    query.add_argument("--tag")
    query.add_argument("--limit", type=int, default=10)
    query.add_argument("--format", choices=["markdown", "json"], default="markdown")
    query.set_defaults(func=cmd_query)

    verify = sub.add_parser("verify")
    verify.set_defaults(func=cmd_verify)
    return parser


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
