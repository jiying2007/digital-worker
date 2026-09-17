from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/runtime-r2-domain-verification.yml"


class RuntimeR2DomainVerificationWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_is_manual_read_only_and_never_calls_a_provider(self) -> None:
        self.assertIn("workflow_dispatch:", self.text)
        self.assertNotIn("pull_request:", self.text)
        self.assertNotIn("\n  push:", self.text)
        self.assertIn("actions: read", self.text)
        self.assertIn("contents: read", self.text)
        self.assertIn('test "$CONFIRMATION" = VERIFY_REAL_R2', self.text)
        self.assertNotIn("openai/codex-action@", self.text)
        self.assertNotIn("anthropics/claude-code-action", self.text)

    def test_cross_run_artifacts_are_exactly_bound(self) -> None:
        self.assertGreaterEqual(self.text.count("run-id: ${{ inputs.provider_run_id }}"), 3)
        self.assertIn("r2-frozen-plan-${{ inputs.provider_run_id }}", self.text)
        self.assertIn("r2-codex-real-${{ inputs.provider_run_id }}", self.text)
        self.assertIn("r2-claude-real-${{ inputs.provider_run_id }}", self.text)
        self.assertIn("native_receipt']['sha256']", self.text)

    def test_incomplete_provider_patch_fails_closed(self) -> None:
        self.assertIn("BLOCKED_PROVIDER_RESULT_HAS_UNTRACKED_FILES_NOT_PRESENT_IN_BINARY_PATCH", self.text)
        self.assertGreaterEqual(self.text.count("grep -q '^?? '"), 1)
        self.assertIn('test -s "$RUNNER_TEMP/r2-codex/codex.patch"', self.text)
        self.assertIn('test -s "$RUNNER_TEMP/r2-claude/claude.patch"', self.text)

    def test_both_runtime_results_are_replayed_and_host_verified(self) -> None:
        self.assertEqual(self.text.count("git -C \"$root\" apply --check"), 2)
        self.assertEqual(self.text.count("python -m unittest discover -s tests -v"), 2)
        self.assertEqual(self.text.count("python verify_ota_manifest.py --manifest ota-manifest.v1.json"), 2)
        self.assertIn("tree_digest(cr) == expected_tree(cn)", self.text)
        self.assertIn("tree_digest(ar) == expected_tree(an)", self.text)

    def test_domain_report_is_bounded_and_review_remains_pending(self) -> None:
        self.assertIn("digital-worker-runtime-r2-domain-verification/v1", self.text)
        self.assertIn("'status': 'pass'", self.text)
        self.assertIn("'comparison_id': 'R2-FEATURE-PCR02-OTA-001'", self.text)
        self.assertIn("'source_repository': 'jiying2007/digital-worker'", self.text)
        self.assertIn("'independent_review_status': 'pending'", self.text)
        self.assertNotIn("'r2_qualified': True", self.text)
        self.assertNotIn("reports/long-term-assets/runtime-portability-current.json", self.text)

    def test_all_actions_are_full_sha_pinned(self) -> None:
        uses = re.findall(r"^\s*uses:\s*([^\s#]+)", self.text, re.MULTILINE)
        self.assertTrue(uses)
        for item in uses:
            self.assertRegex(item, r"^[^@]+@[0-9a-f]{40}$", item)


if __name__ == "__main__":
    unittest.main()
