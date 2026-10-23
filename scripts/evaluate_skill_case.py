#!/usr/bin/env python3
"""Evaluate one Skill invocation against one canonical Skill evaluation case."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from pilot_support import error_result

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "domains" / "edge-foundation" / "evaluation" / "skill-evaluation-plan.yaml"
INVOCATION_SCHEMA = ROOT / "schemas" / "skill-invocation-receipt.v1.schema.json"
EVALUATION_SCHEMA = ROOT / "schemas" / "skill-evaluation-receipt.v1.schema.json"
INVOCATION_VALIDATOR = ROOT / "scripts" / "validate_skill_invocation_receipt.py"
PLAN_REL = "domains/edge-foundation/evaluation/skill-evaluation-plan.yaml"
SEMANTIC_SCHEMA = ROOT / "schemas" / "skill-semantic-evidence.v1.schema.json"


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


def validate_semantic_evidence(semantic: dict, invocation: dict, *, case_id: str,
                               skill_id: str, invocation_sha256: str,
                               base_dir: Path) -> str | None:
    """Re-read materialized evidence; a URI or a declared digest is not proof.

    This validates the local attestation and known identity conflicts, not the
    authenticity of an actor or the correctness of a human's technical verdict.
    """
    if semantic["status"] == "NOT_EVALUATED":
        require(semantic["evaluator_kind"] == "none" and
                all(semantic.get(key) is None for key in
                    ("evaluator_id", "evidence_ref", "evidence_sha256")),
                "NOT_EVALUATED must not invent evaluator/evidence")
        return None
    require(semantic["status"] in {"PASS", "FAIL"}, "unsupported semantic status")
    require(semantic["evaluator_kind"] in {"human-review", "independent-evaluator"},
            "semantic PASS/FAIL requires independent evaluator kind")
    evaluator = semantic.get("evaluator_id")
    require(isinstance(evaluator, str) and bool(evaluator.strip()), "semantic PASS/FAIL requires evaluator_id")
    actors = {str(invocation["runtime_binding"].get(key) or "").strip()
              for key in ("runtime_id", "execution_identity")}
    require(evaluator.strip() not in actors, "semantic evaluator cannot equal invocation runtime or execution identity")
    ref, digest = semantic.get("evidence_ref"), semantic.get("evidence_sha256")
    require(isinstance(ref, str) and bool(ref.strip()) and "://" not in ref,
            "semantic evidence_ref must be a materialized local JSON file; import external evidence first")
    require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
            "semantic PASS/FAIL requires evidence_sha256")
    path = Path(ref)
    path = (base_dir / path).resolve() if not path.is_absolute() else path.resolve()
    require(path.is_file(), "semantic evidence file is missing")
    # Hash and parse the same bytes; never validate one read and hash another.
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == digest, "semantic evidence SHA256 mismatch")
    evidence = json.loads(raw)
    validate_json(evidence, SEMANTIC_SCHEMA)
    require(evidence["case_id"] == case_id and evidence["skill_id"] == skill_id,
            "semantic evidence case or Skill identity mismatch")
    require(evidence["evaluation_plan_sha256"] == sha256(PLAN), "semantic evidence evaluation plan digest mismatch")
    require(evidence["invocation_receipt_sha256"] == invocation_sha256,
            "semantic evidence invocation digest mismatch")
    for key in ("status", "evaluator_kind", "evaluator_id"):
        require(evidence[key] == semantic[key], f"semantic evidence {key} mismatch")
    return path.as_posix()


def evaluate(
    case_id: str,
    invocation_path: Path,
    semantic_status: str,
    semantic_evaluator_kind: str,
    semantic_evaluator_id: str | None,
    semantic_evidence_ref: str | None,
    semantic_evidence_sha256: str | None,
    semantic_notes: str | None,
) -> dict:
    invocation_path = invocation_path.resolve()
    invocation_raw = invocation_path.read_bytes()
    invocation = json.loads(invocation_raw)
    invocation_digest = hashlib.sha256(invocation_raw).hexdigest()
    validate_json(invocation, INVOCATION_SCHEMA)

    from validate_skill_invocation_receipt import validate_receipt
    validate_receipt(invocation_path)

    skill_id, case_kind, case = find_case(case_id)
    skill_match = invocation["skill_id"] == skill_id
    expected_status = case["expected_invocation_status"]
    observed_status = invocation["result"]["status"]
    status_match = observed_status == expected_status
    contract_pass = skill_match and status_match

    semantic = {"status": semantic_status, "evaluator_kind": semantic_evaluator_kind,
                "evaluator_id": semantic_evaluator_id, "evidence_ref": semantic_evidence_ref,
                "evidence_sha256": semantic_evidence_sha256, "notes": semantic_notes}
    semantic["evidence_ref"] = validate_semantic_evidence(
        semantic, invocation, case_id=case_id, skill_id=skill_id,
        invocation_sha256=invocation_digest, base_dir=invocation_path.parent)
    require(sha256(invocation_path) == invocation_digest, "invocation changed during evaluation")

    case_eligible = contract_pass and semantic_status == "PASS"

    receipt = {
        "schema_version": 1,
        "evaluation_id": f"{case_id}:{invocation['invocation_id']}",
        "case_id": case_id,
        "case_kind": case_kind,
        "skill_id": skill_id,
        "plan": {"path": PLAN_REL, "sha256": sha256(PLAN)},
        "invocation_receipt": {
            "ref": invocation_path.as_posix(),
            "sha256": invocation_digest,
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
        "semantic_evaluation": semantic,
        "case_evidence_eligible": case_eligible,
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
    parser.add_argument("--semantic-evidence-ref", help="Local semantic evidence JSON; relative to invocation directory. External receipts must be materialized first.")
    parser.add_argument("--semantic-evidence-sha256")
    parser.add_argument("--semantic-notes")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-case-eligible", action="store_true")
    args = parser.parse_args()

    receipt = evaluate(
        args.case_id,
        args.invocation_receipt,
        args.semantic_status,
        args.semantic_evaluator_kind,
        args.semantic_evaluator_id,
        args.semantic_evidence_ref,
        args.semantic_evidence_sha256,
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
        f"case_evidence_eligible={receipt['case_evidence_eligible']}"
    )
    if args.require_case_eligible and not receipt["case_evidence_eligible"]:
        raise SystemExit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        error, code = error_result(exc)
        print(json.dumps(error, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(code)
