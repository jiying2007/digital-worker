#!/usr/bin/env python3
"""Validate Edge Foundation Material Manifest semantics and terminal readiness."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml
from pilot_support import load_json, validate_json, validation_scope

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "domains" / "edge-foundation" / "schemas" / "material-manifest.schema.json"
POLICY = ROOT / "domains" / "edge-foundation" / "runtime" / "material-requirements.yaml"
RUN_SCHEMA = ROOT / "schemas" / "pilot-run.v1.schema.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def required_materials(task_type: str | None = None, task: dict | None = None) -> set[str]:
    required = {"repo", "base_commit", "test_environment"}
    if task_type is not None:
        rules = yaml.safe_load(POLICY.read_text(encoding="utf-8"))["rules"]
        require(task_type in rules, f"unknown material task type: {task_type}")
        required.update(rules[task_type]["required"])
    verification = (task or {}).get("required_verification", {})
    if any(verification.get(layer) == "required" for layer in ("device", "hil", "release")):
        required.add("device_identity")
    return required


def recompute_blockers(manifest: dict, track: str, task_type: str | None = None, task: dict | None = None) -> list[str]:
    items = manifest["items"]
    kinds = [item["kind"] for item in items]
    require(len(kinds) == len(set(kinds)), "material manifest contains duplicate item kinds")
    by_kind = {item["kind"]: item for item in items}
    required = required_materials(task_type, task)
    for kind in sorted(required):
        require(kind in by_kind, f"material manifest missing required item: {kind}")
    blockers = [item["kind"] for item in items
                if (item["required"] or item["kind"] in required) and item["status"] != "available"]
    if track == "debug":
        require("reproduction" in by_kind, "debug material manifest missing reproduction item")
        require("log" in by_kind, "debug material manifest missing log item")
        if not any(by_kind[kind]["status"] == "available" for kind in ("reproduction", "log")):
            blockers.append("reproduction_or_log")
    return sorted(set(blockers))


def repositories_equal(actual: str | None, expected: str) -> bool:
    if actual == expected:
        return True
    # Only the known GitHub HTTPS spelling is an alias for owner/repository.
    url = re.fullmatch(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?/?", actual or "")
    expected_url = re.fullmatch(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?/?", expected)
    left = url.group(1) if url else actual
    right = expected_url.group(1) if expected_url else expected
    return bool((url or expected_url) and isinstance(left, str) and left.casefold() == right.casefold())


def validate_run_identity(manifest: dict, run: dict) -> bool:
    require(manifest["run_id"] == run.get("run_id"), "material run_id identity mismatch")
    repo, commit = run.get("repo_root"), run.get("base_commit")
    repo_known = isinstance(repo, str) and bool(repo.strip())
    commit_known = isinstance(commit, str) and re.fullmatch(r"[0-9a-fA-F]{40}", commit) is not None
    by_kind = {item["kind"]: item for item in manifest["items"]}
    if repo_known and by_kind["repo"]["status"] == "available":
        require(repositories_equal(by_kind["repo"].get("source"), repo), "material repository identity mismatch")
    if commit_known and by_kind["base_commit"]["status"] == "available":
        value = by_kind["base_commit"].get("version")
        require(isinstance(value, str) and value.lower() == commit.lower(), "material base commit identity mismatch")
    return repo_known and commit_known and all(by_kind[kind]["status"] == "available" for kind in ("repo", "base_commit"))


@validation_scope
def validate_manifest(manifest: dict, track: str, require_terminal_ready: bool = False, *, task_type: str | None = None, task: dict | None = None, pilot_run: dict | None = None) -> dict:
    validate_json(manifest, SCHEMA)
    if pilot_run is not None:
        require(pilot_run.get("pilot_track", track) == track, "material track identity mismatch")
        run_type = pilot_run.get("task_type")
        require(task_type is None or run_type is None or task_type == run_type, "material task type identity mismatch")
        task_type = run_type or task_type
        if task is not None and "work_item_id" in task:
            require(task["work_item_id"] == pilot_run.get("work_item_id"), "material Task Brief identity mismatch")
    blockers = recompute_blockers(manifest, track, task_type, task)
    identity_validated = pilot_run is not None and validate_run_identity(manifest, pilot_run)
    required = required_materials(task_type, task)
    for item in manifest["items"]:
        if (item["kind"] in {"device_identity", "test_environment"}
                and (item["required"] or item["kind"] in required)
                and item["status"] == "available"):
            bound = all(isinstance(item.get(key), str) and item[key].strip()
                        for key in ("source", "evidence_ref"))
            if require_terminal_ready:
                require(bound, f"terminal {item['kind']} requires nonempty source and evidence_ref")
            identity_validated = identity_validated and bound
    recorded = sorted(set(manifest.get("missing_critical", [])))
    require(recorded == blockers, f"material manifest missing_critical drift: recorded={recorded} recomputed={blockers}")
    readiness = manifest["readiness"]
    approver = manifest.get("degradation_approved_by")
    if not blockers:
        require(readiness == "READY", f"material manifest without blockers must be READY, got {readiness}")
        require(approver in (None, ""), "READY material manifest must not carry degradation approval")
    elif readiness == "DEGRADED":
        require(isinstance(approver, str) and approver.strip(), "DEGRADED material manifest requires degradation_approved_by")
    else:
        require(readiness == "BLOCKED", f"material manifest with blockers must be BLOCKED or approved DEGRADED, got {readiness}")
        require(approver in (None, ""), "BLOCKED material manifest must not pretend to have degradation approval")
    if require_terminal_ready:
        require(readiness != "BLOCKED", f"terminal Pilot evidence cannot use BLOCKED material manifest: {blockers}")
        require(pilot_run is not None, "terminal material validation requires Pilot Run context (--pilot-run)")
        require(identity_validated, "terminal material identity is not available")
    return {"run_id": manifest["run_id"], "track": track, "readiness": readiness, "blockers": blockers,
            "identity_validated": identity_validated, "terminal_acceptable": readiness != "BLOCKED" and identity_validated}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--track", choices=["debug", "feature", "review_release"], required=True)
    parser.add_argument("--require-terminal-ready", action="store_true")
    parser.add_argument("--task-type")
    parser.add_argument("--task-brief", type=Path)
    parser.add_argument("--pilot-run", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    run = load_json(args.pilot_run) if args.pilot_run else None
    task = load_json(args.task_brief) if args.task_brief else None
    if run is not None:
        validate_json(run, RUN_SCHEMA)
        # Standalone terminal validation uses the same frozen Task Brief as Pilot.
        from embedded_pilot import safe_ref
        frozen_task = load_json(safe_ref(args.pilot_run.parent, run["task_brief_ref"]))
        if task is not None:
            require(task == frozen_task, "material Task Brief differs from Pilot Run context")
        task = frozen_task
    result = validate_manifest(load_json(args.manifest), args.track, args.require_terminal_ready,
                               task_type=args.task_type, task=task, pilot_run=run)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    print(f"material manifest validation PASS: run={result['run_id']} track={result['track']} readiness={result['readiness']}")


if __name__ == "__main__":
    main()
