#!/usr/bin/env python3
"""Fail-closed provenance gate for L2 Formal Verification / Independent Review.

This gate is intentionally separate from the Pilot lifecycle. Legacy/non-Formal
reports continue to validate against their additive v1 schemas; only a report used
as an L2 Formal decision is required to satisfy the stronger provenance rules.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
VERIFICATION_SCHEMA = ROOT / "domains" / "edge-foundation" / "schemas" / "verification-report.schema.json"
REVIEW_SCHEMA = ROOT / "domains" / "edge-foundation" / "schemas" / "review-report.schema.json"
SHA256_ID = re.compile(r"^sha256:[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class FormalAssuranceError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FormalAssuranceError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise FormalAssuranceError(f"JSON document must be an object: {path}")
    return value


def _validate_schema(doc: dict[str, Any], schema_path: Path, label: str) -> None:
    schema = _load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(doc), key=lambda e: list(e.absolute_path))
    if errors:
        detail = "; ".join(error.message for error in errors[:3])
        raise FormalAssuranceError(f"{label} schema validation failed: {detail}")


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise FormalAssuranceError(message)


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_strings(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_nonempty_string(item) for item in value)


def validate_l2_bootstrap(bootstrap: dict[str, Any]) -> tuple[str, dict[str, str]]:
    _require(bootstrap.get("kind") == "codex-session-bootstrap/v1", "Formal assurance requires codex-session-bootstrap/v1")
    _require(bootstrap.get("status") == "ready", "Formal assurance requires a ready session bootstrap")
    _require(bootstrap.get("mode") == "L2", "Formal assurance requires L2 session bootstrap")

    session_identity = bootstrap.get("session_bootstrap_identity")
    _require(isinstance(session_identity, str) and SHA256_ID.fullmatch(session_identity) is not None, "L2 session bootstrap identity must be sha256:<64hex>")

    source_set = bootstrap.get("execution_source_set")
    _require(isinstance(source_set, dict), "L2 bootstrap must contain execution_source_set")
    _require(source_set.get("kind") == "codex-execution-source-set/v1", "execution source-set kind drift")
    source_set_identity = source_set.get("identity")
    _require(isinstance(source_set_identity, str) and SHA256_ID.fullmatch(source_set_identity) is not None, "execution source-set identity must be sha256:<64hex>")

    digital_worker = bootstrap.get("digital_worker")
    _require(isinstance(digital_worker, dict), "L2 bootstrap must contain digital_worker identity")
    governance = digital_worker.get("governance_identity")
    _require(isinstance(governance, dict), "L2 bootstrap must contain exact Digital Worker governance identity")
    _require(governance.get("provider") == "digital-worker", "Digital Worker governance provider drift")
    _require(governance.get("repository") == "jiying2007/digital-worker", "Digital Worker governance repository drift")
    _require(isinstance(governance.get("provider_commit"), str) and HEX40.fullmatch(governance["provider_commit"]) is not None, "Digital Worker provider commit must be exact 40-hex")
    _require(isinstance(governance.get("contract_catalog_digest"), str) and HEX64.fullmatch(governance["contract_catalog_digest"]) is not None, "Digital Worker contract catalog digest must be exact SHA256")
    _require(_nonempty_strings(governance.get("selected_domain_refs")), "L2 bootstrap requires selected Digital Worker domain refs")
    _require(_nonempty_strings(governance.get("selected_routing_refs")), "L2 bootstrap requires selected Digital Worker routing refs")

    work_identity_raw = bootstrap.get("work_identity")
    _require(isinstance(work_identity_raw, dict), "L2 bootstrap must contain authoritative work_identity")
    work_item_id = work_identity_raw.get("work_item_id")
    run_id = work_identity_raw.get("run_id")
    package_id = work_identity_raw.get("engineering_package_id")
    _require(_nonempty_string(work_item_id), "L2 work_identity requires work_item_id")
    _require(_nonempty_string(run_id), "L2 work_identity requires run_id")
    _require(_nonempty_string(package_id), "L2 work_identity requires engineering_package_id")

    materials = source_set.get("materials")
    _require(isinstance(materials, dict), "L2 execution source-set must contain materials")
    engineering = materials.get("engineering")
    _require(isinstance(engineering, dict), "L2 execution source-set must bind engineering identity")
    _require(engineering.get("work_item_id") == work_item_id, "L2 source-set work_item_id does not match work_identity")
    _require(engineering.get("run_id") == run_id, "L2 source-set run_id does not match work_identity")
    _require(engineering.get("package_id") == package_id, "L2 source-set package_id does not match work_identity")
    _require(isinstance(engineering.get("base_commit"), str) and HEX40.fullmatch(engineering["base_commit"]) is not None, "L2 source-set engineering base_commit must be exact 40-hex")
    _require(isinstance(engineering.get("engineering_task_package_sha256"), str) and HEX64.fullmatch(engineering["engineering_task_package_sha256"]) is not None, "L2 source-set Engineering Task Package SHA256 must be exact")

    return source_set_identity, {
        "work_item_id": str(work_item_id),
        "run_id": str(run_id),
        "engineering_package_id": str(package_id),
    }


def _validate_sequence(current: dict[str, Any], prior: dict[str, Any] | None, label: str) -> None:
    sequence = current.get("report_sequence")
    _require(isinstance(sequence, int) and sequence >= 1, f"Formal {label} requires report_sequence >= 1")
    _require("supersedes" in current, f"Formal {label} requires explicit supersedes (null for first report)")
    supersedes = current.get("supersedes")

    if sequence == 1:
        _require(supersedes is None, f"first Formal {label} report must use supersedes=null")
        _require(prior is None, f"first Formal {label} report cannot be supplied with a prior report")
        return

    _require(prior is not None, f"Formal {label} sequence {sequence} requires the immediately prior report")
    prior_id = prior.get("report_id")
    _require(isinstance(prior_id, str) and prior_id, f"prior Formal {label} report requires report_id")
    _require(supersedes == prior_id, f"Formal {label} supersedes must name the immediately prior report_id")
    _require(current.get("report_id") != prior_id, f"Formal {label} rerun must use a new report_id")
    _require(prior.get("run_id") == current.get("run_id"), f"Formal {label} supersession cannot cross run_id")
    _require(prior.get("report_sequence") == sequence - 1, f"Formal {label} report_sequence must advance by exactly one")


def _validate_formal_report(
    report: dict[str, Any],
    *,
    kind: str,
    source_set_identity: str,
    frozen_run_id: str,
    prior: dict[str, Any] | None,
) -> None:
    schema = VERIFICATION_SCHEMA if kind == "verification" else REVIEW_SCHEMA
    _validate_schema(report, schema, kind)
    if prior is not None:
        _validate_schema(prior, schema, f"prior {kind}")

    _require(report.get("run_id") == frozen_run_id, f"Formal {kind} run_id does not match frozen L2 Work/Run identity")
    _require(isinstance(report.get("report_id"), str) and report["report_id"].strip(), f"Formal {kind} requires report_id")
    _require(report.get("independence_confirmed") is True, f"Formal {kind} requires independence_confirmed=true")
    _require(_nonempty_strings(report.get("independence_evidence_refs")), f"Formal {kind} requires independence_evidence_refs")
    _require(isinstance(report.get("decision_actor_identity_ref"), str) and report["decision_actor_identity_ref"].strip(), f"Formal {kind} requires decision_actor_identity_ref")
    _require(_nonempty_strings(report.get("input_evidence_refs")), f"Formal {kind} requires input_evidence_refs")

    subject = report.get("reviewed_subject")
    _require(isinstance(subject, dict), f"Formal {kind} requires reviewed_subject")
    _require(subject.get("execution_source_set_ref") == source_set_identity, f"Formal {kind} reviewed subject is stale or bound to a different Execution Source Set")
    _require(isinstance(subject.get("result_identity_ref"), str) and subject["result_identity_ref"].strip(), f"Formal {kind} requires exact result_identity_ref")

    implementation_owner = report.get("implementation_owner")
    actor = report["decision_actor_identity_ref"]
    principal = report.get("verifier") if kind == "verification" else report.get("reviewer")
    if isinstance(implementation_owner, str) and implementation_owner.strip():
        _require(principal != implementation_owner, f"Formal {kind} principal cannot equal implementation_owner")
        _require(actor != implementation_owner, f"Formal {kind} decision actor cannot equal implementation_owner")

    _validate_sequence(report, prior, kind)

    if kind == "verification" and report.get("overall") in {"PASS", "PASS_WITH_RISK"}:
        _require(_nonempty_strings(report.get("evidence_refs")), "Formal Verification PASS requires evidence_refs")
    if kind == "review" and report.get("decision") in {"APPROVE", "APPROVE_WITH_RISK"}:
        _require(_nonempty_strings(report.get("evidence_refs")), "Formal Independent Review approval requires evidence_refs")


def validate_formal_assurance(
    *,
    bootstrap: dict[str, Any],
    verification: dict[str, Any],
    review: dict[str, Any] | None = None,
    prior_verification: dict[str, Any] | None = None,
    prior_review: dict[str, Any] | None = None,
    require_review: bool = False,
) -> dict[str, Any]:
    source_set_identity, work_identity = validate_l2_bootstrap(bootstrap)
    _validate_formal_report(
        verification,
        kind="verification",
        source_set_identity=source_set_identity,
        frozen_run_id=work_identity["run_id"],
        prior=prior_verification,
    )

    if require_review:
        _require(review is not None, "Formal assurance policy requires Independent Review")
    if review is not None:
        _validate_formal_report(
            review,
            kind="review",
            source_set_identity=source_set_identity,
            frozen_run_id=work_identity["run_id"],
            prior=prior_review,
        )
        _require(review.get("run_id") == verification.get("run_id"), "Verification and Review run_id mismatch")
        verification_subject = verification["reviewed_subject"]
        review_subject = review["reviewed_subject"]
        _require(review_subject.get("result_identity_ref") == verification_subject.get("result_identity_ref"), "Independent Review must bind the same result identity as Verification")
        verification_source = verification_subject.get("source_identity_ref")
        review_source = review_subject.get("source_identity_ref")
        if verification_source is not None and review_source is not None:
            _require(review_source == verification_source, "Independent Review source identity does not match Verification")
        expected_verification_ref = f"verification-report:{verification['report_id']}"
        _require(expected_verification_ref in review.get("input_evidence_refs", []), "Independent Review input_evidence_refs must include the exact Verification report_id")

    return {
        "kind": "formal-assurance-provenance-validation/v1",
        "validation_status": "PASS",
        "mode": "L2",
        "work_item_id": work_identity["work_item_id"],
        "run_id": work_identity["run_id"],
        "engineering_package_id": work_identity["engineering_package_id"],
        "execution_source_set_ref": source_set_identity,
        "session_bootstrap_ref": bootstrap.get("session_bootstrap_identity"),
        "verification_report_id": verification.get("report_id"),
        "verification_decision": verification.get("overall"),
        "review_report_id": review.get("report_id") if review else None,
        "review_decision": review.get("decision") if review else None,
        "claims": {
            "provenance_validated_only": True,
            "product_qualification_implied": False,
            "release_authorization_implied": False,
        },
    }


def configure_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-bootstrap", type=Path, required=True)
    parser.add_argument("--verification-report", type=Path, required=True)
    parser.add_argument("--review-report", type=Path)
    parser.add_argument("--prior-verification-report", type=Path)
    parser.add_argument("--prior-review-report", type=Path)
    parser.add_argument("--require-review", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = configure_parser().parse_args(argv)
    try:
        receipt = validate_formal_assurance(
            bootstrap=_load_json(args.session_bootstrap),
            verification=_load_json(args.verification_report),
            review=_load_json(args.review_report) if args.review_report else None,
            prior_verification=_load_json(args.prior_verification_report) if args.prior_verification_report else None,
            prior_review=_load_json(args.prior_review_report) if args.prior_review_report else None,
            require_review=args.require_review,
        )
    except FormalAssuranceError as exc:
        print(json.dumps({"kind": "formal-assurance-provenance-validation/v1", "validation_status": "BLOCKED", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2

    text = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
