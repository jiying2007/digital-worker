#!/usr/bin/env python3
"""Aggregate positive+BLOCK Skill case evidence into a bounded EVALUATED/DEFINED summary."""
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
EDGE = ROOT / "domains" / "edge-foundation"
PLAN = EDGE / "evaluation" / "skill-evaluation-plan.yaml"
EVAL_SCHEMA = ROOT / "schemas" / "skill-evaluation-receipt.v1.schema.json"
INVOCATION_SCHEMA = ROOT / "schemas" / "skill-invocation-receipt.v1.schema.json"
SUMMARY_SCHEMA = ROOT / "schemas" / "skill-evaluation-summary.v1.schema.json"
INVOCATION_VALIDATOR = ROOT / "scripts" / "validate_skill_invocation_receipt.py"


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


def validate_invocation(path: Path) -> dict:
    value = load_json(path)
    validate_json(value, INVOCATION_SCHEMA)
    checked = subprocess.run(
        [sys.executable, str(INVOCATION_VALIDATOR), str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if checked.returncode != 0:
        raise AssertionError((checked.stderr or checked.stdout or "Skill invocation validation failed").strip())
    return value


def expected_cases(skill_id: str) -> tuple[str, str]:
    plan = load_yaml(PLAN)
    if skill_id not in plan["skills"]:
        raise AssertionError(f"Skill missing from evaluation plan: {skill_id}")
    cases = plan["skills"][skill_id]
    return cases["positive"]["id"], cases["block"]["id"]


def build_summary(
    skill_id: str,
    positive_eval_path: Path,
    positive_invocation_path: Path,
    block_eval_path: Path,
    block_invocation_path: Path,
) -> dict:
    positive_eval_path = positive_eval_path.resolve()
    block_eval_path = block_eval_path.resolve()
    positive_invocation_path = positive_invocation_path.resolve()
    block_invocation_path = block_invocation_path.resolve()

    pos_eval = load_json(positive_eval_path)
    neg_eval = load_json(block_eval_path)
    validate_json(pos_eval, EVAL_SCHEMA)
    validate_json(neg_eval, EVAL_SCHEMA)
    pos_inv = validate_invocation(positive_invocation_path)
    neg_inv = validate_invocation(block_invocation_path)

    expected_pos, expected_neg = expected_cases(skill_id)
    current_plan_hash = sha256(PLAN)

    checks = {
        "current_plan": pos_eval["plan"]["sha256"] == current_plan_hash and neg_eval["plan"]["sha256"] == current_plan_hash,
        "case_identity": (
            pos_eval["case_kind"] == "positive"
            and neg_eval["case_kind"] == "block"
            and pos_eval["case_id"] == expected_pos
            and neg_eval["case_id"] == expected_neg
        ),
        "skill_identity": (
            pos_eval["skill_id"] == skill_id
            and neg_eval["skill_id"] == skill_id
            and pos_inv["skill_id"] == skill_id
            and neg_inv["skill_id"] == skill_id
        ),
        "case_evidence_eligible": (
            pos_eval["case_evidence_eligible"] is True
            and neg_eval["case_evidence_eligible"] is True
            and pos_eval["contract_verdict"]["status"] == "PASS"
            and neg_eval["contract_verdict"]["status"] == "PASS"
            and pos_eval["semantic_evaluation"]["status"] == "PASS"
            and neg_eval["semantic_evaluation"]["status"] == "PASS"
        ),
        "same_skill_contract": (
            pos_inv["skill_contract"]["sha256"] == neg_inv["skill_contract"]["sha256"]
            and pos_eval["invocation_receipt"]["skill_contract_sha256"] == pos_inv["skill_contract"]["sha256"]
            and neg_eval["invocation_receipt"]["skill_contract_sha256"] == neg_inv["skill_contract"]["sha256"]
        ),
        "same_runtime": (
            pos_inv["runtime_binding"]["provider"] == neg_inv["runtime_binding"]["provider"]
            and pos_inv["runtime_binding"]["runtime_id"] == neg_inv["runtime_binding"]["runtime_id"]
        ),
        "same_source_type": pos_inv["source_type"] == neg_inv["source_type"],
        "invocation_hashes_match": (
            pos_eval["invocation_receipt"]["sha256"] == sha256(positive_invocation_path)
            and neg_eval["invocation_receipt"]["sha256"] == sha256(block_invocation_path)
        ),
    }
    reason_map = {
        "current_plan": "evaluation-receipt-plan-hash-is-not-current",
        "case_identity": "positive-or-block-case-identity-mismatch",
        "skill_identity": "skill-identity-mismatch",
        "case_evidence_eligible": "positive-and-block-case-evidence-not-both-eligible",
        "same_skill_contract": "positive-and-block-do-not-use-same-frozen-skill-contract",
        "same_runtime": "positive-and-block-do-not-use-same-runtime-implementation",
        "same_source_type": "positive-and-block-source-type-mismatch",
        "invocation_hashes_match": "evaluation-to-invocation-hash-mismatch",
    }
    blockers = [reason_map[key] for key, ok in checks.items() if not ok]
    complete = not blockers

    summary = {
        "schema_version": 1,
        "skill_id": skill_id,
        "status": "EVALUATED" if complete else "DEFINED",
        "evaluation_complete": complete,
        "skill_contract_sha256": pos_inv["skill_contract"]["sha256"],
        "evaluation_plan_sha256": current_plan_hash,
        "runtime_binding": {
            "provider": pos_inv["runtime_binding"]["provider"],
            "runtime_id": pos_inv["runtime_binding"]["runtime_id"],
        },
        "source_type": pos_inv["source_type"],
        "positive_case": {
            "case_id": pos_eval["case_id"],
            "evaluation_receipt_sha256": sha256(positive_eval_path),
            "invocation_receipt_sha256": sha256(positive_invocation_path),
        },
        "block_case": {
            "case_id": neg_eval["case_id"],
            "evaluation_receipt_sha256": sha256(block_eval_path),
            "invocation_receipt_sha256": sha256(block_invocation_path),
        },
        "checks": checks,
        "blockers": blockers,
        "portability_proven": False,
        "product_readiness_inherited": False,
        "generated_at": now_iso(),
    }
    validate_json(summary, SUMMARY_SCHEMA)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_id")
    parser.add_argument("--positive-evaluation", type=Path, required=True)
    parser.add_argument("--positive-invocation", type=Path, required=True)
    parser.add_argument("--block-evaluation", type=Path, required=True)
    parser.add_argument("--block-invocation", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-evaluated", action="store_true")
    args = parser.parse_args()

    summary = build_summary(
        args.skill_id,
        args.positive_evaluation,
        args.positive_invocation,
        args.block_evaluation,
        args.block_invocation,
    )
    rendered = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    print(
        f"Skill maturity evaluation: skill={summary['skill_id']} status={summary['status']} "
        f"complete={summary['evaluation_complete']} portability_proven={summary['portability_proven']}"
    )
    if args.require_evaluated and summary["status"] != "EVALUATED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
