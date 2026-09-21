import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/runtime-r2-freeze.yml"
RUNBOOK = ROOT / "docs/runbooks/runtime-r2-local-terminal.md"


class RuntimeR2LocalTerminalContractTest(unittest.TestCase):
    def test_freeze_is_provider_credential_free(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("runtime-owned-local-terminal", text)
        self.assertIn("github_provider_credentials_required':False", text)
        self.assertIn("provider_credentials_must_not_enter_github':True", text)
        self.assertIn("runtime_home_mode':'shared-user-home'", text)
        self.assertIn("credential_state_in_evidence':False", text)
        self.assertIn("scripts/runtime-r2-local.sh", text)
        self.assertIn("control/scripts/runtime-r2-local.sh", text)

        for forbidden in (
            "runtime-r2-provider-execution.yml",
            "CODEX_RUNTIME_CREDENTIAL",
            "CLAUDE_RUNTIME_CREDENTIAL",
            "openai-api-key",
            "anthropic_api_key",
        ):
            self.assertNotIn(forbidden, text)

    def test_runbook_preserves_trust_domain_boundary(self):
        text = RUNBOOK.read_text(encoding="utf-8")
        self.assertIn("ADK_ADMIN_TOKEN", text)
        self.assertIn("Provider authentication stays local to the runtime", text)
        self.assertIn("GitHub must not require or store CODEX_RUNTIME_CREDENTIAL", text)
        self.assertIn("A GitHub PAT must never be reused as OpenAI or Anthropic provider authentication", text)
        self.assertIn("Historical freeze receipts remain immutable audit evidence", text)
        self.assertIn("shared user runtime home", text)
        self.assertIn("credential state", text)
        self.assertIn("Python 3.11", text)
        self.assertIn("Bash(mkdir *)", text)
        self.assertIn("CLAUDE_R2_MAX_TURNS", text)
        self.assertIn("--max-turns", text)
        self.assertIn("1–64", text)
        self.assertNotIn("creates an isolated CODEX_HOME", text)
        self.assertNotIn("creates an isolated HOME", text)
        self.assertIn("does not weaken the real-provider R2 evidence requirement", text)


if __name__ == "__main__":
    unittest.main()
