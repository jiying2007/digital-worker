#!/usr/bin/env python3
"""Validate canonical Edge Foundation Pilot operational contracts."""
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
PILOT = EDGE / "pilot"


def load_json(path: Path): return json.loads(path.read_text(encoding="utf-8"))
def load_yaml(path: Path): return yaml.safe_load(path.read_text(encoding="utf-8"))
def require(condition: bool, message: str):
    if not condition: raise AssertionError(message)
def validate(path: Path, schema: Path):
    schema_doc = load_json(schema); Draft202012Validator.check_schema(schema_doc); Draft202012Validator(schema_doc).validate(load_json(path))


def main():
    plan = load_yaml(PILOT / "pilot-plan.yaml"); requirements = load_yaml(PILOT / "artifact-requirements.yaml")
    run_schema = load_json(ROOT / "schemas" / "pilot-run.v1.schema.json"); run_properties = set(run_schema["properties"]); common = requirements["common"]
    require(plan["artifact_requirements"] == "artifact-requirements.yaml", "Pilot plan must point to artifact requirements")
    require(set(plan["tracks"]) == set(requirements["tracks"]), "Pilot plan/artifact track drift")
    require("reproduction_or_log" in plan["tracks"]["debug"]["required_evidence"], "Debug must preserve reproduction-or-log semantics")
    review_policy = plan["current_stage_review_policy"]
    require(review_policy["stage"] == "iterative-pilot", "review relaxation is only valid for iterative-pilot stage")
    require(review_policy["independent_review"] == "preferred-but-not-required-when-unavailable", "current-stage review policy drift")
    substitute = review_policy["unavailable_review_substitute"]
    require(set(substitute["required_evidence"]) == {"verification_report", "static_checks", "hosted_ci"}, "review substitute must remain Verification + static + hosted CI")
    for key in ["evidence_must_be_traceable", "unavailability_must_be_recorded", "does_not_imply_independent_review_pass", "does_not_imply_release_approval"]: require(substitute.get(key) is True, f"review substitute guard disabled: {key}")
    release_guards = review_policy["review_release_guards"]
    for key in ["device_or_release_evidence_still_required", "human_a7_release_gate_still_required_for_release_action", "hosted_ci_must_not_imply_device_or_release_pass"]: require(release_guards.get(key) is True, f"release guard disabled: {key}")
    for key in ["real_run_requires_exact_base_commit", "real_run_requires_full_40_hex_base_commit", "all_refs_must_resolve_inside_run_directory", "evidence_bundle_required_for_completed_run", "completed_run_is_terminal", "completed_bundle_hashes_revalidated", "superseding_run_required_for_completed_correction"]: require(common.get(key) is True, f"Pilot trust requirement disabled: {key}")
    require(common["current_stage_review_policy"] == "independent-review-optional-when-unavailable", "artifact review policy drift")
    for track, cfg in requirements["tracks"].items():
        require(cfg["required_refs"], f"Pilot track missing structured refs: {track}")
        require("verification_report_ref" in cfg["required_refs"], f"Verification must remain required: {track}")
        require("review_report_ref" not in cfg["required_refs"], f"Independent Review must not hard-block iterative Pilot: {track}")
        for field in cfg["required_refs"]: require(field in run_properties, f"unknown Pilot ref: {track}/{field}")
    require(run_schema["properties"]["base_commit"].get("pattern") == "^[0-9a-fA-F]{40}$", "Pilot base_commit must be full 40-hex")
    validate(ROOT / "tests/fixtures/engineering-task-package.valid.json", EDGE / "schemas/engineering-task-package.schema.json")
    validate(ROOT / "tests/fixtures/delivery-receipt.valid.json", ROOT / "schemas/delivery-receipt.v1.schema.json")
    validate(ROOT / "tests/fixtures/verification-report.valid.json", EDGE / "schemas/verification-report.schema.json")
    validate(ROOT / "tests/fixtures/review-report.valid.json", EDGE / "schemas/review-report.schema.json")
    validate(ROOT / "tests/fixtures/pilot-result.feature.valid.json", ROOT / "schemas/pilot-result.v1.schema.json")
    validate(ROOT / "tests/fixtures/material-manifest.valid.json", EDGE / "schemas/material-manifest.schema.json")
    pilot_cli = (ROOT / "scripts/embedded_pilot.py").read_text(encoding="utf-8")
    for marker in ["exact_git_sha", "validate_bundle_integrity", "TERMINAL_STATUSES", "superseding run", "pilot-receipt", "product-readiness"]: require(marker in pilot_cli, f"Pilot CLI missing terminal marker: {marker}")
    scaffold = (ROOT / "scripts/embedded_pilot_scaffold.py").read_text(encoding="utf-8")
    for marker in ["reproduction_or_log", 'material_item("reproduction"', 'material_item("log"']: require(marker in scaffold, f"Pilot scaffold missing marker: {marker}")
    require((ROOT / "scripts/validate_material_manifest.py").is_file(), "material validator missing")
    require((ROOT / "schemas/pilot-evidence-bundle.v1.schema.json").is_file(), "evidence bundle schema missing")
    require((ROOT / "schemas/pilot-status.v1.schema.json").is_file(), "Pilot status schema missing")
    require((ROOT / "schemas/edge-foundation-pilot-receipt.v1.schema.json").is_file(), "canonical Pilot receipt schema missing")
    require((ROOT / "schemas/edge-foundation-product-readiness.v1.schema.json").is_file(), "product-readiness schema missing")
    print("Edge Foundation Pilot operations validation PASS: canonical target runtime, immutable evidence, optional unavailable-review policy, product readiness decoupled from routing")


if __name__ == "__main__": main()
