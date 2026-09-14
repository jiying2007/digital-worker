#!/usr/bin/env python3
"""Produce a non-canonical Edge Foundation shadow receipt for one Pilot run.

The receipt binds an existing legacy Pilot identity to the target Domain / Expert /
Capability semantics without changing the authoritative execution route.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DOMAIN_ROOT = ROOT / "domains" / "edge-foundation"
LEGACY_ROOT = ROOT / "expert-groups" / "embedded-system"


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_json(instance: dict, schema_path: Path) -> None:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(instance)


def build_receipt(pilot_run_path: Path, pilot_result_path: Path | None, cross_domain_trigger: str | None) -> dict:
    pilot_run = load_json(pilot_run_path)
    validate_json(pilot_run, ROOT / "schemas" / "pilot-run.v1.schema.json")

    legacy = load_yaml(LEGACY_ROOT / "config" / "task-modes.yaml")
    shadow = load_yaml(DOMAIN_ROOT / "routing-shadow.yaml")
    domain = load_yaml(DOMAIN_ROOT / "domain.yaml")

    require(shadow["canonical_routing"] is False, "shadow routing must remain non-canonical")
    require(shadow["policy"]["must_not_change_execution_route"] is True, "shadow receipt must not alter execution routing")
    require(shadow["policy"]["must_not_expand_action_authority"] is True, "shadow receipt must not expand action authority")

    task_type = pilot_run["task_type"]
    workflow_mode = pilot_run["workflow_mode"]
    require(task_type in legacy["routing"], f"Pilot uses unknown legacy task type: {task_type}")
    require(task_type in shadow["routing"], f"Pilot task type is not mapped by shadow routing: {task_type}")

    legacy_route = legacy["routing"][task_type]
    require(workflow_mode in legacy_route["allowed_modes"], f"Pilot workflow_mode {workflow_mode} is not allowed for {task_type}")
    require(workflow_mode in shadow["legacy_mode_translation"], f"Pilot workflow_mode has no target translation: {workflow_mode}")

    target = shadow["routing"][task_type]
    translated_mode = shadow["legacy_mode_translation"][workflow_mode]
    allowed_target_modes = set(target.get("allowed_target_modes", [target["target_mode"]]))
    require(translated_mode in allowed_target_modes, f"Translated target mode {translated_mode} is invalid for {task_type}")

    known_experts = {item["id"]: item for item in domain["experts"]}
    embedded = known_experts["embedded-system-expert"]
    known_capabilities = set(embedded.get("capabilities", []))

    target_mode = target["target_mode"]
    target_experts = list(target.get("primary_experts", []))
    target_capabilities = list(target.get("capabilities", []))
    for expert_id in target_experts:
        require(expert_id in known_experts, f"Shadow route references unknown target expert: {expert_id}")
    for capability_id in target_capabilities:
        require(capability_id in known_capabilities, f"Shadow route references unknown embedded capability: {capability_id}")

    cross_cfg = target.get("cross_domain_escalation")
    cross_candidate = cross_cfg is not None
    cross_activated = False
    if cross_domain_trigger is not None:
        require(cross_cfg is not None, f"Task {task_type} does not allow cross-domain escalation")
        require(cross_domain_trigger in cross_cfg.get("triggers", []), f"Unknown cross-domain trigger for {task_type}: {cross_domain_trigger}")
        target_mode = cross_cfg["possible_mode"]
        target_experts = list(cross_cfg["possible_experts"])
        cross_activated = True
        for expert_id in target_experts:
            require(expert_id in known_experts, f"Cross-domain route references unknown target expert: {expert_id}")

    pilot_result = None
    if pilot_result_path is not None:
        pilot_result = load_json(pilot_result_path)
        validate_json(pilot_result, ROOT / "schemas" / "pilot-result.v1.schema.json")
        require(pilot_result["run_id"] == pilot_run["run_id"], "Pilot run/result run_id mismatch")
        require(pilot_result["source_type"] == pilot_run["source_type"], "Pilot run/result source_type mismatch")
        require(pilot_result["pilot_track"] == pilot_run["pilot_track"], "Pilot run/result pilot_track mismatch")
        require(pilot_result["route"]["actual_mode"] == workflow_mode, "Pilot result actual_mode must match pilot run workflow_mode")

    eligibility_reasons: list[str] = []
    if pilot_run["source_type"] != "real":
        eligibility_reasons.append("synthetic-source-not-eligible")
    if pilot_run["status"] != "completed":
        eligibility_reasons.append("pilot-run-not-completed")
    if pilot_result is None:
        eligibility_reasons.append("pilot-result-not-provided")
    else:
        if pilot_result["outcome"] != "PASS":
            eligibility_reasons.append("pilot-outcome-not-pass")
        if pilot_result["unauthorized_actions"] != 0:
            eligibility_reasons.append("unauthorized-actions-present")
        if pilot_result.get("audit_trace_complete") is not True:
            eligibility_reasons.append("audit-trace-incomplete")

    eligible = not eligibility_reasons
    if eligible:
        eligibility_reasons = ["eligible-real-completed-pass-no-unauthorized-actions-audit-complete"]

    receipt = {
        "schema_version": 1,
        "run_id": pilot_run["run_id"],
        "source_type": pilot_run["source_type"],
        "legacy_task_type": task_type,
        "legacy_workflow_mode": workflow_mode,
        "routing_authority": "legacy",
        "canonical_routing_changed": False,
        "target_mode": target_mode,
        "target_experts": target_experts,
        "target_capabilities": target_capabilities,
        "assurance": list(target.get("assurance", [])),
        "cross_domain": {
            "candidate": cross_candidate,
            "activated": cross_activated,
            "trigger": cross_domain_trigger,
        },
        "pilot_result_evaluated": pilot_result is not None,
        "pilot_outcome": None if pilot_result is None else pilot_result["outcome"],
        "phase3_evidence_eligible": eligible,
        "eligibility_reasons": eligibility_reasons,
    }
    validate_json(receipt, ROOT / "schemas" / "edge-foundation-shadow-receipt.v1.schema.json")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pilot_run", type=Path)
    parser.add_argument("--pilot-result", type=Path)
    parser.add_argument("--cross-domain-trigger")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    receipt = build_receipt(args.pilot_run, args.pilot_result, args.cross_domain_trigger)
    rendered = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    print(
        "edge-foundation pilot shadow receipt PASS: "
        f"run={receipt['run_id']} target_mode={receipt['target_mode']} "
        f"experts={receipt['target_experts']} phase3_evidence_eligible={receipt['phase3_evidence_eligible']}"
    )


if __name__ == "__main__":
    main()
