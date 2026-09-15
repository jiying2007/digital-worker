#!/usr/bin/env python3
"""Validate provider-native Assurance receipt identity as bounded Digital Worker input evidence.

This validator intentionally does not interpret provider verdicts. Digital Worker
Verification / Independent Review remains the decision authority.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "assurance-provider-evidence.v1.schema.json"
LOCK = ROOT / "config" / "integrations" / "cross-repo-lock.json"


class AssuranceProviderEvidenceError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssuranceProviderEvidenceError(f"JSON document must be an object: {path}")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssuranceProviderEvidenceError(message)


def resolve_binding(lock: dict[str, Any], ref: str) -> tuple[str, dict[str, Any]]:
    prefix = "config/integrations/cross-repo-lock.json#/assurance_bindings/"
    require(ref.startswith(prefix), "provider_binding_ref must target cross-repo assurance_bindings")
    key = ref[len(prefix):]
    binding = lock.get("assurance_bindings", {}).get(key)
    require(isinstance(binding, dict), f"unknown assurance binding: {key}")
    return key, binding


def validate_evidence(evidence: dict[str, Any], report: dict[str, Any], report_kind: str) -> dict[str, Any]:
    schema = load_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(evidence), key=lambda e: list(e.absolute_path))
    if errors:
        raise AssuranceProviderEvidenceError("schema validation failed: " + "; ".join(error.message for error in errors[:3]))

    require(report_kind in {"review", "verification"}, "report_kind must be review or verification")
    require(evidence["source_type"] == "real", "synthetic assurance evidence cannot qualify")
    require(evidence["evidence_origin"] == "real-run", "controlled fixture cannot qualify as real assurance evidence")
    require(evidence["integrity_status"] == "verified", "provider receipt integrity must be verified")

    lock = load_json(LOCK)
    _, binding = resolve_binding(lock, evidence["provider_binding_ref"])
    role = evidence["assurance_role"]
    require(role in binding.get("supported_assurance_roles", []), "assurance role is not supported by selected binding")
    if role == "independent-review-evidence":
        require(report_kind == "review", "independent-review-evidence may only support a Review report")
    if role == "verification-evidence":
        require(report_kind == "verification", "verification-evidence may only support a Verification report")

    receipt = evidence["provider_receipt"]
    require(receipt["kind"] == binding.get("review_receipt_kind"), "provider receipt kind does not match binding")
    require(receipt["schema_version"] == binding.get("review_receipt_schema_version"), "provider receipt schema version does not match binding")

    require(evidence["run_id"] == report.get("run_id"), "provider evidence run_id does not match Digital Worker report")
    report_subject = report.get("reviewed_subject")
    require(isinstance(report_subject, dict), "Digital Worker report requires reviewed_subject")
    subject = evidence["reviewed_subject"]
    require(subject["execution_source_set_ref"] == report_subject.get("execution_source_set_ref"), "provider evidence source-set subject mismatch")
    require(subject["result_identity_ref"] == report_subject.get("result_identity_ref"), "provider evidence result subject mismatch")
    provider_source = subject.get("source_identity_ref")
    report_source = report_subject.get("source_identity_ref")
    if provider_source is not None and report_source is not None:
        require(provider_source == report_source, "provider evidence source identity mismatch")

    expected_ref = f"assurance-provider-evidence:{evidence['evidence_id']}"
    require(expected_ref in report.get("input_evidence_refs", []), "Digital Worker report must cite exact assurance provider evidence_id")

    return {
        "kind": "assurance-provider-evidence-validation/v1",
        "validation_status": "PASS",
        "evidence_id": evidence["evidence_id"],
        "work_item_id": evidence["work_item_id"],
        "run_id": evidence["run_id"],
        "provider_binding_ref": evidence["provider_binding_ref"],
        "assurance_role": role,
        "receipt_ref": receipt["ref"],
        "receipt_sha256": receipt["sha256"],
        "provider_subject_fingerprint": evidence["provider_subject"]["fingerprint"],
        "reviewed_subject_validated": True,
        "claims": {
            "provider_receipt_validated_as_input_identity_only": True,
            "verification_pass_implied": False,
            "independent_review_decision_implied": False,
            "release_authorization_implied": False,
            "product_qualification_implied": False,
            "terminal_maturity_implied": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--report-kind", choices=["review", "verification"], required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-eligible", action="store_true")
    args = parser.parse_args(argv)
    try:
        receipt = validate_evidence(load_json(args.evidence), load_json(args.report), args.report_kind)
    except (OSError, json.JSONDecodeError, AssuranceProviderEvidenceError) as exc:
        blocked = {"kind": "assurance-provider-evidence-validation/v1", "validation_status": "BLOCKED", "reason": str(exc)}
        print(json.dumps(blocked, ensure_ascii=False), file=sys.stderr)
        return 2 if args.require_eligible else 0

    text = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
