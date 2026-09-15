from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import jsonschema
import yaml

from scripts.validate_formal_assurance import FormalAssuranceError, validate_formal_assurance

ROOT = Path(__file__).resolve().parents[2]
EDGE = ROOT / "domains" / "edge-foundation"
LEGACY_FEATURE_VERIFICATION = (
    EDGE / "pilot" / "evidence" / "FEATURE-PCR02-OTA-001" / "verification-report.json"
)
VERIFICATION_SCHEMA = EDGE / "schemas" / "verification-report.schema.json"
VERIFICATION_POLICY = EDGE / "assurance" / "verification.yaml"
REVIEW_POLICY = EDGE / "assurance" / "review.yaml"

SOURCE_SET = "sha256:" + "1" * 64
OLD_SOURCE_SET = "sha256:" + "0" * 64
SESSION = "sha256:" + "2" * 64


def bootstrap(source_set: str = SOURCE_SET) -> dict:
    return {
        "kind": "codex-session-bootstrap/v1",
        "status": "ready",
        "mode": "L2",
        "session_bootstrap_identity": SESSION,
        "digital_worker": {
            "governance_identity": {
                "provider": "digital-worker",
                "repository": "jiying2007/digital-worker",
                "provider_commit": "a" * 40,
                "contract_catalog_ref": "contracts/catalog.json",
                "contract_catalog_digest": "b" * 64,
                "selected_domain_refs": ["domains/edge-foundation/domain.yaml"],
                "selected_routing_refs": ["domains/edge-foundation/routing.yaml"],
                "materially_used_domain_skills": [
                    "domains/edge-foundation/skills/verification-plan-builder/SKILL.md"
                ],
            }
        },
        "execution_source_set": {
            "kind": "codex-execution-source-set/v1",
            "identity": source_set,
            "materials": {},
        },
    }


def verification(
    *,
    source_set: str = SOURCE_SET,
    report_id: str = "VR-RUN-001-1",
    sequence: int = 1,
    supersedes: str | None = None,
) -> dict:
    return {
        "report_id": report_id,
        "run_id": "RUN-001",
        "verifier": "independent-verifier",
        "implementation_owner": "implementation-owner",
        "independence_confirmed": True,
        "independence_evidence_refs": ["identity:independent-verifier"],
        "reviewed_subject": {
            "execution_source_set_ref": source_set,
            "result_identity_ref": "repo:firmware@" + "c" * 40,
            "source_identity_ref": "repo:firmware@" + "d" * 40,
            "artifact_identity_refs": ["sha256:" + "e" * 64],
        },
        "decision_actor_identity_ref": "identity:independent-verifier",
        "input_evidence_refs": ["artifact:build-001", "artifact:test-001"],
        "report_sequence": sequence,
        "supersedes": supersedes,
        "layers": {
            "implemented": "pass",
            "host": "pass",
            "cross_build": "pass",
            "sil": "not_applicable",
            "device": "pass",
            "hil": "not_applicable",
            "release": "not_run",
        },
        "overall": "PASS",
        "evidence_refs": ["artifact:test-001"],
        "failures": [],
        "unverified_items": [],
        "risks": [],
    }


def review(
    verification_report: dict,
    *,
    source_set: str = SOURCE_SET,
    report_id: str = "RR-RUN-001-1",
    sequence: int = 1,
    supersedes: str | None = None,
) -> dict:
    return {
        "report_id": report_id,
        "run_id": verification_report["run_id"],
        "reviewer": "independent-reviewer",
        "implementation_owner": "implementation-owner",
        "independence_confirmed": True,
        "independence_evidence_refs": ["identity:independent-reviewer"],
        "reviewed_subject": {
            "execution_source_set_ref": source_set,
            "result_identity_ref": verification_report["reviewed_subject"]["result_identity_ref"],
            "source_identity_ref": verification_report["reviewed_subject"]["source_identity_ref"],
            "artifact_identity_refs": [],
        },
        "decision_actor_identity_ref": "identity:independent-reviewer",
        "input_evidence_refs": [
            f"verification-report:{verification_report['report_id']}",
            "artifact:test-001",
        ],
        "report_sequence": sequence,
        "supersedes": supersedes,
        "decision": "APPROVE",
        "findings": [],
        "evidence_refs": [f"verification-report:{verification_report['report_id']}"],
        "residual_risks": [],
        "unverified_items": [],
    }


