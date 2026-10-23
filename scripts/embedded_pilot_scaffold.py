#!/usr/bin/env python3
"""Scaffold honest task-scoped working artifacts for an Edge Foundation Pilot run."""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
from validate_material_manifest import required_materials
from embedded_pilot import assert_mutable, reject_run_symlinks, safe_ref, validate_run_dir, writer_lock
from pilot_support import PilotError, error_result, load_json, validate_json, validation_scope
EDGE = ROOT / "domains" / "edge-foundation"
MATERIAL_SCHEMA = EDGE / "schemas" / "material-manifest.schema.json"
HYPOTHESIS_SCHEMA = EDGE / "schemas" / "hypothesis-registry.schema.json"


def write_json(path: Path, value: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def material_item(kind: str, required: bool, status: str, source=None, version=None, evidence_ref=None):
    return {"kind": kind, "required": required, "status": status, "source": source, "version": version, "evidence_ref": evidence_ref}


def build_material_manifest(run: dict, task: dict) -> dict:
    debug = run.get("pilot_track") == "debug"
    required_verification = task.get("required_verification", {})
    device_required = any(required_verification.get(k) == "required" for k in ("hil", "device", "release"))
    board = task.get("target_board")
    items = [
        material_item("repo", True, "available" if run.get("repo_root") else "missing", source=run.get("repo_root")),
        material_item("base_commit", True, "available" if run.get("base_commit") else "missing", version=run.get("base_commit")),
        material_item("board_revision", False, "available" if board else "missing", version=board),
        material_item("soc_mcu", False, "missing"), material_item("sdk", False, "missing"),
        material_item("kernel_rtos", False, "missing"), material_item("toolchain", False, "missing"),
        material_item("firmware", False, "missing"),
        material_item("reproduction", False, "missing" if debug else "not_applicable"),
        material_item("log", False, "missing" if debug else "not_applicable"),
        material_item("device_identity", device_required, "missing" if device_required else "not_applicable"),
        material_item("test_environment", True, "missing"),
    ]
    required = required_materials(run.get("task_type"), task)
    present = {item["kind"] for item in items}
    for kind in sorted(required - present):
        items.append(material_item(kind, True, "missing"))
    for item in items:
        if item["kind"] in required:
            item["required"] = True
            if item["status"] == "not_applicable":
                item["status"] = "missing"
    missing_critical = [item["kind"] for item in items if item["required"] and item["status"] != "available"]
    if debug:
        by_kind = {item["kind"]: item for item in items}
        if not any(by_kind[kind]["status"] == "available" for kind in ("reproduction", "log")):
            missing_critical.append("reproduction_or_log")
    manifest = {"run_id": run["run_id"], "items": items, "readiness": "BLOCKED" if missing_critical else "READY", "missing_critical": missing_critical, "degradation_approved_by": None}
    validate_json(manifest, MATERIAL_SCHEMA)
    return manifest


def build_acceptance_matrix(run: dict, task: dict) -> str:
    lines = ["# Acceptance → Evidence Matrix", "", f"- run_id: `{run['run_id']}`", f"- work_item_id: `{run['work_item_id']}`", "- status: `WORKING / NOT_VERIFIED`", "", "| AC | Criterion | Verification layer | Artifact / Device / Test identity | Evidence ref | Result |", "|---|---|---|---|---|---|"]
    criteria = task.get("acceptance_criteria") or []
    for idx, criterion in enumerate(criteria, 1):
        escaped = str(criterion).replace("|", "\\|")
        lines.append(f"| AC-{idx:03d} | {escaped} | TODO | TODO | TODO | UNVERIFIED |")
    if not criteria:
        lines.append("| AC-001 | TODO: add acceptance criterion | TODO | TODO | TODO | UNVERIFIED |")
    lines += ["", "> Completion rule: no criterion may be marked PASS without a concrete verification layer, exact relevant identity, and evidence reference.", ""]
    return "\n".join(lines)


def build_knowledge_harvest(run: dict) -> str:
    return "\n".join([
        "# Knowledge Harvest", "", f"- run_id: `{run['run_id']}`", f"- work_item_id: `{run['work_item_id']}`",
        "- result: `PENDING`  <!-- replace with NO_KNOWLEDGE_DELTA or KNOWLEDGE_CANDIDATE -->", "",
        "## Reusable delta", "", "- TODO: root cause / known issue / design rule / compatibility / checklist / runbook / verification case / skill candidate / stale knowledge", "",
        "## Evidence refs", "", "- TODO", "", "## Existing knowledge reused", "", "- TODO: list Registry knowledge_id(s), or `NONE`", "",
        "> Do not create a candidate only to satisfy process. `NO_KNOWLEDGE_DELTA` is a valid final outcome.", "",
    ])


def build_hypothesis_registry(run: dict) -> dict:
    value = {"run_id": run["run_id"], "hypotheses": []}
    validate_json(value, HYPOTHESIS_SCHEMA)
    return value


def write_once(path: Path, content: str | dict, force: bool):
    if path.exists() and not force:
        raise PilotError("ARTIFACT_EXISTS", f"refusing to overwrite existing artifact without --force: {path}")
    rendered = json.dumps(content, ensure_ascii=False, indent=2) + "\n" if isinstance(content, dict) else content
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            pending = Path(stream.name)
            stream.write(rendered)
            stream.flush()
            os.fsync(stream.fileno())
        pending.replace(path)
    finally:
        if pending is not None:
            pending.unlink(missing_ok=True)


@validation_scope
def scaffold_run(args):
    reject_run_symlinks(args.run_dir)
    run_dir = args.run_dir.resolve()
    with writer_lock(run_dir):
        reject_run_symlinks(run_dir)
        run = validate_run_dir(run_dir)
        assert_mutable(run, "scaffolding working artifacts")
        task = load_json(safe_ref(run_dir, run["task_brief_ref"]))
        working = safe_ref(run_dir, "working", must_exist=False)
        if working.exists() and not working.is_dir():
            raise PilotError("INVALID_WORKING_DIRECTORY", "working must be a directory")
        outputs = {
            working / "material-manifest.json": build_material_manifest(run, task),
            working / "acceptance-evidence-matrix.md": build_acceptance_matrix(run, task),
            working / "knowledge-harvest.md": build_knowledge_harvest(run),
        }
        if run.get("pilot_track") == "debug":
            outputs[working / "hypothesis-registry.json"] = build_hypothesis_registry(run)
        # Check every precondition before publishing even the first draft.
        for path in outputs:
            safe_ref(run_dir, path.relative_to(run_dir).as_posix(), must_exist=False)
            if path.exists() and (not args.force or not path.is_file()):
                raise PilotError("ARTIFACT_EXISTS", f"Existing output conflicts with scaffold: {path}; inspect before --force")
        for path, content in outputs.items():
            write_once(path, content, args.force)
            print(path.relative_to(run_dir))
        print("scaffold complete; unresolved context remains explicitly missing/BLOCKED until filled")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path); parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        scaffold_run(args)
    except Exception as exc:
        result, code = error_result(exc)
        print(f"{result['error_code']}: {result['message']}", file=sys.stderr)
        raise SystemExit(code)


if __name__ == "__main__": main()
