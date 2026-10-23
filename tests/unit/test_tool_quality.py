"""Behavioral regressions for tool-quality-hardening; only temporary evidence."""
from __future__ import annotations

import contextlib
import io
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests/unit"))
import bounded_subprocess as bounded
import embedded_pilot as pilot
import embedded_pilot_source_probe as probe
import embedded_pilot_scaffold as scaffold
import pilot_support as support
import test_review_hardening as fixtures


def invoke(*args, python_args=()):
    return subprocess.run([sys.executable, *python_args, str(ROOT / "scripts/edge_pilot.py"), *map(str, args)],
                          cwd="/tmp", capture_output=True, text=True, timeout=30)


def init_args(root, run_id="中文-Run"):
    return pilot.build_parser().parse_args([
        "init", "--run-id", run_id, "--track", "feature", "--source-type", "synthetic",
        "--task-type", "feature_development", "--workflow-mode", "short_chain",
        "--human-owner", "fixture-owner", "--task-brief", str(ROOT / "tests/fixtures/task-brief.valid.json"),
        "--output-root", str(root)])


def contents(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


class RunTransactionTests(unittest.TestCase):
    def test_run_id_rejects_escape_and_controls_before_creating_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runs"
            for run_id in ["", ".", "..", "../escaped", "/escaped", "a/b", "a\\b", ".git", "x\0y", "x\ny", "x\x7fy", "x\x85y"]:
                with self.subTest(run_id=run_id), self.assertRaises(support.PilotError):
                    pilot.cmd_init(init_args(root, run_id))
            self.assertFalse(root.exists())

    def test_unicode_id_and_atomic_init_validation(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            root = Path(tmp)
            pilot.cmd_init(init_args(root))
            self.assertEqual(pilot.load_run(root / "中文-Run")["run_id"], "中文-Run")
            args = init_args(root, "invalid")
            args.human_owner = ""
            with self.assertRaises(Exception):
                pilot.cmd_init(args)
            self.assertFalse((root / "invalid").exists())

    def test_status_validation_failure_preserves_all_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            value = fixtures.load(root / "verification_report.json")
            value["run_id"] = "OTHER"
            fixtures.write(root / "verification_report.json", value)
            before = contents(root)
            with self.assertRaisesRegex(ValueError, "run_id mismatch"):
                pilot.cmd_status(pilot.build_parser().parse_args(["status", str(root), "cancelled"]))
            self.assertEqual(contents(root), before)
            self.assertEqual(pilot.load_run(root)["status"], "running")

    def test_concurrent_uncooperative_update_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            complete = pilot._complete_candidate
            def raced(args, staged):
                complete(args, staged)
                run = pilot.load_run(root)
                run["notes"].append("concurrent update")
                pilot.write_json(pilot.run_path(root), run)
            with patch.object(pilot, "_complete_candidate", raced), self.assertRaisesRegex(ValueError, "changed"):
                pilot.cmd_complete(pilot.build_parser().parse_args(["complete", str(root)]))
            self.assertIn("concurrent update", pilot.load_run(root)["notes"])
            self.assertEqual(pilot.load_run(root)["status"], "running")

    def test_cross_process_writer_lock_rejects_second_writer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            before = contents(root)
            with pilot.writer_lock(root):
                result = invoke("status", root, "blocked", "--json")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["error_code"], "RUN_LOCKED")
            self.assertEqual(contents(root), before)

    def test_marker_failure_keeps_old_refs_and_recover_never_deletes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            before = contents(root)
            args = pilot.build_parser().parse_args(["complete", str(root)])
            with patch.object(pilot, "publish_marker", side_effect=OSError("fault before marker")), self.assertRaises(OSError):
                pilot.cmd_complete(args)
            for ref, raw in before.items():
                self.assertEqual((root / ref).read_bytes(), raw)
            self.assertEqual(pilot.validate_run_dir(root)["status"], "running")
            snapshot = contents(root)
            result = invoke("recover", root, "--dry-run", "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["unreferenced_generations"])
            self.assertEqual(contents(root), snapshot)
            pilot.cmd_complete(args)
            self.assertEqual(pilot.validate_run_dir(root)["status"], "completed")

    def test_generation_completion_preserves_old_files_and_eligibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            before = contents(root)
            pilot.cmd_complete(pilot.build_parser().parse_args(["complete", str(root)]))
            run = pilot.validate_run_dir(root)
            self.assertTrue(all(ref.startswith("artifacts/") for ref in pilot.referenced_paths(run)))
            for ref, raw in before.items():
                if ref != "pilot-run.json":
                    self.assertEqual((root / ref).read_bytes(), raw)
            self.assertTrue(fixtures.generate(root)["product_readiness_eligible"])
            # Completed evidence remains terminal for every mutation path.
            for command in (["status", str(root), "blocked"], ["bundle", str(root)], ["complete", str(root)]):
                with self.assertRaisesRegex(ValueError, "terminal"):
                    args = pilot.build_parser().parse_args(command)
                    args.func(args)

    def test_post_commit_sync_failure_reports_visible_commit_not_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            sync_directory = pilot.sync_directory
            def fail_only_after_marker(path):
                if path == root:
                    raise OSError("injected sync failure")
                return sync_directory(path)
            with patch.object(pilot, "sync_directory", fail_only_after_marker), self.assertRaises(support.PilotError) as error:
                pilot.cmd_complete(pilot.build_parser().parse_args(["complete", str(root)]))
            self.assertEqual(error.exception.code, "COMMIT_DURABILITY_UNCONFIRMED")
            self.assertEqual(pilot.validate_run_dir(root)["status"], "completed")
            self.assertTrue(fixtures.generate(root)["product_readiness_eligible"])

    def test_old_reader_accepts_new_generation_refs(self):
        baseline = Path(os.environ.get("DW_QUALITY_BASELINE", "/tmp/dw-quality-baseline"))
        if not (baseline / "scripts/embedded_pilot.py").is_file():
            self.skipTest("exact pre-change reader not available in this environment")
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            # This test isolates generation-path compatibility. The new optional
            # Review substitute field needs the new schema; use a real Review
            # fixture here to keep this document within the old schema.
            run = fixtures.load(root / "pilot-run.json")
            verification_path = root / run["verification_report_ref"]
            verification = fixtures.load(verification_path)
            verification.pop("review_substitute", None)
            fixtures.write(verification_path, verification)
            run["review_report_ref"] = "review.json"
            fixtures.write(root / "review.json", fixtures.load(ROOT / "tests/fixtures/review-report.valid.json"))
            fixtures.write(root / "pilot-run.json", run)
            pilot.cmd_complete(pilot.build_parser().parse_args(["complete", str(root)]))
            result = subprocess.run([sys.executable, str(baseline / "scripts/edge_pilot.py"), "validate", str(root)],
                                    cwd="/tmp", capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_schema_cache_never_caches_artifact_pass(self):
        @support.validation_scope
        def scenario(root):
            pilot.validate_run_dir(root)
            ref = pilot.load_run(root)["extra_artifact_refs"]["knowledge_harvest"]
            (root / ref).write_text("tampered", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                pilot.validate_run_dir(root)
        with tempfile.TemporaryDirectory() as tmp:
            scenario(fixtures.fixture_run(Path(tmp) / "run"))

    def test_changed_schema_invalidates_validator_within_scope(self):
        @support.validation_scope
        def scenario(path):
            fixtures.write(path, {"type": "object"})
            support.validate_json({}, path)
            fixtures.write(path, {"type": "object", "required": ["new"]})
            with self.assertRaises(Exception):
                support.validate_json({}, path)
        with tempfile.TemporaryDirectory() as tmp:
            scenario(Path(tmp) / "schema.json")


class SourceAndCliTests(unittest.TestCase):
    def test_schema_error_is_short_and_does_not_dump_instance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            value = pilot.load_run(root)
            value["notes"] = "fixture-private-content" * 1000
            pilot.write_json(pilot.run_path(root), value)
            result = invoke("validate", root, "--json")
            error = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(error["field_path"], ["notes"])
            self.assertLess(len(error["message"]), 300)
            self.assertNotIn("fixture-private-content", result.stdout)
            self.assertNotIn("Failed validating", result.stdout)

    def test_invalid_summary_still_returns_one_json_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run")
            (root / "pilot-run.json").write_text("invalid json")
            result = invoke("summary", tmp, "--json")
            self.assertEqual(result.returncode, 2)
            self.assertTrue(json.loads(result.stdout)["invalid_runs"])

    def test_standalone_json_output_file_also_emits_single_stdout_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            result = subprocess.run([sys.executable, str(ROOT / "scripts/evaluate_edge_foundation_product_readiness.py"),
                                     "--receipt-dir", tmp, "--output", str(output), "--json"], capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), json.loads(output.read_text()))

    def test_source_report_removes_url_credentials_and_query(self):
        with tempfile.TemporaryDirectory() as tmp:
            def git(root, *args, **kwargs):
                if "--show-toplevel" in args: return tmp
                if "--verify" in args: return "a" * 40
                if "config" in args: return "https://fixture-user:fixture-secret@github.com/example/project.git?token=fixture-query#private"
                return ""
            with patch.object(probe, "git", git):
                report = probe.build_report(Path(tmp), [])
            rendered = json.dumps(report)
            for secret in ("fixture-user", "fixture-secret", "fixture-query", "private"):
                self.assertNotIn(secret, rendered)
            self.assertEqual(report["source_identity"]["remote_origin"], "https://github.com/example/project.git")

    def test_uri_ssh_local_and_malformed_forms(self):
        self.assertEqual(support.sanitize_uri("git@github.com:owner/repo.git"), "github.com:owner/repo.git")
        self.assertEqual(support.sanitize_uri("ssh://git@host:2222/a.git?secret=x"), "ssh://host:2222/a.git")
        self.assertEqual(support.sanitize_uri("../local"), "../local")
        self.assertEqual(support.sanitize_uri("https://[bad"), "[invalid-source-uri]")

    def test_missing_run_and_usage_errors_are_single_json(self):
        for args in [("validate", "/definitely/missing/run", "--json"), ("--json", "validate"), ("validate", "--json", "--unknown")]:
            result = invoke(*args)
            self.assertNotEqual(result.returncode, 0)
            error = json.loads(result.stdout)
            self.assertTrue(all(key in error for key in ("error_code", "message", "field_path", "next_actions")))
            self.assertNotIn("Traceback", result.stderr)

    def test_doctor_works_without_site_packages_from_external_cwd(self):
        result = invoke("doctor", "--json", python_args=("-S",))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "BLOCKED")
        self.assertNotIn("Traceback", result.stderr)

    def test_report_blocked_and_required_gate_have_different_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = invoke("product-readiness", tmp, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "BLOCKED")
            result = invoke("product-readiness", tmp, "--require-ready", "--json")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["status"], "BLOCKED")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/evaluate_edge_foundation_product_readiness.py"),
                                     "--receipt-dir", tmp, "--json"], capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "BLOCKED")


