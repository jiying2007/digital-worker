#!/usr/bin/env python3
"""Validate the remaining embedded compatibility execution surface plus target-owned evaluation assets."""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
EMB = ROOT / "expert-groups" / "embedded-system"
EDGE = ROOT / "domains" / "edge-foundation"


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parse_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    require(match is not None, f"missing YAML frontmatter: {path}")
    return yaml.safe_load(match.group(1))


def assert_invalid(instance_path: Path, schema_path: Path) -> None:
    try:
        Draft202012Validator(load_json(schema_path)).validate(load_json(instance_path))
    except ValidationError:
        return
    raise AssertionError(f"negative fixture unexpectedly valid: {instance_path}")


def main() -> None:
    group = load_yaml(EMB / "expert-group.yaml")
    task_modes = load_yaml(EMB / "config/task-modes.yaml")
    workflow = load_yaml(EMB / "config/workflow.yaml")
    legacy_skills = load_yaml(EMB / "config/p0-skills.yaml")
    target_domain = load_yaml(EDGE / "domain.yaml")
    target_skills = load_yaml(EDGE / "skills.yaml")
    target_cases = load_yaml(EDGE / "evaluation/golden-cases.yaml")

    require(group.get("architecture_model") == "provider-neutral", "compatibility execution surface must remain provider-neutral")
    require(group["ssot"].get("provider_binding") == "not_frozen", "provider binding must remain not_frozen")
    require(group["knowledge"]["source_of_truth_policy"] == "stays_at_source", "source-of-truth policy drift")

    legacy_ids = {group["team_lead"]["id"], *(item["id"] for item in group["experts"])}
    require(len(legacy_ids) == 8, f"compatibility execution identity set drift: {len(legacy_ids)}")
    for task_type, route in task_modes["routing"].items():
        require(route["primary_experts"], f"legacy execution route lost primary expert: {task_type}")
        for identity in route["primary_experts"]:
            require(identity in legacy_ids, f"legacy execution route references unknown compatibility identity: {task_type} -> {identity}")

    mode_names = set(task_modes["workflow_modes"])
    require(mode_names == set(workflow["mode_paths"]), "compatibility workflow mode set drift")
    require("phase.execution" not in workflow["mode_paths"]["review_only"], "review_only must not execute engineering")
    require(workflow.get("architecture_model") == "provider-neutral", "compatibility workflow must remain provider-neutral")

    legacy_skill_by_id = {item["id"]: item for item in legacy_skills["skills"]}
    target_skill_by_id = {item["id"]: item for item in target_skills["skills"]}
    require(set(legacy_skill_by_id) == set(target_skill_by_id), "compatibility execution Skill set and target ownership registry must cover the same current Skills")
    require(len(legacy_skill_by_id) == 23, f"expected current 23 Skill baseline, got {len(legacy_skill_by_id)}")
    for skill_id, legacy in legacy_skill_by_id.items():
        path = EMB / legacy["path"]
        require(path.is_file(), f"compatibility Skill implementation missing: {skill_id}")
        frontmatter = parse_frontmatter(path)
        require(frontmatter["id"] == skill_id, f"Skill id drift: {skill_id}")
        require(frontmatter["max_action_level"] in {"A0_READ", "A1_ANALYZE", "A2_GENERATE"}, f"baseline Skill exceeds A2: {skill_id}")

    schemas = list((ROOT / "schemas").glob("*.schema.json")) + list((EMB / "schemas").glob("*.schema.json"))
    require(schemas, "no JSON schemas found")
    for schema_path in schemas:
        Draft202012Validator.check_schema(load_json(schema_path))

    task_schema = ROOT / "schemas/task-brief.v1.schema.json"
    receipt_schema = ROOT / "schemas/delivery-receipt.v1.schema.json"
    hil_schema = ROOT / "schemas/hil-evidence.v1.schema.json"
    Draft202012Validator(load_json(task_schema)).validate(load_json(ROOT / "tests/fixtures/task-brief.valid.json"))
    Draft202012Validator(load_json(receipt_schema)).validate(load_json(ROOT / "tests/fixtures/delivery-receipt.valid.json"))
    Draft202012Validator(load_json(hil_schema)).validate(load_json(ROOT / "tests/fixtures/hil-evidence.valid.json"))
    assert_invalid(ROOT / "tests/fixtures/task-brief.invalid.json", task_schema)
    assert_invalid(ROOT / "tests/fixtures/delivery-receipt.invalid.json", receipt_schema)

    # Golden evaluation authority is target-owned. The compatibility path may only be a pointer.
    pointer = load_yaml(EMB / "tests/golden-cases.yaml")
    require(pointer.get("retired") is True, "legacy Golden path must be retired")
    require("cases" not in pointer, "legacy Golden path must not keep a duplicated case dataset")
    require(pointer.get("authority") == "../../../domains/edge-foundation/evaluation/golden-cases.yaml", "legacy Golden pointer authority drift")

    cases = target_cases["cases"]
    case_ids = {case["id"] for case in cases}
    require(len(cases) == len(case_ids) == 12, "target Golden evaluation baseline must contain 12 unique cases")
    domain_experts = {item["id"] for item in target_domain["experts"]}
    embedded = next(item for item in target_domain["experts"] if item["id"] == "embedded-system-expert")
    capability_ids = set(embedded["capabilities"])
    assurance_ids = set(target_domain["assurance"]["responsibilities"])
    for case in cases:
        require(case["task_type"] in task_modes["routing"], f"Golden Case task type has no compatibility execution route: {case['id']}")
        require(set(case["expected_experts"]).issubset(domain_experts), f"Golden Case unknown target Expert: {case['id']}")
        require(set(case.get("expected_capabilities", [])).issubset(capability_ids), f"Golden Case unknown Capability: {case['id']}")
        require(set(case["required_assurance"]).issubset(assurance_ids), f"Golden Case unknown Assurance responsibility: {case['id']}")
        require(case["legacy_execution_mode"] in mode_names, f"Golden Case comparison mode not executable before switch: {case['id']}")

    pilot = load_yaml(EMB / "pilot/pilot-plan.yaml")
    require(set(pilot["tracks"]) == {"debug", "feature", "review_release"}, "Pilot track set drift")
    for track_name, track in pilot["tracks"].items():
        require(track["minimum_real_completed_runs"] >= 1, f"invalid Pilot minimum: {track_name}")
        for task_type in track["candidate_task_types"]:
            require(task_type in task_modes["routing"], f"Pilot task type not executable: {track_name} -> {task_type}")
        for case_id in track["preferred_golden_cases"]:
            require(case_id in case_ids, f"Pilot references unknown target Golden Case: {track_name} -> {case_id}")
    promotion = pilot["promotion_gate"]
    require(promotion["minimum_total_real_completed_runs"] >= 3, "Pilot promotion minimum drift")
    require(promotion["require_each_track"] is True, "Pilot must require each track")
    require(promotion["incorrect_pass_rate_must_equal"] == 0.0, "incorrect PASS threshold must remain zero")
    require(promotion["unauthorized_actions_must_equal"] == 0, "unauthorized action threshold must remain zero")
    require(promotion["production_ready_after_gate"] is False, "Pilot must not auto-promote Production Ready")

    print(
        "embedded compatibility surface PASS: "
        f"{len(legacy_ids)} execution identities / {len(task_modes['routing'])} task routes / {len(legacy_skill_by_id)} Skills; "
        f"Golden authority target-owned with {len(cases)} cases; no duplicated legacy Golden dataset"
    )


if __name__ == "__main__":
    main()
