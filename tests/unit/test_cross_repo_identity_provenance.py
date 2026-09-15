from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]
IDENTITY = ROOT / "contracts" / "cross-repo" / "identity-envelope.yaml"
OPERATING_SYSTEM = ROOT / "contracts" / "cross-repo" / "embedded-ai-operating-system.yaml"
VERIFICATION_SCHEMA = ROOT / "domains" / "edge-foundation" / "schemas" / "verification-report.schema.json"
REVIEW_SCHEMA = ROOT / "domains" / "edge-foundation" / "schemas" / "review-report.schema.json"
LEGACY_FEATURE_VERIFICATION = (
    ROOT
    / "domains"
    / "edge-foundation"
    / "pilot"
    / "evidence"
    / "FEATURE-PCR02-OTA-001"
    / "verification-report.json"
)


class CrossRepoIdentityProvenanceTests(unittest.TestCase):
    def test_identity_envelope_has_stage1_governance_and_decision_provenance(self) -> None:
        doc = yaml.safe_load(IDENTITY.read_text(encoding="utf-8"))
        self.assertEqual(doc["schema_version"], 3)

        governance = doc["digital_worker_governance"]
        self.assertEqual(governance["provider"], "digital-worker")
        self.assertEqual(governance["repository"], "jiying2007/digital-worker")
        for key in [
            "provider_commit",
            "contract_catalog_ref",
            "contract_catalog_digest",
            "selected_domain_refs",
            "selected_routing_refs",
            "materially_used_domain_skills",
        ]:
            self.assertIn(key, governance)

        escalation = doc["governance_escalation"]
        for key in [
            "from_level",
            "to_level",
            "escalation_reason",
            "prior_context_disposition",
            "new_execution_source_set_ref",
            "new_session_bootstrap_ref",
            "formal_evidence_start_ref",
        ]:
            self.assertIn(key, escalation)

        self.assertIn("reports", doc["verification"])
        self.assertIn("reports", doc["review"])
        self.assertEqual(
            set(doc["qualification_refs"]),
            {
                "product_readiness_ref",
                "terminal_maturity_ref",
                "runtime_qualification_ref",
                "adk_release_qualification_ref",
                "knowledge_provider_qualification_ref",
            },
        )

        rules = "\n".join(doc["rules"])
        for marker in [
            "exact Digital Worker provider commit",
            "L1 to L2 governance escalation requires a new exact Execution Source Set",
            "formal Verification and Review reports bind exact Execution Source Set",
            "must not be silently reused",
            "orthogonal states and never inherit PASS",
        ]:
            self.assertIn(marker, rules)

    def test_operating_system_marks_projection_artifact_semantics_and_state_isolation(self) -> None:
        doc = yaml.safe_load(OPERATING_SYSTEM.read_text(encoding="utf-8"))
        projection = doc["projection_semantics"]
        self.assertTrue(projection["repository_responsibility_projection"])
        self.assertTrue(projection["not_equal_authority_architecture_planes"])

        artifact = doc["artifact_semantics"]
        self.assertEqual(artifact["authority_kinds"], ["contract", "fact", "decision"])
        self.assertEqual(artifact["evidence_layers"], ["fact", "receipt", "report", "qualification"])
        self.assertTrue(artifact["decision_authority_is_orthogonal_to_evidence_layer"])
        self.assertTrue(artifact["classification_is_artifact_level_not_producer_inferred"])

        isolation = doc["qualification_isolation"]
        self.assertEqual(isolation["cross_state_pass_inheritance"], "forbidden")
        self.assertEqual(len(isolation["states"]), 5)

    def test_verification_schema_adds_provenance_without_invalidating_real_feature_receipt(self) -> None:
        schema = json.loads(VERIFICATION_SCHEMA.read_text(encoding="utf-8"))
        legacy = json.loads(LEGACY_FEATURE_VERIFICATION.read_text(encoding="utf-8"))
        jsonschema.validate(instance=legacy, schema=schema)

        extended = copy.deepcopy(legacy)
        extended.update(
            {
                "report_id": "VR-FEATURE-PCR02-OTA-001-2",
                "independence_evidence_refs": ["github-actions/verify-ota@exact-run"],
                "reviewed_subject": {
                    "execution_source_set_ref": "source-set:FEATURE-PCR02-OTA-001:2",
                    "result_identity_ref": "jiying2007/ota_download_test@0123456789abcdef0123456789abcdef01234567",
                    "source_identity_ref": "jiying2007/ota_download_test@eeb926bd1fff75d2a5d5abb9f0ede9c8f582cc6d",
                    "artifact_identity_refs": [
                        "sha256:7687d8058f85271e75ff3726957385afa1618aa2078dc0a6b3215d470af4a4bb"
                    ],
                },
                "decision_actor_identity_ref": "github-actions/verify-ota@exact-run",
                "input_evidence_refs": ["artifact:10355541476"],
                "report_sequence": 2,
                "supersedes": "VR-FEATURE-PCR02-OTA-001-1",
            }
        )
        jsonschema.validate(instance=extended, schema=schema)

    def test_review_schema_adds_same_exact_subject_and_supersession_shape(self) -> None:
        schema = json.loads(REVIEW_SCHEMA.read_text(encoding="utf-8"))
        legacy = {
            "run_id": "FEATURE-PCR02-OTA-001",
            "reviewer": "independent-reviewer",
            "implementation_owner": "engineering-owner",
            "independence_confirmed": True,
            "decision": "APPROVE",
            "findings": [],
            "evidence_refs": [],
        }
        jsonschema.validate(instance=legacy, schema=schema)

        extended = copy.deepcopy(legacy)
        extended.update(
            {
                "report_id": "RR-FEATURE-PCR02-OTA-001-2",
                "independence_evidence_refs": ["reviewer-identity:independent-reviewer"],
                "reviewed_subject": {
                    "execution_source_set_ref": "source-set:FEATURE-PCR02-OTA-001:2",
                    "result_identity_ref": "jiying2007/ota_download_test@0123456789abcdef0123456789abcdef01234567",
                    "source_identity_ref": "jiying2007/ota_download_test@eeb926bd1fff75d2a5d5abb9f0ede9c8f582cc6d",
                    "artifact_identity_refs": [],
                },
                "decision_actor_identity_ref": "reviewer-identity:independent-reviewer",
                "input_evidence_refs": ["verification-report:VR-FEATURE-PCR02-OTA-001-2"],
                "report_sequence": 2,
                "supersedes": "RR-FEATURE-PCR02-OTA-001-1",
            }
        )
        jsonschema.validate(instance=extended, schema=schema)


if __name__ == "__main__":
    unittest.main()
