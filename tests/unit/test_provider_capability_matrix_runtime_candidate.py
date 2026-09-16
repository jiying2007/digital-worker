from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "config" / "integrations" / "provider-capability-matrix.yaml"


class ProviderCapabilityMatrixRuntimeCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.doc = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
        self.runtime = self.doc["roles"]["runtime_binding"]
        self.claude = self.runtime["candidates"]["claude_code"]

    def test_claude_candidate_projects_real_blocked_identity(self) -> None:
        self.assertEqual(self.claude["repository"], "jiying2007/claude")
        self.assertEqual(self.claude["runtime_target"], "claude-code")
        self.assertEqual(self.claude["source_identity_mode"], "exact-release-source-blobs")
        self.assertEqual(self.claude["status"], "binding-candidate-blocked")
        self.assertEqual(self.claude["candidate_pr"], "jiying2007/claude#1")
        self.assertEqual(self.claude["blocker_ref"], "jiying2007/claude#2")
        self.assertEqual(
            self.claude["blocker"],
            "github-hosted-runner-admission-before-step-execution",
        )

    def test_blocked_candidate_cannot_be_projected_as_ready_or_r2(self) -> None:
        self.assertIs(self.claude["r1_binding_ready"], False)
        self.assertEqual(self.claude["r2_real_provider_substitution"], "pending")
        self.assertNotIn(self.claude["status"], {"source-set-bound", "ready", "active"})
        self.assertEqual(self.runtime["decision"], "codex-source-set-bound-default-not-frozen")

    def test_provider_selection_remains_not_frozen(self) -> None:
        self.assertEqual(self.doc["provider_selection"], "not_frozen")
        self.assertTrue(self.doc["rules"]["r1_binding_conformance_is_not_terminal_replaceability"])
        self.assertTrue(self.doc["rules"]["terminal_replaceability_requires_r2_real_provider_substitution"])


if __name__ == "__main__":
    unittest.main()
