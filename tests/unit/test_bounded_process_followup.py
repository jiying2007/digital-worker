"""Cancellation recovery and actual Provider surface budget regressions."""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import bounded_subprocess as bounded
import embedded_knowledge as knowledge


def wait_for(path, process, timeout=5):
    deadline = time.monotonic() + timeout
    while not path.exists():
        if process.poll() is not None or time.monotonic() >= deadline:
            raise AssertionError("fixture did not reach its expected lifecycle state")
        time.sleep(.01)


class RepeatedCancellationTests(unittest.TestCase):
    def test_repeated_term_and_int_preserve_group_cleanup(self):
        for first, second in ((signal.SIGTERM, signal.SIGTERM),
                              (signal.SIGINT, signal.SIGINT),
                              (signal.SIGTERM, signal.SIGINT)):
            with self.subTest(first=first, second=second), tempfile.TemporaryDirectory() as tmp:
                pidfile, cleaning = Path(tmp) / "pid", Path(tmp) / "cleaning"
                child = (
                    "import os,pathlib,signal,sys,time; "
                    "signal.signal(signal.SIGTERM,lambda *_:pathlib.Path(sys.argv[2]).write_text('TERM')); "
                    "pathlib.Path(sys.argv[1]).write_text(str(os.getpid())); time.sleep(30)"
                )
                parent = (
                    "import sys;sys.path.insert(0,sys.argv[1]);import bounded_subprocess as b;"
                    "raise SystemExit(b.cli_entry(lambda:b.run([sys.executable,'-c',sys.argv[2],"
                    "sys.argv[3],sys.argv[4]],capture_output=True,termination_grace=.3)))"
                )
                process = subprocess.Popen([sys.executable, "-B", "-c", parent, str(ROOT / "scripts"),
                                            child, str(pidfile), str(cleaning)],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                pid = None
                try:
                    wait_for(pidfile, process)
                    pid = int(pidfile.read_text())
                    process.send_signal(first)
                    wait_for(cleaning, process)
                    process.send_signal(second)
                    process.communicate(timeout=5)
                    self.assertEqual(process.returncode, 130)
                    self.assertFalse(Path(f"/proc/{pid}").exists(), "cancelled child was not reaped")
                finally:
                    if pid is not None:
                        try:
                            os.killpg(pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                    if process.poll() is None:
                        process.kill()
                        process.communicate(timeout=5)

    def test_cleanup_restores_the_callers_signal_mask(self):
        before = signal.pthread_sigmask(signal.SIG_BLOCK, set())
        with self.assertRaises(bounded.ProcessError):
            bounded.run([sys.executable, "-c", "import time;time.sleep(30)"],
                        timeout=.03, termination_grace=.03, capture_output=True)
        self.assertEqual(signal.pthread_sigmask(signal.SIG_BLOCK, set()), before)


class ProviderBudgetTests(unittest.TestCase):
    def test_public_provider_surfaces_use_the_provider_budget(self):
        wrappers = ("knowledge-context.sh", "knowledge-evidence-pack.sh",
                    "knowledge-action-check.sh", "knowledge-proposal-route.sh")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tools").mkdir()
            for wrapper in wrappers:
                (root / "tools" / wrapper).write_text("sleep 2\n", encoding="utf-8")
                with self.subTest(wrapper=wrapper), patch.object(knowledge, "hub_root", return_value=root), \
                     patch.dict(os.environ, {"DW_PROVIDER_TIMEOUT_SECONDS": ".03", "DW_HOST_TIMEOUT_SECONDS": "5"}):
                    started = time.monotonic()
                    with self.assertRaises(bounded.ProcessError) as error:
                        knowledge.run_hub(Namespace(), wrapper, [])
                    self.assertEqual(error.exception.code, "TIMEOUT")
                    self.assertLess(time.monotonic() - started, 1)

    def test_invalid_explicit_category_is_rejected_before_spawn(self):
        with patch.object(bounded._sp, "Popen") as spawn, self.assertRaises(ValueError):
            bounded.run([sys.executable, "-c", "pass"], category="unknown")
        spawn.assert_not_called()


if __name__ == "__main__":
    unittest.main()
