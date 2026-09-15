#!/usr/bin/env python3
"""Evaluate legacy embedded execution routing against Edge Foundation target semantics.

This script is intentionally shadow-only: it must not mutate canonical routing.
Target Golden Cases are authoritative for target evaluation; legacy routing remains
an execution input until the canonical switch.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOMAIN_ROOT = ROOT / "domains" / "edge-foundation"
LEGACY_ROOT = ROOT / "expert-groups" / "embedded-system"


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def evaluate() -> dict:
    domain = load_yaml(DOMAIN_ROOT / "domain.yaml")
    shadow = load_yaml(DOMAIN_ROOT / "routing-shadow.yaml")
    legacy = load_yaml(LEGACY_ROOT / "config" / "task-modes.yaml")
    golden = load_yaml(DOMAIN_ROOT / "evaluation" / "golden-cases.yaml")

    require(shadow["canonical_routing"] is False, "shadow routing must never be canonical during dual evaluation")
    require(shadow["status"] == "dual-evaluation", "shadow routing status drift")
    require(shadow["policy"]["must_not_change_execution_route"] is True, "shadow evaluator must not alter execution routing")
    require(shadow["policy"]["must_not_expand_action_authority"] is True, "shadow evaluator must not expand authority")
    require(golden["status"] == "phase4-prep-target", "target Golden Case status drift")
    require(golden["canonical_routing_switched"] is False, "target Golden Cases must remain shadow-only before switch")
    require(golden["rules"]["legacy_expert_identity_forbidden"] is True, "target Golden Cases must reject legacy Expert identity")

    legacy_routes = legacy["routing"]
    target_routes = shadow["routing"]
    require(set(target_routes) == set(legacy_routes), f"target routing must cover exact legacy task type set: legacy={sorted(legacy_routes)}, target={sorted(target_routes)}")

    domain_experts = {item["id"]: item for item in domain["experts"]}
    embedded = domain_experts["embedded-system-expert"]
    known_capabilities = set(embedded.get("capabilities", []))
    allowed_modes = set(domain["workflow_semantics"]["frozen_high_level_modes"])
    assurance_ids = set(domain["assurance"]["responsibilities"])
    legacy_ids = {"embedded-system-team-lead"}
    legacy_ids.update(item["id"] for item in load_yaml(LEGACY_ROOT / "expert-group.yaml")["experts"])

    errors: list[str] = []
    rows: list[dict] = []
    for task_type, legacy_route in legacy_routes.items():
        target = target_routes[task_type]
        target_mode = target["target_mode"]
        if target_mode not in allowed_modes:
            errors.append(f"{task_type}: unknown target_mode {target_mode}")

        for expert_id in target.get("primary_experts", []):
            if expert_id not in domain_experts:
                errors.append(f"{task_type}: unknown target expert {expert_id}")
            if expert_id in legacy_ids:
                errors.append(f"{task_type}: legacy expert leaked into target routing: {expert_id}")

        for capability_id in target.get("capabilities", []):
            if capability_id not in known_capabilities:
                errors.append(f"{task_type}: unknown embedded capability {capability_id}")

        for assurance_id in target.get("assurance", []):
            if assurance_id not in assurance_ids:
                errors.append(f"{task_type}: unknown Assurance responsibility {assurance_id}")

        legacy_default = legacy_route["default_mode"]
        translated = shadow["legacy_mode_translation"][legacy_default]
        allowed_target = set(target.get("allowed_target_modes", [target_mode]))
        if translated not in allowed_target:
            errors.append(
                f"{task_type}: legacy default mode {legacy_default} translates to {translated}, "
                f"but target allows {sorted(allowed_target)}"
            )

        if legacy_default == "diagnostic_chain" and target_mode != "diagnostic":
            errors.append(f"{task_type}: diagnostic legacy route must remain diagnostic")
        if legacy_default in {"review_only", "release_chain"} and target_mode != "review":
            errors.append(f"{task_type}: review/release legacy route must map to review")
        if target.get("execution_forbidden") and legacy_default != "review_only":
            errors.append(f"{task_type}: execution_forbidden is only valid for legacy review_only tasks")

        cross_domain = target.get("cross_domain_escalation")
        if cross_domain:
            possible_mode = cross_domain.get("possible_mode")
            if possible_mode != "multi_domain":
                errors.append(f"{task_type}: cross-domain escalation must use multi_domain")
            possible_experts = cross_domain.get("possible_experts", [])
            if len(set(possible_experts)) < 2:
                errors.append(f"{task_type}: cross-domain escalation must name at least two Domain Experts")
            for expert_id in possible_experts:
                if expert_id not in domain_experts:
                    errors.append(f"{task_type}: cross-domain escalation names unknown expert {expert_id}")
            if not cross_domain.get("triggers"):
                errors.append(f"{task_type}: cross-domain escalation requires evidence triggers")

        rows.append(
            {
                "task_type": task_type,
                "legacy_default_mode": legacy_default,
                "legacy_primary_experts": legacy_route.get("primary_experts", []),
                "target_mode": target_mode,
                "target_primary_experts": target.get("primary_experts", []),
                "target_capabilities": target.get("capabilities", []),
                "assurance": target.get("assurance", []),
                "cross_domain_candidate": bool(cross_domain),
            }
        )

    golden_cases = golden["cases"]
    for case in golden_cases:
        case_id = case["id"]
        task_type = case["task_type"]
        if task_type not in target_routes:
            errors.append(f"golden case {case_id}: task type is not mapped: {task_type}")
            continue
        target = target_routes[task_type]
        legacy_mode = case["legacy_execution_mode"]
        if legacy_mode not in shadow["legacy_mode_translation"]:
            errors.append(f"golden case {case_id}: legacy mode not translated: {legacy_mode}")
            continue
        translated = shadow["legacy_mode_translation"][legacy_mode]
        allowed_target = set(target.get("allowed_target_modes", [target["target_mode"]]))
        if translated not in allowed_target:
            errors.append(f"golden case {case_id}: translated target mode {translated} not allowed for {task_type}")
        if case["target_mode"] != target["target_mode"]:
            errors.append(f"golden case {case_id}: target mode disagrees with routing shadow")
        if case["expected_experts"] != target.get("primary_experts", []):
            errors.append(f"golden case {case_id}: target Expert expectation disagrees with routing shadow")
        if not set(target.get("capabilities", [])).issubset(set(case.get("expected_capabilities", []))):
            errors.append(f"golden case {case_id}: target Capability expectation drops routed capability")
        if case["required_assurance"] != target.get("assurance", []):
            errors.append(f"golden case {case_id}: Assurance expectation disagrees with routing shadow")
        for expert_id in case["expected_experts"]:
            if expert_id in legacy_ids:
                errors.append(f"golden case {case_id}: legacy Expert leaked into target evaluation")

    require(not errors, "edge-foundation shadow evaluation failed: " + "; ".join(errors))

    summary = {
        "status": "PASS",
        "canonical_routing_changed": False,
        "golden_case_authority": "domains/edge-foundation/evaluation/golden-cases.yaml",
        "legacy_execution_routing_authority": "expert-groups/embedded-system/config/task-modes.yaml",
        "task_types_evaluated": len(rows),
        "legacy_task_types": len(legacy_routes),
        "golden_cases_evaluated": len(golden_cases),
        "target_domain_experts": sorted(domain_experts),
        "embedded_core_capabilities": sorted(known_capabilities),
        "cross_domain_candidates": sorted(row["task_type"] for row in rows if row["cross_domain_candidate"]),
        "routes": rows,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    summary = evaluate()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        "edge-foundation shadow evaluation PASS: "
        f"{summary['task_types_evaluated']} task types, "
        f"{summary['golden_cases_evaluated']} target golden cases, "
        f"cross-domain candidates={summary['cross_domain_candidates']}, canonical routing unchanged"
    )


if __name__ == "__main__":
    main()
