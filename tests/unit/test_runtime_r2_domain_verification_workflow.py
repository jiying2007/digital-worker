from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/runtime-r2-domain-verification.yml"
INTAKE = ROOT / "scripts/runtime_r2_intake.py"


class RuntimeR2DomainVerificationWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = WORKFLOW.read_text(encoding="utf-8")
        self.intake = INTAKE.read_text(encoding="utf-8")

    def test_is_manual_read_only_and_never_calls_a_provider(self) -> None:
        self.assertIn("workflow_dispatch:", self.text)
        self.assertNotIn("pull_request:", self.text)
        self.assertNotIn("\n  push:", self.text)
        self.assertIn("contents: read", self.text)
        self.assertIn('test "$CONFIRMATION" = VERIFY_REAL_R2', self.text)
        for forbidden in (
            "CODEX_RUNTIME_CREDENTIAL",
            "CLAUDE_RUNTIME_CREDENTIAL",
            "openai/codex-action@",
            "anthropics/claude-code-action",
        ):
            self.assertNotIn(forbidden, self.text)

    def test_intake_is_tracked_attested_and_exactly_bound(self) -> None:
        self.assertIn("reports/runtime-r2/intake/", self.text)
        self.assertIn("scripts/runtime_r2_intake.py", self.text)
        self.assertIn("gh\", \"attestation\", \"verify", self.intake)
        self.assertIn("--signer-workflow", self.intake)
        self.assertIn("--source-digest", self.intake)
        self.assertIn("frozen plan is not byte-identical", self.intake)
        self.assertIn("project-receipt", self.intake)

    def test_untracked_files_are_covered_by_replay_complete_tree(self) -> None:
        self.assertIn("result-tree.tar.gz", self.intake)
        self.assertIn("safe_extract_tar(result_archive, result_tree)", self.intake)
        self.assertNotIn("BLOCKED_PROVIDER_RESULT_HAS_UNTRACKED_FILES_NOT_PRESENT_IN_BINARY_PATCH", self.text)
        self.assertIn("tree_digest(cr)==expected(cn)", self.text)
        self.assertIn("tree_digest(ar)==expected(an)", self.text)

    def test_both_runtime_results_are_host_verified(self) -> None:
        self.assertEqual(self.text.count("python -m unittest discover -s tests -v"), 2)
        self.assertEqual(self.text.count("python verify_ota_manifest.py --manifest ota-manifest.v1.json"), 2)
        self.assertIn("github-oidc-attestation", self.text)
        self.assertIn("replay-complete-result-tree", self.text)

    def test_domain_report_is_bounded_and_review_remains_pending(self) -> None:
        for token in (
            "digital-worker-runtime-r2-domain-verification/v1",
            "'status':'pass'",
            "'source_repository':'jiying2007/digital-worker'",
            "'independent_review_status':'pending'",
            "'verification_pass_claimed_by_runtime':False",
            "'provider_workflow_runs':collection['provider_workflow_runs']",
            "'provider_execution_actors':collection['provider_execution_actors']",
        ):
            self.assertIn(token, self.text)
        self.assertNotIn("'r2_qualified':True", self.text)
        self.assertNotIn("reports/long-term-assets/runtime-portability-current.json", self.text)

    def test_all_actions_are_full_sha_pinned(self) -> None:
        uses = re.findall(r"^\s*uses:\s*([^\s#]+)", self.text, re.MULTILINE)
        self.assertTrue(uses)
        for item in uses:
            self.assertRegex(item, r"^[^@]+@[0-9a-f]{40}$", item)


if __name__ == "__main__":
    unittest.main()
