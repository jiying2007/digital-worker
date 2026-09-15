from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
EDGE = ROOT / "domains" / "edge-foundation"
LEGACY_IDS = {
    "embedded-system-team-lead", "embedded-architecture-expert", "linux-bsp-expert", "mcu-rtos-expert",
    "driver-component-expert", "debug-reliability-expert", "verification-expert", "embedded-review-governor",
}


class EdgeTargetRuntimeTests(unittest.TestCase):
    def test_target_runtime_has_no_legacy_identity(self):
        for rel in ["runtime/task-modes.yaml", "runtime/workflow.yaml", "routing.yaml"]:
            text = (EDGE / rel).read_text(encoding="utf-8")
            for legacy in LEGACY_IDS:
                self.assertNotIn(legacy, text, f"{legacy} leaked into {rel}")

    def test_canonical_routing_covers_all_task_types(self):
        runtime = yaml.safe_load((EDGE / "runtime/task-modes.yaml").read_text(encoding="utf-8"))["routing"]
        routing = yaml.safe_load((EDGE / "routing.yaml").read_text(encoding="utf-8"))
        self.assertTrue(routing["canonical_routing"])
        self.assertEqual(set(runtime), set(routing["routing"]))
        self.assertEqual(len(runtime), 14)

    def test_target_pilot_schemas_skills_and_legacy_absence(self):
        self.assertTrue((EDGE / "pilot/pilot-plan.yaml").is_file())
        self.assertTrue((EDGE / "pilot/evidence/FEATURE-PCR02-OTA-001/task-brief.json").is_file())
        for name in ["material-manifest.schema.json", "verification-report.schema.json", "engineering-task-package.schema.json"]:
            self.assertTrue((EDGE / "schemas" / name).is_file(), name)
        self.assertEqual(len(list((EDGE / "skills").glob("*/SKILL.md"))), 23)
        self.assertFalse((ROOT / "expert-groups/embedded-system").exists())
        self.assertFalse((EDGE / "compatibility").exists())
        self.assertFalse((EDGE / "routing-shadow.yaml").exists())

    def test_target_cli_can_initialize_scaffold_and_generate_receipt_without_legacy_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run([
                sys.executable, str(ROOT / "scripts/edge_pilot.py"), "init",
                "--run-id", "EDGE-TARGET-CI-001", "--track", "feature", "--source-type", "synthetic",
                "--task-type", "feature_development", "--workflow-mode", "short_chain", "--human-owner", "ci",
                "--task-brief", str(ROOT / "tests/fixtures/task-brief.valid.json"), "--repo-root", "firmware/main",
                "--base-commit", "0123456789abcdef0123456789abcdef01234567", "--output-root", str(root),
            ], cwd=ROOT, check=True)
            run_dir = root / "EDGE-TARGET-CI-001"
            subprocess.run([sys.executable, str(ROOT / "scripts/edge_pilot_scaffold.py"), str(run_dir)], cwd=ROOT, check=True)
            run = json.loads((run_dir / "pilot-run.json").read_text(encoding="utf-8"))
            self.assertEqual(run["status"], "planned")
            self.assertTrue((run_dir / "working/material-manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
