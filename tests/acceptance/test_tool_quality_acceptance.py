"""Reproducible local acceptance and sanitized evidence generation.

Run after source changes stabilize. Independent human review is never inferred
from this author-run suite. Set DW_QUALITY_BASELINE to the pre-change snapshot.
"""
from __future__ import annotations

import hashlib
import contextlib
import io
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
import unittest
import unittest.mock
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = Path(os.environ.get("DW_QUALITY_REPORTS", str(ROOT / "reports/validation/tool-quality-hardening")))
BASELINE = Path(os.environ.get("DW_QUALITY_BASELINE", "/tmp/dw-quality-baseline"))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests/unit"))
import embedded_pilot as pilot
import test_review_hardening as fixtures
import test_tool_quality as quality


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_snapshot(root):
    entries = {p.relative_to(root).as_posix(): digest(p)
               for directory in ("scripts", "schemas", "domains", "tests", ".github/workflows")
               for p in (root / directory).rglob("*")
               if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}
    if (root / "requirements-dev.txt").is_file():
        entries["requirements-dev.txt"] = digest(root / "requirements-dev.txt")
    return {"sha256": hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest(), "files": entries}


def record(name, payload):
    REPORTS.mkdir(parents=True, exist_ok=True)
    doc = {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
           "verifier": "author-run-local-acceptance", "python": platform.python_version(),
           "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "input_snapshot": source_snapshot(ROOT), "result": payload}
    (REPORTS / name).write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def command(args, *, timeout=180):
    started = time.monotonic()
    completed = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return completed, {"command": list(map(str, args)), "exit_code": completed.returncode,
                       "elapsed_seconds": time.monotonic() - started,
                       "stdout_sha256": hashlib.sha256(completed.stdout.encode()).hexdigest(),
                       "stderr_sha256": hashlib.sha256(completed.stderr.encode()).hexdigest(),
                       "result_tail": (completed.stderr or completed.stdout)[-2400:]}


class ToolQualityAcceptance(unittest.TestCase):
    def test_00_baseline_and_plan_readback(self):
        self.assertTrue((BASELINE / "scripts/embedded_pilot.py").is_file(), "pre-change snapshot required")
        plan = ROOT / "docs/changes/tool-quality-hardening/requirements.md"
        state = ROOT / "docs/changes/tool-quality-hardening/state.md"
        self.assertIn("G0–G5", plan.read_text())
        self.assertIn("task-package v2", plan.read_text())
        record("G0-baseline.json", {"baseline_snapshot": source_snapshot(BASELINE),
                                    "plan_sha256": digest(plan), "state_readback": state.is_file(),
                                    "prior_suite_count": 218, "existing_dirty_policy": "authorized files extended; no reset, checkout or clean"})

    def test_10_new_behavioral_regressions(self):
        suite = unittest.defaultTestLoader.loadTestsFromModule(quality)
        result = unittest.TestResult()
        suite.run(result)
        failures = [(str(test), text[-1600:]) for test, text in result.failures + result.errors]
        payload = {"tests_run": result.testsRun, "failures": failures,
                   "skipped": [(str(test), reason) for test, reason in result.skipped], "passed": result.wasSuccessful()}
        for filename in ("G1-lifecycle.json", "G2-cli-compatibility.json", "G3-process-lifecycle.json"):
            record(filename, payload)
        self.assertTrue(result.wasSuccessful(), failures)

    def test_20_performance(self):
        measurements, commands = {}, []
        for label, root in (("before", BASELINE), ("after", ROOT)):
            completed, evidence = command([sys.executable, str(ROOT / "tests/acceptance/benchmark_workload.py"), str(root)], timeout=180)
            commands.append(evidence)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            measurements[label] = json.loads(completed.stdout)
        comparisons = {}
        for operation, before in measurements["before"]["operations"].items():
            after = measurements["after"]["operations"][operation]
            comparisons[operation] = {"median_reduction": 1 - after["median_ms"] / before["median_ms"],
                                      "p95_ratio": after["p95_ms"] / before["p95_ms"]}
        passed = all(value["median_reduction"] >= .30 and value["p95_ratio"] <= 1.10 for value in comparisons.values())
        record("G3-benchmark.json", {"measurements": measurements, "comparisons": comparisons,
                                     "commands": commands, "passed": passed, "production_sla": False})
        self.assertTrue(passed, comparisons)

    def test_30_regression_and_static_checks(self):
        checks = []
        completed, evidence = command([sys.executable, "-m", "unittest", "discover", "-s", "tests/unit", "-p", "test_*.py"], timeout=180)
        checks.append(evidence)
        # Preserve all commands' outcomes in the report even when a check fails.
        validators = ["validate_repo_layout", "validate_skills_overview", "validate_provider_neutral_architecture",
                      "validate_edge_foundation_architecture", "validate_edge_foundation_target_assets",
                      "validate_skill_evaluation_plan", "validate_core_reference", "validate_zero_live_legacy_refs",
                      "validate_branch_gc", "validate_contract_catalog", "validate_embedded_closed_loop",
                      "validate_cross_repo_integration", "validate_pilot_operations", "validate_terminal_consistency"]
        for validator in validators:
            _, evidence = command([sys.executable, f"scripts/{validator}.py"])
            checks.append(evidence)
        _, evidence = command([sys.executable, "scripts/generate_edge_foundation_review_snapshot.py",
                               "--check-json", "reports/review/edge-foundation-review-snapshot.json",
                               "--check-markdown", "嵌入式系统专家团-核心参考/00-评审导览/03 当前机器状态快照.md"])
        checks.append(evidence)
        _, evidence = command(["git", "diff", "--check"])
        checks.append(evidence)
        for path in sorted((ROOT / "scripts").glob("*.py")):
            compile(path.read_bytes(), str(path), "exec")
        for path in (ROOT / ".github/workflows").glob("*.yml"):
            pilot.load_yaml(path)
        failed = [item for item in checks if item["exit_code"] != 0]
        record("G4-regression.json", {"checks": checks, "failed": failed, "passed": not failed,
                                      "external_network_checks": "not-run; existing mandatory CI checks retained",
                                      "python_3_12": "CI matrix configured; not locally verified"})
        self.assertFalse(failed, failed)

    def test_40_user_journeys_and_retained_feature(self):
        journeys = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = ROOT / "domains/edge-foundation/pilot/evidence/FEATURE-PCR02-OTA-001"
            def cli(*args, expected=0):
                completed = quality.invoke(*args, "--json")
                self.assertEqual(completed.returncode, expected, completed.stderr or completed.stdout)
                return json.loads(completed.stdout)
            run_id = "FEATURE-PCR02-OTA-001"
            run_dir = root / run_id
            cli("init", "--run-id", run_id, "--track", "feature", "--source-type", "real",
                "--task-type", "component_development", "--workflow-mode", "short_chain", "--human-owner", "embedded-system",
                "--task-brief", source / "task-brief.json", "--repo-root", "jiying2007/ota_download_test",
                "--base-commit", "eeb926bd1fff75d2a5d5abb9f0ede9c8f582cc6d", "--output-root", root)
            cli("complete", run_dir, "--engineering-task-package", source / "engineering-task-package.json",
                "--delivery-receipt", source / "delivery-receipt.json", "--verification-report", source / "verification-report.review-policy-v2.json",
                "--pilot-result", source / "pilot-result.json", "--extra", f"material_manifest={source}/extras/material_manifest.json",
                "--extra", f"acceptance_evidence_matrix={source}/extras/acceptance_evidence_matrix.md",
                "--extra", f"knowledge_harvest={source}/extras/knowledge_harvest.md")
            self.assertEqual(cli("validate", run_dir)["status"], "completed")
            self.assertTrue(cli("pilot-receipt", run_dir)["product_readiness_eligible"])
            self.assertEqual(cli("product-readiness", root, "--require-ready", expected=2)["status"], "BLOCKED")
            journeys.append({"case": "retained-real-feature-replay", "passed": True,
                             "boundary": "retained evidence replay, not a new device execution or product qualification"})
            for track, task_type in (("debug", "defect_debugging"), ("review_release", "code_review")):
                args = quality.init_args(root, track)
                args.track, args.task_type = track, task_type
                modes = pilot.load_yaml(pilot.TASK_MODES)["routing"][task_type]
                args.workflow_mode = modes["allowed_modes"][0]
                with contextlib.redirect_stdout(io.StringIO()):
                    pilot.cmd_init(args)
                location = root / track
                cli("status", location, "blocked", "--note", "missing evidence")
                self.assertFalse(cli("pilot-receipt", location)["product_readiness_eligible"])
                cli("status", location, "running", "--note", "retry after inputs supplied")
                cli("validate", location)
                journeys.append({"case": f"{track}-blocked-and-retry", "passed": True, "qualification": False})
            interrupted = fixtures.fixture_run(root / "interrupted", completed=False)
            with unittest.mock.patch.object(pilot, "publish_marker", side_effect=OSError("injected interruption")), self.assertRaises(OSError):
                pilot.cmd_complete(pilot.build_parser().parse_args(["complete", str(interrupted)]))
            self.assertTrue(cli("recover", interrupted, "--dry-run")["unreferenced_generations"])
            cli("complete", interrupted)
            cli("validate", interrupted)
            journeys.append({"case": "interruption-preview-and-retry", "passed": True})
        record("G5-user-journeys.json", {"automated_journeys": journeys, "passed": True,
                                        "representative_user_acceptance": "pending", "independent_review": "pending"})


if __name__ == "__main__":
    unittest.main()
