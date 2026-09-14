#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("embedded_pilot_edge_cli", ROOT / "scripts" / "embedded_pilot.py")
assert SPEC and SPEC.loader
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


class EdgePilotCliTests(unittest.TestCase):
    def test_edge_shadow_wraps_existing_evaluator_without_mutating_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp).resolve()
            (run_dir / "pilot-run.json").write_text("{}\n", encoding="utf-8")
            result_path = run_dir / "pilot-result.json"
            result_path.write_text("{}\n", encoding="utf-8")
            output = run_dir / "edge-foundation-shadow-receipt.json"
            run = {"pilot_result_ref": "pilot-result.json"}
            completed = SimpleNamespace(returncode=0)

            with (
                mock.patch.object(pilot, "validate_run_dir", return_value=run) as validate_run,
                mock.patch.object(pilot, "safe_ref", return_value=result_path),
                mock.patch.object(pilot.subprocess, "run", return_value=completed) as run_process,
            ):
                pilot.cmd_edge_shadow(
                    SimpleNamespace(
                        run_dir=run_dir,
                        output=output,
                        cross_domain_trigger=None,
                    )
                )

            validate_run.assert_called_once_with(run_dir)
            command = run_process.call_args.args[0]
            self.assertEqual(command[0], pilot.sys.executable)
            self.assertEqual(Path(command[1]), pilot.EDGE_SHADOW_EVALUATOR)
            self.assertIn(str(run_dir / "pilot-run.json"), command)
            self.assertIn("--pilot-result", command)
            self.assertIn(str(result_path), command)
            self.assertIn("--output", command)
            self.assertIn(str(output), command)

    def test_phase3_readiness_propagates_fail_closed_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            runs_root = Path(tmp).resolve()
            completed = SimpleNamespace(returncode=2)
            with mock.patch.object(pilot.subprocess, "run", return_value=completed) as run_process:
                with self.assertRaises(SystemExit) as ctx:
                    pilot.cmd_phase3_readiness(
                        SimpleNamespace(
                            runs_root=runs_root,
                            output=None,
                            require_ready=True,
                        )
                    )
            self.assertEqual(ctx.exception.code, 2)
            command = run_process.call_args.args[0]
            self.assertEqual(Path(command[1]), pilot.EDGE_READINESS_EVALUATOR)
            self.assertIn("--receipt-dir", command)
            self.assertIn(str(runs_root), command)
            self.assertIn("--require-ready", command)


if __name__ == "__main__":
    unittest.main()