class FormalAssuranceProvenanceTests(unittest.TestCase):
    def test_legacy_real_feature_verification_remains_schema_valid(self) -> None:
        schema = json.loads(VERIFICATION_SCHEMA.read_text(encoding="utf-8"))
        legacy = json.loads(LEGACY_FEATURE_VERIFICATION.read_text(encoding="utf-8"))
        jsonschema.validate(instance=legacy, schema=schema)
        self.assertNotIn("reviewed_subject", legacy)

    def test_formal_verification_passes_without_review_at_current_stage(self) -> None:
        result = validate_formal_assurance(
            bootstrap=bootstrap(),
            verification=verification(),
        )
        self.assertEqual(result["validation_status"], "PASS")
        self.assertEqual(result["execution_source_set_ref"], SOURCE_SET)
        self.assertIsNone(result["review_report_id"])
        self.assertFalse(result["claims"]["product_qualification_implied"])
        self.assertFalse(result["claims"]["release_authorization_implied"])

    def test_stale_verification_source_set_is_blocked(self) -> None:
        with self.assertRaisesRegex(FormalAssuranceError, "stale or bound to a different Execution Source Set"):
            validate_formal_assurance(
                bootstrap=bootstrap(),
                verification=verification(source_set=OLD_SOURCE_SET),
            )

    def test_formal_require_review_is_fail_closed(self) -> None:
        with self.assertRaisesRegex(FormalAssuranceError, "requires Independent Review"):
            validate_formal_assurance(
                bootstrap=bootstrap(),
                verification=verification(),
                require_review=True,
            )

    def test_formal_review_binds_exact_verification_and_result(self) -> None:
        vr = verification()
        rr = review(vr)
        result = validate_formal_assurance(
            bootstrap=bootstrap(),
            verification=vr,
            review=rr,
            require_review=True,
        )
        self.assertEqual(result["review_report_id"], rr["report_id"])
        self.assertEqual(result["review_decision"], "APPROVE")

    def test_review_of_different_result_is_blocked(self) -> None:
        vr = verification()
        rr = review(vr)
        rr["reviewed_subject"]["result_identity_ref"] = "repo:firmware@" + "f" * 40
        with self.assertRaisesRegex(FormalAssuranceError, "same result identity"):
            validate_formal_assurance(bootstrap=bootstrap(), verification=vr, review=rr)

    def test_review_missing_exact_verification_ref_is_blocked(self) -> None:
        vr = verification()
        rr = review(vr)
        rr["input_evidence_refs"] = ["artifact:test-001"]
        with self.assertRaisesRegex(FormalAssuranceError, "exact Verification report_id"):
            validate_formal_assurance(bootstrap=bootstrap(), verification=vr, review=rr)

    def test_self_verification_is_blocked(self) -> None:
        vr = verification()
        vr["verifier"] = vr["implementation_owner"]
        with self.assertRaisesRegex(FormalAssuranceError, "principal cannot equal implementation_owner"):
            validate_formal_assurance(bootstrap=bootstrap(), verification=vr)

    def test_sequence_two_requires_immediately_prior_report(self) -> None:
        current = verification(report_id="VR-RUN-001-2", sequence=2, supersedes="VR-RUN-001-1")
        with self.assertRaisesRegex(FormalAssuranceError, "requires the immediately prior report"):
            validate_formal_assurance(bootstrap=bootstrap(), verification=current)

    def test_new_source_set_can_only_replace_old_report_through_explicit_supersession(self) -> None:
        prior = verification(source_set=OLD_SOURCE_SET, report_id="VR-RUN-001-1")
        current = verification(
            source_set=SOURCE_SET,
            report_id="VR-RUN-001-2",
            sequence=2,
            supersedes=prior["report_id"],
        )
        result = validate_formal_assurance(
            bootstrap=bootstrap(),
            verification=current,
            prior_verification=prior,
        )
        self.assertEqual(result["verification_report_id"], "VR-RUN-001-2")

    def test_sequence_must_increment_exactly(self) -> None:
        prior = verification(report_id="VR-RUN-001-1")
        current = verification(
            report_id="VR-RUN-001-3",
            sequence=3,
            supersedes=prior["report_id"],
        )
        with self.assertRaisesRegex(FormalAssuranceError, "advance by exactly one"):
            validate_formal_assurance(
                bootstrap=bootstrap(),
                verification=current,
                prior_verification=prior,
            )

    def test_assurance_contracts_point_to_the_formal_gate(self) -> None:
        verification_policy = yaml.safe_load(VERIFICATION_POLICY.read_text(encoding="utf-8"))
        review_policy = yaml.safe_load(REVIEW_POLICY.read_text(encoding="utf-8"))
        for policy in (verification_policy, review_policy):
            formal = policy["formal_provenance"]
            self.assertEqual(formal["applies_when"], "L2-formal-evidence")
            self.assertEqual(formal["gate"], "scripts/validate_formal_assurance.py")
            self.assertEqual(formal["stale_subject_policy"], "BLOCKED")
            self.assertTrue(policy["rules"]["formal_report_must_bind_exact_execution_source_set"])
            self.assertTrue(policy["rules"]["formal_report_must_not_silently_reuse_stale_subject"])
        self.assertFalse(review_policy["formal_provenance"]["current_stage_default_required"])
        self.assertEqual(review_policy["formal_provenance"]["require_review_switch"], "--require-review")


if __name__ == "__main__":
    unittest.main()
