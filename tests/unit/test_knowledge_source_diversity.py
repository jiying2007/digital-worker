from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = (
    ROOT
    / "domains"
    / "edge-foundation"
    / "pilot"
    / "evidence"
    / "KNOWLEDGE-E3-SOURCE-DIVERSITY-001"
    / "source-diversity-receipt.json"
)
INVENTORY = (
    ROOT
    / "domains"
    / "edge-foundation"
    / "pilot"
    / "evidence"
    / "KNOWLEDGE-E3-SOURCE-INVENTORY-001"
    / "source-inventory.json"
)


class KnowledgeSourceDiversityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))

    def test_three_source_classes_satisfy_issue_coverage_rule(self) -> None:
        result = self.receipt["result"]
        classes = self.receipt["evaluated_classes"]

        self.assertEqual(len(classes), 3)
        self.assertTrue(all(item["qualifies_for_coverage"] for item in classes))
        self.assertEqual(result["status"], "SATISFIED")
        self.assertEqual(result["qualifying_source_classes"], 3)
        self.assertEqual(result["auditable_real_read_classes"], 2)
        self.assertEqual(result["explicit_not_applicable_classes"], 1)
        self.assertTrue(result["source_class_coverage_requirement_met"])

    def test_drive_not_applicable_evidence_does_not_become_integration(self) -> None:
        drive = next(
            item
            for item in self.receipt["evaluated_classes"]
            if item["source_class"] == "enterprise-collaboration-drive"
        )
        inventory_drive = next(
            item
            for item in self.inventory["source_classes"]
            if item["source_class"] == "enterprise-collaboration-drive"
        )

        self.assertEqual(
            drive["evidence_state"],
            "explicit-not-applicable-after-authenticated-discovery",
        )
        self.assertEqual(inventory_drive["integration_state"], "not-integrated")
        self.assertEqual(inventory_drive["adoption_state"], "not-adopted")

    def test_inventory_closes_only_source_class_coverage_subgap(self) -> None:
        coverage = self.inventory["source_class_coverage"]
        progress = self.inventory["progress"]

        self.assertEqual(coverage["status"], "satisfied")
        self.assertEqual(coverage["qualifying_source_classes"], 3)
        self.assertEqual(progress["source_class_coverage_requirement"], "satisfied")
        self.assertNotIn(
            "broader-real-source-diversity-or-explicit-not-applicable-evidence",
            self.inventory["open_requirements"],
        )
        self.assertIn("acl-negative-real-evidence", self.inventory["open_requirements"])
        self.assertFalse(progress["issue_16_complete"])

    def test_source_coverage_does_not_overclaim_provider_or_maturity(self) -> None:
        does_not_imply = set(self.receipt["does_not_imply"])
        for claim in {
            "acl-negative-evidence-complete",
            "google-drive-integration",
            "google-drive-adoption",
            "knowledge-provider-qualification",
            "provider-default-selection",
            "issue-16-complete",
            "product-readiness",
            "terminal-maturity",
        }:
            self.assertIn(claim, does_not_imply)


if __name__ == "__main__":
    unittest.main()
