from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "evaluate_knowledge_reuse_evidence.py"
SPEC = importlib.util.spec_from_file_location("real_knowledge_reuse_evaluator", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

EVIDENCE_DIR = (
    ROOT
    / "domains"
    / "edge-foundation"
    / "pilot"
    / "evidence"
    / "KNOWLEDGE-E3-GOVERNANCE-001"
)


class RealKnowledgeReuseEvidenceTests(unittest.TestCase):
    def test_checked_in_real_reuse_receipt_matches_canonical_evaluator(self) -> None:
        evidence = json.loads(
            (EVIDENCE_DIR / "knowledge-reuse-evidence.json").read_text(encoding="utf-8")
        )
        expected = json.loads(
            (EVIDENCE_DIR / "knowledge-reuse-receipt.json").read_text(encoding="utf-8")
        )
        actual = MODULE.evaluate(evidence)

        self.assertEqual(actual, expected)
        self.assertEqual(actual["status"], "ELIGIBLE")
        self.assertTrue(actual["e3_knowledge_reuse_eligible"])
        self.assertEqual(actual["qualification_scope"], "knowledge-reuse-only")
        self.assertEqual(actual["blockers"], [])
        self.assertIn("terminal-maturity", actual["does_not_imply"])

    def test_real_use_and_harvest_records_preserve_non_promotion_boundary(self) -> None:
        use_record = json.loads(
            (EVIDENCE_DIR / "actual-use-record.json").read_text(encoding="utf-8")
        )
        harvest = json.loads(
            (EVIDENCE_DIR / "knowledge-harvest.json").read_text(encoding="utf-8")
        )

        self.assertTrue(use_record["actual_use"]["materially_used"])
        self.assertFalse(
            use_record["actual_use"]["provider_output_promoted_to_domain_decision"]
        )
        self.assertFalse(harvest["canonical_knowledge_mutation_performed"])
        self.assertFalse(harvest["owner_gate_bypassed"])
        self.assertEqual(
            harvest["outcome"], "existing-authority-reused-no-duplicate-candidate"
        )
        self.assertIn("issue-16-complete", use_record["does_not_imply"])


if __name__ == "__main__":
    unittest.main()
