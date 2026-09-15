#!/usr/bin/env python3
"""Fail-closed validation for canonical Embedded Domain Closed Loop V1 assets."""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
STRATEGY = ROOT / "docs" / "strategy" / "embedded-domain-closed-loop-v1.md"
TRUST = ROOT / "docs" / "strategy" / "r0-trust-closure.md"
REGISTRY = EDGE / "knowledge" / "registry.yaml"
REQUIREMENTS = EDGE / "pilot" / "artifact-requirements.yaml"
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
    assert_true("current-stage-baseline" in strategy, "closed-loop strategy must remain current-stage-baseline")
    for marker in ["V1-1", "V1-2", "V1-3", "V1-4", "V1-5", "V1-6", "V1-7"]:
        assert_true(marker in strategy, f"closed-loop strategy missing {marker}")
    for marker in [
        "Enterprise Digital Thread 不是前置条件",
        "Edge Coordination",
        "Embedded System Expert",
        "Capability",
        "Assurance",
        "Canonical runtime 与 Product readiness 解耦",
        "Product readiness",
        "E2",
        "E3",
        "Production Ready",
    ]:
        assert_true(marker in strategy, f"closed-loop strategy missing canonical marker: {marker}")
    assert_true("Product readiness 正确保持 BLOCKED 1/3" in strategy, "strategy must preserve truthful current product-readiness state")
    assert_true("不会控制或回退 canonical routing" in strategy, "product readiness must stay decoupled from routing authority")

    retired_tokens = [
        "embedded-system-team-lead", "embedded-architecture-expert", "linux-bsp-expert", "mcu-rtos-expert",
        "driver-component-expert", "debug-reliability-expert", "verification-expert", "embedded-review-governor",
        "Compatibility execution surface", "routing" + "-shadow", "canonical_routing_switched" + "=false",
    ]
    for stale in retired_tokens:
        assert_true(stale not in strategy, f"retired migration/organization semantic returned to active strategy: {stale}")

    domain = load_yaml(EDGE / "domain.yaml")
    assert_true(domain["status"] == "canonical-v1", "closed-loop must bind canonical Edge Foundation domain")
    assert_true(domain["execution"]["authority"] == "canonical", "closed-loop execution authority must be canonical")
    assert_true(domain["execution"]["legacy_compatibility_removed"] is True, "retired compatibility must stay removed")
    assert_true(domain["product_readiness"]["controls_routing_authority"] is False, "product readiness must not control routing authority")

    trust = TRUST.read_text(encoding="utf-8")
    for token in ["R0 Trust Closure", "full 40-hex Git SHA", "completed/cancelled", "contract path/version", "canonical JSON SHA-256", "server-side enforcement"]:
        assert_true(token in trust, f"R0 trust gate missing marker: {token}")

    governance = load_json(GOVERNANCE)
    stage_policy = governance.get("stage_policy", {})
    assert_true(governance.get("schema_version") == 2, "repository governance contract must use stage-aware schema v2")
    assert_true(governance.get("current_stage") == "iterative-development", "repository stage must remain iterative-development until explicitly promoted")
    assert_true(stage_policy.get("server_side_protection_required") is False, "main protection must not block current iterative-development")
    assert_true(stage_policy.get("blocks_real_pilot_acceptance") is False, "repository protection must not block real Pilot acceptance")
    assert_true(stage_policy.get("repository_local_ci_still_required") is True, "repo-local CI remains required")
    assert_true(stage_policy.get("strict_enforcement_stage") == "productionization", "strict governance must remain a productionization gate")
    governance_audit = GOVERNANCE_AUDIT.read_text(encoding="utf-8")
    for token in ["--strict", "DEFERRED_CURRENT_STAGE", "BLOCKED_SERVER_GOVERNANCE"]:
        assert_true(token in governance_audit, f"stage-aware governance audit missing marker: {token}")

    registry = load_yaml(REGISTRY)
    assert_true(registry["status"] == "canonical-bootstrap", "knowledge registry must be canonical-bootstrap")
    assert_true(registry["source_of_truth_policy"] in {"stays-at-source", "stays_at_source"}, "knowledge registry must preserve source authority")
    assert_true(registry["provider_binding"] == "not_frozen", "knowledge provider must remain not_frozen")
    entries = registry["entries"]
    assert_true(50 <= len(entries) <= 100, f"V1 registry must keep a bounded 50-100 entry bootstrap, got {len(entries)}")

    ids = [item["knowledge_id"] for item in entries]
    assert_true(len(ids) == len(set(ids)), "duplicate knowledge IDs")
    assert_true(all(re.fullmatch(r"EKR-\d{3}", item_id) for item_id in ids), "knowledge IDs must use EKR-NNN")
    allowed_types = {"authority", "engineering", "operational", "ai_execution"}
    allowed_authority = {"canonical", "interpretive", "procedure"}
    defaults = registry["defaults"]
    assert_true(defaults["source_provider"] == "git", "bootstrap registry must use git sources")
    assert_true(defaults["version"] == "tracked-by-git", "bootstrap registry version must be tracked-by-git")

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
        assert_true(("expert-groups" + "/embedded-system") not in item["source_ref"], f"registry source points at retired execution tree: {item['knowledge_id']}")

    by_id = {item["knowledge_id"]: item for item in entries}
    expected_bindings = {
        "EKR-003": "docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md",
        "EKR-005": "domains/edge-foundation/domain.yaml",
        "EKR-007": "domains/edge-foundation/runtime/workflow.yaml",
        "EKR-008": "domains/edge-foundation/runtime/task-modes.yaml",
        "EKR-009": "domains/edge-foundation/gate-policy.yaml",
        "EKR-012": "domains/edge-foundation/skills.yaml",
        "EKR-015": "domains/edge-foundation/pilot/pilot-plan.yaml",
        "EKR-018": "domains/edge-foundation/evaluation/golden-cases.yaml",
        "EKR-035": "domains/edge-foundation/coordination.yaml",
        "EKR-041": "domains/edge-foundation/assurance/verification.yaml",
        "EKR-042": "domains/edge-foundation/assurance/review.yaml",
    }
    for kid, ref in expected_bindings.items():
        assert_true(by_id[kid]["source_ref"] == ref, f"canonical Registry binding drift: {kid}")

    requirements = load_yaml(REQUIREMENTS)
    required_closed_loop = set(requirements["common"]["closed_loop_v1_artifacts"])
    assert_true(required_closed_loop == {"material_manifest", "acceptance_evidence_matrix", "knowledge_harvest"}, "closed-loop artifact set changed unexpectedly")
    for key in ["real_run_requires_full_40_hex_base_commit", "completed_run_is_terminal", "completed_bundle_hashes_revalidated", "superseding_run_required_for_completed_correction"]:
        assert_true(requirements["common"].get(key) is True, f"R0 Pilot trust requirement disabled: {key}")
    for track, cfg in requirements["tracks"].items():
        extras = set(cfg["required_extra_artifacts"])
        assert_true(required_closed_loop <= extras, f"Pilot track missing closed-loop artifacts: {track}")
    assert_true("hypothesis_registry" in requirements["tracks"]["debug"]["required_extra_artifacts"], "Debug must keep Hypothesis Registry")

    material_fixture = ROOT / "tests" / "fixtures" / "material-manifest.valid.json"
    material_schema = EDGE / "schemas" / "material-manifest.schema.json"
    schema = load_json(material_schema)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(load_json(material_fixture))

    matrix_template = (EDGE / "templates" / "acceptance-evidence-matrix.md").read_text(encoding="utf-8")
    harvest_template = (EDGE / "templates" / "knowledge-harvest.md").read_text(encoding="utf-8")
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
        assert_true(token in knowledge_text, f"knowledge helper missing governance behavior: {token}")
    quickstart = QUICKSTART.read_text(encoding="utf-8")
    for token in [
        "edge_pilot_scaffold.py", "edge_knowledge.py verify", "full 40-hex immutable base commit SHA",
        "NO_KNOWLEDGE_DELTA", "completed/cancelled Run cannot be reopened or rebundled",
        "Product readiness does not control or revert canonical routing", "verify_repository_governance.py --strict",
    ]:
        assert_true(token in quickstart, f"closed-loop quickstart missing canonical token: {token}")

    print(
        f"embedded closed-loop V1 validation PASS: canonical responsibility/runtime, 7 must-haves, "
        f"iterative-stage R0 trust baseline, {len(entries)} registry entries, 3 closed-loop artifacts, product readiness decoupled"
    )


if __name__ == "__main__":
    main()
