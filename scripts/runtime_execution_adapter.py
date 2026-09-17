#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "config/integrations/runtime-execution-profiles.json"


class RuntimeExecutionError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _run_text(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(
        list(args),
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeExecutionError(completed.stderr.strip() or f"command failed: {' '.join(args)}")
    return completed.stdout.strip()


def _git(cwd: Path, *args: str) -> str:
    return _run_text("git", *args, cwd=cwd)


def _profiles() -> dict[str, Any]:
    try:
        value = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeExecutionError(f"invalid runtime execution profile registry: {PROFILE_PATH}") from exc
    if value.get("schema_version") != 1 or value.get("status") != "active":
        raise RuntimeExecutionError("runtime execution profile registry is not active schema v1")
    profiles = value.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise RuntimeExecutionError("runtime execution profile registry has no profiles")
    return value


def _profile(name: str) -> dict[str, Any]:
    registry = _profiles()
    value = registry["profiles"].get(name)
    if not isinstance(value, dict):
        raise RuntimeExecutionError(f"unknown runtime execution profile: {name}")
    return value


def describe(name: str) -> dict[str, Any]:
    profile = _profile(name)
    return {
        "schema": "digital-worker-runtime-execution-profile/v1",
        "profile": name,
        "runtime": profile.get("runtime"),
        "runtime_target": profile.get("runtime_target"),
        "executor": profile.get("executor"),
        "credential_mode": profile.get("credential_mode"),
        "endpoint_mode": profile.get("endpoint_mode"),
        "intended_scope": profile.get("intended_scope", []),
        "source_set_binding": profile.get("source_set_binding"),
        "verification_authority": profile.get("verification_authority"),
    }


def _validate_formal(args: argparse.Namespace, workdir: Path) -> dict[str, Any]:
    if not args.formal:
        return {"formal": False}
    if not args.expected_head:
        raise RuntimeExecutionError("formal execution requires --expected-head")
    if not args.source_set_identity or not args.distribution_identity:
        raise RuntimeExecutionError(
            "formal execution requires --source-set-identity and --distribution-identity"
        )
    actual_head = _git(workdir, "rev-parse", "HEAD")
    if actual_head != args.expected_head:
        raise RuntimeExecutionError(
            f"formal execution HEAD mismatch: expected {args.expected_head}, got {actual_head}"
        )
    dirty = _git(workdir, "status", "--porcelain=v1", "--untracked-files=all")
    if dirty:
        raise RuntimeExecutionError("formal execution requires a clean exact-base worktree")
    return {
        "formal": True,
        "expected_head": args.expected_head,
        "source_set_identity_ref": args.source_set_identity,
        "runtime_distribution_identity_ref": args.distribution_identity,
    }


def run_codex_native(args: argparse.Namespace, profile: dict[str, Any]) -> int:
    if profile.get("runtime") != "codex" or profile.get("executor") != "native-cli":
        raise RuntimeExecutionError(
            "native execution adapter currently supports only the codex-cli-native profile"
        )
    workdir = Path(args.working_directory).expanduser().resolve()
    prompt_path = Path(args.prompt_file).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    receipt_path = Path(args.receipt).expanduser().resolve()
    if not workdir.is_dir():
        raise RuntimeExecutionError(f"working directory does not exist: {workdir}")
    if not prompt_path.is_file():
        raise RuntimeExecutionError(f"prompt file does not exist: {prompt_path}")

    formal = _validate_formal(args, workdir)
    executable = shutil.which(str(profile.get("executable") or "codex"))
    if not executable:
        raise RuntimeExecutionError("codex CLI is not available on PATH")

    env = os.environ.copy()
    if args.codex_home:
        codex_home = Path(args.codex_home).expanduser().resolve()
        if not codex_home.is_dir():
            raise RuntimeExecutionError(f"CODEX_HOME does not exist: {codex_home}")
        env["CODEX_HOME"] = str(codex_home)
    else:
        codex_home = Path(env["CODEX_HOME"]).expanduser().resolve() if env.get("CODEX_HOME") else None

    version = _run_text(executable, "--version", env=env)
    prompt = prompt_path.read_text(encoding="utf-8")
    command = [executable, "exec"]
    if args.model:
        command.extend(["--model", args.model])
    if args.sandbox:
        command.extend(["--sandbox", args.sandbox])
    command.append("-")

    started_at = _now()
    completed = subprocess.run(
        command,
        cwd=workdir,
        env=env,
        input=prompt,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    finished_at = _now()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path = output_path.with_suffix(output_path.suffix + ".stderr.log")
    stderr_path.write_text(completed.stderr, encoding="utf-8")

    descriptor = describe(args.profile)
    receipt = {
        "schema": "digital-worker-runtime-execution-adapter-receipt/v1",
        "status": "completed" if completed.returncode == 0 else "failed",
        "verification_pass_claimed": False,
        "runtime": descriptor["runtime"],
        "runtime_target": descriptor["runtime_target"],
        "runtime_version": version,
        "model": args.model or "runtime-configured",
        "transport": {
            "execution_profile": args.profile,
            "executor": descriptor["executor"],
            "credential_mode": descriptor["credential_mode"],
            "endpoint_mode": descriptor["endpoint_mode"],
            "endpoint_class": args.endpoint_class,
            "gateway_identity": args.gateway_identity,
            "credential_material_recorded": False,
        },
        "worktree": {
            "path": str(workdir),
            "head": _git(workdir, "rev-parse", "HEAD"),
            "dirty_after_execution": bool(
                _git(workdir, "status", "--porcelain=v1", "--untracked-files=all")
            ),
        },
        "formal_identity": formal,
        "execution": {
            "started_at": started_at,
            "finished_at": finished_at,
            "exit_code": completed.returncode,
            "output_sha256": _sha256(output_path),
            "stderr_sha256": _sha256(stderr_path),
        },
        "codex_home": str(codex_home) if codex_home else "runtime-default",
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return completed.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Provider-neutral runtime execution adapter; native Codex CLI is the default development path."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    d = sub.add_parser("describe")
    d.add_argument("--profile", default=None)

    r = sub.add_parser("run")
    r.add_argument("--profile", default=None)
    r.add_argument("--working-directory", required=True)
    r.add_argument("--prompt-file", required=True)
    r.add_argument("--output", required=True)
    r.add_argument("--receipt", required=True)
    r.add_argument("--codex-home")
    r.add_argument("--model")
    r.add_argument("--sandbox", choices=("read-only", "workspace-write", "danger-full-access"))
    r.add_argument("--endpoint-class", default="runtime-managed")
    r.add_argument("--gateway-identity", default="runtime-managed")
    r.add_argument("--formal", action="store_true")
    r.add_argument("--expected-head")
    r.add_argument("--source-set-identity")
    r.add_argument("--distribution-identity")

    args = parser.parse_args(argv)
    registry = _profiles()
    selected = args.profile or registry["default_development_profile"]
    args.profile = selected
    try:
        if args.command == "describe":
            print(json.dumps(describe(selected), ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        return run_codex_native(args, _profile(selected))
    except RuntimeExecutionError as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
