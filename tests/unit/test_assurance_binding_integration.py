from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("formal_assurance_with_provider", ROOT / "scripts/validate_formal_assurance.py")
assert SPEC and SPEC.loader
formal = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(formal)

SOURCE_SET = "sha256:" + "1" * 64
SESSION = "sha256:" + "2" * 64
WORK_ITEM_ID = "EMB-ASSURANCE-001"
RUN_ID = "RUN-ASSURANCE-001"
PACKAGE_ID = "PKG-ASSURANCE-001"
RESULT_REF = "repo:firmware@" + "c" * 40
SOURCE_REF = "repo:firmware@" + "d" * 40
BINDING_REF = "config/integrations/cross-repo-lock.json#/assurance_bindings/codex_review_safe"


def bootstrap() -> dict:
    return {
        "kind": "codex-session-bootstrap/v1",
        "status": "ready",
        "mode": "L2",
        "session_bootstrap_identity": SESSION,
        "work_identity": {"work_item_id": WORK_ITEM_ID, "run_id": RUN_ID, "engineering_package_id": PACKAGE_ID},
        "digital_worker": {"governance_identity": {
            "provider": "digital-worker", "repository": "jiying2007/digital-worker",
            "provider_commit": "a" * 40, "contract_catalog_ref": "contracts/catalog.json",
            "contract_catalog_digest": "b" * 64,
            "selected_domain_refs": ["domains/edge-foundation/domain.yaml"],
            "selected_routing_refs": ["domains/edge-foundation/routing.yaml"],
            "materially_used_domain_skills": ["domains/edge-foundation/skills/verification-plan-builder/SKILL.md"],
        }},
        "execution_source_set": {"kind": "codex-execution-source-set/v1", "identity": SOURCE_SET, "materials": {"engineering": {
            "package_id": PACKAGE_ID, "work_item_id": WORK_ITEM_ID, "run_id": RUN_ID,
            "repo_root": "firmware/main", "base_commit": "4" * 40,
            "engineering_task_package_ref": "/tmp/engineering-task-package.json",
            "engineering_task_package_sha256": "3" * 64,
        }}},
    }


def verification() -> dict:
    return {
        "report_id": "VR-ASSURANCE-001", "run_id": RUN_ID, "verifier": "independent-verifier",
        "implementation_owner": "implementation-owner", "independence_confirmed": True,
        "independence_evidence_refs": ["identity:independent-verifier"],
        "reviewed_subject": {"execution_source_set_ref": SOURCE_SET, "result_identity_ref": RESULT_REF,
                             "source_identity_ref": SOURCE_REF, "artifact_identity_refs": ["sha256:" + "e" * 64]},
        "decision_actor_identity_ref": "identity:independent-verifier",
        "input_evidence_refs": ["artifact:build-001", "artifact:test-001"],
        "report_sequence": 1, "supersedes": None,
        "layers": {"implemented": "pass", "host": "pass", "cross_build": "pass", "sil": "not_applicable",
                   "device": "pass", "hil": "not_applicable", "release": "not_run"},
        "overall": "PASS", "evidence_refs": ["artifact:test-001"], "failures": [], "unverified_items": [], "risks": [],
    }


def review(vr: dict) -> dict:
    return {
        "report_id": "RR-ASSURANCE-001", "run_id": RUN_ID, "reviewer": "independent-reviewer",
        "implementation_owner": "implementation-owner", "independence_confirmed": True,
        "independence_evidence_refs": ["identity:independent-reviewer"],
        "reviewed_subject": {"execution_source_set_ref": SOURCE_SET, "result_identity_ref": RESULT_REF,
                             "source_identity_ref": SOURCE_REF, "artifact_identity_refs": []},
        "decision_actor_identity_ref": "identity:independent-reviewer",
        "input_evidence_refs": [f"verification-report:{vr['report_id']}", "assurance-provider-evidence:APE-REVIEW-001"],
        "report_sequence": 1, "supersedes": None, "decision": "APPROVE", "findings": [],
        "evidence_refs": [f"verification-report:{vr['report_id']}"], "residual_risks": [], "unverified_items": [],
    }


def provider_evidence() -> dict:
    return {
        "schema_version": 1, "evidence_id": "APE-REVIEW-001", "work_item_id": WORK_ITEM_ID, "run_id": RUN_ID,
        "source_type": "real", "evidence_origin": "real-run", "assurance_role": "independent-review-evidence",
        "provider_binding_ref": BINDING_REF,
        "provider_receipt": {"ref": "artifact://codex-review-safe/receipt-001.json", "sha256": "f" * 64,
                             "kind": "codex-review", "schema_version": 5},
        "provider_subject": {"ref": "codex-review-subject://001", "fingerprint": "9" * 64},
        "reviewed_subject": {"execution_source_set_ref": SOURCE_SET, "result_identity_ref": RESULT_REF,
                             "source_identity_ref": SOURCE_REF},
        "subject_mapping_evidence_refs": ["mapping://codex-review-to-dw/001"],
        "integrity_status": "verified", "collected_at": "2026-09-16T00:00:00Z",
    }


