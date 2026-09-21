from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "config" / "integrations" / "cross-repo-lock.json"
CAPABILITY = ROOT / "config" / "integrations" / "provider-capability-matrix.yaml"
POLICY = ROOT / "manifests" / "runtime-r2-qualification-policy.json"


class RuntimePortabilityConsumerProjectionTests(unittest.TestCase):
    def test_runtime_eval_is_optional_observer_not_r2_decision_authority(self) -> None:
        lock = json.loads(LOCK.read_text(encoding="utf-8"))
        runtime_eval = lock["providers"]["runtime_practice_eval"]

        self.assertEqual(runtime_eval["repository"], "jiying2007/llm_agent")
        self.assertRegex(runtime_eval["commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(runtime_eval["role"], "optional-evolution-observer")
        self.assertEqual(runtime_eval["qualification_authority"], "jiying2007/digital-worker")
        self.assertEqual(
            runtime_eval["qualification_policy"],
            "manifests/runtime-r2-qualification-policy.json",
        )
        self.assertEqual(
            runtime_eval["runtime_portability_evidence_level"],
            "R2-periodic-real-provider-substitution",
        )
        self.assertEqual(
            runtime_eval["runtime_portability_status"],
            "periodic-qualification-policy-active-current-evidence-blocked",
        )

        for retired in (
            "runtime_portability_certifier",
            "runtime_portability_certifier_test",
            "runtime_portability_qualification_manifest",
            "runtime_portability_cli_contract",
        ):
            self.assertNotIn(retired, runtime_eval)

        rules = lock["rules"]
        self.assertTrue(rules["terminal_replaceability_requires_r2_real_provider_substitution"])
        self.assertTrue(rules["r1_binding_conformance_is_not_terminal_replaceability"])
        self.assertFalse(rules["repository_closure_requires_r2"])
        self.assertFalse(rules["product_release_requires_r2"])
        self.assertTrue(rules["runtime_binding_r1_required"])
        self.assertTrue(rules["runtime_portability_qualification_requires_r2"])
        self.assertTrue(rules["r2_is_periodic_qualification"])
        self.assertTrue(rules["r2_failure_does_not_invalidate_repository_health"])

    def test_capability_projection_keeps_r2_claim_gated_without_root_certifier(self) -> None:
        capability = yaml.safe_load(CAPABILITY.read_text(encoding="utf-8"))
        runtime_eval = capability["roles"]["runtime_practice_eval"]
        caps = runtime_eval["capabilities"]

        self.assertEqual(
            runtime_eval["evidence"],
            {
                "identity_ref": "config/integrations/cross-repo-lock.json#/providers/runtime_practice_eval",
                "checkout_verification": "permanent-digital-worker-ci",
            },
        )
        self.assertEqual(runtime_eval["decision"], "optional-evolution-observer")
        self.assertEqual(caps["runtime_binding_comparison"], "periodic-r2-observer")
        self.assertEqual(caps["exact_release_source_set_comparison"], "periodic-r2-observer")
        self.assertEqual(caps["r2_qualification_authority"], "digital-worker-independent-verifier")
        self.assertEqual(caps["r2_real_provider_evidence"], "current-campaign-blocked")
        self.assertEqual(caps["terminal_replaceability"], "claim-gated-by-fresh-r2")
        self.assertEqual(caps["production_runtime"], "unsupported-by-design")
        self.assertNotIn("runtime_portability_certifier", caps)
        self.assertNotIn("runtime_portability_certifier_readiness", caps)

        rules = capability["rules"]
        self.assertFalse(rules["repository_closure_requires_r2"])
        self.assertFalse(rules["product_release_requires_r2"])
        self.assertTrue(rules["runtime_binding_r1_required"])
        self.assertTrue(rules["runtime_portability_qualification_requires_r2"])
        self.assertTrue(rules["r2_is_periodic_qualification"])
        self.assertTrue(rules["r2_failure_does_not_invalidate_repository_health"])

    def test_machine_policy_defines_periodic_claim_freshness_boundary(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertEqual(policy["cadence"]["period"], "quarterly")
        self.assertEqual(policy["cadence"]["recommended_max_age_days"], 120)
        self.assertFalse(policy["scope"]["repository_closure_blocking"])
        self.assertFalse(policy["scope"]["product_release_blocking"])
        self.assertTrue(policy["scope"]["runtime_portability_claim_requires_r2"])
        self.assertTrue(policy["campaign"]["replay_without_provider_state_required"])
        self.assertFalse(policy["campaign"]["independent_human_review_required"])
        self.assertFalse(policy["campaign"]["root_certifier_required"])
        self.assertTrue(policy["governance"]["failed_campaigns_are_valid_evidence"])


if __name__ == "__main__":
    unittest.main()
