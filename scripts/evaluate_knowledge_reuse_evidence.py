#!/usr/bin/env python3
"""Evaluate whether a real Work Item has machine-auditable Knowledge reuse evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "knowledge-reuse-evidence.v1.schema.json"
LOCK = ROOT / "config" / "integrations" / "cross-repo-lock.json"

PROVIDER_FIELDS = (
    "repository",
    "commit",
    "contract",
    "contract_version",
    "contract_canonical_sha256",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(document: dict) -> dict:
    schema = load_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(document)

    lock = load_json(LOCK)
    expected_provider = lock["providers"]["knowledge_control_plane"]
    actual_provider = document["knowledge_provider"]

    blockers: list[str] = []
    if document["source_type"] != "real":
        blockers.append("synthetic-source-not-eligible")
    if document["evidence_origin"] != "real-run":
        blockers.append("controlled-fixture-not-eligible")

    for field in PROVIDER_FIELDS:
        if actual_provider.get(field) != expected_provider.get(field):
            blockers.append(f"knowledge-provider-identity-mismatch:{field}")

    for index, item in enumerate(document["reuse_items"], start=1):
        prefix = f"reuse-item-{index}"
        if item["source_real"] is not True:
            blockers.append(f"{prefix}:source-not-real")
        if item["acl_state"] != "allowed":
            blockers.append(f"{prefix}:acl-not-allowed")
        if item["freshness_state"] != "fresh":
            blockers.append(f"{prefix}:freshness-not-fresh")
        if item["conflict_state"] != "none":
            blockers.append(f"{prefix}:authority-conflict-unresolved")

    blockers = sorted(set(blockers))
    eligible = not blockers
    return {
        "schema_version": 1,
        "work_item_id": document["work_item_id"],
        "run_id": document["run_id"],
        "status": "ELIGIBLE" if eligible else "BLOCKED",
        "e3_knowledge_reuse_eligible": eligible,
        "qualification_scope": "knowledge-reuse-only",
        "knowledge_provider_identity_ref": "config/integrations/cross-repo-lock.json#/providers/knowledge_control_plane",
        "context_fingerprint": actual_provider["context_fingerprint"],
        "reused_knowledge_ids": [item["knowledge_id"] for item in document["reuse_items"]],
        "reuse_item_count": len(document["reuse_items"]),
        "blockers": blockers,
        "does_not_imply": [
            "knowledge-provider-qualification",
            "product-readiness",
            "terminal-maturity",
            "production-ready",
            "release-ready",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-eligible", action="store_true")
    args = parser.parse_args()

    receipt = evaluate(load_json(args.evidence))
    rendered = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    if args.require_eligible and not receipt["e3_knowledge_reuse_eligible"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
