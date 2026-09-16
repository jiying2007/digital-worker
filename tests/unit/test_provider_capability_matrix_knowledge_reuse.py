from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "config" / "integrations" / "provider-capability-matrix.yaml"


class ProviderCapabilityMatrixKnowledgeReuseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
        self.knowledge = self.doc["roles"]["knowledge_control_plane"]

    def test_first_real_reuse_is_projected_without_provider_promotion(self) -> None:
        self.assertEqual(
            self.knowledge["capabilities"]["digital_worker_real_reuse_evidence"],
            "first-real-run-eligible-broader-source-coverage-pending",
        )
        self.assertEqual(self.knowledge["decision"], "candidate-not-default")
        self.assertEqual(self.doc["status"], "evidence-in-progress")
        self.assertEqual(self.doc["provider_selection"], "not_frozen")

    def test_first_real_reuse_cannot_imply_provider_qualification(self) -> None:
        self.assertTrue(
            self.doc["rules"]["first_real_reuse_does_not_imply_provider_qualification"]
        )
        self.assertTrue(
            self.doc["rules"]["knowledge_closed_loop_requires_real_reuse_evidence"]
        )
        self.assertTrue(self.doc["rules"]["no_poc_evidence_no_pass"])


if __name__ == "__main__":
    unittest.main()
