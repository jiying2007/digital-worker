from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

from jsonschema import ValidationError, validate

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "validate_assurance_provider_evidence.py"
SPEC = importlib.util.spec_from_file_location("assurance_provider_evidence", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

BINDING_REF = "config/integrations/cross-repo-lock.json#/assurance_bindings/codex_review_safe"
SOURCE_SET = "sha256:" + "a" * 64
RESULT = "git-result:" + "b" * 40


def evidence() -> dict:
    return {
        "schema_version": 1,
        "evidence_id": "APE-REVIEW-001",
        "work_item_id": "WORK-001",
        "run_id": "RUN-001",
        "source_type": "real",
        "evidence_origin": "real-run",
        "assurance_role": "independent-review-evidence",
        "provider_binding_ref": BINDING_REF,
        "provider_receipt": {
            "ref": "artifact://codex-review-safe/receipt-001.json",
            "sha256": "c" * 64,
            "kind": "codex-review",
            "schema_version": 5,
        },
        "provider_subject": {"ref": "codex-review-subject://001", "fingerprint": "d" * 64},
        "reviewed_subject": {
            "execution_source_set_ref": SOURCE_SET,
            "result_identity_ref": RESULT,
            "source_identity_ref": "git-source:" + "e" * 40,
        },
        "subject_mapping_evidence_refs": ["mapping://codex-review-to-dw/001"],
        "integrity_status": "verified",
        "collected_at": "2026-09-15T16:30:00Z",
    }


def report() -> dict:
    return {
        "run_id": "RUN-001",
        "reviewed_subject": {
            "execution_source_set_ref": SOURCE_SET,
            "result_identity_ref": RESULT,
            "source_identity_ref": "git-source:" + "e" * 40,
        },
        "input_evidence_refs": ["verification-report:VER-001", "assurance-provider-evidence:APE-REVIEW-001"],
    }


class AssuranceProviderEvidenceTests(unittest.TestCase):
    def test_real_review_provider_evidence_validates_as_input_only(self):
        result = MODULE.validate_evidence(evidence(), report(), "review")
        self.assertEqual(result["validation_status"], "PASS")
        self.assertTrue(result["claims"]["provider_receipt_validated_as_input_identity_only"])
        self.assertFalse(result["claims"]["independent_review_decision_implied"])
        self.assertFalse(result["claims"]["verification_pass_implied"])
        self.assertFalse(result["claims"]["product_qualification_implied"])

    def test_synthetic_and_controlled_fixture_fail_closed(self):
        for field, value, expected in [
            ("source_type", "synthetic", "synthetic assurance evidence cannot qualify"),
            ("evidence_origin", "controlled-fixture", "controlled fixture cannot qualify"),
            ("integrity_status", "unverified", "provider receipt integrity must be verified"),
        ]:
            with self.subTest(field=field):
                value_doc = evidence(); value_doc[field] = value
                with self.assertRaisesRegex(MODULE.AssuranceProviderEvidenceError, expected):
                    MODULE.validate_evidence(value_doc, report(), "review")

    def test_receipt_contract_drift_fails_closed(self):
        for field, value in [("kind", "other-review"), ("schema_version", 4)]:
            with self.subTest(field=field):
                value_doc = evidence(); value_doc["provider_receipt"][field] = value
                with self.assertRaises(MODULE.AssuranceProviderEvidenceError):
                    MODULE.validate_evidence(value_doc, report(), "review")

    def test_subject_mapping_is_exact(self):
        cases = [
            ("execution_source_set_ref", "sha256:" + "f" * 64),
            ("result_identity_ref", "git-result:" + "1" * 40),
            ("source_identity_ref", "git-source:" + "2" * 40),
        ]
        for field, value in cases:
            with self.subTest(field=field):
                value_doc = evidence(); value_doc["reviewed_subject"][field] = value
                with self.assertRaises(MODULE.AssuranceProviderEvidenceError):
                    MODULE.validate_evidence(value_doc, report(), "review")

    def test_report_must_cite_exact_evidence_id(self):
        report_doc = report(); report_doc["input_evidence_refs"] = ["verification-report:VER-001"]
        with self.assertRaisesRegex(MODULE.AssuranceProviderEvidenceError, "must cite exact"):
            MODULE.validate_evidence(evidence(), report_doc, "review")

    def test_review_binding_cannot_be_reinterpreted_as_verification(self):
        with self.assertRaisesRegex(MODULE.AssuranceProviderEvidenceError, "Review report"):
            MODULE.validate_evidence(evidence(), report(), "verification")

    def test_envelope_cannot_carry_provider_decision_or_approval(self):
        schema = json.loads((ROOT / "schemas/assurance-provider-evidence.v1.schema.json").read_text(encoding="utf-8"))
        for forbidden in ("decision", "approval", "verdict"):
            with self.subTest(forbidden=forbidden):
                value_doc = copy.deepcopy(evidence()); value_doc[forbidden] = "PASS"
                with self.assertRaises(ValidationError):
                    validate(instance=value_doc, schema=schema)


if __name__ == "__main__":
    unittest.main()
