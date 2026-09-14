#!/usr/bin/env python3
"""Generate a non-applying phase-3 canonical-routing review package.

This tool never switches routing. It only produces a review artifact after the
phase-3 readiness gate is already ELIGIBLE_FOR_REVIEW.
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
READINESS_SCHEMA = ROOT / "schemas" / "edge-foundation-phase3-readiness.v1.schema.json"
PACKAGE_SCHEMA = ROOT / "schemas" / "edge-foundation-phase3-review-package.v1.schema.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_json(doc: dict, schema_path: Path) -> None:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(doc)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_package(readiness_path: Path) -> dict:
    readiness = load_json(readiness_path)
    validate_json(readiness, READINESS_SCHEMA)

    require(readiness["status"] == "ELIGIBLE_FOR_REVIEW", "phase-3 readiness is not ELIGIBLE_FOR_REVIEW")
    require(readiness["eligible_for_phase3_review"] is True, "phase-3 review eligibility is false")
    require(readiness["canonical_routing_switched"] is False, "canonical routing is already switched")
    require(not readiness["blockers"], f"phase-3 readiness still has blockers: {readiness['blockers']}")

    domain = load_yaml(DOMAIN)
    mapping = load_yaml(MAPPING)
    compatibility = domain["legacy_compatibility"]
    require(compatibility["canonical_routing_switched"] is False, "domain contract already marks canonical routing switched")
    require(compatibility["migration_phase"] == "phase-2-dual-evaluation", "review package may only be prepared from phase-2")

    phases = {item["id"]: item for item in mapping["phases"]}
    require(phases["phase-3-canonical-switch"]["status"] == "blocked-on-evidence", "unexpected phase-3 migration status")

    invariants = list(mapping["migration_invariants"])
    required_invariants = {
        "no-legacy-identity-orphan",
        "no-verification-self-approval-regression",
        "no-review-independence-regression",
        "no-provider-binding-regression",
        "source-of-truth-stays-at-source",
    }
    require(required_invariants.issubset(set(invariants)), "required migration invariants are missing")

    package = {
        "schema_version": 1,
        "status": "READY_FOR_INDEPENDENT_REVIEW",
        "readiness_status": readiness["status"],
        "readiness_sha256": file_sha256(readiness_path),
        "evidence_run_ids": list(readiness["evidence_run_ids"]),
        "current_routing_authority": "legacy-embedded-1plus7",
        "proposed_routing_authority": "edge-foundation",
        "canonical_routing_currently_switched": False,
        "automatic_apply_allowed": False,
        "migration_invariants": invariants,
        "proposed_changes": [
            "set-edge-foundation-as-canonical-routing-authority",
            "mark-phase-2-dual-evaluation-completed",
            "mark-phase-3-canonical-switch-completed-after-independent-review",
            "preserve-legacy-1plus7-as-compatibility-surface",
        ],
        "explicit_non_goals": [
            "do-not-deprecate-legacy-identities-in-phase-3",
            "do-not-remove-legacy-identities-in-phase-3",
            "do-not-expand-a0-a7-authority",
            "do-not-change-verification-or-review-independence",
            "do-not-bind-orchestration-to-a-specific-provider",
        ],
        "rollback_plan": [
            "restore-legacy-embedded-1plus7-as-canonical-routing-authority",
            "set-canonical-routing-switched-false",
            "retain-all-pilot-shadow-receipts-and-readiness-evidence",
            "record-switch-failure-as-new-evidence-before-another-review",
        ],
        "required_review_checks": [
            "readiness-artifact-identity-verified",
            "all-evidence-run-ids-traceable",
            "legacy-compatibility-preserved",
            "verification-independence-preserved",
            "review-independence-preserved",
            "provider-neutrality-preserved",
            "source-of-truth-authority-preserved",
            "rollback-plan-accepted",
        ],
    }
    validate_json(package, PACKAGE_SCHEMA)
    return package


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("readiness", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        package = build_package(args.readiness)
    except (AssertionError, Exception) as exc:
        # jsonschema and parse failures also fail closed as exit=2 for review preparation.
        print(f"phase-3 review package BLOCKED: {exc}")
        raise SystemExit(2)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "phase-3 review package READY_FOR_INDEPENDENT_REVIEW: "
        f"runs={len(package['evidence_run_ids'])} readiness_sha256={package['readiness_sha256']}"
    )


if __name__ == "__main__":
    main()
