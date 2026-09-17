#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def tree_digest(root: Path) -> str:
    rows = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts):
        rows.append((path.relative_to(root).as_posix(), sha(path)))
    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode("utf-8")).hexdigest()


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def authorize(plan_path: Path, auth_path: Path, prompt_path: Path) -> None:
    raw = plan_path.read_bytes()
    plan = json.loads(raw)
    if plan.get("schema") != "digital-worker-runtime-r2-plan/v1":
        raise ValueError("unexpected frozen plan schema")
    if plan.get("provider_execution_authorized") is not False or plan.get("automatic_execution_enabled") is not False:
        raise ValueError("frozen plan must never authorize provider execution")
    plan_sha = hashlib.sha256(raw).hexdigest()
    auth = {
        "schema": "digital-worker-runtime-r2-provider-authorization/v1",
        "authorized": True,
        "authorization_mode": "explicit-workflow-dispatch",
        "actor": os.environ["GITHUB_ACTOR"],
        "workflow_run_id": os.environ["GITHUB_RUN_ID"],
        "workflow_sha": os.environ["GITHUB_SHA"],
        "frozen_plan_sha256": plan_sha,
        "frozen_inputs_sha256": plan["frozen_inputs_sha256"],
        "scope": "codex-and-claude-same-frozen-task-provider-execution-only",
        "verification_or_release_authority": False,
    }
    write(auth_path, auth)
    prompt_path.write_text(plan["prompt"] + "\n", encoding="utf-8")


def codex_install(home: Path, output: Path, binding_commit: str) -> None:
    managed_path = home / "control/state/managed-files.json"
    managed = load(managed_path)
    source = {
        "runtime_binding_repository": "jiying2007/codex",
        "runtime_binding_commit": binding_commit,
        "profile": managed.get("profile"),
        "source_fingerprint": managed.get("source_fingerprint"),
        "managed_state_sha256": sha(managed_path),
    }
    files = [
        {"path": p.relative_to(home).as_posix(), "sha256": sha(p)}
        for p in sorted(x for x in home.rglob("*") if x.is_file())
    ]
    write(
        output,
        {
            "schema": "codex-r2-runtime-install/v2",
            "source_set_identity_ref": "sha256:" + hashlib.sha256(canonical(source)).hexdigest(),
            "runtime_distribution_identity_ref": "sha256:" + hashlib.sha256(canonical(files)).hexdigest(),
            "profile": managed.get("profile"),
            "files": len(files),
        },
    )


def codex_native(args: argparse.Namespace) -> None:
    plan = load(Path(args.plan))
    auth = load(Path(args.authorization))
    install = load(Path(args.install))
    transport = load(Path(args.transport))
    target = Path(args.target)
    provider_output = Path(args.provider_output)
    controlled = plan["controlled_task"]
    if auth.get("authorized") is not True or auth.get("frozen_inputs_sha256") != plan.get("frozen_inputs_sha256"):
        raise ValueError("provider authorization does not bind the frozen plan")
    version = Path(args.version_file).read_text(encoding="utf-8").strip()
    receipt = {
        "schema_version": 2,
        "work_item_id": controlled["work_item_id"],
        "run_id": controlled["run_id"],
        "execution_source_set_identity": controlled["runtime_source_set_identity_ref"],
        "digital_worker_governance_identity": controlled["digital_worker_governance_identity_ref"].removeprefix("sha256:"),
        "runtime_binding": {
            "repository": "jiying2007/codex",
            "commit": args.binding_commit,
            "target": "codex-cli",
            "runtime_profile": install["profile"],
            "runtime_host": "github-actions:" + os.environ["GITHUB_RUN_ID"],
            "source_set_identity_ref": install["source_set_identity_ref"],
            "runtime_distribution_identity_ref": install["runtime_distribution_identity_ref"],
        },
        "agent_assets": {
            "provider_repository": plan["adk_release_identity"]["repository"],
            "release_version": plan["adk_release_identity"]["version"],
            "release_tag": plan["adk_release_identity"]["tag"],
            "release_commit": plan["adk_release_identity"]["commit"],
            "asset_profile": controlled["adk_asset_profile"],
            "source_set_identity": install["source_set_identity_ref"],
        },
        "runtime": {
            "provider": "openai",
            "cli_version": version,
            "model": args.model,
            "model_provider": "openai",
        },
        "permissions": {
            "sandbox": "workspace-write",
            "approval": "explicit-workflow-dispatch",
            "network": "resolved-by-runtime-transport-adapter",
        },
        "repository": {
            "repository": args.target_repository,
            "base_commit": controlled["exact_base_commit"],
            "result_commit": None,
        },
        "execution": {
            "status": "completed",
            "runtime_local_gates": ["exact-base", "source-set-applied", "transport-resolved", "codex-action-success"],
            "started_at": Path(args.started_at).read_text(encoding="utf-8").strip(),
            "finished_at": Path(args.finished_at).read_text(encoding="utf-8").strip(),
        },
        "evidence_refs": [
            "provider-authorization:sha256:" + sha(Path(args.authorization)),
            "transport-resolution:sha256:" + sha(Path(args.transport)),
            "provider-output:sha256:" + sha(provider_output),
            "worktree-result:sha256:" + tree_digest(target),
        ],
    }
    if transport.get("status") != "ready" or transport.get("runtime") != "codex":
        raise ValueError("Codex transport resolution is not ready")
    write(Path(args.output), receipt)


