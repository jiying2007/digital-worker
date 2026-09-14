#!/usr/bin/env python3
"""Generate a non-applying canonical-routing switch dry-run plan.

This consumes an independently reviewable phase-3 review package and freezes the
only change classes that a future canonical switch PR may contain. It never
changes routing and never authorizes automatic application.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = ROOT / "domains" / "edge-foundation" / "domain.yaml"
MAPPING = ROOT / "domains" / "edge-foundation" / "compatibility" / "embedded-1plus7-mapping.yaml"
REVIEW_SCHEMA = ROOT / "schemas" / "edge-foundation-phase3-review-package.v1.schema.json"
PLAN_SCHEMA = ROOT / "schemas" / "edge-foundation-canonical-switch-plan.v1.schema.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_json(value: dict, schema_path: Path) -> None:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_plan(review_package_path: Path) -> dict:
    review_package_path = review_package_path.resolve()
    review = load_json(review_package_path)
    validate_json(review, REVIEW_SCHEMA)

    require(review["status"] == "READY_FOR_INDEPENDENT_REVIEW", "phase-3 review package is not ready")
    require(review["readiness_status"] == "ELIGIBLE_FOR_REVIEW", "review package is not backed by eligible readiness")
    require(review["canonical_routing_currently_switched"] is False, "canonical routing is already switched")
    require(review["automatic_apply_allowed"] is False, "review package must forbid automatic apply")
    require(review["current_routing_authority"] == "legacy-embedded-1plus7", "unexpected current routing authority")
    require(review["proposed_routing_authority"] == "edge-foundation", "unexpected proposed routing authority")

    domain = load_yaml(DOMAIN)
    mapping = load_yaml(MAPPING)
    compatibility = domain["legacy_compatibility"]
    require(compatibility["canonical_routing_switched"] is False, "domain contract already marks canonical routing switched")
    require(compatibility["automatic_canonical_switch_forbidden"] is True, "automatic switch must remain forbidden")
    require(compatibility["legacy_machine_contract_preserved"] is True, "legacy compatibility must remain preserved")

    phases = {item["id"]: item for item in mapping["phases"]}
    require(phases["phase-3-canonical-switch"]["status"] == "blocked-on-evidence", "phase-3 status drift before switch review")
    require(phases["phase-4-deprecation"]["status"] == "blocked-on-phase-3", "phase-4 must remain separate from phase-3")
    require(phases["phase-5-removal"]["status"] == "blocked-on-real-pilot", "phase-5 must remain separate from phase-3")

    forbidden = [
        "legacy-identity-removal",
        "legacy-identity-deprecation",
        "skill-owner-rewrite",
        "pilot-threshold-change",
        "action-authority-expansion",
        "verification-independence-change",
        "review-independence-change",
        "provider-binding-change",
        "source-of-truth-authority-change",
        "production-ready-claim",
    ]
    invariants = list(review["migration_invariants"])
    required_invariants = {
        "no-verification-self-approval-regression",
        "no-review-independence-regression",
        "no-provider-binding-regression",
        "source-of-truth-stays-at-source",
    }
    require(required_invariants.issubset(set(invariants)), "review package is missing required migration invariants")

    plan = {
        "schema_version": 1,
        "status": "DRY_RUN_ONLY",
        "review_package_sha256": sha256(review_package_path),
        "review_package_status": review["status"],
        "current_canonical_authority": review["current_routing_authority"],
        "proposed_canonical_authority": review["proposed_routing_authority"],
        "canonical_routing_switched": False,
        "apply_allowed": False,
        "allowed_change_classes": [
            "canonical-routing-authority",
            "migration-phase-status",
            "routing-selector-entrypoint",
        ],
        "forbidden_change_classes": forbidden,
        "required_preserved_invariants": invariants,
        "required_followup_phases": ["phase-4-deprecation", "phase-5-removal"],
        "rollback_authority": "legacy-embedded-1plus7",
        "evidence_run_ids": list(review["evidence_run_ids"]),
    }
    validate_json(plan, PLAN_SCHEMA)
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review_package", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    plan = build_plan(args.review_package)
    rendered = json.dumps(plan, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    print(
        "edge-foundation canonical switch dry-run PASS: "
        f"evidence_runs={len(plan['evidence_run_ids'])} apply_allowed={plan['apply_allowed']}"
    )


if __name__ == "__main__":
    main()
