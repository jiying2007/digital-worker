#!/usr/bin/env python3
"""Fail-closed structural validation for the embedded expert-team assets."""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
EMB = ROOT / "expert-groups" / "embedded-system"


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def assert_true(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def parse_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert_true(match is not None, f"missing YAML frontmatter: {path}")
    return yaml.safe_load(match.group(1))


def resolve_declared_ref(owner_file: Path, value: str) -> Path:
    path = (owner_file.parent / value).resolve()
    assert_true(ROOT.resolve() in path.parents or path == ROOT.resolve(), f"reference escapes repository: {owner_file}: {value}")
    assert_true(path.exists(), f"missing referenced path: {owner_file}: {value}")
    return path


def validate_schema(schema_path: Path):
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    return schema


def assert_invalid(instance_path: Path, schema_path: Path):
    instance = load_json(instance_path)
    schema = load_json(schema_path)
    try:
        Draft202012Validator(schema).validate(instance)
    except ValidationError:
        return
    raise AssertionError(f"negative fixture unexpectedly valid: {instance_path}")


def main():
    expert_group = load_yaml(EMB / "expert-group.yaml")
    task_modes = load_yaml(EMB / "config" / "task-modes.yaml")
    workflow = load_yaml(EMB / "config" / "workflow.yaml")
    skills = load_yaml(EMB / "config" / "p0-skills.yaml")

    assert_true(expert_group.get("architecture_model") == "provider-neutral", "expert group must declare provider-neutral architecture")
    assert_true(expert_group["ssot"].get("provider_binding") == "not_frozen", "provider binding must remain not_frozen")
    assert_true("../../docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md" in expert_group["upstream_contracts"], "ADR-003 must be an upstream contract")
    assert_true(expert_group["engineering_runtime"]["execution_role"] == "engineer-plus-engineering-agent", "engineering runtime role must be provider-neutral")
    assert_true(expert_group["engineering_runtime"]["provider_selection"] == "not_frozen", "engineering runtime provider must not be frozen")
    assert_true(expert_group["knowledge"]["source_of_truth_policy"] == "stays_at_source", "knowledge source-of-truth policy must stay_at_source")
    assert_true(expert_group["knowledge"]["provider_selection"] == "not_frozen", "knowledge provider must not be frozen")

    expert_ids = {expert_group["team_lead"]["id"]}
    expert_ids.update(item["id"] for item in expert_group["experts"])
    assert_true(len(expert_ids) == 8, f"expected 1+7 expert IDs, got {len(expert_ids)}")

    for route_id, route in task_modes["routing"].items():
        for expert_id in route.get("primary_experts", []):
            assert_true(expert_id in expert_ids, f"unknown expert in route {route_id}: {expert_id}")

    mode_names = set(task_modes["workflow_modes"])
    path_names = set(workflow["mode_paths"])
    assert_true(mode_names == path_names, f"workflow mode mismatch: task_modes={sorted(mode_names)}, workflow={sorted(path_names)}")
    assert_true(workflow.get("architecture_model") == "provider-neutral", "workflow must be provider-neutral")

    stage_ids = {stage["id"] for stage in workflow["stages"]}
    for mode, path in workflow["mode_paths"].items():
        unknown = [stage for stage in path if stage not in stage_ids]
        assert_true(not unknown, f"unknown stages in mode {mode}: {unknown}")
    assert_true("phase.execution" not in workflow["mode_paths"]["review_only"], "review_only must not execute engineering")
    assert_true("phase.execution" not in workflow["mode_paths"]["single_expert"], "single_expert must not execute engineering")

    execution_stage = None
    for stage in workflow["stages"]:
        owner = stage.get("owner")
        if owner not in {"routed-domain-expert", "engineer-plus-engineering-agent"}:
            assert_true(owner in expert_ids, f"unknown workflow owner: {owner}")
        if stage["id"] == "phase.execution":
            execution_stage = stage
        if stage.get("schema"):
            resolve_declared_ref(EMB / "config" / "workflow.yaml", stage["schema"])
    assert_true(execution_stage is not None, "missing phase.execution")
    assert_true(execution_stage.get("runtime_provider") == "selectable", "execution runtime provider must be selectable")
    assert_true(execution_stage.get("interaction_provider_direct_control") == "forbidden_by_default", "interaction provider direct control must be forbidden by default")

    for key in ["team_run_state_schema", "gate_ledger_schema"]:
        resolve_declared_ref(EMB / "config" / "workflow.yaml", workflow["recovery"][key])

    registry = skills["skills"]
    ids = [item["id"] for item in registry]
    assert_true(len(ids) == len(set(ids)), "duplicate P0 skill IDs")
    assert_true(len(ids) >= 20, "P0 baseline must contain at least 20 registered skills")
    for item in registry:
        assert_true(item["owner"] in expert_ids, f"unknown skill owner: {item['id']} -> {item['owner']}")
        path = EMB / item["path"]
        assert_true(path.exists(), f"registered skill path missing: {item['id']} -> {path}")
        fm = parse_frontmatter(path)
        assert_true(fm["id"] == item["id"], f"skill ID mismatch: {item['id']}")
        assert_true(fm["owner"] == item["owner"], f"skill owner mismatch: {item['id']}")
        assert_true(fm["max_action_level"] in {"A0_READ", "A1_ANALYZE", "A2_GENERATE"}, f"P0 skill exceeds A2: {item['id']}")

    schemas = list((ROOT / "schemas").glob("*.schema.json")) + list((EMB / "schemas").glob("*.schema.json"))
    assert_true(schemas, "no JSON schemas found")
    for schema_path in schemas:
        validate_schema(schema_path)

    task_schema = ROOT / "schemas" / "task-brief.v1.schema.json"
    receipt_schema = ROOT / "schemas" / "delivery-receipt.v1.schema.json"
    hil_schema = ROOT / "schemas" / "hil-evidence.v1.schema.json"
    Draft202012Validator(load_json(task_schema)).validate(load_json(ROOT / "tests" / "fixtures" / "task-brief.valid.json"))
    Draft202012Validator(load_json(receipt_schema)).validate(load_json(ROOT / "tests" / "fixtures" / "delivery-receipt.valid.json"))
    Draft202012Validator(load_json(hil_schema)).validate(load_json(ROOT / "tests" / "fixtures" / "hil-evidence.valid.json"))
    assert_invalid(ROOT / "tests" / "fixtures" / "task-brief.invalid.json", task_schema)
    assert_invalid(ROOT / "tests" / "fixtures" / "delivery-receipt.invalid.json", receipt_schema)

    task = load_json(ROOT / "tests" / "fixtures" / "task-brief.valid.json")
    receipt = load_json(ROOT / "tests" / "fixtures" / "delivery-receipt.valid.json")
    assert_true(task["work_item_id"] == receipt["work_item_id"], "handoff work_item_id mismatch")
    assert_true(receipt["repo_root"] in task["repo_roots"], "delivery repo_root not authorized by task brief")

    handoff = EMB / "contracts" / "engineering-handoff.yaml"
    handoff_doc = load_yaml(handoff)
    exec_handoff = handoff_doc["stages"]["engineering_execution"]
    assert_true(exec_handoff.get("executor_role") == "engineer-plus-engineering-agent", "engineering handoff executor must be provider-neutral")
    assert_true(exec_handoff.get("runtime_provider") == "selectable", "engineering handoff runtime must be selectable")
    assert_true(exec_handoff.get("interaction_provider_direct_control") == "forbidden_by_default", "engineering handoff must forbid direct interaction-provider control by default")
    for stage in handoff_doc["stages"].values():
        if stage.get("input_schema"):
            resolve_declared_ref(handoff, stage["input_schema"])
        for ref in stage.get("input_schemas", []):
            resolve_declared_ref(handoff, ref)
        if stage.get("output_schema"):
            resolve_declared_ref(handoff, stage["output_schema"])

    product_handoff = EMB / "contracts" / "cross-team" / "product-expert-handoff.yaml"
    product_doc = load_yaml(product_handoff)
    request_schema_path = resolve_declared_ref(product_handoff, product_doc["request"]["schema"])
    response_schema_path = resolve_declared_ref(product_handoff, product_doc["response"]["schema"])
    request_fixture = load_json(ROOT / "tests" / "fixtures" / "technical-review-request.valid.json")
    response_fixture = load_json(ROOT / "tests" / "fixtures" / "embedded-feasibility-review.valid.json")
    Draft202012Validator(load_json(request_schema_path)).validate(request_fixture)
    Draft202012Validator(load_json(response_schema_path)).validate(response_fixture)
    assert_true(request_fixture["work_item_id"] == response_fixture["work_item_id"], "cross-team work_item_id mismatch")
    assert_true(product_doc["request"]["entry_task_type"] in task_modes["routing"], "cross-team entry task type is not routable")
    assert_true(product_doc["request"]["workflow_mode"] in mode_names, "cross-team workflow mode is unknown")

    ownership_file = EMB / "contracts" / "cross-team" / "edge-foundation-ownership.yaml"
    ownership = load_yaml(ownership_file)
    resolve_declared_ref(ownership_file, ownership["source_reference"])
    allowed_ownership = set(ownership["policy"]["allowed_ownership"])
    for item in ownership["candidate_domains"]:
        if item["status"] == "unresolved":
            assert_true(item["ownership"] is None, f"unresolved ownership must remain null: {item['domain']}")
        else:
            assert_true(item["ownership"] in allowed_ownership, f"invalid ownership decision: {item['domain']}")

    golden_doc = load_yaml(EMB / "tests" / "golden-cases.yaml")
    golden_schema = load_json(EMB / "schemas" / "golden-case.schema.json")
    cases = golden_doc["cases"]
    assert_true(len(cases) >= 10, "golden-case baseline must contain at least 10 cases")
    case_ids = [case["id"] for case in cases]
    assert_true(len(case_ids) == len(set(case_ids)), "duplicate golden-case IDs")
    for case in cases:
        Draft202012Validator(golden_schema).validate(case)
        assert_true(case["task_type"] in task_modes["routing"], f"golden case has unknown task type: {case['id']}")
        route = task_modes["routing"][case["task_type"]]
        assert_true(case["workflow_mode"] in route["allowed_modes"], f"golden case mode not allowed by task route: {case['id']}")
        for expert_id in case["expected_primary_experts"]:
            assert_true(expert_id in route["primary_experts"], f"golden case primary expert disagrees with task route: {case['id']} -> {expert_id}")
        for expert_id in case.get("secondary_experts", []):
            assert_true(expert_id in expert_ids, f"golden case unknown secondary expert: {case['id']} -> {expert_id}")

    pilot_plan = load_yaml(EMB / "pilot" / "pilot-plan.yaml")
    assert_true(set(pilot_plan["tracks"]) == {"debug", "feature", "review_release"}, "pilot must define exactly three required tracks")
    for track_name, track in pilot_plan["tracks"].items():
        assert_true(track["minimum_real_completed_runs"] >= 1, f"pilot track has invalid minimum: {track_name}")
        for task_type in track["candidate_task_types"]:
            assert_true(task_type in task_modes["routing"], f"pilot track has unknown task type: {track_name} -> {task_type}")
        for case_id in track["preferred_golden_cases"]:
            assert_true(case_id in case_ids, f"pilot track references unknown golden case: {track_name} -> {case_id}")
    promotion = pilot_plan["promotion_gate"]
    assert_true(promotion["minimum_total_real_completed_runs"] >= 3, "pilot promotion gate needs at least three real runs")
    assert_true(promotion["require_each_track"] is True, "pilot promotion gate must require each track")
    assert_true(promotion["incorrect_pass_rate_must_equal"] == 0.0, "incorrect PASS gate must stay zero")
    assert_true(promotion["unauthorized_actions_must_equal"] == 0, "unauthorized action gate must stay zero")
    assert_true(promotion["production_ready_after_gate"] is False, "pilot must not auto-promote to Production Ready")

    pilot_run_schema = ROOT / "schemas" / "pilot-run.v1.schema.json"
    pilot_result_schema = ROOT / "schemas" / "pilot-result.v1.schema.json"
    Draft202012Validator(load_json(pilot_run_schema)).validate(load_json(ROOT / "tests" / "fixtures" / "pilot-run.valid.json"))
    Draft202012Validator(load_json(pilot_result_schema)).validate(load_json(ROOT / "tests" / "fixtures" / "pilot-result.valid.json"))
    Draft202012Validator(load_json(pilot_result_schema)).validate(load_json(ROOT / "tests" / "fixtures" / "pilot-result.incorrect-pass.json"))

    print(f"embedded asset validation PASS: {len(expert_ids)} experts, {len(ids)} P0 skills, {len(schemas)} schemas, {len(cases)} golden cases, provider-neutral runtime, 3 pilot tracks")


if __name__ == "__main__":
    main()