def claude_native(args: argparse.Namespace) -> None:
    plan = load(Path(args.plan))
    auth = load(Path(args.authorization))
    source = load(Path(args.source_set))
    distribution = load(Path(args.distribution))
    transport = load(Path(args.transport))
    target = Path(args.target)
    execution_file = Path(args.execution_file)
    if auth.get("authorized") is not True or auth.get("frozen_inputs_sha256") != plan.get("frozen_inputs_sha256"):
        raise ValueError("provider authorization does not bind the frozen plan")
    if transport.get("status") != "ready" or transport.get("runtime") != "claude-code":
        raise ValueError("Claude transport resolution is not ready")
    version = Path(args.version_file).read_text(encoding="utf-8").strip()
    result_identity = hashlib.sha256((sha(execution_file) + tree_digest(target)).encode("utf-8")).hexdigest()
    receipt = {
        "schema_version": 2,
        "status": "completed",
        "runtime": "claude-code",
        "frozen_inputs_sha256": plan["frozen_inputs_sha256"],
        "verification_pass_claimed": False,
        "runtime_identity": {
            "runtime_binding_repository": "jiying2007/claude",
            "runtime_binding_commit": args.binding_commit,
            "runtime_target": "claude-code",
            "runtime_profile": "solo-dev",
            "runtime_host": "github-actions:" + os.environ["GITHUB_RUN_ID"],
            "runtime_provider": "anthropic",
            "runtime_version": version,
            "runtime_source_set_identity_ref": source["identity"],
            "runtime_distribution_identity_ref": distribution["identity"],
        },
        "execution": {
            "started_at": Path(args.started_at).read_text(encoding="utf-8").strip(),
            "completed_at": Path(args.finished_at).read_text(encoding="utf-8").strip(),
            "result_identity_ref": "sha256:" + result_identity,
            "source_identity_ref": plan["controlled_task"]["runtime_source_set_identity_ref"],
            "exit_code": 0,
            "summary": "Real Claude Code execution via resolved transport; no Verification PASS claim.",
        },
        "evidence_refs": [
            "provider-authorization:sha256:" + sha(Path(args.authorization)),
            "transport-resolution:sha256:" + sha(Path(args.transport)),
            "claude-execution-file:sha256:" + sha(execution_file),
            "worktree-result:sha256:" + tree_digest(target),
        ],
    }
    write(Path(args.output), receipt)


def collect(plan_path: Path, codex_path: Path, claude_path: Path, output: Path) -> None:
    plan = load(plan_path)
    codex = load(codex_path)
    claude = load(claude_path)
    if {codex.get("runtime"), claude.get("runtime")} != {"codex", "claude-code"}:
        raise ValueError("portable receipt runtime set is not exact")
    if codex.get("status") != "completed" or claude.get("status") != "completed":
        raise ValueError("portable receipts are not completed")
    if codex.get("frozen_inputs_sha256") != plan.get("frozen_inputs_sha256") or claude.get("frozen_inputs_sha256") != plan.get("frozen_inputs_sha256"):
        raise ValueError("portable receipts do not share the same frozen task")
    if codex.get("verification_pass_claimed") is not False or claude.get("verification_pass_claimed") is not False:
        raise ValueError("runtime receipts must not claim Verification PASS")
    write(
        output,
        {
            "schema": "digital-worker-runtime-r2-execution-collection/v1",
            "status": "provider-executions-collected-pending-digital-worker-verification-review",
            "frozen_inputs_sha256": plan["frozen_inputs_sha256"],
            "verification_pass_claimed": False,
            "r2_qualified": False,
            "runtime_receipts": {
                "codex": {"ref": "codex-portable.json", "sha256": sha(codex_path)},
                "claude-code": {"ref": "claude-portable.json", "sha256": sha(claude_path)},
            },
            "next_gate": "shared-digital-worker-verification-and-review-then-root-runtime-portability-certifier",
        },
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assemble non-terminal R2 runtime execution receipts.")
    sub = parser.add_subparsers(dest="command", required=True)

    a = sub.add_parser("authorize")
    a.add_argument("--plan", required=True)
    a.add_argument("--authorization", required=True)
    a.add_argument("--prompt", required=True)

    i = sub.add_parser("codex-install")
    i.add_argument("--home", required=True)
    i.add_argument("--binding-commit", required=True)
    i.add_argument("--output", required=True)

    c = sub.add_parser("codex-native")
    for name in ("plan", "authorization", "install", "transport", "target", "provider-output", "version-file", "started-at", "finished-at", "model", "binding-commit", "target-repository", "output"):
        c.add_argument("--" + name, required=True)

    cl = sub.add_parser("claude-native")
    for name in ("plan", "authorization", "source-set", "distribution", "transport", "target", "execution-file", "version-file", "started-at", "finished-at", "binding-commit", "output"):
        cl.add_argument("--" + name, required=True)

    co = sub.add_parser("collect")
    co.add_argument("--plan", required=True)
    co.add_argument("--codex", required=True)
    co.add_argument("--claude", required=True)
    co.add_argument("--output", required=True)

    args = parser.parse_args(argv)
    if args.command == "authorize":
        authorize(Path(args.plan), Path(args.authorization), Path(args.prompt))
    elif args.command == "codex-install":
        codex_install(Path(args.home), Path(args.output), args.binding_commit)
    elif args.command == "codex-native":
        codex_native(args)
    elif args.command == "claude-native":
        claude_native(args)
    else:
        collect(Path(args.plan), Path(args.codex), Path(args.claude), Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
