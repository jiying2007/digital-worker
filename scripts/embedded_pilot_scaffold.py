#!/usr/bin/env python3
"""Scaffold honest, task-scoped V1 working artifacts for an embedded pilot run.

This helper never claims missing engineering context is READY. It creates editable
working artifacts from pilot-run.json + task-brief.json and marks unresolved
identity/context as missing/BLOCKED until a human or trusted source fills it.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EMB = ROOT / "expert-groups" / "embedded-system"
MATERIAL_SCHEMA = EMB / "schemas" / "material-manifest.schema.json"
HYPOTHESIS_SCHEMA = EMB / "schemas" / "hypothesis-registry.schema.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_json(value: dict, schema_path: Path):
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def material_item(kind: str, required: bool, status: str, source=None, version=None, evidence_ref=None):
    return {
        "kind": kind,
        "required": required,
        "status": status,
        "source": source,
        "version": version,
        "evidence_ref": evidence_ref,
    }


def build_material_manifest(run: dict, task: dict) -> dict:
    debug = run.get("pilot_track") == "debug"
    required_verification = task.get("required_verification", {})
    device_required = any(required_verification.get(k) == "required" for k in ("hil", "device", "release"))

    board = task.get("target_board")
    items = [
        material_item("repo", True, "available" if run.get("repo_root") else "missing", source=run.get("repo_root")),
        material_item("base_commit", True, "available" if run.get("base_commit") else "missing", version=run.get("base_commit")),
        material_item("board_revision", False, "available" if board else "missing", version=board),
        material_item("soc_mcu", False, "missing"),
        material_item("sdk", False, "missing"),
        material_item("kernel_rtos", False, "missing"),
        material_item("toolchain", False, "missing"),
        material_item("firmware", False, "missing"),
        material_item("reproduction", debug, "missing" if debug else "not_applicable"),
        material_item("device_identity", device_required, "missing" if device_required else "not_applicable"),
        material_item("test_environment", True, "missing"),
    ]
    missing_critical = [item["kind"] for item in items if item["required"] and item["status"] != "available"]
    manifest = {
        "run_id": run["run_id"],
        "items": items,
        "readiness": "BLOCKED" if missing_critical else "READY",
        "missing_critical": missing_critical,
        "degradation_approved_by": None,
    }
    validate_json(manifest, MATERIAL_SCHEMA)
    return manifest


def build_acceptance_matrix(run: dict, task: dict) -> str:
    lines = [
        "# Acceptance → Evidence Matrix",
        "",
        f"- run_id: `{run['run_id']}`",
        f"- work_item_id: `{run['work_item_id']}`",
        "- status: `WORKING / NOT_VERIFIED`",
        "",
        "| AC | Criterion | Verification layer | Artifact / Device / Test identity | Evidence ref | Result |",
        "|---|---|---|---|---|---|",
    ]
    criteria = task.get("acceptance_criteria") or []
    for idx, criterion in enumerate(criteria, 1):
        safe = str(criterion).replace("|", "\\|")
        lines.append(f"| AC-{idx:03d} | {safe} | TODO | TODO | TODO | UNVERIFIED |")
    if not criteria:
        lines.append("| AC-001 | TODO: add acceptance criterion | TODO | TODO | TODO | UNVERIFIED |")
    lines += [
        "",
        "> Completion rule: no criterion may be marked PASS without a concrete verification layer, exact relevant identity, and evidence reference.",
        "",
    ]
    return "\n".join(lines)


def build_knowledge_harvest(run: dict) -> str:
    return "\n".join([
        "# Knowledge Harvest",
        "",
        f"- run_id: `{run['run_id']}`",
        f"- work_item_id: `{run['work_item_id']}`",
        "- result: `PENDING`  <!-- replace with NO_KNOWLEDGE_DELTA or KNOWLEDGE_CANDIDATE -->",
        "",
        "## Reusable delta",
        "",
        "- TODO: root cause / known issue / design rule / compatibility / checklist / runbook / verification case / skill candidate / stale knowledge",
        "",
        "## Evidence refs",
        "",
        "- TODO",
        "",
        "## Existing knowledge reused",
        "",
        "- TODO: list Registry knowledge_id(s), or `NONE`",
        "",
        "> Do not create a candidate only to satisfy process. `NO_KNOWLEDGE_DELTA` is a valid final outcome.",
        "",
    ])


def build_hypothesis_registry(run: dict) -> dict:
    value = {"run_id": run["run_id"], "hypotheses": []}
    validate_json(value, HYPOTHESIS_SCHEMA)
    return value


def write_once(path: Path, content: str | dict, force: bool):
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite existing artifact without --force: {path}")
    if isinstance(content, dict):
        write_json(path, content)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    run = load_json(run_dir / "pilot-run.json")
    task = load_json(run_dir / run["task_brief_ref"])
    working = run_dir / "working"

    outputs = {
        working / "material-manifest.json": build_material_manifest(run, task),
        working / "acceptance-evidence-matrix.md": build_acceptance_matrix(run, task),
        working / "knowledge-harvest.md": build_knowledge_harvest(run),
    }
    if run.get("pilot_track") == "debug":
        outputs[working / "hypothesis-registry.json"] = build_hypothesis_registry(run)

    for path, content in outputs.items():
        write_once(path, content, args.force)
        print(path.relative_to(run_dir))

    print("scaffold complete; unresolved context remains explicitly missing/BLOCKED until filled")


if __name__ == "__main__":
    main()
