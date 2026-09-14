#!/usr/bin/env python3
"""Fail-closed validation for the Edge Foundation target responsibility architecture."""
from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOMAIN_ROOT = ROOT / "domains" / "edge-foundation"
LEGACY_ROOT = ROOT / "expert-groups" / "embedded-system"


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    domain_path = DOMAIN_ROOT / "domain.yaml"
    mapping_path = DOMAIN_ROOT / "compatibility" / "embedded-1plus7-mapping.yaml"
    switch_policy_path = DOMAIN_ROOT / "canonical-switch-dry-run.yaml"
    legacy_path = LEGACY_ROOT / "expert-group.yaml"
    adr_path = ROOT / "docs" / "adr" / "ADR-004-edge-foundation-digital-responsibility-architecture.md"
    required_paths = [
        domain_path,
        mapping_path,
        switch_policy_path,
        DOMAIN_ROOT / "routing-shadow.yaml",
        ROOT / "scripts" / "evaluate_edge_foundation_shadow.py",
        ROOT / "scripts" / "evaluate_edge_foundation_pilot_shadow.py",
        ROOT / "scripts" / "evaluate_edge_foundation_phase3_readiness.py",
        ROOT / "scripts" / "generate_edge_foundation_phase3_review_package.py",
        ROOT / "scripts" / "generate_edge_foundation_canonical_switch_plan.py",
        ROOT / "scripts" / "validate_edge_foundation_canonical_switch_candidate.py",
        ROOT / "schemas" / "edge-foundation-shadow-receipt.v1.schema.json",
        ROOT / "schemas" / "edge-foundation-phase3-readiness.v1.schema.json",
        ROOT / "schemas" / "edge-foundation-phase3-review-package.v1.schema.json",
        ROOT / "schemas" / "edge-foundation-canonical-switch-plan.v1.schema.json",
        ROOT / "schemas" / "edge-foundation-canonical-switch-change-manifest.v1.schema.json",
        LEGACY_ROOT / "pilot" / "pilot-plan.yaml",
        legacy_path,
        adr_path,
    ]
    for path in required_paths:
        require(path.is_file(), f"missing required edge-foundation asset: {path.relative_to(ROOT)}")

    domain = load_yaml(domain_path)
    mapping = load_yaml(mapping_path)
    policy = load_yaml(switch_policy_path)
    legacy = load_yaml(legacy_path)

    require(domain["id"] == "edge-foundation", "edge-foundation domain id drift")
    require(domain["architecture_model"] == "provider-neutral", "edge-foundation must remain provider-neutral")
    require(domain["responsibility_model"] == "contract-first", "responsibility model must remain contract-first")
    require(domain["runtime_topology"] == "not_frozen", "runtime topology must not be frozen")
    require("legacy_compatibility" not in domain, "deprecated duplicated legacy_compatibility block reintroduced")

    orchestration = domain["orchestration"]
    require(orchestration["provider_binding"] == "not_frozen", "orchestration provider must not be frozen")
    require(orchestration["implementation_binding"] == "not_frozen", "orchestration implementation must not be frozen")
    forbidden = set(orchestration["forbidden_assumptions"])
    require({"workbuddy-is-required", "one-expert-equals-one-agent", "capability-equals-agent"}.issubset(forbidden), "provider/runtime decoupling invariant drift")

    coordination = domain["coordination_role"]
    require(coordination["type"] == "role", "edge coordination must be a Role")
    require(coordination["is_domain_expert"] is False, "edge coordination must not become a fourth Expert")
    require(coordination["runtime_binding"] == "not_frozen", "edge coordination runtime must not be frozen")

    expert_ids = [item["id"] for item in domain["experts"]]
    expected_experts = ["structure-expert", "hardware-expert", "embedded-system-expert"]
    require(expert_ids == expected_experts, f"expected baseline Domain Experts {expected_experts}, got {expert_ids}")
    embedded = next(item for item in domain["experts"] if item["id"] == "embedded-system-expert")
    expected_capabilities = {
        "embedded.architecture",
        "embedded.linux-bsp",
        "embedded.mcu-rtos",
        "embedded.driver-component",
        "embedded.debug-reliability",
    }
    require(set(embedded.get("capabilities", [])) == expected_capabilities, "embedded capability baseline drift")
    require(domain["capability_policy"]["capability_is_agent"] is False, "Capability must not become Agent identity")
    require(domain["capability_policy"]["expert_promotion_requires_adr"] is True, "Capability -> Expert promotion must require ADR")

    execution = domain["execution"]
    assurance = domain["assurance"]
    require(execution["runtime_binding"] == "not_frozen", "execution runtime must remain replaceable")
    require(execution["responsibility_separation_required"] is True, "execution separation must remain required")
    require(assurance["independent_from_execution"] is True, "Assurance must remain independent from execution")
    require(assurance["responsibilities"]["verification"]["self_approval_by_implementation"] is False, "implementation must not self-approve Verification")
    require(assurance["responsibilities"]["review"]["independent_from_domain_decision_and_execution"] is True, "Independent Review separation drift")
    require(assurance["responsibilities"]["evidence"]["source_of_truth_stays_at_source"] is True, "Source of Truth must stay at source")

    require(domain["workflow_semantics"]["frozen_high_level_modes"] == ["single_domain", "multi_domain", "diagnostic", "review"], "high-level workflow semantics drift")
    require(domain["workflow_semantics"]["concrete_workflows_not_frozen"] is True, "concrete workflows must remain evolvable")
    require(domain["cross_domain_collaboration"]["model"] == "claim-evidence-driven", "cross-domain collaboration must stay evidence-driven")
    require(domain["knowledge"]["source_of_truth_policy"] == "stays_at_source", "knowledge authority drift")

    migration = domain["migration"]
    expected_migration_keys = {
        "legacy_surface",
        "identity_mapping",
        "shadow_routing",
        "readiness_evaluator",
        "switch_policy",
        "canonical_routing_switched",
        "automatic_canonical_switch_forbidden",
        "phase4_deprecation_separate",
        "phase5_removal_separate",
        "real_pilot_evidence_required",
        "synthetic_pilot_counts_for_promotion",
    }
    require(set(migration) == expected_migration_keys, f"migration contract must stay minimal; got keys={sorted(migration)}")
    require(migration["legacy_surface"] == "../../expert-groups/embedded-system/expert-group.yaml", "legacy surface pointer drift")
    require(migration["identity_mapping"] == "compatibility/embedded-1plus7-mapping.yaml", "identity mapping pointer drift")
    require(migration["shadow_routing"] == "routing-shadow.yaml", "shadow routing pointer drift")
    require(migration["readiness_evaluator"] == "../../scripts/evaluate_edge_foundation_phase3_readiness.py", "readiness evaluator pointer drift")
    require(migration["switch_policy"] == "canonical-switch-dry-run.yaml", "switch policy pointer drift")
    require(migration["canonical_routing_switched"] is False, "canonical routing switched before evidence/review")
    require(migration["automatic_canonical_switch_forbidden"] is True, "automatic canonical switch must remain forbidden")
    require(migration["phase4_deprecation_separate"] is True and migration["phase5_removal_separate"] is True, "deprecation/removal must stay separate")
    require(migration["real_pilot_evidence_required"] is True, "phase-3 must require real Pilot evidence")
    require(migration["synthetic_pilot_counts_for_promotion"] is False, "synthetic Pilot must never promote phase-3")

    # The identity bridge is static mapping only. Mutable phase/readiness state must never be copied here.
    forbidden_mapping_keys = {"status", "migration_mode", "shadow_routing", "phases", "migration_phase", "canonical_routing_switched"}
    require(not (set(mapping) & forbidden_mapping_keys), f"mutable migration state reintroduced into identity mapping: {sorted(set(mapping) & forbidden_mapping_keys)}")
    legacy_ids = {legacy["team_lead"]["id"]}
    legacy_ids.update(item["id"] for item in legacy["experts"])
    mapped = mapping["legacy_identities"]
    mapped_ids = [item["legacy_id"] for item in mapped]
    require(len(legacy_ids) == 8 and len(mapped_ids) == 8, "legacy bridge must remain exactly 8/8 during compatibility period")
    require(set(mapped_ids) == legacy_ids and len(mapped_ids) == len(set(mapped_ids)), "legacy identity mapping mismatch/duplicate")
    allowed_target_kinds = {"role", "capability-routing", "capability", "assurance", "method-set", "criteria-set"}
    for item in mapped:
        require(item.get("target_bindings"), f"legacy identity has no target binding: {item['legacy_id']}")
        require(item.get("removal_gate"), f"legacy identity missing explicit removal gate: {item['legacy_id']}")
        for binding in item["target_bindings"]:
            require(binding["kind"] in allowed_target_kinds, f"unknown target binding kind: {binding['kind']}")
    invariants = set(mapping["migration_invariants"])
    for invariant in [
        "no-verification-self-approval-regression",
        "no-review-independence-regression",
        "no-provider-binding-regression",
        "source-of-truth-stays-at-source",
        "shadow-routing-does-not-change-execution",
    ]:
        require(invariant in invariants, f"missing migration invariant: {invariant}")

    lifecycle = legacy["semantic_lifecycle"]
    require(lifecycle["status"] == "legacy-compatibility-surface", "legacy surface lifecycle drift")
    require(lifecycle["target_domain"] == "../../domains/edge-foundation/domain.yaml", "legacy target pointer drift")
    require(lifecycle["compatibility_mapping"] == "../../domains/edge-foundation/compatibility/embedded-1plus7-mapping.yaml", "legacy mapping pointer drift")
    require(lifecycle["canonical_routing_switched"] is False, "legacy surface cannot be retired before canonical switch")
    require(lifecycle["no_new_legacy_expert_roles"] is True and lifecycle["direct_removal_forbidden"] is True, "legacy bridge safety drift")
    for deprecated in ["migration_phase", "shadow_routing", "legacy_machine_contract_preserved", "canonical_target_responsibility_model"]:
        require(deprecated not in lifecycle, f"duplicated lifecycle field reintroduced: {deprecated}")
    require("current_status" not in legacy["cross_team"]["edge_foundation_team"], "duplicated mutable cross-team status reintroduced")

    require(policy["canonical_routing_switched"] is False, "switch policy must remain unswitched")
    require(policy["automatic_apply_allowed"] is False, "switch policy must remain non-applying")
    require(policy["allowed_change_classes"] == ["canonical-routing-authority", "routing-selector-entrypoint"], "phase-3 change classes are too broad")
    require(set(policy["allowed_paths"]) == {"canonical-routing-authority", "routing-selector-entrypoint"}, "phase-3 path allowlist drift")
    require("compatibility-mapping-rewrite" in policy["forbidden_change_classes"], "phase-3 must forbid compatibility mapping rewrites")
    require(policy["required_followup_phases"] == ["phase-4-deprecation", "phase-5-removal"], "phase-4/5 follow-up contract drift")

    adr_text = adr_path.read_text(encoding="utf-8")
    for marker in [
        "领域（Domain）",
        "能力域（Capability）",
        "编排平面（Orchestration Plane）",
        "可信保障平面（Assurance Plane）",
        "运行时（Runtime）",
        "|Contract|契约|",
        "|Progressive Disclosure|渐进式披露 / 按需加载|",
    ]:
        require(marker in adr_text, f"ADR-004 missing bilingual terminology marker: {marker}")

    print(
        "edge-foundation architecture validation PASS: "
        f"3 Domain Experts, {len(expected_capabilities)} embedded core Capabilities, 8/8 static legacy mappings, "
        "single minimal migration contract, phase-3 compatibility mapping immutable, independent Assurance"
    )


if __name__ == "__main__":
    main()
