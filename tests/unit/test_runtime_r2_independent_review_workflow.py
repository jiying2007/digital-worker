from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/runtime-r2-independent-review.yml"


class RuntimeR2IndependentReviewWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_review_is_manual_read_only_and_provider_free(self) -> None:
        self.assertIn("workflow_dispatch:", self.text)
        self.assertNotIn("pull_request:", self.text)
        self.assertNotIn("\n  push:", self.text)
        self.assertIn("contents: read", self.text)
        self.assertNotIn("actions: read", self.text)
        self.assertIn('test "$DECISION" = APPROVE_R2_REVIEW', self.text)
        for forbidden in (
            "CODEX_RUNTIME_CREDENTIAL",
            "CLAUDE_RUNTIME_CREDENTIAL",
            "openai/codex-action@",
            "anthropics/claude-code-action",
        ):
            self.assertNotIn(forbidden, self.text)

    def test_review_consumes_tracked_local_verification_receipt(self) -> None:
        for token in (
            "verification_report_path",
            "reports/runtime-r2/verification/",
            "digital-worker-runtime-r2-domain-verification/v1",
            "value['status']=='pass'",
            "value['verification_execution_venue']=='local-terminal'",
            "value['runtime_home_mode']=='shared-user-home'",
            "value['credential_state_in_evidence'] is False",
            "value['github_provider_credentials_required'] is False",
            "value['independent_review_status']=='pending'",
            "value['verification_pass_claimed_by_runtime'] is False",
            "provider_execution_actors",
            "provider_execution_evidence",
            "verification_tool_commit",
        ):
            self.assertIn(token, self.text)
        self.assertNotIn("verification_run_id", self.text)
        self.assertNotIn("Runtime R2 Domain Verification", self.text)
        self.assertNotIn("actions/download-artifact", self.text)

    def test_reviewer_must_be_distinct_from_provider_executors_and_local_verifier(self) -> None:
        self.assertIn("reviewer not in set(actors.values())", self.text)
        self.assertIn("reviewer!=verifier", self.text)
        self.assertIn("review_actor_distinct_from_all_provider_executors", self.text)
        self.assertIn("review_actor_distinct_from_verifier", self.text)
        self.assertIn("BLOCKED_INDEPENDENT_REVIEW_REQUIRES_HUMAN_ACTOR", self.text)

    def test_review_report_matches_certifier_shape_but_remains_non_terminal(self) -> None:
        for token in (
            "digital-worker-runtime-r2-independent-review/v1",
            "'status':'pass'",
            "'independent':True",
            "'execution_receipts':verification['execution_receipts']",
            "'provider_execution_evidence':verification['provider_execution_evidence']",
            "'standard_id':verification['standard_id']",
            "'source_commit':verification['source_commit']",
            "'verification_tool_commit':verification['verification_tool_commit']",
            "'runtime_home_mode':'shared-user-home'",
            "'credential_state_in_evidence':False",
            "'verification_report_ref':os.environ['VERIFICATION_REPORT_PATH']",
            "'r2_qualified':False",
            "'release_ready_claimed':False",
            "'next_gate':'root-runtime-portability-certifier'",
        ):
            self.assertIn(token, self.text)
        self.assertNotIn("provider_workflow_runs", self.text)
        self.assertNotIn("reports/long-term-assets/runtime-portability-current.json", self.text)

    def test_all_actions_are_full_sha_pinned(self) -> None:
        uses = re.findall(r"^\s*uses:\s*([^\s#]+)", self.text, re.MULTILINE)
        self.assertTrue(uses)
        for item in uses:
            self.assertRegex(item, r"^[^@]+@[0-9a-f]{40}$", item)


if __name__ == "__main__":
    unittest.main()