class AssuranceBindingIntegrationTests(unittest.TestCase):
    def test_provider_receipt_is_consumed_as_bounded_input_evidence(self) -> None:
        vr = verification(); rr = review(vr)
        result = formal.validate_formal_assurance(
            bootstrap=bootstrap(), verification=vr, review=rr, require_review=True,
            assurance_provider_evidence=provider_evidence(),
        )
        self.assertEqual(result["validation_status"], "PASS")
        self.assertEqual(result["assurance_provider_evidence_id"], "APE-REVIEW-001")
        self.assertEqual(result["assurance_provider_binding_ref"], BINDING_REF)
        self.assertEqual(result["review_decision"], "APPROVE")
        self.assertTrue(result["claims"]["provider_receipt_is_input_evidence_only"])
        self.assertFalse(result["claims"]["provider_receipt_decision_implied"])

    def test_provider_evidence_is_optional_for_existing_formal_path(self) -> None:
        result = formal.validate_formal_assurance(bootstrap=bootstrap(), verification=verification())
        self.assertIsNone(result["assurance_provider_evidence_id"])
        self.assertFalse(result["claims"]["provider_receipt_is_input_evidence_only"])

    def test_review_provider_evidence_requires_review_report(self) -> None:
        with self.assertRaisesRegex(formal.FormalAssuranceError, "requires a Review report"):
            formal.validate_formal_assurance(
                bootstrap=bootstrap(), verification=verification(), assurance_provider_evidence=provider_evidence()
            )

    def test_synthetic_provider_evidence_fails_closed_through_formal_gate(self) -> None:
        vr = verification(); rr = review(vr); evidence = provider_evidence(); evidence["source_type"] = "synthetic"
        with self.assertRaisesRegex(formal.FormalAssuranceError, "synthetic assurance evidence"):
            formal.validate_formal_assurance(
                bootstrap=bootstrap(), verification=vr, review=rr, assurance_provider_evidence=evidence
            )

    def test_provider_evidence_must_bind_frozen_work_item(self) -> None:
        vr = verification(); rr = review(vr); evidence = provider_evidence(); evidence["work_item_id"] = "OTHER-WORK"
        with self.assertRaisesRegex(formal.FormalAssuranceError, "work_item_id does not match"):
            formal.validate_formal_assurance(
                bootstrap=bootstrap(), verification=vr, review=rr, assurance_provider_evidence=evidence
            )

    def test_provider_evidence_subject_mismatch_fails_closed(self) -> None:
        vr = verification(); rr = review(vr); evidence = provider_evidence()
        evidence["reviewed_subject"]["result_identity_ref"] = "repo:firmware@" + "8" * 40
        with self.assertRaisesRegex(formal.FormalAssuranceError, "result subject mismatch"):
            formal.validate_formal_assurance(
                bootstrap=bootstrap(), verification=vr, review=rr, assurance_provider_evidence=evidence
            )

    def test_machine_contract_keeps_assurance_binding_bounded(self) -> None:
        lock = json.loads((ROOT / "config/integrations/cross-repo-lock.json").read_text(encoding="utf-8"))
        binding = lock["assurance_bindings"]["codex_review_safe"]
        self.assertEqual(binding["repository"], "jiying2007/codex-review")
        self.assertEqual(binding["ref"], "v4.8.7")
        self.assertEqual(binding["commit"], "25f38b965968f2672cf526ef3d5fb7e823714dfe")
        self.assertEqual(binding["review_receipt_schema_version"], 5)
        self.assertIn("REAL_RUN_USAGE_PENDING", binding["validation"])
        self.assertTrue(lock["rules"]["assurance_binding_is_not_control_plane"])
        self.assertTrue(lock["rules"]["assurance_provider_receipt_is_input_evidence_not_decision"])
        self.assertTrue(lock["rules"]["external_assurance_provider_is_optional_for_human_or_other_provider_path"])

        matrix = yaml.safe_load((ROOT / "config/integrations/provider-capability-matrix.yaml").read_text(encoding="utf-8"))
        self.assertEqual(matrix["roles"]["assurance_binding"]["decision"], "codex-review-safe-candidate-not-default-real-run-evidence-pending")
        self.assertTrue(matrix["rules"]["assurance_binding_is_not_control_plane"])
        self.assertTrue(matrix["rules"]["human_or_other_provider_path_must_remain_valid"])

        operating = yaml.safe_load((ROOT / "contracts/cross-repo/embedded-ai-operating-system.yaml").read_text(encoding="utf-8"))
        assurance = operating["assurance_bindings"]["contract"]
        self.assertIn("independent-review-decision", assurance["must_not_own"])
        self.assertIn("release-authorization", assurance["must_not_own"])

        catalog = json.loads((ROOT / "contracts/catalog.json").read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in catalog["contracts"]}
        self.assertEqual(by_id["assurance-provider-evidence"]["compatibility"], "optional-refs-first-fail-closed-v1")


if __name__ == "__main__":
    unittest.main()
