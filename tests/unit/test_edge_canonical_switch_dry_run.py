#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "canonical_switch_plan",
    ROOT / "scripts" / "generate_edge_foundation_canonical_switch_plan.py",
)
assert SPEC and SPEC.loader
switch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(switch)


class CanonicalSwitchDryRunTests(unittest.TestCase):
    def test_domain_registers_dry_run_contract_without_switching(self):
        domain = yaml.safe_load((ROOT / "domains" / "edge-foundation" / "domain.yaml").read_text(encoding="utf-8"))
        compat = domain["legacy_compatibility"]
        self.assertEqual(compat["canonical_switch_dry_run_policy"], "canonical-switch-dry-run.yaml")
        self.assertEqual(
            compat["canonical_switch_plan_generator"],
            "../../scripts/generate_edge_foundation_canonical_switch_plan.py",
        )
        self.assertEqual(
            compat["canonical_switch_plan_schema"],
            "../../schemas/edge-foundation-canonical-switch-plan.v1.schema.json",
        )
        self.assertTrue(compat["canonical_switch_dry_run_must_not_apply"])
        self.assertTrue(compat["phase4_deprecation_must_be_separate_from_phase3"])
        self.assertTrue(compat["phase5_removal_must_be_separate_from_phase3"])
        self.assertFalse(compat["canonical_routing_switched"])

    def test_policy_keeps_phase3_narrow_and_non_applying(self):
        policy = yaml.safe_load(
            (ROOT / "domains" / "edge-foundation" / "canonical-switch-dry-run.yaml").read_text(encoding="utf-8")
        )
        self.assertFalse(policy["canonical_routing_switched"])
        self.assertFalse(policy["automatic_apply_allowed"])
        self.assertEqual(
            policy["allowed_change_classes"],
            ["canonical-routing-authority", "migration-phase-status", "routing-selector-entrypoint"],
        )
        self.assertIn("legacy-identity-deprecation", policy["forbidden_change_classes"])
        self.assertIn("legacy-identity-removal", policy["forbidden_change_classes"])
        self.assertIn("action-authority-expansion", policy["forbidden_change_classes"])
        self.assertIn("provider-binding-change", policy["forbidden_change_classes"])
        self.assertIn("production-ready-claim", policy["forbidden_change_classes"])
        self.assertEqual(policy["required_followup_phases"], ["phase-4-deprecation", "phase-5-removal"])
        self.assertEqual(policy["rollback_authority"], "legacy-embedded-1plus7")

    def test_review_package_generates_dry_run_only_plan(self):
        review_package = {
            "schema_version": 1,
            "status": "READY_FOR_INDEPENDENT_REVIEW",
            "readiness_status": "ELIGIBLE_FOR_REVIEW",
            "readiness_sha256": "a" * 64,
            "evidence_run_ids": ["REAL-DEBUG-001", "REAL-FEATURE-001", "REAL-REVIEW-001"],
            "current_routing_authority": "legacy-embedded-1plus7",
            "proposed_routing_authority": "edge-foundation",
            "canonical_routing_currently_switched": False,
            "automatic_apply_allowed": False,
            "migration_invariants": [
                "no-verification-self-approval-regression",
                "no-review-independence-regression",
                "no-provider-binding-regression",
                "source-of-truth-stays-at-source",
            ],
            "proposed_changes": [
                "switch-canonical-routing-authority-to-edge-foundation",
                "preserve-legacy-1plus7-as-compatibility-surface",
            ],
            "explicit_non_goals": ["do-not-deprecate-legacy-identities-in-phase-3"],
            "rollback_plan": ["restore-legacy-embedded-1plus7-as-canonical-routing-authority"],
            "required_review_checks": ["evidence-identity-check"],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "review-package.json"
            path.write_text(json.dumps(review_package), encoding="utf-8")
            plan = switch.build_plan(path)
        self.assertEqual(plan["status"], "DRY_RUN_ONLY")
        self.assertFalse(plan["apply_allowed"])
        self.assertFalse(plan["canonical_routing_switched"])
        self.assertEqual(plan["proposed_canonical_authority"], "edge-foundation")
        self.assertEqual(plan["rollback_authority"], "legacy-embedded-1plus7")
        self.assertIn("legacy-identity-deprecation", plan["forbidden_change_classes"])
        self.assertIn("phase-4-deprecation", plan["required_followup_phases"])
        self.assertEqual(plan["evidence_run_ids"], review_package["evidence_run_ids"])


if __name__ == "__main__":
    unittest.main()
