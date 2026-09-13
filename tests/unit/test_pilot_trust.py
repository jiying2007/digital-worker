#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("embedded_pilot", ROOT / "scripts" / "embedded_pilot.py")
assert SPEC and SPEC.loader
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


class PilotTrustTests(unittest.TestCase):
    def test_real_commit_requires_full_sha(self):
        self.assertTrue(pilot.exact_git_sha("0123456789abcdef0123456789abcdef01234567"))
        self.assertFalse(pilot.exact_git_sha("0123456"))
        self.assertFalse(pilot.exact_git_sha("main"))

    def test_terminal_run_cannot_be_mutated(self):
        with self.assertRaisesRegex(ValueError, "terminal"):
            pilot.assert_mutable({"status": "completed"}, "rebundling")
        with self.assertRaisesRegex(ValueError, "terminal"):
            pilot.assert_mutable({"status": "cancelled"}, "restart")
        pilot.assert_mutable({"status": "blocked"}, "resume")

    def test_bundle_integrity_detects_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = root / "task-brief.json"
            artifact.write_text("before\n", encoding="utf-8")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            run = {
                "pilot_track": "feature",
                "task_brief_ref": "task-brief.json",
                "engineering_task_package_ref": None,
                "delivery_receipt_ref": None,
                "verification_report_ref": None,
                "review_report_ref": None,
                "pilot_result_ref": None,
                "extra_artifact_refs": {},
            }
            original = pilot.required_artifacts
            pilot.required_artifacts = lambda _run: (["task_brief_ref"], [])
            try:
                bundle = {"artifacts": [{"kind": "task-brief", "path": "task-brief.json", "sha256": digest, "required": True}]}
                pilot.validate_bundle_integrity(root, run, bundle)
                artifact.write_text("after\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                    pilot.validate_bundle_integrity(root, run, bundle)
            finally:
                pilot.required_artifacts = original


if __name__ == "__main__":
    unittest.main()