class ProcessLifecycleTests(unittest.TestCase):
    def test_exited_leader_with_live_descendant_fails_closed_and_cleans_group(self):
        for leader_exit in (0, 7):
            with self.subTest(leader_exit=leader_exit), tempfile.TemporaryDirectory() as tmp:
                pidfile = Path(tmp) / "child-pid"
                latefile = Path(tmp) / "late-output"
                child = "import sys,time,pathlib,signal; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(1); pathlib.Path(sys.argv[1]).write_text('late'); print('late-output',flush=True); time.sleep(30)"
                parent = "import sys,subprocess,pathlib; p=subprocess.Popen([sys.executable,'-c',sys.argv[3],sys.argv[2]]); pathlib.Path(sys.argv[1]).write_text(str(p.pid)); print('leader-output',flush=True); raise SystemExit(int(sys.argv[4]))"
                with self.assertRaises(bounded.ProcessError) as error:
                    bounded.run([sys.executable, "-c", parent, str(pidfile), str(latefile), child, str(leader_exit)],
                                capture_output=True, text=True, timeout=2, termination_grace=.1)
                self.assertEqual(error.exception.code, "ORPHANED_PROCESS_GROUP")
                pid = int(pidfile.read_text())
                stat = Path(f"/proc/{pid}/stat")
                self.assertTrue(not stat.exists() or stat.read_text().split()[2] == "Z")
                self.assertFalse(latefile.exists())

    def test_waited_descendant_output_is_complete_and_remains_successful(self):
        child = "import time; time.sleep(.05); print('complete-child-output')"
        parent = "import subprocess,sys; p=subprocess.Popen([sys.executable,'-c',sys.argv[1]]); p.wait(); print('complete-parent-output')"
        result = bounded.run([sys.executable, "-c", parent, child], capture_output=True, text=True, timeout=2)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.splitlines(), ["complete-child-output", "complete-parent-output"])

    def test_sigterm_of_cli_reaps_its_separate_process_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            pidfile = Path(tmp) / "pid"
            child = "import os,sys,time,pathlib; pathlib.Path(sys.argv[1]).write_text(str(os.getpid())); time.sleep(30)"
            parent = "import sys; sys.path.insert(0,sys.argv[1]); import bounded_subprocess as b; raise SystemExit(b.cli_entry(lambda:b.run([sys.executable,'-c',sys.argv[3],sys.argv[2]],capture_output=True,termination_grace=.1)))"
            process = subprocess.Popen([sys.executable, "-c", parent, str(ROOT / "scripts"), str(pidfile), child],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                for _ in range(100):
                    if pidfile.exists(): break
                    time.sleep(.02)
                self.assertTrue(pidfile.exists())
                pid = int(pidfile.read_text())
                process.send_signal(signal.SIGTERM)
                process.communicate(timeout=5)
                self.assertEqual(process.returncode, 130)
                self.assertFalse(Path(f"/proc/{pid}").exists())
            finally:
                if process.poll() is None:
                    process.kill()
                    process.communicate(timeout=5)

    def test_machine_output_stdin_stderr_and_failure_contract(self):
        result = bounded.run([sys.executable, "-c", "import sys; print(sys.stdin.read()); print('error', file=sys.stderr)"],
                             input="input", text=True, capture_output=True)
        self.assertEqual(result.stdout.strip(), "input")
        self.assertEqual(result.stderr.strip(), "error")
        with self.assertRaises(bounded.CalledProcessError):
            bounded.run([sys.executable, "-c", "raise SystemExit(3)"], capture_output=True, check=True)

    def test_timeout_terminates_group_including_term_ignoring_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            pidfile = Path(tmp) / "pid"
            child = "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)"
            parent = "import subprocess,sys,time,pathlib; p=subprocess.Popen([sys.executable,'-c',sys.argv[2]]); pathlib.Path(sys.argv[1]).write_text(str(p.pid)); time.sleep(30)"
            started = time.monotonic()
            with self.assertRaises(bounded.ProcessError) as error:
                bounded.run([sys.executable, "-c", parent, str(pidfile), child], timeout=.5, termination_grace=.1, capture_output=True)
            self.assertEqual(error.exception.exit_code, 124)
            self.assertLess(time.monotonic() - started, 3)
            pid = int(pidfile.read_text())
            proc = Path(f"/proc/{pid}/stat")
            for _ in range(50):
                if not proc.exists() or proc.read_text().split()[2] == "Z": break
                time.sleep(.02)
            self.assertTrue(not proc.exists() or proc.read_text().split()[2] == "Z")

    def test_output_limit_fails_instead_of_returning_truncated_success(self):
        with self.assertRaises(bounded.ProcessError) as error:
            bounded.run([sys.executable, "-c", "import sys; sys.stdout.write('x'*2000000)"], capture_output=True,
                        max_output_bytes=65536, termination_grace=.1)
        self.assertEqual(error.exception.code, "OUTPUT_LIMIT")

    def test_timeout_tail_redacts_uri_secrets(self):
        with self.assertRaises(bounded.ProcessError) as error:
            bounded.run([sys.executable, "-c", "import time; print('https://user:secret@host/a?token=private', flush=True); time.sleep(30)"],
                        timeout=.2, capture_output=True, termination_grace=.1)
        self.assertNotIn("secret", str(error.exception))
        self.assertNotIn("private", str(error.exception))

    def test_invalid_budgets_rejected_before_spawn(self):
        for timeout in [0, -1, float("nan"), float("inf")]:
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                bounded.run([sys.executable, "-c", "pass"], timeout=timeout)

    def test_keyboard_interrupt_cleans_child(self):
        processes = []
        original_popen, original_sleep = bounded._sp.Popen, time.sleep
        first = True
        def spawn(*args, **kwargs):
            process = original_popen(*args, **kwargs)
            processes.append(process)
            return process
        def interrupt_once(seconds):
            nonlocal first
            if first:
                first = False
                raise KeyboardInterrupt()
            original_sleep(seconds)
        with patch.object(bounded._sp, "Popen", spawn), patch.object(bounded.time, "sleep", interrupt_once), self.assertRaises(KeyboardInterrupt):
            bounded.run([sys.executable, "-c", "import time; time.sleep(30)"], capture_output=True, termination_grace=.1)
        self.assertTrue(all(process.poll() is not None for process in processes))


class ScaffoldBoundaryTests(unittest.TestCase):
    def scaffold(self, root, force=False):
        from argparse import Namespace
        with contextlib.redirect_stdout(io.StringIO()):
            return scaffold.scaffold_run(Namespace(run_dir=root, force=force))

    def test_working_directory_link_never_writes_outside(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            outside = Path(tmp) / "outside"
            outside.mkdir()
            (root / "working").symlink_to(outside, target_is_directory=True)
            for force in (False, True):
                with self.assertRaisesRegex(ValueError, "symlink"):
                    self.scaffold(root, force)
                self.assertEqual(list(outside.iterdir()), [])

    def test_output_leaf_links_and_dangling_links_rejected_even_with_force(self):
        for exists in (False, True):
            with self.subTest(exists=exists), tempfile.TemporaryDirectory() as tmp:
                root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
                outside = Path(tmp) / "external.json"
                if exists: outside.write_text("retain-user-content")
                (root / "working").mkdir()
                (root / "working/material-manifest.json").symlink_to(outside)
                with self.assertRaisesRegex(ValueError, "symlink"):
                    self.scaffold(root, True)
                self.assertEqual(outside.read_text() if exists else outside.exists(), "retain-user-content" if exists else False)

    def test_root_link_and_escaping_task_ref_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            alias = Path(tmp) / "alias"
            alias.symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                self.scaffold(alias)
            run = pilot.load_run(root)
            run["task_brief_ref"] = "../outside.json"
            fixtures.write(Path(tmp) / "outside.json", {})
            pilot.write_json(pilot.run_path(root), run)
            with self.assertRaisesRegex(ValueError, "escapes"):
                self.scaffold(root)
            self.assertFalse((root / "working").exists())

    def test_all_conflicts_checked_before_first_output(self):
        for directory in (False, True):
            with self.subTest(directory=directory), tempfile.TemporaryDirectory() as tmp:
                root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
                (root / "working").mkdir()
                conflicting = root / "working/acceptance-evidence-matrix.md"
                if directory: conflicting.mkdir()
                else: conflicting.write_text("retain")
                before = contents(root)
                with self.assertRaises(support.PilotError):
                    self.scaffold(root, force=directory)
                self.assertEqual(contents(root), before)
                self.assertFalse((root / "working/material-manifest.json").exists())

    def test_terminal_run_cannot_be_scaffolded_even_with_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run")
            before = contents(root)
            with self.assertRaisesRegex(ValueError, "terminal"):
                self.scaffold(root, True)
            self.assertEqual(contents(root), before)

    def test_scaffold_obeys_cross_process_run_writer_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            before = contents(root)
            with pilot.writer_lock(root):
                result = subprocess.run([sys.executable, str(ROOT / "scripts/edge_pilot_scaffold.py"), str(root)],
                                        capture_output=True, text=True, cwd="/tmp", timeout=30)
            self.assertEqual(result.returncode, 2)
            self.assertIn("RUN_LOCKED", result.stderr)
            self.assertEqual(contents(root), before)

    def test_force_breaks_hardlinks_and_preserves_existing_material(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            source = pilot.safe_ref(root, pilot.load_run(root)["extra_artifact_refs"]["material_manifest"])
            before = source.read_bytes()
            working = root / "working"
            working.mkdir()
            os.link(source, working / "material-manifest.json")
            (working / "user-notes.txt").write_text("retain")
            marker = pilot.run_path(root).read_bytes()
            self.scaffold(root, True)
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(pilot.run_path(root).read_bytes(), marker)
            self.assertEqual((working / "user-notes.txt").read_text(), "retain")
            self.assertEqual(fixtures.load(working / "material-manifest.json")["readiness"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
