#!/usr/bin/env python3
"""Operational CLI for fail-closed embedded expert-team pilot runs."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EMB = ROOT / "expert-groups" / "embedded-system"
PILOT_DIR = EMB / "pilot"
PLAN = PILOT_DIR / "pilot-plan.yaml"
REQUIREMENTS = PILOT_DIR / "artifact-requirements.yaml"
TASK_MODES = EMB / "config" / "task-modes.yaml"
RUN_SCHEMA = ROOT / "schemas" / "pilot-run.v1.schema.json"
TASK_SCHEMA = ROOT / "schemas" / "task-brief.v1.schema.json"
BUNDLE_SCHEMA = ROOT / "schemas" / "pilot-evidence-bundle.v1.schema.json"
STATUS_SCHEMA = ROOT / "schemas" / "pilot-status.v1.schema.json"
EDGE_SHADOW_EVALUATOR = ROOT / "scripts" / "evaluate_edge_foundation_pilot_shadow.py"
EDGE_READINESS_EVALUATOR = ROOT / "scripts" / "evaluate_edge_foundation_phase3_readiness.py"
MATERIAL_VALIDATOR = ROOT / "scripts" / "validate_material_manifest.py"
TERMINAL_STATUSES = {"completed", "cancelled"}

REF_SCHEMAS = {
    "engineering_task_package_ref": EMB / "schemas" / "engineering-task-package.schema.json",
    "delivery_receipt_ref": ROOT / "schemas" / "delivery-receipt.v1.schema.json",
    "verification_report_ref": EMB / "schemas" / "verification-report.schema.json",
    "review_report_ref": EMB / "schemas" / "review-report.schema.json",
    "pilot_result_ref": ROOT / "schemas" / "pilot-result.v1.schema.json",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_json(value: dict, schema_path: Path):
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def assert_true(condition: bool, message: str):
    if not condition:
        raise ValueError(message)


def exact_git_sha(value: str | None) -> bool:
    """Return true only for a canonical full 40-hex Git object id."""
    return re.fullmatch(r"[0-9a-fA-F]{40}", value or "") is not None


def assert_mutable(run: dict, operation: str) -> None:
    assert_true(
        run.get("status") not in TERMINAL_STATUSES,
        f"pilot run is terminal ({run.get('status')}); create a superseding run instead of {operation}",
    )


def safe_ref(run_dir: Path, ref: str, must_exist: bool = True) -> Path:
    relative = Path(ref)
    assert_true(not relative.is_absolute(), f"pilot artifact ref must be relative: {ref}")
    root = run_dir.resolve()
    path = (run_dir / relative).resolve()
    assert_true(path == root or root in path.parents, f"pilot artifact ref escapes run directory: {ref}")
    if must_exist:
        assert_true(path.is_file(), f"pilot artifact ref missing: {ref}")
    return path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_path(run_dir: Path) -> Path:
    return run_dir / "pilot-run.json"


def load_run(run_dir: Path) -> dict:
    path = run_path(run_dir)
    assert_true(path.is_file(), f"pilot-run.json not found: {run_dir}")
    run = load_json(path)
    validate_json(run, RUN_SCHEMA)
    return run


def check_route(run: dict):
    plan = load_yaml(PLAN)
    modes = load_yaml(TASK_MODES)
    track = plan["tracks"].get(run["pilot_track"])
    assert_true(track is not None, f"unknown pilot track: {run['pilot_track']}")
    assert_true(run["task_type"] in track["candidate_task_types"], f"task type not allowed by pilot track: {run['task_type']}")
    route = modes["routing"].get(run["task_type"])
    assert_true(route is not None, f"unknown task type: {run['task_type']}")
    assert_true(run["workflow_mode"] in route["allowed_modes"], f"workflow mode not allowed for task type: {run['workflow_mode']}")


def required_artifacts(run: dict) -> tuple[list[str], list[str]]:
    cfg = load_yaml(REQUIREMENTS)["tracks"][run["pilot_track"]]
    return list(cfg["required_refs"]), list(cfg["required_extra_artifacts"])


def validate_material_manifest_ref(run_dir: Path, run: dict, require_terminal_ready: bool = False):
    ref = run.get("extra_artifact_refs", {}).get("material_manifest")
    if not ref:
        return None
    path = safe_ref(run_dir, ref)
    manifest = load_json(path)
    assert_true(manifest.get("run_id") == run["run_id"], "material manifest run_id mismatch")
    command = [
        sys.executable,
        str(MATERIAL_VALIDATOR),
        str(path),
        "--track",
        run["pilot_track"],
    ]
    if require_terminal_ready:
        command.append("--require-terminal-ready")
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    detail = (completed.stderr or completed.stdout or "material manifest validator failed").strip()
    assert_true(completed.returncode == 0, f"material manifest validation failed: {detail}")
    return completed


def validate_linked_document(run_dir: Path, run: dict, field: str, schema_path: Path):
    ref = run.get(field)
    if not ref:
        return None
    path = safe_ref(run_dir, ref)
    doc = load_json(path)
    validate_json(doc, schema_path)
    if field == "engineering_task_package_ref":
        assert_true(doc["run_id"] == run["run_id"], "engineering task package run_id mismatch")
        if run.get("repo_root"):
            assert_true(doc["repo_root"] == run["repo_root"], "engineering task package repo_root mismatch")
        if run.get("base_commit"):
            assert_true(doc["base_commit"] == run["base_commit"], "engineering task package base_commit mismatch")
    elif field == "delivery_receipt_ref":
        assert_true(doc["work_item_id"] == run["work_item_id"], "delivery receipt work_item_id mismatch")
        if run.get("repo_root"):
            assert_true(doc["repo_root"] == run["repo_root"], "delivery receipt repo_root mismatch")
        if run.get("base_commit"):
            assert_true(doc["base_commit"] == run["base_commit"], "delivery receipt base_commit mismatch")
    elif field in {"verification_report_ref", "review_report_ref"}:
        assert_true(doc["run_id"] == run["run_id"], f"{field} run_id mismatch")
        if run["status"] == "completed":
            assert_true(doc.get("independence_confirmed", False), f"{field} must confirm independence for completed run")
    elif field == "pilot_result_ref":
        assert_true(doc["run_id"] == run["run_id"], "pilot result run_id mismatch")
        assert_true(doc["source_type"] == run["source_type"], "pilot result source_type mismatch")
        assert_true(doc["pilot_track"] == run["pilot_track"], "pilot result track mismatch")
    return doc


def current_artifacts(run_dir: Path, run: dict) -> tuple[list[dict], list[str]]:
    required_refs, required_extra = required_artifacts(run)
    required_ref_set = set(required_refs)
    required_extra_set = set(required_extra)
    artifacts: list[dict] = []
    missing: list[str] = []
    fields = [
        "task_brief_ref",
        "engineering_task_package_ref",
        "delivery_receipt_ref",
        "verification_report_ref",
        "review_report_ref",
        "pilot_result_ref",
    ]
    for field in fields:
        ref = run.get(field)
        required = field in required_ref_set
        if not ref:
            if required:
                missing.append(field)
            continue
        path = safe_ref(run_dir, ref)
        artifacts.append({"kind": field.removesuffix("_ref"), "path": ref, "sha256": sha256(path), "required": required})
    extras = run.get("extra_artifact_refs", {})
    for kind in required_extra:
        if kind not in extras:
            missing.append(f"extra:{kind}")
    for kind, ref in sorted(extras.items()):
        path = safe_ref(run_dir, ref)
        artifacts.append({"kind": kind, "path": ref, "sha256": sha256(path), "required": kind in required_extra_set})
    return artifacts, missing


def collect_bundle(run_dir: Path, run: dict) -> dict:
    artifacts, missing = current_artifacts(run_dir, run)
    bundle = {
        "schema_version": 1,
        "run_id": run["run_id"],
        "work_item_id": run["work_item_id"],
        "source_type": run["source_type"],
        "generated_at": now_iso(),
        "artifacts": artifacts,
        "complete": not missing,
        "missing_required": missing,
    }
    validate_json(bundle, BUNDLE_SCHEMA)
    return bundle


def validate_bundle_integrity(run_dir: Path, run: dict, bundle: dict) -> None:
    """Recompute every artifact digest; a completed run must match its frozen bundle exactly."""
    expected, missing = current_artifacts(run_dir, run)
    assert_true(not missing, f"completed run now misses required artifacts: {missing}")
    actual_by_path = {item["path"]: item for item in bundle.get("artifacts", [])}
    expected_by_path = {item["path"]: item for item in expected}
    assert_true(len(actual_by_path) == len(bundle.get("artifacts", [])), "evidence bundle contains duplicate artifact paths")
    assert_true(set(actual_by_path) == set(expected_by_path), "evidence bundle artifact set no longer matches run refs")
    for path, expected_item in expected_by_path.items():
        recorded = actual_by_path[path]
        assert_true(recorded.get("kind") == expected_item["kind"], f"evidence kind drift: {path}")
        assert_true(recorded.get("required") == expected_item["required"], f"evidence required flag drift: {path}")
        assert_true(recorded.get("sha256") == expected_item["sha256"], f"evidence SHA256 mismatch: {path}")


def validate_run_dir(run_dir: Path) -> dict:
    run_dir = run_dir.resolve()
    run = load_run(run_dir)
    check_route(run)

    task = load_json(safe_ref(run_dir, run["task_brief_ref"]))
    validate_json(task, TASK_SCHEMA)
    assert_true(task["work_item_id"] == run["work_item_id"], "task brief work_item_id mismatch")
    if run.get("repo_root"):
        assert_true(run["repo_root"] in task["repo_roots"], "pilot repo_root is not authorized by task brief")
    if run["source_type"] == "real":
        assert_true(bool(run.get("repo_root")), "real pilot requires repo_root")
        assert_true(exact_git_sha(run.get("base_commit")), "real pilot base_commit must be a full 40-hex Git SHA")

    for field, schema_path in REF_SCHEMAS.items():
        validate_linked_document(run_dir, run, field, schema_path)
    for kind, ref in run.get("extra_artifact_refs", {}).items():
        assert_true(re.fullmatch(r"[A-Za-z0-9_.-]+", kind) is not None, f"invalid extra artifact kind: {kind}")
        safe_ref(run_dir, ref)
    validate_material_manifest_ref(run_dir, run, require_terminal_ready=run["status"] == "completed")

    if run["status"] == "completed":
        required_refs, required_extra = required_artifacts(run)
        for field in required_refs:
            assert_true(bool(run.get(field)), f"completed {run['pilot_track']} run missing required ref: {field}")
        extras = run.get("extra_artifact_refs", {})
        for kind in required_extra:
            assert_true(kind in extras, f"completed {run['pilot_track']} run missing required extra artifact: {kind}")
        assert_true(bool(run.get("evidence_bundle_ref")), "completed run requires evidence_bundle_ref")
        bundle = load_json(safe_ref(run_dir, run["evidence_bundle_ref"]))
        validate_json(bundle, BUNDLE_SCHEMA)
        assert_true(bundle["run_id"] == run["run_id"], "evidence bundle run_id mismatch")
        assert_true(bundle["work_item_id"] == run["work_item_id"], "evidence bundle work_item_id mismatch")
        assert_true(bundle["source_type"] == run["source_type"], "evidence bundle source_type mismatch")
        assert_true(bundle["complete"] is True and not bundle["missing_required"], "completed run evidence bundle is incomplete")
        validate_bundle_integrity(run_dir, run, bundle)
    return run


def copy_into(run_dir: Path, source: Path, filename: str) -> str:
    assert_true(source.is_file(), f"artifact source missing: {source}")
    target = run_dir / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target.relative_to(run_dir).as_posix()


def cmd_init(args):
    task = load_json(args.task_brief)
    validate_json(task, TASK_SCHEMA)
    plan = load_yaml(PLAN)
    assert_true(args.track in plan["tracks"], f"unknown pilot track: {args.track}")
    assert_true(args.task_type in plan["tracks"][args.track]["candidate_task_types"], "task type is not permitted for selected pilot track")
    route = load_yaml(TASK_MODES)["routing"].get(args.task_type)
    assert_true(route is not None and args.workflow_mode in route["allowed_modes"], "workflow mode is not permitted for task type")
    if args.source_type == "real":
        assert_true(bool(args.repo_root), "real pilot init requires --repo-root")
        assert_true(exact_git_sha(args.base_commit), "real pilot --base-commit must be a full 40-hex Git SHA")
    if args.repo_root:
        assert_true(args.repo_root in task["repo_roots"], "--repo-root is not authorized by task brief")

    run_dir = args.output_root / args.run_id
    assert_true(not run_dir.exists(), f"pilot run already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    shutil.copy2(args.task_brief, run_dir / "task-brief.json")
    run = {
        "schema_version": 1,
        "run_id": args.run_id,
        "pilot_track": args.track,
        "source_type": args.source_type,
        "work_item_id": task["work_item_id"],
        "task_type": args.task_type,
        "workflow_mode": args.workflow_mode,
        "human_owner": args.human_owner,
        "repo_root": args.repo_root,
        "base_commit": args.base_commit,
        "task_brief_ref": "task-brief.json",
        "engineering_task_package_ref": None,
        "delivery_receipt_ref": None,
        "verification_report_ref": None,
        "review_report_ref": None,
        "pilot_result_ref": None,
        "evidence_bundle_ref": None,
        "extra_artifact_refs": {},
        "status": "planned",
        "started_at": None,
        "finished_at": None,
        "notes": [],
    }
    write_json(run_path(run_dir), run)
    validate_run_dir(run_dir)
    print(run_dir)


def cmd_status(args):
    run = load_run(args.run_dir)
    assert_mutable(run, "changing status")
    assert_true(args.status != "completed", "use complete command to enter completed state")
    run["status"] = args.status
    if args.status == "running" and not run.get("started_at"):
        run["started_at"] = now_iso()
    if args.status == "cancelled":
        run["finished_at"] = now_iso()
    if args.note:
        run.setdefault("notes", []).append(args.note)
    write_json(run_path(args.run_dir), run)
    validate_run_dir(args.run_dir)


def parse_extra(values: list[str]) -> dict[str, Path]:
    result = {}
    for value in values:
        assert_true("=" in value, f"--extra must be KIND=PATH: {value}")
        kind, raw = value.split("=", 1)
        assert_true(re.fullmatch(r"[A-Za-z0-9_.-]+", kind) is not None, f"invalid extra artifact kind: {kind}")
        assert_true(kind not in result, f"duplicate extra artifact kind: {kind}")
        result[kind] = Path(raw)
    return result


def cmd_complete(args):
    run_dir = args.run_dir.resolve()
    run = load_run(run_dir)
    assert_mutable(run, "completing again")
    attachments = {
        "engineering_task_package_ref": (args.engineering_task_package, "engineering-task-package.json"),
        "delivery_receipt_ref": (args.delivery_receipt, "delivery-receipt.json"),
        "verification_report_ref": (args.verification_report, "verification-report.json"),
        "review_report_ref": (args.review_report, "review-report.json"),
        "pilot_result_ref": (args.pilot_result, "pilot-result.json"),
    }
    for field, (source, filename) in attachments.items():
        if source:
            run[field] = copy_into(run_dir, source, filename)
    extras = run.setdefault("extra_artifact_refs", {})
    for kind, source in parse_extra(args.extra).items():
        suffix = source.suffix if source.suffix else ".artifact"
        extras[kind] = copy_into(run_dir, source, f"extras/{kind}{suffix}")
    if not run.get("started_at"):
        run["started_at"] = now_iso()
    run["status"] = "running"
    run["finished_at"] = None
    write_json(run_path(run_dir), run)
    validate_run_dir(run_dir)
    validate_material_manifest_ref(run_dir, run, require_terminal_ready=True)

    bundle = collect_bundle(run_dir, run)
    assert_true(bundle["complete"], f"cannot complete pilot run; missing required artifacts: {bundle['missing_required']}")
    write_json(run_dir / "evidence-bundle.json", bundle)
    run["evidence_bundle_ref"] = "evidence-bundle.json"
    run["status"] = "completed"
    run["finished_at"] = now_iso()
    write_json(run_path(run_dir), run)
    validate_run_dir(run_dir)


def cmd_bundle(args):
    run_dir = args.run_dir.resolve()
    run = load_run(run_dir)
    assert_mutable(run, "regenerating evidence bundle")
    bundle = collect_bundle(run_dir, run)
    write_json(run_dir / "evidence-bundle.json", bundle)
    run["evidence_bundle_ref"] = "evidence-bundle.json"
    write_json(run_path(run_dir), run)
    if args.fail_incomplete and not bundle["complete"]:
        raise SystemExit(2)


def cmd_validate(args):
    run = validate_run_dir(args.run_dir)
    print(f"pilot run validation PASS: {run['run_id']} ({run['pilot_track']}/{run['status']})")


def cmd_summary(args):
    statuses = Counter()
    tracks = Counter()
    real = synthetic = 0
    invalid = []
    run_files = sorted(args.runs_root.rglob("pilot-run.json")) if args.runs_root.exists() else []
    for path in run_files:
        try:
            run = validate_run_dir(path.parent)
        except Exception as exc:
            invalid.append(f"{path.parent}: {exc}")
            continue
        statuses[run["status"]] += 1
        tracks[run["pilot_track"]] += 1
        if run["source_type"] == "real":
            real += 1
        else:
            synthetic += 1
    summary = {
        "schema_version": 1,
        "total_runs": len(run_files),
        "real_runs": real,
        "synthetic_runs": synthetic,
        "by_status": dict(sorted(statuses.items())),
        "by_track": dict(sorted(tracks.items())),
        "invalid_runs": invalid,
    }
    validate_json(summary, STATUS_SCHEMA)
    text = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    if invalid:
        raise SystemExit(2)


def cmd_edge_shadow(args):
    run_dir = args.run_dir.resolve()
    run = validate_run_dir(run_dir)
    output = (args.output or (run_dir / "edge-foundation-shadow-receipt.json")).resolve()
    command = [
        sys.executable,
        str(EDGE_SHADOW_EVALUATOR),
        str(run_path(run_dir)),
        "--output",
        str(output),
    ]
    pilot_result_ref = run.get("pilot_result_ref")
    if pilot_result_ref:
        command.extend(["--pilot-result", str(safe_ref(run_dir, pilot_result_ref))])
    if args.cross_domain_trigger:
        command.extend(["--cross-domain-trigger", args.cross_domain_trigger])
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    print(output)


def cmd_phase3_readiness(args):
    command = [
        sys.executable,
        str(EDGE_READINESS_EVALUATOR),
        "--receipt-dir",
        str(args.runs_root.resolve()),
    ]
    if args.output:
        command.extend(["--output", str(args.output.resolve())])
    if args.require_ready:
        command.append("--require-ready")
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("--run-id", required=True)
    init.add_argument("--track", choices=["debug", "feature", "review_release"], required=True)
    init.add_argument("--source-type", choices=["real", "synthetic"], required=True)
    init.add_argument("--task-type", required=True)
    init.add_argument("--workflow-mode", required=True)
    init.add_argument("--human-owner", required=True)
    init.add_argument("--task-brief", type=Path, required=True)
    init.add_argument("--repo-root")
    init.add_argument("--base-commit")
    init.add_argument("--output-root", type=Path, default=PILOT_DIR / "runs")
    init.set_defaults(func=cmd_init)

    status = sub.add_parser("status")
    status.add_argument("run_dir", type=Path)
    status.add_argument("status", choices=["planned", "running", "blocked", "cancelled"])
    status.add_argument("--note")
    status.set_defaults(func=cmd_status)

    complete = sub.add_parser("complete")
    complete.add_argument("run_dir", type=Path)
    complete.add_argument("--engineering-task-package", type=Path)
    complete.add_argument("--delivery-receipt", type=Path)
    complete.add_argument("--verification-report", type=Path)
    complete.add_argument("--review-report", type=Path)
    complete.add_argument("--pilot-result", type=Path)
    complete.add_argument("--extra", action="append", default=[])
    complete.set_defaults(func=cmd_complete)

    bundle = sub.add_parser("bundle")
    bundle.add_argument("run_dir", type=Path)
    bundle.add_argument("--fail-incomplete", action="store_true")
    bundle.set_defaults(func=cmd_bundle)

    validate = sub.add_parser("validate")
    validate.add_argument("run_dir", type=Path)
    validate.set_defaults(func=cmd_validate)

    summary = sub.add_parser("summary")
    summary.add_argument("runs_root", type=Path)
    summary.add_argument("--output", type=Path)
    summary.set_defaults(func=cmd_summary)

    edge_shadow = sub.add_parser("edge-shadow", help="Generate a non-canonical Edge Foundation shadow receipt for one run.")
    edge_shadow.add_argument("run_dir", type=Path)
    edge_shadow.add_argument("--cross-domain-trigger")
    edge_shadow.add_argument("--output", type=Path)
    edge_shadow.set_defaults(func=cmd_edge_shadow)

    readiness = sub.add_parser("phase3-readiness", help="Aggregate Edge Foundation shadow receipts into phase-3 review readiness.")
    readiness.add_argument("runs_root", type=Path, nargs="?", default=PILOT_DIR / "runs")
    readiness.add_argument("--output", type=Path)
    readiness.add_argument("--require-ready", action="store_true")
    readiness.set_defaults(func=cmd_phase3_readiness)
    return parser


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
