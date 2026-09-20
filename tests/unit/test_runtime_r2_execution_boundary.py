from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / ".github/workflows/runtime-r2-freeze.yml"
REVIEW = ROOT / ".github/workflows/runtime-r2-independent-review.yml"
INTAKE = ROOT / "scripts/runtime_r2_intake.py"
LOCAL_VERIFY = ROOT / "scripts/runtime_r2_local_verify.py"
CONTRACT = ROOT / ".github/workflows/runtime-r2-harness-contract.yml"
RETIRED = (
    ROOT / ".github/workflows/runtime-r2-real-provider.yml",
    ROOT / ".github/workflows/runtime-r2-domain-verification.yml",
)


class RuntimeR2ExecutionBoundaryTests(unittest.TestCase):
    def test_dead_github_provider_and_domain_verification_workflows_are_retired(self) -> None:
        for path in RETIRED:
            self.assertFalse(path.exists(), path)

    def test_digital_worker_holds_no_provider_credentials_or_provider_actions(self) -> None:
        for path in (FREEZE, REVIEW, INTAKE, LOCAL_VERIFY):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("CODEX_RUNTIME_CREDENTIAL", text)
            self.assertNotIn("CLAUDE_RUNTIME_CREDENTIAL", text)
            self.assertNotIn("openai/codex-action@", text)
            self.assertNotIn("anthropics/claude-code-action", text)

    def test_freeze_is_manual_main_only_and_local_terminal_handoff(self) -> None:
        text = FREEZE.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("\n  push:", text)
        self.assertIn('test "$CONFIRMATION" = FREEZE_REAL_R2', text)
        self.assertIn("provider_credentials_held_by_digital_worker':False", text)
        self.assertIn("provider_execution_authorized':False", text)
        self.assertIn("'mode':'runtime-owned-local-terminal'", text)
        self.assertIn("'github_provider_credentials_required':False", text)
        self.assertIn("'provider_credentials_must_not_enter_github':True", text)
        self.assertIn("'codex':'scripts/runtime-r2-local.sh'", text)
        self.assertIn("'claude-code':'control/scripts/runtime-r2-local.sh'", text)
        self.assertNotIn("runtime-r2-provider-execution.yml", text)

    def test_local_intake_is_exact_and_provider_credential_free(self) -> None:
        text = INTAKE.read_text(encoding="utf-8")
        self.assertIn("digital-worker-runtime-r2-local-intake/v1", text)
        self.assertIn("runtime-owned-local-terminal", text)
        self.assertIn("github_provider_credential_used", text)
        self.assertIn("native-to-portable projection", text)
        self.assertIn("result-tree.tar.gz", text)
        self.assertIn("worktree-result:sha256:", text)
        self.assertIn("sys.executable", text)
        self.assertNotIn('gh", "attestation", "verify', text)
        self.assertNotIn("--signer-workflow", text)
        self.assertNotIn("provider_workflow_runs", text)

    def test_local_verifier_runs_both_runtime_host_checks(self) -> None:
        text = LOCAL_VERIFY.read_text(encoding="utf-8")
        self.assertIn("digital-worker-runtime-r2-domain-verification/v1", text)
        self.assertIn("local-evidence-integrity", text)
        self.assertIn("replay-complete-result-tree", text)
        self.assertIn("provider_execution_evidence", text)
        self.assertIn("verification_execution_venue", text)
        self.assertIn("local-terminal", text)
        self.assertIn('"independent_review_status": "pending"', text)
        self.assertNotIn("provider_workflow_runs", text)

    def test_all_remaining_workflow_actions_are_full_sha_pinned(self) -> None:
        for path in (FREEZE, REVIEW, CONTRACT):
            text = path.read_text(encoding="utf-8")
            uses = re.findall(r"^\s*uses:\s*([^\s#]+)", text, re.MULTILINE)
            self.assertTrue(uses, path)
            for item in uses:
                self.assertRegex(item, r"^[^@]+@[0-9a-f]{40}$", item)


if __name__ == "__main__":
    unittest.main()
