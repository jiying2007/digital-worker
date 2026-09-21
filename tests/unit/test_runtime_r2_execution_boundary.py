from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / ".github/workflows/runtime-r2-freeze.yml"
INTAKE = ROOT / "scripts/runtime_r2_intake.py"
LOCAL_VERIFY = ROOT / "scripts/runtime_r2_local_verify.py"
CONTRACT = ROOT / ".github/workflows/runtime-r2-harness-contract.yml"
POLICY = ROOT / "manifests/runtime-r2-qualification-policy.json"
RETIRED = (
    ROOT / ".github/workflows/runtime-r2-real-provider.yml",
    ROOT / ".github/workflows/runtime-r2-domain-verification.yml",
    ROOT / ".github/workflows/runtime-r2-independent-review.yml",
)


class RuntimeR2ExecutionBoundaryTests(unittest.TestCase):
    def test_dead_github_provider_review_and_domain_workflows_are_retired(self) -> None:
        for path in RETIRED:
            self.assertFalse(path.exists(), path)

    def test_digital_worker_holds_no_provider_credentials_or_provider_actions(self) -> None:
        for path in (FREEZE, INTAKE, LOCAL_VERIFY):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("CODEX_RUNTIME_CREDENTIAL", text)
            self.assertNotIn("CLAUDE_RUNTIME_CREDENTIAL", text)
            self.assertNotIn("openai/codex-action@", text)
            self.assertNotIn("anthropics/claude-code-action", text)

    def test_freeze_is_manual_main_only_local_terminal_and_non_blocking(self) -> None:
        text = FREEZE.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("\n  push:", text)
        self.assertIn('test "$CONFIRMATION" = FREEZE_REAL_R2', text)
        self.assertIn("provider_credentials_held_by_digital_worker':False", text)
        self.assertIn("provider_execution_authorized':False", text)
        self.assertIn("'mode':'runtime-owned-local-terminal'", text)
        self.assertIn("'runtime_home_mode':'shared-user-home'", text)
        self.assertIn("'credential_state_in_evidence':False", text)
        self.assertIn("'github_provider_credentials_required':False", text)
        self.assertIn("'provider_credentials_must_not_enter_github':True", text)
        self.assertIn("'qualification_mode':'periodic-non-blocking'", text)
        self.assertIn("'repository_closure_blocking':False", text)
        self.assertIn("'product_release_blocking':False", text)
        self.assertIn("'codex':'scripts/runtime-r2-local.sh'", text)
        self.assertIn("'claude-code':'control/scripts/runtime-r2-local.sh'", text)
        self.assertNotIn("runtime-r2-provider-execution.yml", text)

    def test_local_intake_is_exact_and_provider_credential_free(self) -> None:
        text = INTAKE.read_text(encoding="utf-8")
        self.assertIn("digital-worker-runtime-r2-local-intake/v1", text)
        self.assertIn("runtime-owned-local-terminal", text)
        self.assertIn("github_provider_credential_used", text)
        self.assertIn("runtime_home_mode", text)
        self.assertIn("shared-user-home", text)
        self.assertIn("credential_state_in_evidence", text)
        self.assertIn("native-to-portable projection", text)
        self.assertIn("result-tree.tar.gz", text)
        self.assertIn("worktree-result:sha256:", text)
        self.assertIn("sys.executable", text)
        self.assertNotIn('gh", "attestation", "verify', text)
        self.assertNotIn("--signer-workflow", text)
        self.assertNotIn("provider_workflow_runs", text)

    def test_local_verifier_is_final_periodic_qualification_authority(self) -> None:
        text = LOCAL_VERIFY.read_text(encoding="utf-8")
        self.assertIn("digital-worker-runtime-r2-domain-verification/v1", text)
        self.assertIn("local-evidence-integrity", text)
        self.assertIn("replay-complete-result-tree", text)
        self.assertIn("provider_execution_evidence", text)
        self.assertIn("verification_execution_venue", text)
        self.assertIn("local-terminal", text)
        self.assertIn("shared-user-home", text)
        self.assertIn("credential_state_in_evidence", text)
        self.assertIn('"qualification_status": "qualified"', text)
        self.assertIn('"r2_qualified": True', text)
        self.assertIn('"repository_closure_blocking": False', text)
        self.assertIn('"product_release_blocking": False', text)
        self.assertNotIn('"independent_review_status": "pending"', text)
        self.assertNotIn("provider_workflow_runs", text)

    def test_policy_keeps_r2_claim_specific_and_periodic(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertEqual(policy["cadence"]["period"], "quarterly")
        self.assertFalse(policy["scope"]["repository_closure_blocking"])
        self.assertFalse(policy["scope"]["product_release_blocking"])
        self.assertTrue(policy["scope"]["runtime_binding_r1_required"])
        self.assertTrue(policy["scope"]["runtime_portability_claim_requires_r2"])
        self.assertFalse(policy["campaign"]["independent_human_review_required"])
        self.assertFalse(policy["campaign"]["root_certifier_required"])

    def test_all_remaining_workflow_actions_are_full_sha_pinned(self) -> None:
        for path in (FREEZE, CONTRACT):
            text = path.read_text(encoding="utf-8")
            uses = re.findall(r"^\s*uses:\s*([^\s#]+)", text, re.MULTILINE)
            self.assertTrue(uses, path)
            for item in uses:
                self.assertRegex(item, r"^[^@]+@[0-9a-f]{40}$", item)


if __name__ == "__main__":
    unittest.main()
