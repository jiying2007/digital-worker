"""Bounded internal subprocess adapter for noninteractive local tool commands.

Never truncate successful machine output. Limit violations fail closed; only
diagnostic exceptions contain a redacted 64 KiB tail. No shell invocation.
"""
from __future__ import annotations

import math
import os
import signal
import subprocess as _sp
import sys
import tempfile
import threading
import time
from contextlib import ExitStack, contextmanager
from pathlib import Path

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from pilot_support import PilotError, redact_text

PIPE, STDOUT, DEVNULL = _sp.PIPE, _sp.STDOUT, _sp.DEVNULL
CalledProcessError, CompletedProcess = _sp.CalledProcessError, _sp.CompletedProcess
TimeoutExpired = _sp.TimeoutExpired
TAIL_BYTES = 64 * 1024
DEFAULT_OUTPUT_LIMIT = 64 * 1024 * 1024


class ProcessError(PilotError):
    pass


def _positive(value, label):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"{label} must be finite and positive")
    return number


@contextmanager
def _defer_cleanup_signals():
    # The first cancellation must not let subsequent TERM/INT skip group KILL
    # or wait(). Restore the caller's mask only after all resources are reaped.
    previous = None
    if threading.current_thread() is threading.main_thread():
        previous = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGTERM, signal.SIGINT})
    try:
        yield
    finally:
        if previous is not None:
            signal.pthread_sigmask(signal.SIG_SETMASK, previous)


def _terminate(process, grace):
    with _defer_cleanup_signals():
        _terminate_group(process, grace)


def _terminate_group(process, grace):
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    deadline = time.monotonic() + grace
    # Wait for the group, not merely its leader: children may ignore TERM.
    while time.monotonic() < deadline:
        process.poll()
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            break
        time.sleep(0.02)
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()
    # SIGKILL delivery is asynchronous. Reaping only the leader can return
    # while an orphaned descendant is still running on another CPU.
    _wait_group_stopped(process.pid, max(1.0, grace))


def _group_has_live_members(pgid):
    for path in Path("/proc").iterdir():
        if not path.name.isdigit():
            continue
        try:
            fields = (path / "stat").read_text().rsplit(")", 1)[1].split()
        except (FileNotFoundError, ProcessLookupError):
            continue
        if int(fields[2]) == pgid and fields[0] not in {"Z", "X", "x"}:
            return True
    return False


def _wait_group_stopped(pgid, seconds):
    deadline = time.monotonic() + seconds
    while _group_exists(pgid) and _group_has_live_members(pgid):
        if time.monotonic() >= deadline:
            raise ProcessError("CLEANUP_UNCONFIRMED", "Process group still has live members after KILL", exit_code=1)
        time.sleep(0.01)


def _group_exists(pid):
    try:
        os.killpg(pid, 0)
    except ProcessLookupError:
        return False
    return True


