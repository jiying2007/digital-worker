#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "switch_candidate",
    ROOT / "scripts" / "validate_edge_foundation_canonical_switch_candidate.py",
)
assert SPEC and SPEC.loader
candidate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(candidate)


def plan() -> dict:
    return {
        "schema_version": 1,
        "status": "DRY_RUN_ONLY",
        "review_package_sha256": "a" * 64,
        "review_package_status": "READY_FOR_INDEPENDENT_REVIEW",
        "current_canonical_authority": "legacy-embedded-1plus7",
        "proposed_canonical_authority": "edge-foundation",
        "canonical_routing_switched": False,
        "apply_allowed": False,
        "allowed_change_classes": ["canonical-routing-authority", "routing-selector-entrypoint"],
        "forbidden_change_classes": [
            "legacy-identity-removal",
            "legacy-identity-deprecation",
            "compatibility-mapping-rewrite",
            "skill-owner-rewrite",
            "pilot-threshold-change",
            "action-authority-expansion",
            "verification-independence-change",
            "review-independence-change",
            "provider-binding-change",
            "source-of-truth-authority-change",
            "production-ready-claim",
        ],
        "required_preserved_invariants": [
            "no-verification-self-approval-regression",
            "no-review-independence-regression",
            "no-provider-binding-regression",
            "source-of-truth-stays-at-source",
        ],
        "required_followup_phases": ["phase-4-deprecation", "phase-5-removal"],
        "rollback_authority": "legacy-embedded-1plus7",
        "evidence_run_ids": ["REAL-DEBUG-001", "REAL-FEATURE-001", "REAL-REVIEW-001"],
    }


class CanonicalSwitchCandidateTests(unittest.TestCase):
    def _files(self, root: Path, changed: list[str], include_compat: bool = False):
        plan_path = root / "plan.json"
        plan_path.write_text(json.dumps(plan()), encoding="utf-8")
        digest = hashlib.sha256(plan_path.read_bytes()).hexdigest()
        changes = [
            {"path": "domains/edge-foundation/domain.yaml", "change_class": "canonical-routing-authority"},
            {"path": "domains/edge-foundation/canonical-routing.yaml", "change_class": "routing-selector-entrypoint"},
        ]
        if include_compat:
            changes.append({
                "path": "domains/edge-foundation/compatibility/embedded-1plus7-mapping.yaml",
                "change_class": "routing-selector-entrypoint",
            })
        manifest = {
            "schema_version": 1,
            "status": "CANDIDATE_ONLY",
            "switch_plan_sha256": digest,
            "candidate_base_sha": "1" * 40,
            "candidate_head_sha": "2" * 40,
            "canonical_routing_target": "edge-foundation",
            "legacy_compatibility_preserved": True,
            "phase4_deprecation_included": False,
            "phase5_removal_included": False,
            "action_authority_changed": False,
            "verification_independence_changed": False,
            "review_independence_changed": False,
            "provider_binding_changed": False,
            "changes": changes,
        }
        manifest_path = root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        changed_path = root / "changed.txt"
        changed_path.write_text("\n".join(changed) + "\n", encoding="utf-8")
        return manifest_path, plan_path, changed_path

    def test_exact_declared_diff_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            expected = [
                "domains/edge-foundation/domain.yaml",
                "domains/edge-foundation/canonical-routing.yaml",
            ]
            manifest, switch_plan, changed = self._files(root, expected)
            result = candidate.validate_candidate(manifest, switch_plan, changed)
            self.assertEqual(result["status"], "PASS")
            self.assertTrue(result["legacy_compatibility_preserved"])

    def test_compatibility_mapping_change_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            changed_files = [
                "domains/edge-foundation/domain.yaml",
                "domains/edge-foundation/canonical-routing.yaml",
                "domains/edge-foundation/compatibility/embedded-1plus7-mapping.yaml",
            ]
            manifest, switch_plan, changed = self._files(root, changed_files, include_compat=True)
            with self.assertRaises(Exception):
                candidate.validate_candidate(manifest, switch_plan, changed)

    def test_extra_legacy_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            changed_files = [
                "domains/edge-foundation/domain.yaml",
                "domains/edge-foundation/canonical-routing.yaml",
                "expert-groups/embedded-system/expert-group.yaml",
            ]
            manifest, switch_plan, changed = self._files(root, changed_files)
            with self.assertRaisesRegex(AssertionError, "changed files do not match manifest"):
                candidate.validate_candidate(manifest, switch_plan, changed)


if __name__ == "__main__":
    unittest.main()
