from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts" / "embedded_pilot.py"
FIXTURES = ROOT / "tests" / "fixtures"


class PilotReviewOptionalCurrentStageTests(unittest.TestCase):
    def test_feature_can_complete_without_independent_review_when_verification_is_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp)
            run_dir = runs_root / "CI-PILOT-001"

            subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "init",
                    "--run-id",
                    "CI-PILOT-001",
                    "--track",
                    "feature",
                    "--source-type",
                    "synthetic",
                    "--task-type",
                    "feature_development",
                    "--workflow-mode",
                    "short_chain",
                    "--human-owner",
                    "ci",
                    "--task-brief",
                    str(FIXTURES / "task-brief.valid.json"),
                    "--repo-root",
                    "firmware/main",
                    "--base-commit",
                    "0123456789abcdef0123456789abcdef01234567",
                    "--output-root",
                    str(runs_root),
                ],
                cwd=ROOT,
                check=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "complete",
                    str(run_dir),
                    "--engineering-task-package",
                    str(FIXTURES / "engineering-task-package.valid.json"),
                    "--delivery-receipt",
                    str(FIXTURES / "delivery-receipt.valid.json"),
                    "--verification-report",
                    str(FIXTURES / "verification-report.valid.json"),
                    "--pilot-result",
                    str(FIXTURES / "pilot-result.feature.valid.json"),
                    "--extra",
                    f"material_manifest={FIXTURES / 'material-manifest.valid.json'}",
                    "--extra",
                    f"acceptance_evidence_matrix={FIXTURES / 'acceptance-evidence-matrix.valid.md'}",
                    "--extra",
                    f"knowledge_harvest={FIXTURES / 'knowledge-harvest.valid.md'}",
                ],
                cwd=ROOT,
                check=True,
            )

            subprocess.run(
                [sys.executable, str(CLI), "validate", str(run_dir)],
                cwd=ROOT,
                check=True,
            )

            run = json.loads((run_dir / "pilot-run.json").read_text(encoding="utf-8"))
            self.assertEqual(run["status"], "completed")
            self.assertIsNone(run["review_report_ref"])
            self.assertIsNotNone(run["verification_report_ref"])
            self.assertIsNotNone(run["evidence_bundle_ref"])


if __name__ == "__main__":
    unittest.main()
