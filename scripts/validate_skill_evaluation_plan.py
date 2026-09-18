#!/usr/bin/env python3
"""Fail-closed validation for the canonical Skill evaluation plan."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
PLAN = EDGE / "evaluation" / "skill-evaluation-plan.yaml"
SKILLS = EDGE / "skills.yaml"


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    plan = load(PLAN)
    registry = load(SKILLS)
    registered = {item["id"] for item in registry["skills"]}
    planned = set(plan["skills"])

    require(plan["status"] == "canonical-plan", "Skill evaluation plan status drift")
    require(planned == registered and len(planned) == 23, "Skill evaluation plan must cover exactly all 23 canonical Skills")
    for key in [
        "every_registered_skill_requires_positive_and_block_case",
        "case_definition_is_not_evaluation_evidence",
        "invocation_receipt_required_for_case_verdict",
        "semantic_quality_must_be_independently_evaluated",
        "synthetic_contract_check_does_not_imply_skill_evaluated",
        "evaluation_does_not_imply_product_readiness",
        "evaluation_does_not_expand_action_authority",
    ]:
        require(plan["rules"].get(key) is True, f"Skill evaluation safety rule disabled: {key}")

    case_ids = []
    for skill_id, cases in plan["skills"].items():
        require(set(cases) == {"positive", "block"}, f"Skill must have exactly positive+block cases: {skill_id}")
        positive, block = cases["positive"], cases["block"]
        require(positive["expected_invocation_status"] == "COMPLETED", f"positive case must expect COMPLETED: {skill_id}")
        require(block["expected_invocation_status"] == "BLOCKED", f"block case must expect BLOCKED: {skill_id}")
        for kind, case in cases.items():
            require(case.get("id") and case.get("scenario") and case.get("focus"), f"incomplete {kind} case: {skill_id}")
            case_ids.append(case["id"])

    require(len(case_ids) == 46 == len(set(case_ids)), "Skill evaluation case IDs must be unique and total 46")
    print("Skill evaluation plan PASS: 23 Skills / 46 positive+BLOCK cases / no maturity inheritance")


if __name__ == "__main__":
    main()
