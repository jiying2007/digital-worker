from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "config" / "integrations" / "provider-capability-matrix.yaml"


class ProviderCapabilityMatrixKnowledgeReuseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
        self.knowledge = self.doc["roles"]["knowledge_control_plane"]

    def test_first_real_reuse_projection_matches_checked_in_receipt(self) -> None:
        evidence = self.knowledge["evidence"]
        receipt_path = ROOT / evidence["first_real_reuse_receipt"]
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

        self.assertEqual(
            evidence["first_real_reuse_work_item"], "KNOWLEDGE-E3-GOVERNANCE-001"
        )
        self.assertEqual(receipt["status"], "ELIGIBLE")
        self.assertTrue(receipt["e3_knowledge_reuse_eligible"])
        self.assertEqual(receipt["qualification_scope"], "knowledge-reuse-only")
        self.assertEqual(
            self.knowledge["capabilities"]["digital_worker_real_reuse_evidence"],
            "first-real-reuse-eligible",
        )

    def test_real_reuse_does_not_promote_provider_selection_or_qualification(self) -> None:
        self.assertEqual(self.knowledge["decision"], "candidate-not-default")
        self.assertEqual(self.doc["provider_selection"], "not_frozen")
        self.assertTrue(
            self.doc["rules"]["single_real_reuse_does_not_imply_provider_qualification"]
        )
        self.assertTrue(
            self.doc["rules"]["knowledge_closed_loop_requires_real_reuse_evidence"]
        )


if __name__ == "__main__":
    unittest.main()
