from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/runtime-r2-real-provider.yml"
CONTRACT = ROOT / ".github/workflows/runtime-r2-harness-contract.yml"
PROFILES = ROOT / "config/integrations/runtime-execution-profiles.json"


class RuntimeR2RealProviderWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = WORKFLOW.read_text(encoding="utf-8")
        self.profiles = json.loads(PROFILES.read_text(encoding="utf-8"))

    def test_native_codex_cli_is_default_development_path(self) -> None:
        self.assertEqual(self.profiles["default_development_profile"], "codex-cli-native")
        profile = self.profiles["profiles"]["codex-cli-native"]
        self.assertEqual(profile["executor"], "native-cli")
        self.assertEqual(profile["credential_mode"], "runtime-managed-session")
        self.assertEqual(profile["endpoint_mode"], "runtime-managed")
        self.assertIn("development", profile["intended_scope"])

    def test_is_manual_only_and_requires_explicit_human_confirmation(self) -> None:
        self.assertIn("workflow_dispatch:", self.text)
        self.assertNotIn("pull_request:", self.text)
        self.assertNotIn("\n  push:", self.text)
        self.assertIn('test "$GITHUB_EVENT_NAME" = workflow_dispatch', self.text)
        self.assertIn('test "$GITHUB_REF" = refs/heads/main', self.text)
        self.assertIn('test "$CONFIRMATION" = RUN_REAL_R2', self.text)

    def test_runtime_contract_does_not_bind_vendor_secret_names(self) -> None:
        self.assertNotIn("secrets.OPENAI_API_KEY", self.text)
        self.assertNotIn("secrets.ANTHROPIC_API_KEY", self.text)
        self.assertNotIn("BLOCKED_MISSING_OPENAI_API_KEY", self.text)
        self.assertNotIn("BLOCKED_MISSING_ANTHROPIC_API_KEY", self.text)
        self.assertIn("secrets.CODEX_RUNTIME_CREDENTIAL", self.text)
        self.assertIn("secrets.CLAUDE_RUNTIME_CREDENTIAL", self.text)
        self.assertIn("BLOCKED_MISSING_CODEX_RUNTIME_CREDENTIAL", self.text)
        self.assertIn("BLOCKED_MISSING_CLAUDE_RUNTIME_CREDENTIAL", self.text)

    def test_transport_is_profile_driven_and_endpoint_is_optional(self) -> None:
        self.assertIn("config/integrations/runtime-execution-profiles.json", self.text)
        self.assertIn("codex-github-adapter", self.text)
        self.assertIn("claude-github-adapter", self.text)
        self.assertIn("vars.CODEX_RUNTIME_ENDPOINT", self.text)
        self.assertIn("vars.CLAUDE_RUNTIME_ENDPOINT", self.text)
        self.assertIn("vars.CODEX_GATEWAY_IDENTITY", self.text)
        self.assertIn("vars.CLAUDE_GATEWAY_IDENTITY", self.text)
        self.assertIn("credential_material_recorded", self.text)
        self.assertIn("transport-descriptor", self.text)

    def test_actions_are_full_sha_pinned(self) -> None:
        uses = re.findall(r"^\s*uses:\s*([^\s#]+)", self.text, re.MULTILINE)
        self.assertTrue(uses)
        for item in uses:
            self.assertRegex(item, r"^[^@]+@[0-9a-f]{40}$", item)
        self.assertIn(
            "openai/codex-action@5c3f4ccdb2b8790f73d6b21751ac00e602aa0c02",
            self.text,
        )
        self.assertIn(
            "anthropics/claude-code-action/base-action@3b8197d3d486006dd4af54613517f21ac6ac625e",
            self.text,
        )

    def test_exact_current_runtime_and_task_identities_are_bound(self) -> None:
        for token in (
            "eeb926bd1fff75d2a5d5abb9f0ede9c8f582cc6d",
            "d12e782b46430d6bfc828f24a41f94f871a7a19a",
            "8cd87956507f9dbde0438c9135493c96f3b2d318",
            "9e732da34eac52d1418b52691ca63eec15674363",
            "e36dfec69f21806431b07daddc4bd78412179e62",
        ):
            self.assertIn(token, self.text)
        self.assertIn("scripts/runtime_r2_evidence.py prepare", self.text)
        self.assertIn("scripts/runtime_r2_evidence.py project-receipt", self.text)

    def test_frozen_plan_never_authorizes_itself(self) -> None:
        self.assertIn('plan["provider_execution_authorized"] is False', self.text)
        self.assertIn('plan["automatic_execution_enabled"] is False', self.text)
        self.assertIn("digital-worker-runtime-r2-provider-authorization/v1", self.text)
        self.assertIn("explicit-workflow-dispatch", self.text)
        self.assertIn("verification_or_release_authority", self.text)

    def test_real_runtimes_consume_isolated_bound_source_sets(self) -> None:
        self.assertIn("tools.codex_assets build", self.text)
        self.assertIn("tools.codex_assets apply", self.text)
        self.assertIn("tools.codex_assets diff", self.text)
        self.assertIn("codex-home: ${{ runner.temp }}/codex-home", self.text)
        self.assertIn("claude-binding/control/scripts/dw_runtime.py materialize", self.text)
        self.assertIn(
            'cp -a "$RUNNER_TEMP/claude-materialized/distribution/." "$RUNNER_TEMP/claude-home/.claude/"',
            self.text,
        )
        self.assertIn("HOME: ${{ runner.temp }}/claude-home", self.text)
        self.assertIn("CLAUDE_WORKING_DIR: ${{ github.workspace }}/r2-target-claude", self.text)

    def test_receipt_collection_is_non_terminal_and_cannot_write_root_pass(self) -> None:
        self.assertIn(
            "provider-executions-collected-pending-digital-worker-verification-review",
            self.text,
        )
        self.assertIn("'r2_qualified': False", self.text)
        self.assertIn("'verification_pass_claimed': False", self.text)
        self.assertNotIn("reports/long-term-assets/runtime-portability-current.json", self.text)
        self.assertNotRegex(self.text, r"['\"]r2_qualified['\"]\s*:\s*[Tt]rue")
        self.assertNotRegex(
            self.text,
            r"['\"]verification_pass_claimed['\"]\s*:\s*[Tt]rue",
        )

    def test_permanent_contract_workflow_exists(self) -> None:
        text = CONTRACT.read_text(encoding="utf-8")
        self.assertIn("runtime-r2-real-provider.yml", text)
        self.assertIn("runtime-execution-profiles.json", text)
        self.assertIn("runtime_execution_adapter.py", text)
        self.assertIn("test_runtime_execution_adapter.py", text)
        self.assertIn("test_runtime_r2_real_provider_workflow.py", text)
        uses = re.findall(r"^\s*uses:\s*([^\s#]+)", text, re.MULTILINE)
        self.assertTrue(uses)
        for item in uses:
            self.assertRegex(item, r"^[^@]+@[0-9a-f]{40}$", item)


if __name__ == "__main__":
    unittest.main()
