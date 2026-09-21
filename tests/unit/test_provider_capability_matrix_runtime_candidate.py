from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "config" / "integrations" / "provider-capability-matrix.yaml"
LOCK = ROOT / "config" / "integrations" / "cross-repo-lock.json"


class ProviderCapabilityMatrixRuntimeCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
        self.lock = json.loads(LOCK.read_text(encoding="utf-8"))
        self.runtime = self.doc["roles"]["runtime_binding"]
        self.claude = self.runtime["candidates"]["claude_code"]
        self.authoritative_claude = self.lock["runtime_bindings"]["claude-code"]

    def test_claude_candidate_projects_exact_r1_ready_identity(self) -> None:
        self.assertEqual(
            self.claude["identity_ref"],
            "config/integrations/cross-repo-lock.json#/runtime_bindings/claude-code",
        )
        self.assertEqual(self.claude["repository"], "jiying2007/claude")
        self.assertEqual(self.claude["runtime_target"], "claude-code")
        self.assertEqual(self.claude["source_identity_mode"], "exact-release-source-blobs")
        self.assertEqual(self.claude["status"], "source-set-bound")
        self.assertEqual(
            self.claude["binding_commit"],
            self.authoritative_claude["commit"],
        )
        self.assertEqual(
            self.claude["r1_exact_head_workflow_run"],
            self.authoritative_claude["r1_exact_head_workflow_run"],
        )
        self.assertEqual(
            self.claude["r1_fresh_main_workflow_run"],
            self.authoritative_claude["r1_fresh_main_workflow_run"],
        )

    def test_r1_ready_candidate_remains_non_terminal(self) -> None:
        self.assertIs(self.claude["r1_binding_ready"], True)
        self.assertEqual(self.claude["verified_runtime_execution_receipt"], "pending")
        self.assertEqual(self.claude["r2_real_provider_substitution"], "pending")
        self.assertIn(self.claude["status"], {"source-set-bound", "ready", "active"})
        self.assertEqual(self.runtime["decision"], "codex-source-set-bound-default-not-frozen")

    def test_provider_selection_remains_not_frozen(self) -> None:
        self.assertEqual(self.doc["provider_selection"], "not_frozen")
        self.assertTrue(self.doc["rules"]["r1_binding_conformance_is_not_terminal_replaceability"])
        self.assertTrue(self.doc["rules"]["terminal_replaceability_requires_r2_real_provider_substitution"])


if __name__ == "__main__":
    unittest.main()
