#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "phase3_review_package",
    ROOT / "scripts" / "generate_edge_foundation_phase3_review_package.py",
)
assert SPEC and SPEC.loader
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


def readiness(status: str) -> dict:
    eligible = status == "ELIGIBLE_FOR_REVIEW"
    run_ids = ["REAL-DEBUG-001", "REAL-FEATURE-001", "REAL-REVIEW-001"] if eligible else []
    count = 1 if eligible else 0
    return {
        "schema_version": 1,
        "status": status,
        "eligible_for_phase3_review": eligible,
        "canonical_routing_switched": False,
        "promotion_gate_source": "expert-groups/embedded-system/pilot/pilot-plan.yaml",
        "required_tracks": ["debug", "feature", "review_release"],
        "track_coverage": {
            "debug": {"minimum_required": 1, "eligible_count": count, "run_ids": run_ids[0:1]},
            "feature": {"minimum_required": 1, "eligible_count": count, "run_ids": run_ids[1:2]},
            "review_release": {"minimum_required": 1, "eligible_count": count, "run_ids": run_ids[2:3]},
        },
        "receipts_scanned": 3 if eligible else 0,
        "eligible_real_receipts": 3 if eligible else 0,
        "evidence_run_ids": run_ids,
        "blockers": [] if eligible else ["debug:0/1", "feature:0/1", "review_release:0/1", "eligible-real-receipts:0/3"],
    }


class Phase3ReviewPackageTests(unittest.TestCase):
    def test_blocked_readiness_cannot_generate_review_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "readiness.json"
            path.write_text(json.dumps(readiness("BLOCKED")), encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "not ELIGIBLE_FOR_REVIEW"):
                review.build_package(path)

    def test_eligible_readiness_generates_non_applying_review_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "readiness.json"
            path.write_text(json.dumps(readiness("ELIGIBLE_FOR_REVIEW")), encoding="utf-8")
            package = review.build_package(path)
            self.assertEqual(package["status"], "READY_FOR_INDEPENDENT_REVIEW")
            self.assertFalse(package["canonical_routing_currently_switched"])
            self.assertFalse(package["automatic_apply_allowed"])
            self.assertEqual(len(package["evidence_run_ids"]), 3)
            self.assertIn("preserve-legacy-1plus7-as-compatibility-surface", package["proposed_changes"])
            self.assertIn("do-not-deprecate-legacy-identities-in-phase-3", package["explicit_non_goals"])
            self.assertIn("restore-legacy-embedded-1plus7-as-canonical-routing-authority", package["rollback_plan"])


if __name__ == "__main__":
    unittest.main()
