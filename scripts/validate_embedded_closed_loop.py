#!/usr/bin/env python3
"""Fail-closed validation for Embedded Domain Closed Loop V1 assets."""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EMB = ROOT / "expert-groups" / "embedded-system"
STRATEGY = ROOT / "docs" / "strategy" / "embedded-domain-closed-loop-v1.md"
REGISTRY = EMB / "knowledge" / "registry.yaml"
REQUIREMENTS = EMB / "pilot" / "artifact-requirements.yaml"
QUICKSTART = ROOT / "docs" / "runbooks" / "embedded-closed-loop-quickstart.md"
SCAFFOLD = ROOT / "scripts" / "embedded_pilot_scaffold.py"
KNOWLEDGE_CLI = ROOT / "scripts" / "embedded_knowledge.py"


def assert_true(condition: bool, message: str):
    if not condition:
        raise AssertionError(message)


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    strategy = STRATEGY.read_text(encoding="utf-8")
    assert_true("current-stage-baseline" in strategy, "closed-loop strategy must be current-stage-baseline")
    for marker in ["V1-1", "V1-2", "V1-3", "V1-4", "V1-5", "V1-6", "V1-7"]:
        assert_true(marker in strategy, f"closed-loop strategy missing {marker}")
    assert_true("Enterprise Digital Thread 不是前置条件" in strategy, "strategy must keep enterprise integration non-blocking")
    assert_true("当前目标只推进到 **E2，并为 E3 建基础**" in strategy, "strategy must constrain maturity claim")

    registry = load_yaml(REGISTRY)
    assert_true(registry["status"] == "internal-seed", "knowledge registry must declare internal-seed status")
    assert_true(registry["source_of_truth_policy"] == "stays_at_source", "knowledge registry must preserve source authority")
    assert_true(registry["provider_binding"] == "not_frozen", "knowledge registry must remain provider-neutral")
    entries = registry["entries"]
    assert_true(50 <= len(entries) <= 100, f"V1 registry must seed 50-100 entries, got {len(entries)}")

    ids = [item["knowledge_id"] for item in entries]
    assert_true(len(ids) == len(set(ids)), "duplicate knowledge IDs")
    assert_true(all(re.fullmatch(r"EKR-\d{3}", item_id) for item_id in ids), "knowledge IDs must use EKR-NNN")
    allowed_types = {"authority", "engineering", "operational", "ai_execution"}
    allowed_authority = {"canonical", "interpretive", "procedure"}
    defaults = registry["defaults"]
    assert_true(defaults["source_provider"] == "git", "internal seed must use git sources")
    assert_true(defaults["version"] == "tracked-by-git", "internal seed version must be tracked-by-git")

    required_fields = {"knowledge_id", "title", "domain", "knowledge_type", "authority", "source_ref", "owner", "tags"}
    for item in entries:
        missing = required_fields - set(item)
        assert_true(not missing, f"knowledge entry missing fields: {item.get('knowledge_id')} -> {sorted(missing)}")
        assert_true(item["knowledge_type"] in allowed_types, f"invalid knowledge type: {item['knowledge_id']}")
        assert_true(item["authority"] in allowed_authority, f"invalid authority: {item['knowledge_id']}")
        source = (ROOT / item["source_ref"]).resolve()
        assert_true(ROOT.resolve() in source.parents or source == ROOT.resolve(), f"knowledge source escapes repo: {item['knowledge_id']}")
        assert_true(source.is_file(), f"knowledge source missing: {item['knowledge_id']} -> {item['source_ref']}")
        assert_true(item["tags"], f"knowledge entry must have tags: {item['knowledge_id']}")

    requirements = load_yaml(REQUIREMENTS)
    required_closed_loop = set(requirements["common"]["closed_loop_v1_artifacts"])
    assert_true(required_closed_loop == {"material_manifest", "acceptance_evidence_matrix", "knowledge_harvest"}, "closed-loop V1 artifact set changed unexpectedly")
    for track, cfg in requirements["tracks"].items():
        extras = set(cfg["required_extra_artifacts"])
        assert_true(required_closed_loop <= extras, f"pilot track missing closed-loop artifacts: {track}")
    assert_true("hypothesis_registry" in requirements["tracks"]["debug"]["required_extra_artifacts"], "debug must keep hypothesis registry")

    material_fixture = ROOT / "tests" / "fixtures" / "material-manifest.valid.json"
    material_schema = EMB / "schemas" / "material-manifest.schema.json"
    schema = load_json(material_schema)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(load_json(material_fixture))

    matrix_template = (EMB / "templates" / "acceptance-evidence-matrix.md").read_text(encoding="utf-8")
    harvest_template = (EMB / "templates" / "knowledge-harvest.md").read_text(encoding="utf-8")
    for token in ["Acceptance Criterion", "Verification Layer", "Evidence Ref", "PASS|FAIL|BLOCKED|NOT_RUN"]:
        assert_true(token in matrix_template, f"acceptance-evidence template missing token: {token}")
    for token in ["NO_KNOWLEDGE_DELTA", "KNOWLEDGE_CANDIDATE", "Evidence Ref"]:
        assert_true(token in harvest_template, f"knowledge-harvest template missing token: {token}")

    matrix_fixture = (ROOT / "tests" / "fixtures" / "acceptance-evidence-matrix.valid.md").read_text(encoding="utf-8")
    harvest_fixture = (ROOT / "tests" / "fixtures" / "knowledge-harvest.valid.md").read_text(encoding="utf-8")
    assert_true("CI-PILOT-001" in matrix_fixture and "EMB-001" in matrix_fixture, "matrix fixture identity mismatch")
    assert_true(re.search(r"\|\s*PASS\s*\|", matrix_fixture) is not None, "matrix fixture must demonstrate evidence-mapped PASS")
    assert_true("CI-PILOT-001" in harvest_fixture and "NO_KNOWLEDGE_DELTA" in harvest_fixture, "knowledge harvest fixture invalid")

    for path in [SCAFFOLD, KNOWLEDGE_CLI, QUICKSTART]:
        assert_true(path.is_file(), f"closed-loop operational helper missing: {path.relative_to(ROOT)}")
    scaffold_text = SCAFFOLD.read_text(encoding="utf-8")
    for token in ["missing_critical", '"BLOCKED"', "acceptance-evidence-matrix.md", "knowledge-harvest.md", "hypothesis-registry.json"]:
        assert_true(token in scaffold_text, f"scaffold helper missing fail-safe behavior: {token}")
    knowledge_text = KNOWLEDGE_CLI.read_text(encoding="utf-8")
    for token in ["Candidate list only", "source ACL/version/provenance", "missing_git_sources", "query"]:
        assert_true(token in knowledge_text, f"knowledge helper missing governance behavior: {token}")
    quickstart = QUICKSTART.read_text(encoding="utf-8")
    for token in ["embedded_pilot_scaffold.py", "embedded_knowledge.py verify", "exact immutable base commit SHA", "NO_KNOWLEDGE_DELTA"]:
        assert_true(token in quickstart, f"closed-loop quickstart missing token: {token}")

    print(f"embedded closed-loop V1 validation PASS: 7 must-haves, {len(entries)} registry entries, 3 closed-loop artifacts, operational helpers guarded")


if __name__ == "__main__":
    main()
