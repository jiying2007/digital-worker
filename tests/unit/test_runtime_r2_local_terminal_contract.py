import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/runtime-r2-freeze.yml"
RUNBOOK = ROOT / "docs/runbooks/runtime-r2-local-terminal.md"
POLICY = ROOT / "manifests/runtime-r2-qualification-policy.json"


class RuntimeR2LocalTerminalContractTest(unittest.TestCase):
    def test_freeze_is_provider_credential_free_and_non_blocking(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("runtime-owned-local-terminal", text)
        self.assertIn("github_provider_credentials_required':False", text)
        self.assertIn("provider_credentials_must_not_enter_github':True", text)
        self.assertIn("runtime_home_mode':'shared-user-home'", text)
        self.assertIn("credential_state_in_evidence':False", text)
        self.assertIn("qualification_mode':'periodic-non-blocking'", text)
        self.assertIn("repository_closure_blocking':False", text)
        self.assertIn("product_release_blocking':False", text)
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

    def test_policy_separates_r1_daily_baseline_from_periodic_r2_claim(self):
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertEqual(
            policy["schema"],
            "digital-worker-runtime-r2-qualification-policy/v1",
        )
        scope = policy["scope"]
        self.assertFalse(scope["repository_closure_blocking"])
        self.assertFalse(scope["product_release_blocking"])
        self.assertTrue(scope["runtime_binding_r1_required"])
        self.assertTrue(scope["runtime_portability_claim_requires_r2"])
        self.assertTrue(scope["terminal_replaceability_claim_requires_r2"])
        self.assertFalse(scope["r2_failure_invalidates_repository_health"])

        cadence = policy["cadence"]
        self.assertEqual(cadence["mode"], "periodic-plus-change-triggered")
        self.assertEqual(cadence["period"], "quarterly")
        self.assertEqual(cadence["recommended_max_age_days"], 120)

        campaign = policy["campaign"]
        self.assertTrue(campaign["frozen_same_task_required"])
        self.assertTrue(campaign["independent_real_runtime_execution_required"])
        self.assertTrue(campaign["replay_without_provider_state_required"])
        self.assertTrue(campaign["independent_verifier_required"])
        self.assertFalse(campaign["independent_human_review_required"])
        self.assertFalse(campaign["root_certifier_required"])
        self.assertTrue(campaign["verifier_actor_must_be_distinct_from_provider_execution_actors"])

    def test_runbook_preserves_qualification_and_trust_boundaries(self):
        text = RUNBOOK.read_text(encoding="utf-8")
        for token in (
            "ADK_ADMIN_TOKEN",
            "GitHub and provider credentials remain separate trust domains",
            "Historical freezes are immutable",
            "Python 3.11",
            "same frozen task",
            "real provider execution",
            "replay postflight",
            "quarterly",
            "qualified",
            "blocked",
            "stale",
            "not_run",
            "repository closure",
            "product release",
        ):
            self.assertIn(token, text)
        self.assertNotIn("creates an isolated CODEX_HOME", text)
        self.assertNotIn("creates an isolated HOME", text)
        self.assertNotIn("root-runtime-portability-certifier", text)


if __name__ == "__main__":
    unittest.main()
