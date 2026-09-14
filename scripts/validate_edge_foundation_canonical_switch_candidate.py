#!/usr/bin/env python3
"""Fail-closed guard for a future Edge Foundation canonical-routing switch PR."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = ROOT / "schemas" / "edge-foundation-canonical-switch-change-manifest.v1.schema.json"
PLAN_SCHEMA = ROOT / "schemas" / "edge-foundation-canonical-switch-plan.v1.schema.json"

ALLOWED_PATH_CLASS = {
    "domains/edge-foundation/domain.yaml": "canonical-routing-authority",
    "domains/edge-foundation/compatibility/embedded-1plus7-mapping.yaml": "migration-phase-status",
    "domains/edge-foundation/canonical-routing.yaml": "routing-selector-entrypoint",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_json(value: dict, schema_path: Path) -> None:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_candidate(manifest_path: Path, switch_plan_path: Path, changed_files_path: Path) -> dict:
    manifest = load_json(manifest_path)
    validate_json(manifest, MANIFEST_SCHEMA)
    plan = load_json(switch_plan_path)
    validate_json(plan, PLAN_SCHEMA)

    require(plan["status"] == "DRY_RUN_ONLY", "switch plan must remain DRY_RUN_ONLY")
    require(plan["apply_allowed"] is False, "dry-run plan must not authorize apply")
    require(plan["canonical_routing_switched"] is False, "dry-run plan must remain unswitched")
    require(manifest["switch_plan_sha256"] == sha256(switch_plan_path), "manifest switch_plan_sha256 mismatch")
    require(manifest["canonical_routing_target"] == "edge-foundation", "unexpected routing target")
    require(manifest["legacy_compatibility_preserved"] is True, "legacy compatibility must remain preserved")

    declared = manifest["changes"]
    declared_paths = [item["path"] for item in declared]
    require(len(declared_paths) == len(set(declared_paths)), "duplicate declared changed path")

    for item in declared:
        path = item["path"]
        require(path in ALLOWED_PATH_CLASS, f"switch candidate declares forbidden path: {path}")
        require(
            item["change_class"] == ALLOWED_PATH_CLASS[path],
            f"wrong change class for {path}: expected {ALLOWED_PATH_CLASS[path]}, got {item['change_class']}",
        )

    changed_files = [line.strip() for line in changed_files_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    require(len(changed_files) == len(set(changed_files)), "changed-file list contains duplicates")
    require(set(changed_files) == set(declared_paths), f"changed files do not match manifest: actual={sorted(changed_files)} declared={sorted(declared_paths)}")

    forbidden_prefixes = (
        "expert-groups/embedded-system/",
        "contracts/",
        "schemas/pilot-",
        "config/integrations/",
    )
    for path in changed_files:
        require(not path.startswith(forbidden_prefixes), f"phase-3 switch candidate touches forbidden surface: {path}")

    return {
        "status": "PASS",
        "changed_files": sorted(changed_files),
        "base_sha": manifest["candidate_base_sha"],
        "head_sha": manifest["candidate_head_sha"],
        "canonical_routing_target": manifest["canonical_routing_target"],
        "legacy_compatibility_preserved": manifest["legacy_compatibility_preserved"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--switch-plan", type=Path, required=True)
    parser.add_argument("--changed-files", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = validate_candidate(args.manifest, args.switch_plan, args.changed_files)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    print(f"edge-foundation canonical switch candidate PASS: files={len(result['changed_files'])}")


if __name__ == "__main__":
    main()
