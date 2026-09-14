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
    base_pattern = run_schema["properties"]["base_commit"].get("pattern")
    assert_true(base_pattern == "^[0-9a-fA-F]{40}$", "pilot-run schema must require full 40-hex base commit when present")

    for track, cfg in requirements["tracks"].items():
        assert_true(cfg["required_refs"], f"pilot track must require at least one structured ref: {track}")
        for field in cfg["required_refs"]:
            assert_true(field in run_properties, f"artifact requirements references unknown pilot-run field: {track} -> {field}")
        for kind in cfg["required_extra_artifacts"]:
            assert_true(kind and isinstance(kind, str), f"invalid required extra artifact kind: {track}")

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
    print("embedded pilot operations validation PASS: plan/requirements/fixtures/CLI/material readiness semantics are consistent")


if __name__ == "__main__":
    main()
