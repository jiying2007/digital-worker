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
    plan_path = PILOT / "pilot-plan.yaml"
    requirements_path = PILOT / "artifact-requirements.yaml"
    plan = load_yaml(plan_path)
    requirements = load_yaml(requirements_path)
    run_schema = load_json(ROOT / "schemas" / "pilot-run.v1.schema.json")
    run_properties = set(run_schema["properties"])

    assert_true(plan["artifact_requirements"] == "artifact-requirements.yaml", "pilot plan must point to artifact-requirements.yaml")
    assert_true(set(plan["tracks"]) == set(requirements["tracks"]), "pilot plan and artifact requirements track sets differ")
    assert_true(requirements["common"]["real_run_requires_exact_base_commit"] is True, "real pilots must require exact base commit")
    assert_true(requirements["common"]["all_refs_must_resolve_inside_run_directory"] is True, "pilot refs must remain inside run directory")
    assert_true(requirements["common"]["evidence_bundle_required_for_completed_run"] is True, "completed pilots must require evidence bundle")

    for track, cfg in requirements["tracks"].items():
        assert_true(cfg["required_refs"], f"pilot track must require at least one structured ref: {track}")
        for field in cfg["required_refs"]:
            assert_true(field in run_properties, f"artifact requirements references unknown pilot-run field: {track} -> {field}")
        for kind in cfg["required_extra_artifacts"]:
            assert_true(kind and isinstance(kind, str), f"invalid required extra artifact kind: {track}")

    validate(ROOT / "tests" / "fixtures" / "engineering-task-package.valid.json", EMB / "schemas" / "engineering-task-package.schema.json")
    validate(ROOT / "tests" / "fixtures" / "verification-report.valid.json", EMB / "schemas" / "verification-report.schema.json")
    validate(ROOT / "tests" / "fixtures" / "review-report.valid.json", EMB / "schemas" / "review-report.schema.json")
    validate(ROOT / "tests" / "fixtures" / "pilot-result.feature.valid.json", ROOT / "schemas" / "pilot-result.v1.schema.json")

    assert_true((ROOT / "scripts" / "embedded_pilot.py").is_file(), "embedded pilot CLI missing")
    assert_true((ROOT / "schemas" / "pilot-evidence-bundle.v1.schema.json").is_file(), "pilot evidence bundle schema missing")
    assert_true((ROOT / "schemas" / "pilot-status.v1.schema.json").is_file(), "pilot status schema missing")
    print("embedded pilot operations validation PASS: plan/requirements/fixtures/CLI are consistent")


if __name__ == "__main__":
    main()
