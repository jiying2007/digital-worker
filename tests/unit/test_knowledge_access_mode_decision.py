from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DECISION = (
    ROOT
    / "domains"
    / "edge-foundation"
    / "pilot"
    / "evidence"
    / "KNOWLEDGE-E3-ACCESS-MODE-001"
    / "access-mode-decision.json"
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
MATRIX = ROOT / "config" / "integrations" / "provider-capability-matrix.yaml"


class KnowledgeAccessModeDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.decision = json.loads(DECISION.read_text(encoding="utf-8"))
        self.inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        self.matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))

    def test_decision_is_not_frozen_without_default_or_backup(self) -> None:
        selection = self.decision["selection"]

        self.assertEqual(selection["decision"], "not_frozen")
        self.assertIsNone(selection["default_mode"])
        self.assertIsNone(selection["backup_mode"])
        self.assertEqual(selection["leading_candidate"], "knowledge-hub-governed-reuse")
        self.assertEqual(selection["leading_candidate_status"], "candidate-not-default")

    def test_decision_binds_real_positive_and_negative_evidence(self) -> None:
        basis = self.decision["evidence_basis"]

        for ref in basis.values():
            self.assertTrue((ROOT / ref).is_file(), ref)

        by_mode = {item["mode"]: item for item in self.decision["observed_modes"]}
        self.assertEqual(
            by_mode["knowledge-hub-governed-reuse"]["state"],
            "validated-candidate-not-default",
        )
        self.assertEqual(
            by_mode["source-system-direct-fact-observation"]["state"],
            "bounded-fact-path-not-knowledge-default",
        )
        self.assertEqual(
            by_mode["enterprise-collaboration-drive"]["state"],
            "discovery-tested-not-ready",
        )

    def test_access_decision_does_not_freeze_provider_matrix(self) -> None:
        knowledge = self.matrix["roles"]["knowledge_control_plane"]

        self.assertEqual(self.matrix["provider_selection"], "not_frozen")
        self.assertEqual(knowledge["decision"], "candidate-not-default")
        self.assertEqual(
            knowledge["capabilities"]["digital_worker_real_reuse_evidence"],
            "first-real-reuse-eligible",
        )

    def test_inventory_closes_only_access_mode_decision_subgap(self) -> None:
        access = self.inventory["access_mode_decision"]
        progress = self.inventory["progress"]

        self.assertEqual(access["status"], "evidence-backed-not-frozen")
        self.assertIsNone(access["default_mode"])
        self.assertIsNone(access["backup_mode"])
        self.assertEqual(progress["knowledge_access_mode_decision"], "not_frozen")
        self.assertNotIn(
            "knowledge-access-default-backup-not-frozen-decision",
            self.inventory["open_requirements"],
        )
        self.assertIn("acl-negative-real-evidence", self.inventory["open_requirements"])
        self.assertFalse(progress["issue_16_complete"])
        self.assertFalse(progress["knowledge_provider_qualification"])
        self.assertFalse(progress["provider_default_selected"])

    def test_not_frozen_decision_does_not_overclaim_maturity(self) -> None:
        does_not_imply = set(self.decision["does_not_imply"])
        for claim in {
            "provider-default-selection",
            "backup-provider-selection",
            "knowledge-provider-qualification",
            "issue-16-complete",
            "product-readiness",
            "terminal-maturity",
        }:
            self.assertIn(claim, does_not_imply)


if __name__ == "__main__":
    unittest.main()
