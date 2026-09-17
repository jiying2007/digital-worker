from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / ".github/workflows/runtime-r2-freeze.yml"
DOMAIN = ROOT / ".github/workflows/runtime-r2-domain-verification.yml"
REVIEW = ROOT / ".github/workflows/runtime-r2-independent-review.yml"
INTAKE = ROOT / "scripts/runtime_r2_intake.py"
CONTRACT = ROOT / ".github/workflows/runtime-r2-harness-contract.yml"
RETIRED = ROOT / ".github/workflows/runtime-r2-real-provider.yml"


class RuntimeR2ExecutionBoundaryTests(unittest.TestCase):
    def test_combined_provider_execution_is_retired(self) -> None:
        self.assertFalse(RETIRED.exists())

    def test_digital_worker_holds_no_provider_credentials_or_provider_actions(self) -> None:
        for path in (FREEZE, DOMAIN, REVIEW):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("CODEX_RUNTIME_CREDENTIAL", text)
            self.assertNotIn("CLAUDE_RUNTIME_CREDENTIAL", text)
            self.assertNotIn("openai/codex-action@", text)
            self.assertNotIn("anthropics/claude-code-action", text)

    def test_freeze_is_manual_main_only_and_never_authorizes_execution(self) -> None:
        text = FREEZE.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("\n  push:", text)
        self.assertIn('test "$CONFIRMATION" = FREEZE_REAL_R2', text)
        self.assertIn("provider_credentials_held_by_digital_worker':False", text)
        self.assertIn("provider_execution_authorized':False", text)
        self.assertIn("jiying2007/codex/.github/workflows/runtime-r2-provider-execution.yml", text)
        self.assertIn("jiying2007/claude/.github/workflows/runtime-r2-provider-execution.yml", text)

    def test_intake_requires_attested_runtime_owned_evidence(self) -> None:
        text = INTAKE.read_text(encoding="utf-8")
        for token in (
            "gh\", \"attestation\", \"verify",
            "--signer-workflow",
            "--source-ref",
            "--source-digest",
            "jiying2007/codex/.github/workflows/runtime-r2-provider-execution.yml",
            "jiying2007/claude/.github/workflows/runtime-r2-provider-execution.yml",
            "provider-executions-collected-pending-digital-worker-verification-review",
            '"verification_pass_claimed": False',
            '"r2_qualified": False',
        ):
            self.assertIn(token, text)

    def test_all_workflow_actions_are_full_sha_pinned(self) -> None:
        for path in (FREEZE, DOMAIN, REVIEW, CONTRACT):
            text = path.read_text(encoding="utf-8")
            uses = re.findall(r"^\s*uses:\s*([^\s#]+)", text, re.MULTILINE)
            self.assertTrue(uses, path)
            for item in uses:
                self.assertRegex(item, r"^[^@]+@[0-9a-f]{40}$", item)


if __name__ == "__main__":
    unittest.main()
