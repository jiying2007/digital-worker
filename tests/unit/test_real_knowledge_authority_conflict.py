from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = (
    ROOT
    / "domains"
    / "edge-foundation"
    / "pilot"
    / "evidence"
    / "KNOWLEDGE-E3-AUTHORITY-CONFLICT-001"
    / "authority-conflict-evidence.json"
)
LOCK = ROOT / "config" / "integrations" / "cross-repo-lock.json"


class RealKnowledgeAuthorityConflictTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.lock = json.loads(LOCK.read_text(encoding="utf-8"))
        self.sources = {
            source["knowledge_id"]: source
            for source in self.evidence["observed_sources"]
        }

    def test_conflict_uses_exact_pinned_provider_identity(self) -> None:
        provider = self.evidence["knowledge_provider"]
        authoritative = self.lock["providers"]["knowledge_control_plane"]

        for key in (
            "repository",
            "commit",
            "contract",
            "contract_version",
            "contract_canonical_sha256",
        ):
            self.assertEqual(provider[key], authoritative[key])

    def test_two_exact_real_candidates_have_materially_different_near_term_positions(self) -> None:
        original = self.sources[
            "pcr02-customer-ubi-startup-optimization-20260803"
        ]
        review = self.sources[
            "pcr02-customer-ubi-startup-optimization-review-20260804"
        ]

        self.assertEqual(
            original["source_blob_sha"], "d192a237f144d2774f13897a08a24cc96b91b96c"
        )
        self.assertEqual(
            review["source_blob_sha"], "67fe37b0237445a5b1e3f23fc654ff6ecef868ab"
        )
        self.assertEqual(original["lifecycle_status"], "reviewing")
        self.assertEqual(review["lifecycle_status"], "reviewing")
        self.assertEqual(original["promotion"], "none")
        self.assertEqual(review["promotion"], "none")
        self.assertTrue(original["manual_validation_pending"])
        self.assertTrue(review["manual_validation_pending"])
        self.assertTrue(review["supersedes_candidate_tag"])
        self.assertNotEqual(original["position_summary"], review["position_summary"])

    def test_conflict_is_unresolved_and_no_authority_is_selected(self) -> None:
        conflict = self.evidence["conflict_evaluation"]
        disposition = self.evidence["reuse_disposition"]

        self.assertEqual(conflict["state"], "detected-unresolved")
        self.assertTrue(conflict["overlapping_scope"] if "overlapping_scope" in conflict else self.evidence["topic"]["overlapping_scope"])
        self.assertFalse(conflict["authoritative_supersession_proven"])
        self.assertEqual(conflict["resolution_authority"], "not-proven")
        self.assertFalse(disposition["eligible_for_reuse"])
        self.assertEqual(disposition["decision"], "BLOCKED_AUTHORITY_CONFLICT")
        self.assertIsNone(disposition["selected_authority"])
        self.assertFalse(disposition["actual_use_performed"])
        self.assertFalse(disposition["promotion_performed"])

    def test_conflict_detection_does_not_create_owner_or_maturity_decision(self) -> None:
        does_not_imply = set(self.evidence["does_not_imply"])
        for claim in {
            "owner-decision",
            "authoritative-supersession",
            "active-knowledge-promotion",
            "acl-negative-evidence-complete",
            "issue-16-complete",
            "knowledge-provider-qualification",
            "provider-default-selection",
            "product-readiness",
            "terminal-maturity",
        }:
            self.assertIn(claim, does_not_imply)


if __name__ == "__main__":
    unittest.main()
