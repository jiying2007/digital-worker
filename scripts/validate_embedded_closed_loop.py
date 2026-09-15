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
TRUST = ROOT / "docs" / "strategy" / "r0-trust-closure.md"
REGISTRY = EMB / "knowledge" / "registry.yaml"
REQUIREMENTS = EMB / "pilot" / "artifact-requirements.yaml"
QUICKSTART = ROOT / "docs" / "runbooks" / "embedded-closed-loop-quickstart.md"
SCAFFOLD = ROOT / "scripts" / "embedded_pilot_scaffold.py"
KNOWLEDGE_CLI = ROOT / "scripts" / "embedded_knowledge.py"
GOVERNANCE = ROOT / ".github" / "repository-governance-contract.json"
GOVERNANCE_AUDIT = ROOT / "scripts" / "verify_repository_governance.py"


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
    for marker in [
        "ADR-004",
        "Edge Coordination",
        "Embedded System Expert",
        "Capability",
        "Assurance",
        "Domain → Expert → Capability → Skill",
        "compatibility execution surface",
    ]:
        assert_true(marker in strategy, f"closed-loop strategy missing target responsibility marker: {marker}")
    for stale in [
        "1+7",
        "Team Lead + Architecture Expert",
        "第 8 个 Expert",
        "embedded-system-team-lead",
        "embedded-architecture-expert",
        "linux-bsp-expert",
        "mcu-rtos-expert",
        "driver-component-expert",
        "debug-reliability-expert",
        "verification-expert",
        "embedded-review-governor",
    ]:
        assert_true(stale not in strategy, f"legacy organization semantic returned to active closed-loop strategy: {stale}")

    trust = TRUST.read_text(encoding="utf-8")
    for token in ["R0 Trust Closure", "full 40-hex Git SHA", "completed/cancelled", "contract path/version", "canonical JSON SHA-256", "server-side enforcement"]:
        assert_true(token in trust, f"R0 trust gate missing marker: {token}")

    governance = load_json(GOVERNANCE)
    stage_policy = governance.get("stage_policy", {})
    assert_true(governance.get("schema_version") == 2, "repository governance contract must use stage-aware schema v2")
    assert_true(governance.get("current_stage") == "iterative-development", "current repository stage must remain iterative-development until explicitly promoted")
    assert_true(stage_policy.get("server_side_protection_required") is False, "main protection must not block the current iterative-development stage")
    assert_true(stage_policy.get("blocks_real_pilot_acceptance") is False, "repository protection must not block real Pilot acceptance in current stage")
    assert_true(stage_policy.get("repository_local_ci_still_required") is True, "repo-local CI remains required while main protection is deferred")
    assert_true(stage_policy.get("strict_enforcement_stage") == "productionization", "strict repository governance must remain a productionization gate")
    governance_audit = GOVERNANCE_AUDIT.read_text(encoding="utf-8")
    for token in ["--strict", "DEFERRED_CURRENT_STAGE", "BLOCKED_SERVER_GOVERNANCE"]:
        assert_true(token in governance_audit, f"stage-aware governance audit missing marker: {token}")

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
        if "core-reference" in item["tags"]:
            for stale_path in ["/01-数字组织与岗位/", "嵌入式架构领域指南.md", "Linux BSP领域指南.md", "MCU RTOS领域指南.md", "驱动与组件领域指南.md", "调试与可靠性领域指南.md", "验证领域指南.md", "独立审查领域指南.md"]:
                assert_true(stale_path not in item["source_ref"], f"core-reference registry entry points at retired source: {item['knowledge_id']} -> {item['source_ref']}")

    by_id = {item["knowledge_id"]: item for item in entries}
    assert_true(by_id["EKR-003"]["source_ref"] == "docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md", "registry must index ADR-004 as embedded target architecture")
    assert_true(by_id["EKR-005"]["source_ref"] == "domains/edge-foundation/domain.yaml", "registry target machine entry must resolve to Edge Foundation domain contract")
    assert_true(by_id["EKR-009"]["source_ref"] == "domains/edge-foundation/gate-policy.yaml", "registry Gate authority must use target ownership contract")
    assert_true(by_id["EKR-012"]["source_ref"] == "domains/edge-foundation/skills.yaml", "registry Skill authority must use target ownership contract")
    assert_true(by_id["EKR-018"]["source_ref"] == "domains/edge-foundation/evaluation/golden-cases.yaml", "registry Golden authority must use target dataset")

    requirements = load_yaml(REQUIREMENTS)
    required_closed_loop = set(requirements["common"]["closed_loop_v1_artifacts"])
    assert_true(required_closed_loop == {"material_manifest", "acceptance_evidence_matrix", "knowledge_harvest"}, "closed-loop V1 artifact set changed unexpectedly")
    for key in ["real_run_requires_full_40_hex_base_commit", "completed_run_is_terminal", "completed_bundle_hashes_revalidated", "superseding_run_required_for_completed_correction"]:
        assert_true(requirements["common"].get(key) is True, f"R0 pilot trust requirement disabled: {key}")
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

    for path in [SCAFFOLD, KNOWLEDGE_CLI, QUICKSTART, GOVERNANCE, GOVERNANCE_AUDIT]:
        assert_true(path.is_file(), f"closed-loop operational helper missing: {path.relative_to(ROOT)}")
    scaffold_text = SCAFFOLD.read_text(encoding="utf-8")
    for token in ["missing_critical", '"BLOCKED"', "acceptance-evidence-matrix.md", "knowledge-harvest.md", "hypothesis-registry.json"]:
        assert_true(token in scaffold_text, f"scaffold helper missing fail-safe behavior: {token}")
    knowledge_text = KNOWLEDGE_CLI.read_text(encoding="utf-8")
    for token in ["bootstrap-local-catalog", "Candidate list only", "BLOCKED_PROVIDER_IDENTITY_MISMATCH", "contract_canonical_sha256"]:
        assert_true(token in knowledge_text, f"knowledge helper missing R0 governance behavior: {token}")
    quickstart = QUICKSTART.read_text(encoding="utf-8")
    for token in ["embedded_pilot_scaffold.py", "embedded_knowledge.py verify", "full 40-hex immutable base commit SHA", "NO_KNOWLEDGE_DELTA", "Do not run `bundle` after completion", "Main branch protection is intentionally not a current-stage acceptance gate", "verify_repository_governance.py --strict"]:
        assert_true(token in quickstart, f"closed-loop quickstart missing R0 token: {token}")

    print(
        f"embedded closed-loop V1 validation PASS: target responsibility model ratcheted, 7 must-haves, "
        f"iterative-stage R0 trust baseline, {len(entries)} registry entries, 3 closed-loop artifacts"
    )


if __name__ == "__main__":
    main()
