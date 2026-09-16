from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = (
    ROOT
    / "domains"
    / "edge-foundation"
    / "pilot"
    / "evidence"
    / "KNOWLEDGE-E3-SOURCE-INVENTORY-001"
    / "source-inventory.json"
)
REUSE_RECEIPT = (
    ROOT
    / "domains"
    / "edge-foundation"
    / "pilot"
    / "evidence"
    / "KNOWLEDGE-E3-GOVERNANCE-001"
    / "knowledge-reuse-receipt.json"
)


class KnowledgeSourceInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        self.by_class = {
            item["source_class"]: item for item in self.inventory["source_classes"]
        }

    def test_inventory_covers_three_honest_source_class_states(self) -> None:
        self.assertEqual(
            set(self.by_class),
            {
                "governed-repository-markdown",
                "github-issue-pr-ci-fact-source",
                "enterprise-collaboration-drive",
            },
        )
        self.assertEqual(
            self.by_class["governed-repository-markdown"]["status"],
            "applicable-read-verified-and-reused",
        )
        self.assertEqual(
            self.by_class["github-issue-pr-ci-fact-source"]["status"],
            "read-verified-observation-only",
        )
        self.assertEqual(
            self.by_class["enterprise-collaboration-drive"]["status"],
            "discovery-tested-no-applicable-source",
        )

    def test_governed_markdown_inventory_matches_real_reuse_receipt(self) -> None:
        source = self.by_class["governed-repository-markdown"]
        receipt = json.loads(REUSE_RECEIPT.read_text(encoding="utf-8"))

        self.assertEqual(
            source["provider_commit"],
            "51e4f8166657d9d082f523335d350d0e8c2890a9",
        )
        self.assertEqual(source["source_ref"], "registry/schema.md")
        self.assertEqual(
            source["knowledge_id"],
            "knowledge-hub-registry-schema-readability-extension",
        )
        self.assertTrue(source["actual_use"]["materially_used"])
        self.assertEqual(receipt["status"], "ELIGIBLE")
        self.assertTrue(receipt["e3_knowledge_reuse_eligible"])
        self.assertFalse(source["promotion_performed"])

    def test_issue_source_remains_observation_not_active_knowledge(self) -> None:
        source = self.by_class["github-issue-pr-ci-fact-source"]
        disposition = source["knowledge_disposition"]

        self.assertEqual(source["source_identity"]["issue_number"], 2)
        self.assertEqual(source["source_identity"]["issue_id"], 5468835804)
        self.assertEqual(source["acl"]["state"], "allowed")
        self.assertFalse(disposition["eligible_for_direct_active_write"])
        self.assertFalse(disposition["promotion_performed"])

    def test_drive_discovery_does_not_become_integration_or_adoption(self) -> None:
        source = self.by_class["enterprise-collaboration-drive"]
        by_query = {item["query"]: item for item in source["discovery"]["queries"]}

        self.assertEqual(by_query["PCR02"]["applicable_results"], 0)
        self.assertEqual(by_query["SSC305"]["applicable_results"], 0)
        self.assertEqual(by_query["UBIFS"]["applicable_results"], 0)
        self.assertEqual(by_query["OTA"]["applicable_results"], 0)
        self.assertEqual(source["integration_state"], "not-integrated")
        self.assertEqual(source["adoption_state"], "not-adopted")
        self.assertEqual(source["acl"]["negative_acl_test"], "not-yet-proven")

    def test_real_stale_case_closes_only_stale_detection_subgap(self) -> None:
        stale = self.inventory["negative_evidence"]["stale_source"]
        conflict = self.inventory["negative_evidence"]["authority_conflict"]

        self.assertEqual(stale["status"], "real-detected-blocked")
        self.assertFalse(stale["reuse_eligible"])
        self.assertEqual(stale["review_after"], "2026-09-15")
        self.assertEqual(stale["checked_on"], "2026-09-16")
        self.assertEqual(conflict["status"], "not-yet-proven")
        self.assertEqual(self.inventory["progress"]["real_stale_source_cases"], 1)

    def test_inventory_advances_without_promoting_issue_or_provider(self) -> None:
        progress = self.inventory["progress"]
        self.assertTrue(progress["source_inventory_subgap_advanced"])
        self.assertFalse(progress["issue_16_complete"])
        self.assertFalse(progress["knowledge_provider_qualification"])
        self.assertFalse(progress["provider_default_selected"])
        self.assertFalse(progress["terminal_maturity"])
        self.assertFalse(progress["product_readiness_promoted"])
        self.assertIn(
            "acl-negative-real-evidence", self.inventory["open_requirements"]
        )
        self.assertIn(
            "authority-conflict-real-evidence", self.inventory["open_requirements"]
        )
        self.assertNotIn(
            "stale-source-or-authority-conflict-real-evidence",
            self.inventory["open_requirements"],
        )


if __name__ == "__main__":
    unittest.main()
