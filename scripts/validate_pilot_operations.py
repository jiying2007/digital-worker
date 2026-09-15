#!/usr/bin/env python3
"""Validate pilot operational contracts without executing a real pilot."""
from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EMB = ROOT / "expert-groups" / "embedded-system"
PILOT = EMB / "pilot"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def assert_true(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def validate(path: Path, schema: Path):
    schema_doc = load_json(schema)
    Draft202012Validator.check_schema(schema_doc)
    Draft202012Validator(schema_doc).validate(load_json(path))


def main():
    plan = load_yaml(PILOT / "pilot-plan.yaml")
    requirements = load_yaml(PILOT / "artifact-requirements.yaml")
    run_schema = load_json(ROOT / "schemas" / "pilot-run.v1.schema.json")
    run_properties = set(run_schema["properties"])
    common = requirements["common"]

    assert_true(plan["artifact_requirements"] == "artifact-requirements.yaml", "pilot plan must point to artifact-requirements.yaml")
    assert_true(set(plan["tracks"]) == set(requirements["tracks"]), "pilot plan and artifact requirements track sets differ")
    assert_true(
        "reproduction_or_log" in plan["tracks"]["debug"]["required_evidence"],
        "debug Pilot must preserve reproduction-or-log evidence semantics",
    )

    review_policy = plan["current_stage_review_policy"]
    assert_true(review_policy["stage"] == "iterative-pilot", "review relaxation is only valid for iterative-pilot stage")
    assert_true(
        review_policy["independent_review"] == "preferred-but-not-required-when-unavailable",
        "current-stage review policy drift",
    )
    substitute = review_policy["unavailable_review_substitute"]
    assert_true(
        set(substitute["required_evidence"]) == {"verification_report", "static_checks", "hosted_ci"},
        "review substitute must stay verification + static + hosted CI",
    )
    for key in [
        "evidence_must_be_traceable",
        "unavailability_must_be_recorded",
        "does_not_imply_independent_review_pass",
        "does_not_imply_release_approval",
    ]:
        assert_true(substitute.get(key) is True, f"review-substitute safety requirement disabled: {key}")
    release_guards = review_policy["review_release_guards"]
    for key in [
        "device_or_release_evidence_still_required",
        "human_a7_release_gate_still_required_for_release_action",
        "hosted_ci_must_not_imply_device_or_release_pass",
    ]:
        assert_true(release_guards.get(key) is True, f"review/release guard disabled: {key}")

    for key in [
        "real_run_requires_exact_base_commit",
        "real_run_requires_full_40_hex_base_commit",
        "all_refs_must_resolve_inside_run_directory",
        "evidence_bundle_required_for_completed_run",
        "completed_run_is_terminal",
        "completed_bundle_hashes_revalidated",
        "superseding_run_required_for_completed_correction",
    ]:
        assert_true(common.get(key) is True, f"pilot trust requirement disabled: {key}")
    assert_true(common["current_stage_review_policy"] == "independent-review-optional-when-unavailable", "artifact review policy drift")
    for key in [
        "review_report_optional_for_completion",
        "review_substitute_requires_verification_report",
        "review_substitute_requires_traceable_static_or_hosted_ci_evidence",
        "review_substitute_does_not_imply_independent_review_pass",
        "review_substitute_does_not_imply_release_approval",
    ]:
        assert_true(common.get(key) is True, f"artifact review safety requirement disabled: {key}")

    base_pattern = run_schema["properties"]["base_commit"].get("pattern")
    assert_true(base_pattern == "^[0-9a-fA-F]{40}$", "pilot-run schema must require full 40-hex base commit when present")

    for track, cfg in requirements["tracks"].items():
        assert_true(cfg["required_refs"], f"pilot track must require at least one structured ref: {track}")
        assert_true("verification_report_ref" in cfg["required_refs"], f"Verification must remain required for current-stage completion: {track}")
        assert_true("review_report_ref" not in cfg["required_refs"], f"Independent Review must not hard-block iterative Pilot completion: {track}")
        for field in cfg["required_refs"]:
            assert_true(field in run_properties, f"artifact requirements references unknown pilot-run field: {track} -> {field}")
        for kind in cfg["required_extra_artifacts"]:
            assert_true(kind and isinstance(kind, str), f"invalid required extra artifact kind: {track}")

    assert_true(
        "human_release_decision_when_release_action" in plan["tracks"]["review_release"]["required_evidence"],
        "review/release track must preserve human release decision evidence",
    )
    assert_true(
        "static_ci_or_review_evidence" in plan["tracks"]["review_release"]["required_evidence"],
        "review/release track must preserve static/CI-or-review evidence",
    )

    validate(ROOT / "tests" / "fixtures" / "engineering-task-package.valid.json", EMB / "schemas" / "engineering-task-package.schema.json")
    validate(ROOT / "tests" / "fixtures" / "delivery-receipt.valid.json", ROOT / "schemas" / "delivery-receipt.v1.schema.json")
    validate(ROOT / "tests" / "fixtures" / "verification-report.valid.json", EMB / "schemas" / "verification-report.schema.json")
    validate(ROOT / "tests" / "fixtures" / "review-report.valid.json", EMB / "schemas" / "review-report.schema.json")
    validate(ROOT / "tests" / "fixtures" / "pilot-result.feature.valid.json", ROOT / "schemas" / "pilot-result.v1.schema.json")
    validate(ROOT / "tests" / "fixtures" / "material-manifest.valid.json", EMB / "schemas" / "material-manifest.schema.json")

    pilot_cli = (ROOT / "scripts" / "embedded_pilot.py").read_text(encoding="utf-8")
    for marker in ["exact_git_sha", "validate_bundle_integrity", "TERMINAL_STATUSES", "superseding run"]:
        assert_true(marker in pilot_cli, f"embedded pilot CLI missing trust marker: {marker}")

    scaffold = (ROOT / "scripts" / "embedded_pilot_scaffold.py").read_text(encoding="utf-8")
    for marker in ["reproduction_or_log", 'material_item("reproduction"', 'material_item("log"']:
        assert_true(marker in scaffold, f"Pilot scaffold missing debug evidence-alternative marker: {marker}")
    material_validator = ROOT / "scripts" / "validate_material_manifest.py"
    assert_true(material_validator.is_file(), "material manifest semantic validator missing")
    validator_text = material_validator.read_text(encoding="utf-8")
    for marker in ["recompute_blockers", "reproduction_or_log", "require_terminal_ready", "DEGRADED"]:
        assert_true(marker in validator_text, f"material manifest validator missing semantic marker: {marker}")

    assert_true((ROOT / "schemas" / "pilot-evidence-bundle.v1.schema.json").is_file(), "pilot evidence bundle schema missing")
    assert_true((ROOT / "schemas" / "pilot-status.v1.schema.json").is_file(), "pilot status schema missing")
    print("embedded pilot operations validation PASS: current-stage review is optional when unavailable; Verification/static/CI and release guards remain fail-closed")


if __name__ == "__main__":
    main()
