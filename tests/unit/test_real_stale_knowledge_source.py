from __future__ import annotations

import json
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = (
    ROOT
    / "domains"
    / "edge-foundation"
    / "pilot"
    / "evidence"
    / "KNOWLEDGE-E3-STALE-SOURCE-001"
    / "stale-source-evidence.json"
)
LOCK = ROOT / "config" / "integrations" / "cross-repo-lock.json"


class RealStaleKnowledgeSourceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.lock = json.loads(LOCK.read_text(encoding="utf-8"))

    def test_stale_observation_uses_exact_pinned_provider_identity(self) -> None:
        provider = self.evidence["knowledge_provider"]
        authoritative = self.lock["providers"]["knowledge_control_plane"]

        self.assertEqual(provider["repository"], authoritative["repository"])
        self.assertEqual(provider["commit"], authoritative["commit"])
        self.assertEqual(provider["contract"], authoritative["contract"])
        self.assertEqual(
            provider["contract_version"], authoritative["contract_version"]
        )
        self.assertEqual(
            provider["contract_canonical_sha256"],
            authoritative["contract_canonical_sha256"],
        )

    def test_exact_real_item_is_past_review_after(self) -> None:
        item = self.evidence["observed_item"]
        freshness = self.evidence["freshness_evaluation"]
        review_after = date.fromisoformat(item["review_after"])
        checked_on = date.fromisoformat(self.evidence["checked_on"])

        self.assertEqual(
            item["knowledge_id"],
            "xcrz-pcr02-warm-current-workload-cmdq-debug-v2-20260815",
        )
        self.assertEqual(
            item["source_blob_sha"], "faad0cb51ea5eb825b24a3dff6bd9cda33447068"
        )
        self.assertEqual(item["lifecycle_status"], "reviewing")
        self.assertTrue(item["manual_validation_pending"])
        self.assertLess(review_after, checked_on)
        self.assertEqual((checked_on - review_after).days, 1)
        self.assertEqual(freshness["state"], "stale")
        self.assertEqual(freshness["days_past_review_after"], 1)

    def test_stale_item_is_detected_but_not_reused_or_promoted(self) -> None:
        access = self.evidence["access_observation"]
        disposition = self.evidence["reuse_disposition"]

        self.assertTrue(access["source_real"])
        self.assertTrue(access["exact_provider_commit_fetched"])
        self.assertTrue(access["exact_source_file_fetched"])
        self.assertTrue(access["does_not_count_as_acl_negative_test"])
        self.assertFalse(disposition["eligible_for_reuse"])
        self.assertEqual(disposition["decision"], "BLOCKED_STALE_SOURCE")
        self.assertFalse(disposition["actual_use_performed"])
        self.assertFalse(disposition["promotion_performed"])

    def test_stale_detection_does_not_overclaim_other_maturity(self) -> None:
        does_not_imply = set(self.evidence["does_not_imply"])
        for claim in {
            "acl-negative-evidence-complete",
            "authority-conflict-evidence-complete",
            "issue-16-complete",
            "knowledge-provider-qualification",
            "provider-default-selection",
            "product-readiness",
            "terminal-maturity",
        }:
            self.assertIn(claim, does_not_imply)


if __name__ == "__main__":
    unittest.main()