def run(args, *, cwd=None, env=None, input=None, text=False, encoding=None,
        errors=None, capture_output=False, stdout=None, stderr=None, check=False,
        timeout=None, max_output_bytes=None, termination_grace=5, category=None):
    if isinstance(args, (str, bytes)):
        raise ValueError("command must be an argument sequence, never a shell string")
    name = Path(str(args[0])).name
    if category is None:
        category = "GIT" if name == "git" else "HOST"
        if name in {"codex", "claude"}:
            category = "RUNTIME"
        elif name in {"gpg", "gpg2"} or any("knowledge-provider" in str(arg) for arg in args):
            category = "PROVIDER"
    defaults = {"GIT": 60, "HOST": 300, "RUNTIME": 3600, "PROVIDER": 120}
    if category not in defaults:
        raise ValueError("unknown subprocess budget category")
    default = defaults[category]
    child_env = os.environ if env is None else env
    seconds = _positive(timeout if timeout is not None else child_env.get(f"DW_{category}_TIMEOUT_SECONDS", default), "timeout")
    limit = _positive(max_output_bytes if max_output_bytes is not None else child_env.get("DW_MAX_OUTPUT_BYTES", DEFAULT_OUTPUT_LIMIT), "output limit")
    grace = _positive(termination_grace, "termination grace")
    if capture_output:
        if stdout is not None or stderr is not None:
            raise ValueError("capture_output cannot be combined with stdout/stderr")
        stdout = stderr = PIPE
    codec = encoding or "utf-8"
    with ExitStack() as stack:
        if threading.current_thread() is threading.main_thread():
            def cancelled(signum, frame):
                raise KeyboardInterrupt()
            previous = signal.signal(signal.SIGTERM, cancelled)
            stack.callback(signal.signal, signal.SIGTERM, previous)
        out = stack.enter_context(tempfile.TemporaryFile())
        err = out if stderr == STDOUT else stack.enter_context(tempfile.TemporaryFile())
        stdin = None
        if input is not None:
            stdin = stack.enter_context(tempfile.TemporaryFile())
            stdin.write(input.encode(codec) if isinstance(input, str) else input)
            stdin.seek(0)
        process = _sp.Popen(args, cwd=cwd, env=env, stdin=stdin,
                            stdout=out, stderr=err, start_new_session=True)
        deadline = time.monotonic() + seconds
        failure = None
        try:
            while True:
                size = os.fstat(out.fileno()).st_size + (os.fstat(err.fileno()).st_size if err is not out else 0)
                if size > limit:
                    failure = ("OUTPUT_LIMIT", "Process output exceeded the configured limit", 1)
                    break
                if process.poll() is not None:
                    break
                if time.monotonic() >= deadline:
                    failure = ("TIMEOUT", f"Process exceeded {seconds:g} seconds", 124)
                    break
                time.sleep(0.02)
            if failure:
                diagnostic = out if os.fstat(out.fileno()).st_size else err
                diagnostic.seek(max(0, os.fstat(diagnostic.fileno()).st_size - TAIL_BYTES))
                tail = redact_text(diagnostic.read(TAIL_BYTES).decode(codec, errors="replace"))
                raise ProcessError(failure[0], failure[1] + "\n" + tail, exit_code=failure[2])
            process.wait()
            if _group_exists(process.pid):
                raise ProcessError("ORPHANED_PROCESS_GROUP",
                                   "Leader exited with a remaining process group; output completeness is unconfirmed",
                                   exit_code=1)
            size = os.fstat(out.fileno()).st_size + (os.fstat(err.fileno()).st_size if err is not out else 0)
            if size > limit:
                raise ProcessError("OUTPUT_LIMIT", "Completed process output exceeded the configured limit", exit_code=1)
        except BaseException:
            # The leader can have exited while its descendants still own output.
            _terminate(process, grace)
            raise
        out.seek(0)
        err.seek(0)
        output = out.read()
        error = b"" if err is out else err.read()
        if text or encoding:
            output, error = output.decode(codec, errors=errors or "strict"), error.decode(codec, errors=errors or "strict")
        for value, destination, default_stream in ((output, stdout, sys.stdout), (error, stderr, sys.stderr)):
            if destination in (PIPE, STDOUT, DEVNULL):
                continue
            stream = default_stream if destination is None else destination
            if value:
                if isinstance(value, bytes):
                    getattr(stream, "buffer", stream).write(value)
                else:
                    stream.write(value)
        result = CompletedProcess(args, process.returncode, output if stdout == PIPE else None,
                                  error if stderr == PIPE else None)
        if check and result.returncode:
            raise CalledProcessError(result.returncode, args, result.stdout, result.stderr)
        return result


def check_output(args, **kwargs):
    return run(args, check=True, stdout=PIPE, **kwargs).stdout


def cli_entry(function):
    try:
        return function()
    except ProcessError as exc:
        print(f"{exc.code}: {exc}", file=sys.stderr)
        return exc.exit_code
    except KeyboardInterrupt:
        return 130
