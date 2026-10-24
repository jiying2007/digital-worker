#!/usr/bin/env python3
"""Canonical Edge Foundation Pilot lifecycle and CLI."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import uuid
import unicodedata
from contextlib import contextmanager, ExitStack
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from pilot_support import (PilotError, error_result, load_json, load_yaml,
                           redact_text, validate_json, validation_scope)

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
PILOT_DIR = EDGE / "pilot"
PLAN = PILOT_DIR / "pilot-plan.yaml"
REQUIREMENTS = PILOT_DIR / "artifact-requirements.yaml"
TASK_MODES = EDGE / "runtime" / "task-modes.yaml"
RUN_SCHEMA = ROOT / "schemas" / "pilot-run.v1.schema.json"
TASK_SCHEMA = ROOT / "schemas" / "task-brief.v1.schema.json"
BUNDLE_SCHEMA = ROOT / "schemas" / "pilot-evidence-bundle.v1.schema.json"
STATUS_SCHEMA = ROOT / "schemas" / "pilot-status.v1.schema.json"
PILOT_RECEIPT_EVALUATOR = ROOT / "scripts" / "evaluate_edge_foundation_pilot.py"
PRODUCT_READINESS_EVALUATOR = ROOT / "scripts" / "evaluate_edge_foundation_product_readiness.py"
MATERIAL_VALIDATOR = ROOT / "scripts" / "validate_material_manifest.py"
SKILL_RECEIPT_SCHEMA = ROOT / "schemas" / "skill-invocation-receipt.v1.schema.json"
SKILL_RECEIPT_VALIDATOR = ROOT / "scripts" / "validate_skill_invocation_receipt.py"
TERMINAL_STATUSES = {"completed", "cancelled"}

REF_SCHEMAS = {
    "engineering_task_package_ref": EDGE / "schemas" / "engineering-task-package.schema.json",
    "delivery_receipt_ref": ROOT / "schemas" / "delivery-receipt.v1.schema.json",
    "verification_report_ref": EDGE / "schemas" / "verification-report.schema.json",
    "review_report_ref": EDGE / "schemas" / "review-report.schema.json",
    "pilot_result_ref": ROOT / "schemas" / "pilot-result.v1.schema.json",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, value: dict):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def assert_true(condition: bool, message: str):
    if not condition:
        raise ValueError(message)


def exact_git_sha(value: str | None) -> bool:
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
    from validate_material_manifest import validate_manifest
    try:
        return validate_manifest(manifest, run["pilot_track"], require_terminal_ready,
                                 task_type=run.get("task_type"),
                                 task=load_json(safe_ref(run_dir, run["task_brief_ref"])), pilot_run=run)
    except AssertionError as exc:
        raise ValueError(f"material manifest validation failed: {exc}") from exc


def validate_skill_invocation_ref(run_dir: Path, run: dict, ref: str):
    path = safe_ref(run_dir, ref)
    doc = load_json(path)
    validate_json(doc, SKILL_RECEIPT_SCHEMA)
    from validate_skill_invocation_receipt import validate_receipt
    return validate_receipt(path, pilot_run=run)


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
            principal_key = "verifier" if field == "verification_report_ref" else "reviewer"
            owner, principal = doc.get("implementation_owner"), doc.get(principal_key)
            assert_true(isinstance(owner, str) and bool(owner.strip()),
                        f"{field} requires implementation_owner for completed run")
            assert_true(isinstance(principal, str) and bool(principal.strip()),
                        f"{field} requires nonempty {principal_key}")
            assert_true(principal.strip() != owner.strip(),
                        f"{field} {principal_key} cannot equal implementation_owner")
            if "decision_actor_identity_ref" in doc:
                actor = doc["decision_actor_identity_ref"]
                assert_true(isinstance(actor, str) and bool(actor.strip()),
                            f"{field} requires nonempty decision actor")
                assert_true(actor.strip() != owner.strip(),
                            f"{field} decision actor cannot equal implementation_owner")
    elif field == "pilot_result_ref":
        assert_true(doc["run_id"] == run["run_id"], "pilot result run_id mismatch")
        assert_true(doc["source_type"] == run["source_type"], "pilot result source_type mismatch")
        assert_true(doc["pilot_track"] == run["pilot_track"], "pilot result track mismatch")
    return doc


def traceable_evidence_ref(value) -> bool:
    """Require a locator, rather than a prose assertion of success."""
    from urllib.parse import urlsplit
    if not isinstance(value, str) or any(c.isspace() for c in value):
        return False
    if re.fullmatch(r"sha256:[0-9a-fA-F]{64}", value):
        return True
    try:
        parts = urlsplit(value)
        return bool(parts.scheme and parts.netloc and not parts.username and not parts.password)
    except ValueError:
        return False


def validate_review_policy(run_dir: Path, run: dict) -> bool:
    """Validate the same frozen policy for completion and receipt consumers."""
    if run.get("review_report_ref"):
        review = load_json(safe_ref(run_dir, run["review_report_ref"]))
        return review["decision"] in {"APPROVE", "APPROVE_WITH_RISK"}
    verification = load_json(safe_ref(run_dir, run["verification_report_ref"]))
    substitute = verification.get("review_substitute")
    assert_true(isinstance(substitute, dict), "missing Review requires structured review_substitute evidence")
    assert_true(bool(substitute.get("unavailable_reason", "").strip()), "Review unavailable reason is required")
    assert_true(verification["overall"] in {"PASS", "PASS_WITH_RISK"}, "Review substitute requires passing Verification")
    policy = load_yaml(PLAN)["current_stage_review_policy"]["unavailable_review_substitute"]
    for kind in policy["required_evidence"]:
        if kind == "verification_report":
            continue
        item = substitute.get(kind, {})
        ref = item.get("evidence_ref")
        assert_true(item.get("status") == "pass" and traceable_evidence_ref(ref)
                    and ref in verification["evidence_refs"],
                    f"Review substitute requires traceable passing {kind} evidence")
    return True


def current_artifacts(run_dir: Path, run: dict) -> tuple[list[dict], list[str]]:
    required_refs, required_extra = required_artifacts(run)
    required_ref_set = set(required_refs)
    required_extra_set = set(required_extra)
    artifacts: list[dict] = []
    missing: list[str] = []
    fields = [
        "task_brief_ref", "engineering_task_package_ref", "delivery_receipt_ref",
        "verification_report_ref", "review_report_ref", "pilot_result_ref",
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
    for ref in run.get("skill_invocation_refs", []):
        path = safe_ref(run_dir, ref)
        doc = load_json(path)
        artifacts.append({"kind": f"skill_invocation:{doc['skill_id']}", "path": ref, "sha256": sha256(path), "required": False})
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


@validation_scope
def validate_run_dir(run_dir: Path, *, run: dict | None = None) -> dict:
    run_dir = run_dir.resolve()
    run = load_run(run_dir) if run is None else run
    validate_json(run, RUN_SCHEMA)
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
    for ref in run.get("skill_invocation_refs", []):
        validate_skill_invocation_ref(run_dir, run, ref)
    validate_material_manifest_ref(run_dir, run, require_terminal_ready=run["status"] == "completed")
    if run["status"] == "completed":
        required_refs, required_extra = required_artifacts(run)
        for field in required_refs:
            assert_true(bool(run.get(field)), f"completed {run['pilot_track']} run missing required ref: {field}")
        extras = run.get("extra_artifact_refs", {})
        for kind in required_extra:
            assert_true(kind in extras, f"completed {run['pilot_track']} run missing required extra artifact: {kind}")
        validate_review_policy(run_dir, run)
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
    target = safe_ref(run_dir, filename, must_exist=False)
    assert_true(not (run_dir / filename).is_symlink(), "artifact target must not be a symlink")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target.relative_to(run_dir).as_posix()


def cmd_init(args):
    validate_run_id(args.run_id)
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
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    run_dir = output_root / args.run_id
    assert_true(run_dir.resolve().parent == output_root, "Run ID escapes output root")
    run = {
        "schema_version": 1, "run_id": args.run_id, "pilot_track": args.track,
        "source_type": args.source_type, "work_item_id": task["work_item_id"],
        "task_type": args.task_type, "workflow_mode": args.workflow_mode,
        "human_owner": args.human_owner, "repo_root": args.repo_root, "base_commit": args.base_commit,
        "task_brief_ref": "task-brief.json", "engineering_task_package_ref": None,
        "delivery_receipt_ref": None, "verification_report_ref": None, "review_report_ref": None,
        "pilot_result_ref": None, "skill_invocation_refs": [], "evidence_bundle_ref": None, "extra_artifact_refs": {},
        "status": "planned", "started_at": None, "finished_at": None, "notes": [],
    }
    with writer_lock(run_dir):
        assert_true(not run_dir.exists() and not run_dir.is_symlink(), f"pilot run already exists: {run_dir}")
        with tempfile.TemporaryDirectory(prefix=".pilot-init-", dir=output_root) as tmp:
            staged = Path(tmp) / "candidate"
            staged.mkdir()
            shutil.copy2(args.task_brief, staged / "task-brief.json")
            write_json(run_path(staged), run)
            validate_run_dir(staged)
            sync_tree(staged)
            staged.rename(run_dir)
            sync_after_commit(output_root)
    print(run_dir)
    return {"run_dir": str(run_dir), "run_id": run["run_id"], "status": run["status"]}


def cmd_status(args):
    def update(staged):
        run = load_run(staged)
        assert_true(args.status != "completed", "use complete command to enter completed state")
        run["status"] = args.status
        if args.status == "running" and not run.get("started_at"):
            run["started_at"] = now_iso()
        if args.status == "cancelled":
            run["finished_at"] = now_iso()
        if args.note:
            run.setdefault("notes", []).append(args.note)
        write_json(run_path(staged), run)
    return mutate_run(args.run_dir, update)


def parse_extra(values: list[str]) -> dict[str, Path]:
    result = {}
    for value in values:
        assert_true("=" in value, f"--extra must be KIND=PATH: {value}")
        kind, raw = value.split("=", 1)
        assert_true(re.fullmatch(r"[A-Za-z0-9_.-]+", kind) is not None, f"invalid extra artifact kind: {kind}")
        assert_true(kind not in result, f"duplicate extra artifact kind: {kind}")
        result[kind] = Path(raw)
    return result


def reject_run_symlinks(run_dir: Path) -> None:
    assert_true(not run_dir.is_symlink(), "Pilot Run must not be a symlink")
    for path in run_dir.rglob("*"):
        assert_true(not path.is_symlink(), f"Pilot Run contains a symlink: {path.relative_to(run_dir)}")


def validate_run_id(value: str) -> None:
    if (not value or value in {".", ".."} or value.casefold() == ".git"
            or "/" in value or "\\" in value or Path(value).is_absolute()
            or any(unicodedata.category(char) == "Cc" for char in value)):
        raise PilotError("INVALID_RUN_ID", "Run ID must be one safe directory component", field_path="run_id")


@contextmanager
def writer_lock(run_dir: Path):
    import fcntl
    # Keep the lock inode outside the Run; do not unlink it (ABA lock race).
    identity = hashlib.sha256(str(run_dir.resolve()).encode()).hexdigest()
    path = run_dir.parent / f".pilot-lock-{identity}"
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise PilotError("RUN_LOCKED", "Another writer owns this Run; retry after it finishes") from exc
        yield
    finally:
        os.close(fd)


def sync_directory(path: Path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def sync_tree(root: Path):
    for path in root.rglob("*"):
        if path.is_file():
            with path.open("rb") as stream:
                os.fsync(stream.fileno())
    for path in sorted((p for p in root.rglob("*") if p.is_dir()), reverse=True):
        sync_directory(path)
    sync_directory(root)


def referenced_paths(run: dict) -> list[str]:
    refs = [run.get(key) for key in ["task_brief_ref", *REF_SCHEMAS, "evidence_bundle_ref"]]
    refs.extend(run.get("skill_invocation_refs", []))
    refs.extend(run.get("extra_artifact_refs", {}).values())
    return list(dict.fromkeys(ref for ref in refs if ref))


def write_derived_json(raw_output: Path, value: dict, *, locked_root: Path | None = None):
    """Publish derived output without rewriting any Run-owned evidence."""
    output = Path(os.path.abspath(raw_output))
    for component in (output, *output.parents):
        assert_true(not component.is_symlink(), "derived output must not traverse a symlink")
    owners = sorted((p for p in output.parents if run_path(p).exists()), key=str)
    with ExitStack() as guards:
        for owner in owners:
            if owner != locked_root:
                guards.enter_context(writer_lock(owner))
        for owner in owners:
            reject_run_symlinks(owner)
            run = load_run(owner)
            protected = {run_path(owner), *(safe_ref(owner, ref) for ref in referenced_paths(run))}
            assert_true(output not in protected, "derived output collides with Run marker or frozen evidence")
            assert_true(output.name != "pilot-run.json", "derived output cannot create a nested Run marker")
        output.parent.mkdir(parents=True, exist_ok=True)
        # A failed serialization/write cannot leave a half-written receipt.
        fd, name = tempfile.mkstemp(prefix=".pilot-derived-", dir=output.parent)
        temporary = Path(name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            temporary.replace(output)
            sync_after_commit(output.parent)
        finally:
            temporary.unlink(missing_ok=True)


def input_snapshot(root: Path, run: dict):
    return {ref: sha256(safe_ref(root, ref)) for ref in ["pilot-run.json", *referenced_paths(run)]}


def publish_marker(staged: Path, run_dir: Path):
    run_path(staged).replace(run_path(run_dir))
    sync_after_commit(run_dir)


def sync_after_commit(path: Path):
    try:
        sync_directory(path)
    except OSError as exc:
        raise PilotError("COMMIT_DURABILITY_UNCONFIRMED",
                         f"Commit is visible but directory sync failed at {path}; inspect recover before retrying",
                         exit_code=1) from exc


@validation_scope
def mutate_run(raw_dir: Path, update):
    reject_run_symlinks(raw_dir)
    root = raw_dir.resolve()
    with writer_lock(root):
        original = load_run(root)
        assert_mutable(original, "modifying frozen evidence")
        before = input_snapshot(root, original)
        with tempfile.TemporaryDirectory(prefix=".pilot-transaction-", dir=root.parent) as tmp:
            staged = Path(tmp) / "candidate"
            staged.mkdir()
            for ref in ["pilot-run.json", *referenced_paths(original)]:
                copy_into(staged, safe_ref(root, ref), ref)
            update(staged)
            candidate = validate_run_dir(staged)
            generation = f"artifacts/{uuid.uuid4().hex}"
            mapping = {}
            for index, ref in enumerate(referenced_paths(candidate)):
                if ref == candidate.get("evidence_bundle_ref"):
                    continue
                mapping[ref] = copy_into(staged, safe_ref(staged, ref),
                                         f"{generation}/{index:03d}-{Path(ref).name}")
            for key in ["task_brief_ref", *REF_SCHEMAS]:
                if candidate.get(key):
                    candidate[key] = mapping[candidate[key]]
            candidate["skill_invocation_refs"] = [mapping[ref] for ref in candidate.get("skill_invocation_refs", [])]
            candidate["extra_artifact_refs"] = {kind: mapping[ref] for kind, ref in candidate.get("extra_artifact_refs", {}).items()}
            if candidate.get("evidence_bundle_ref"):
                candidate["evidence_bundle_ref"] = f"{generation}/evidence-bundle.json"
                write_json(staged / candidate["evidence_bundle_ref"], collect_bundle(staged, candidate))
            write_json(run_path(staged), candidate)
            validate_run_dir(staged)
            sync_tree(staged / generation)
            with run_path(staged).open("rb") as stream:
                os.fsync(stream.fileno())
            reject_run_symlinks(root)
            if input_snapshot(root, original) != before:
                raise PilotError("RUN_CONFLICT", "Run or input changed during validation; no update committed")
            destination = root / generation
            destination.parent.mkdir(exist_ok=True)
            (staged / generation).rename(destination)
            sync_directory(destination.parent)
            # A crash here leaves an unreferenced generation, never mixed refs.
            if input_snapshot(root, original) != before:
                raise PilotError("RUN_CONFLICT", "Run changed before marker publication; inspect recover preview")
            publish_marker(staged, root)
            return candidate


def cmd_complete(args):
    return mutate_run(args.run_dir, lambda staged: _complete_candidate(args, staged))


def _complete_candidate(args, run_dir: Path):
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
    skill_refs = run.setdefault("skill_invocation_refs", [])
    for source in args.skill_invocation:
        doc = load_json(source)
        validate_json(doc, SKILL_RECEIPT_SCHEMA)
        index = len(skill_refs) + 1
        skill_refs.append(copy_into(run_dir, source, f"skill-invocations/{index:02d}-{doc['skill_id']}.json"))
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
    def update(staged):
        run = load_run(staged)
        bundle = collect_bundle(staged, run)
        if args.fail_incomplete and not bundle["complete"]:
            raise PilotError("INCOMPLETE_BUNDLE", f"Missing artifacts: {bundle['missing_required']}")
        write_json(staged / "evidence-bundle.json", bundle)
        run["evidence_bundle_ref"] = "evidence-bundle.json"
        write_json(run_path(staged), run)
    return mutate_run(args.run_dir, update)


def cmd_validate(args):
    run = validate_run_dir(args.run_dir)
    print(f"pilot run validation PASS: {run['run_id']} ({run['pilot_track']}/{run['status']})")
    return run


def cmd_summary(args):
    statuses, tracks = Counter(), Counter()
    real = synthetic = 0
    invalid = []
    run_files = sorted(p for p in args.runs_root.rglob("pilot-run.json")
                       if not any(part.startswith(".pilot-") for part in p.relative_to(args.runs_root).parts)) if args.runs_root.exists() else []
    for path in run_files:
        try:
            run = validate_run_dir(path.parent)
        except Exception as exc:
            error, _ = error_result(exc)
            # Keep the v1 string-list contract without serializing exception
            # reprs, which can contain the full private instance and schema.
            diagnostic = json.dumps({key: error[key] for key in
                                     ("error_code", "field_path", "message")}, ensure_ascii=False)
            invalid.append(f"{redact_text(str(path.parent))}: {diagnostic[:2048]}")
            continue
        statuses[run["status"]] += 1
        tracks[run["pilot_track"]] += 1
        if run["source_type"] == "real": real += 1
        else: synthetic += 1
    summary = {
        "schema_version": 1, "total_runs": len(run_files), "real_runs": real,
        "synthetic_runs": synthetic, "by_status": dict(sorted(statuses.items())),
        "by_track": dict(sorted(tracks.items())), "invalid_runs": invalid,
    }
    validate_json(summary, STATUS_SCHEMA)
    text = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    if args.output: write_derived_json(args.output, summary)
    else: print(text, end="")
    return summary


@validation_scope
def cmd_pilot_receipt(args):
    from evaluate_edge_foundation_pilot import build_receipt
    reject_run_symlinks(args.run_dir)
    run_dir = args.run_dir.resolve()
    output = Path(os.path.abspath(args.output or (run_dir / "edge-foundation-pilot-receipt.json")))
    with writer_lock(run_dir):
        run = validate_run_dir(run_dir)
        result_path = safe_ref(run_dir, run["pilot_result_ref"]) if run.get("pilot_result_ref") else None
        result = build_receipt(run_path(run_dir), result_path, args.cross_domain_trigger, receipt_dir=output.parent)
        write_derived_json(output, result, locked_root=run_dir)
    print(output)
    return result


def cmd_product_readiness(args):
    from evaluate_edge_foundation_product_readiness import collect_receipts, evaluate
    result = evaluate(collect_receipts(args.runs_root, []))
    if args.output:
        write_derived_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def cmd_doctor(args):
    import importlib.metadata
    import platform
    expected = {"PyYAML": "6.0.3", "jsonschema": "4.26.0"}
    checks = {"python": sys.version_info[:2] in {(3, 11), (3, 12)},
              "platform": platform.system() == "Linux", "git": shutil.which("git") is not None}
    versions = {}
    for package, version in expected.items():
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
        checks[package] = versions[package] == version
    result = {"status": "PASS" if all(checks.values()) else "BLOCKED", "checks": checks,
              "python": platform.python_version(), "versions": versions, "expected_versions": expected,
              "next_actions": [] if all(checks.values()) else ["使用 Linux Python 3.11/3.12 并安装 requirements-dev.txt"]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def cmd_recover(args):
    root = args.run_dir
    reject_run_symlinks(root)
    run = validate_run_dir(root)
    active = {Path(ref).parts[1] for ref in referenced_paths(run)
              if len(Path(ref).parts) >= 3 and Path(ref).parts[0] == "artifacts"}
    generations = root / "artifacts"
    result = {"run_id": run["run_id"], "read_only": True, "status": run["status"],
              "unreferenced_generations": sorted(p.name for p in generations.iterdir()
                                                  if p.is_dir() and p.name not in active) if generations.exists() else [],
              "next_actions": ["核对未引用目录；本命令不删除或重写任何证据。"]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


class PilotArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise PilotError("ARGUMENT_ERROR", message)


def build_parser():
    parser = PilotArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor", help="Check the supported local environment without third-party imports.")
    doctor.set_defaults(func=cmd_doctor)
    recover = sub.add_parser("recover", help="Read-only recovery preview; never removes evidence.")
    recover.add_argument("run_dir", type=Path); recover.add_argument("--dry-run", action="store_true"); recover.set_defaults(func=cmd_recover)
    init = sub.add_parser("init")
    init.add_argument("--run-id", required=True); init.add_argument("--track", choices=["debug", "feature", "review_release"], required=True)
    init.add_argument("--source-type", choices=["real", "synthetic"], required=True); init.add_argument("--task-type", required=True)
    init.add_argument("--workflow-mode", required=True); init.add_argument("--human-owner", required=True); init.add_argument("--task-brief", type=Path, required=True)
    init.add_argument("--repo-root"); init.add_argument("--base-commit"); init.add_argument("--output-root", type=Path, default=PILOT_DIR / "runs"); init.set_defaults(func=cmd_init)
    status = sub.add_parser("status"); status.add_argument("run_dir", type=Path); status.add_argument("status", choices=["planned", "running", "blocked", "cancelled"]); status.add_argument("--note"); status.set_defaults(func=cmd_status)
    complete = sub.add_parser("complete"); complete.add_argument("run_dir", type=Path); complete.add_argument("--engineering-task-package", type=Path); complete.add_argument("--delivery-receipt", type=Path); complete.add_argument("--verification-report", type=Path); complete.add_argument("--review-report", type=Path); complete.add_argument("--pilot-result", type=Path); complete.add_argument("--skill-invocation", type=Path, action="append", default=[]); complete.add_argument("--extra", action="append", default=[]); complete.set_defaults(func=cmd_complete)
    bundle = sub.add_parser("bundle"); bundle.add_argument("run_dir", type=Path); bundle.add_argument("--fail-incomplete", action="store_true"); bundle.set_defaults(func=cmd_bundle)
    validate = sub.add_parser("validate"); validate.add_argument("run_dir", type=Path); validate.set_defaults(func=cmd_validate)
    summary = sub.add_parser("summary"); summary.add_argument("runs_root", type=Path); summary.add_argument("--output", type=Path); summary.set_defaults(func=cmd_summary)
    receipt = sub.add_parser("pilot-receipt", help="Generate canonical Edge Foundation Pilot receipt for one run.")
    receipt.add_argument("run_dir", type=Path); receipt.add_argument("--cross-domain-trigger"); receipt.add_argument("--output", type=Path); receipt.set_defaults(func=cmd_pilot_receipt)
    readiness = sub.add_parser("product-readiness", help="Aggregate canonical Pilot receipts into product readiness.")
    readiness.add_argument("runs_root", type=Path, nargs="?", default=PILOT_DIR / "runs"); readiness.add_argument("--output", type=Path); readiness.add_argument("--require-ready", action="store_true"); readiness.set_defaults(func=cmd_product_readiness)
    parser.add_argument("--json", action="store_true", default=False)
    parser.add_argument("--debug", action="store_true", default=False)
    for command_parser in sub.choices.values():
        command_parser.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
        command_parser.add_argument("--debug", action="store_true", default=argparse.SUPPRESS)
    return parser


def main():
    import contextlib
    import io
    args = None
    wants_json = "--json" in sys.argv
    try:
        args = build_parser().parse_args()
        # Existing handlers print small summaries; no subprocess output is buffered here.
        with contextlib.redirect_stdout(io.StringIO()) if args.json else contextlib.nullcontext():
            result = args.func(args)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.command == "doctor" and result["status"] != "PASS":
            raise SystemExit(2)
        if args.command == "product-readiness" and args.require_ready and not result["eligible_for_product_review"]:
            raise SystemExit(2)
        if args.command == "summary" and result["invalid_runs"]:
            raise SystemExit(2)
    except KeyboardInterrupt:
        if wants_json:
            print(json.dumps({"error_code": "CANCELLED", "message": "操作已取消", "field_path": None, "next_actions": ["执行 recover --dry-run 检查状态。"]}, ensure_ascii=False))
        raise SystemExit(130)
    except Exception as exc:
        if args is not None and args.debug:
            raise
        result, code = error_result(exc)
        if wants_json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(f"{result['error_code']}: {result['message']}\n" + " ".join(result["next_actions"]), file=sys.stderr)
        raise SystemExit(code)


if __name__ == "__main__":
    main()
