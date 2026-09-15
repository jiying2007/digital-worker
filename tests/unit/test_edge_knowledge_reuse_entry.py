from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "embedded_knowledge.py"
SPEC = importlib.util.spec_from_file_location("embedded_knowledge_reuse_entry", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class EdgeKnowledgeReuseEntryTests(unittest.TestCase):
    def test_parser_exposes_canonical_reuse_evidence_command(self) -> None:
        args = MODULE.build_parser().parse_args(
            [
                "reuse-evidence",
                "--evidence",
                "reuse.json",
                "--output",
                "receipt.json",
                "--require-eligible",
            ]
        )
        self.assertIs(args.func, MODULE.cmd_reuse_evidence)
        self.assertEqual(args.evidence, "reuse.json")
        self.assertEqual(args.output, "receipt.json")
        self.assertTrue(args.require_eligible)

    def test_missing_evidence_fails_closed_before_evaluator(self) -> None:
        args = MODULE.build_parser().parse_args(
            ["reuse-evidence", "--evidence", "/definitely/missing/reuse.json"]
        )
        with mock.patch.object(MODULE.subprocess, "run") as run:
            with self.assertRaises(SystemExit) as ctx:
                MODULE.cmd_reuse_evidence(args)
        self.assertEqual(ctx.exception.code, 2)
        run.assert_not_called()

    def test_canonical_entry_delegates_to_domain_owned_evaluator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "reuse.json"
            receipt = Path(tmp) / "receipt.json"
            evidence.write_text("{}\n", encoding="utf-8")
            args = MODULE.build_parser().parse_args(
                [
                    "reuse-evidence",
                    "--evidence",
                    str(evidence),
                    "--output",
                    str(receipt),
                    "--require-eligible",
                ]
            )
            completed = subprocess.CompletedProcess(args=[], returncode=0)
            with mock.patch.object(MODULE.subprocess, "run", return_value=completed) as run:
                MODULE.cmd_reuse_evidence(args)
            command = run.call_args.args[0]
            self.assertEqual(command[0], sys.executable)
            self.assertEqual(Path(command[1]), MODULE.E3_REUSE_EVALUATOR)
            self.assertEqual(Path(command[2]), evidence.resolve())
            self.assertIn("--output", command)
            self.assertIn(str(receipt.resolve()), command)
            self.assertIn("--require-eligible", command)
            self.assertEqual(run.call_args.kwargs["cwd"], ROOT)
            self.assertFalse(run.call_args.kwargs["check"])

    def test_nonzero_evaluator_status_propagates_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "reuse.json"
            evidence.write_text("{}\n", encoding="utf-8")
            args = MODULE.build_parser().parse_args(
                ["reuse-evidence", "--evidence", str(evidence), "--require-eligible"]
            )
            completed = subprocess.CompletedProcess(args=[], returncode=2)
            with mock.patch.object(MODULE.subprocess, "run", return_value=completed):
                with self.assertRaises(SystemExit) as ctx:
                    MODULE.cmd_reuse_evidence(args)
            self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
