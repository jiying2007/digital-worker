#!/usr/bin/env python3
"""Validate Embedded Material Manifest semantics and terminal readiness.

This validator is intentionally small: it validates the existing Material Manifest
schema, recomputes critical blockers, models the Debug `reproduction OR log`
alternative, and can reject BLOCKED manifests for terminal Pilot evidence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "expert-groups" / "embedded-system" / "schemas" / "material-manifest.schema.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_json(value: dict, schema_path: Path) -> None:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def recompute_blockers(manifest: dict, track: str) -> list[str]:
    items = manifest["items"]
    kinds = [item["kind"] for item in items]
    require(len(kinds) == len(set(kinds)), "material manifest contains duplicate item kinds")
    by_kind = {item["kind"]: item for item in items}

    blockers = [item["kind"] for item in items if item["required"] and item["status"] != "available"]
    if track == "debug":
        require("reproduction" in by_kind, "debug material manifest missing reproduction item")
        require("log" in by_kind, "debug material manifest missing log item")
        if not any(by_kind[kind]["status"] == "available" for kind in ("reproduction", "log")):
            blockers.append("reproduction_or_log")
    return sorted(set(blockers))


def validate_manifest(manifest: dict, track: str, require_terminal_ready: bool = False) -> dict:
    validate_json(manifest, SCHEMA)
    blockers = recompute_blockers(manifest, track)
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

    return {
        "run_id": manifest["run_id"],
        "track": track,
        "readiness": readiness,
        "blockers": blockers,
        "terminal_acceptable": readiness != "BLOCKED",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--track", choices=["debug", "feature", "review_release"], required=True)
    parser.add_argument("--require-terminal-ready", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = validate_manifest(load_json(args.manifest), args.track, args.require_terminal_ready)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    print(
        "material manifest validation PASS: "
        f"run={result['run_id']} track={result['track']} readiness={result['readiness']}"
    )


if __name__ == "__main__":
    main()
