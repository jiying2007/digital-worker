#!/usr/bin/env python3
"""Evaluate one Skill invocation against one canonical Skill evaluation case."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "domains" / "edge-foundation" / "evaluation" / "skill-evaluation-plan.yaml"
INVOCATION_SCHEMA = ROOT / "schemas" / "skill-invocation-receipt.v1.schema.json"
EVALUATION_SCHEMA = ROOT / "schemas" / "skill-evaluation-receipt.v1.schema.json"
INVOCATION_VALIDATOR = ROOT / "scripts" / "validate_skill_invocation_receipt.py"
PLAN_REL = "domains/edge-foundation/evaluation/skill-evaluation-plan.yaml"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_json(value: dict, schema_path: Path):
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def find_case(case_id: str) -> tuple[str, str, dict]:
    plan = load_yaml(PLAN)
    for skill_id, cases in plan["skills"].items():
        for case_kind in ("positive", "block"):
            case = cases[case_kind]
            if case["id"] == case_id:
                return skill_id, case_kind, case
    raise AssertionError(f"unknown Skill evaluation case: {case_id}")


def evaluate(
    case_id: str,
    invocation_path: Path,
    semantic_status: str,
    semantic_evaluator_kind: str,
    semantic_evaluator_id: str | None,
    semantic_evidence_ref: str | None,
    semantic_notes: str | None,
) -> dict:
    invocation_path = invocation_path.resolve()
    invocation = load_json(invocation_path)
    validate_json(invocation, INVOCATION_SCHEMA)

    checked = subprocess.run(
        [sys.executable, str(INVOCATION_VALIDATOR), str(invocation_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    require(checked.returncode == 0, (checked.stderr or checked.stdout or "Skill invocation receipt validation failed").strip())

    skill_id, case_kind, case = find_case(case_id)
    skill_match = invocation["skill_id"] == skill_id
    expected_status = case["expected_invocation_status"]
    observed_status = invocation["result"]["status"]
    status_match = observed_status == expected_status
    contract_pass = skill_match and status_match

    if semantic_status == "NOT_EVALUATED":
        require(semantic_evaluator_kind == "none", "NOT_EVALUATED semantic status requires evaluator_kind=none")
        require(semantic_evaluator_id is None and semantic_evidence_ref is None, "NOT_EVALUATED must not invent evaluator/evidence")
    else:
        require(semantic_evaluator_kind in {"human-review", "independent-evaluator"}, "semantic PASS/FAIL requires independent evaluator kind")
        require(bool(semantic_evaluator_id), "semantic PASS/FAIL requires evaluator_id")
        require(bool(semantic_evidence_ref), "semantic PASS/FAIL requires evidence_ref")

    lifecycle_eligible = contract_pass and semantic_status == "PASS"

    receipt = {
        "schema_version": 1,
        "evaluation_id": f"{case_id}:{invocation['invocation_id']}",
        "case_id": case_id,
        "case_kind": case_kind,
        "skill_id": skill_id,
        "plan": {"path": PLAN_REL, "sha256": sha256(PLAN)},
        "invocation_receipt": {
            "ref": invocation_path.as_posix(),
            "sha256": sha256(invocation_path),
            "source_type": invocation["source_type"],
            "runtime_provider": invocation["runtime_binding"]["provider"],
            "runtime_id": invocation["runtime_binding"]["runtime_id"],
            "skill_contract_sha256": invocation["skill_contract"]["sha256"],
        },
        "contract_verdict": {
            "status": "PASS" if contract_pass else "FAIL",
            "expected_invocation_status": expected_status,
            "observed_invocation_status": observed_status,
            "checks": {
                "receipt_valid": True,
                "skill_match": skill_match,
                "status_match": status_match,
            },
        },
        "semantic_evaluation": {
            "status": semantic_status,
            "evaluator_kind": semantic_evaluator_kind,
            "evaluator_id": semantic_evaluator_id,
            "evidence_ref": semantic_evidence_ref,
            "notes": semantic_notes,
        },
        "lifecycle_evaluation_eligible": lifecycle_eligible,
        "generated_at": now_iso(),
    }
    validate_json(receipt, EVALUATION_SCHEMA)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_id")
    parser.add_argument("invocation_receipt", type=Path)
    parser.add_argument("--semantic-status", choices=["NOT_EVALUATED", "PASS", "FAIL"], default="NOT_EVALUATED")
    parser.add_argument("--semantic-evaluator-kind", choices=["none", "human-review", "independent-evaluator"], default="none")
    parser.add_argument("--semantic-evaluator-id")
    parser.add_argument("--semantic-evidence-ref")
    parser.add_argument("--semantic-notes")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-lifecycle-eligible", action="store_true")
    args = parser.parse_args()

    receipt = evaluate(
        args.case_id,
        args.invocation_receipt,
        args.semantic_status,
        args.semantic_evaluator_kind,
        args.semantic_evaluator_id,
        args.semantic_evidence_ref,
        args.semantic_notes,
    )
    rendered = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    print(
        "skill evaluation receipt: "
        f"case={receipt['case_id']} skill={receipt['skill_id']} "
        f"contract={receipt['contract_verdict']['status']} "
        f"semantic={receipt['semantic_evaluation']['status']} "
        f"lifecycle_eligible={receipt['lifecycle_evaluation_eligible']}"
    )
    if args.require_lifecycle_eligible and not receipt["lifecycle_evaluation_eligible"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
