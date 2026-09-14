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
    adr_path = ROOT / "docs" / "adr" / "ADR-004-edge-foundation-digital-responsibility-architecture.md"
    legacy_path = LEGACY_ROOT / "expert-group.yaml"

    for path in (domain_path, mapping_path, adr_path, legacy_path):
        require(path.is_file(), f"missing required edge-foundation architecture asset: {path.relative_to(ROOT)}")

    domain = load_yaml(domain_path)
    mapping = load_yaml(mapping_path)
    legacy = load_yaml(legacy_path)

    require(domain["id"] == "edge-foundation", "edge-foundation domain id drift")
    require(domain["architecture_model"] == "provider-neutral", "edge-foundation must remain provider-neutral")
    require(domain["responsibility_model"] == "contract-first", "responsibility model must remain contract-first")
    require(domain["runtime_topology"] == "not_frozen", "runtime topology must not be frozen")
    require(domain["canonical_adr"] == "../../docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md", "canonical ADR reference drift")

    orchestration = domain["orchestration"]
    require(orchestration["provider_binding"] == "not_frozen", "orchestration provider must not be frozen")
    require(orchestration["implementation_binding"] == "not_frozen", "orchestration implementation must not be frozen")
    forbidden = set(orchestration["forbidden_assumptions"])
    require("workbuddy-is-required" in forbidden, "architecture must explicitly forbid WorkBuddy lock-in")
    require("one-expert-equals-one-agent" in forbidden, "architecture must decouple Expert from Agent topology")
    require("capability-equals-agent" in forbidden, "architecture must decouple Capability from Agent topology")

    coordination = domain["coordination_role"]
    require(coordination["type"] == "role", "edge coordination must be modeled as a Role")
    require(coordination["is_domain_expert"] is False, "edge coordination must not become a fourth Domain Expert")
    require(coordination["runtime_binding"] == "not_frozen", "edge coordination runtime must not be frozen")

    experts = domain["experts"]
    expert_ids = [item["id"] for item in experts]
    expected_experts = ["structure-expert", "hardware-expert", "embedded-system-expert"]
    require(expert_ids == expected_experts, f"expected three baseline Domain Experts {expected_experts}, got {expert_ids}")
    require(len(expert_ids) == len(set(expert_ids)), "duplicate Domain Expert id")
    require(coordination["id"] not in expert_ids, "Coordinator Role must remain separate from Domain Experts")

    embedded = next(item for item in experts if item["id"] == "embedded-system-expert")
    embedded_capabilities = set(embedded.get("capabilities", []))
    expected_capabilities = {
        "embedded.architecture",
        "embedded.linux-bsp",
        "embedded.mcu-rtos",
        "embedded.driver-component",
        "embedded.debug-reliability",
    }
    require(embedded_capabilities == expected_capabilities, f"embedded core capability baseline drift: {sorted(embedded_capabilities)}")

    capability_policy = domain["capability_policy"]
    require(capability_policy["capability_is_agent"] is False, "Capability must not be defined as an Agent")
    require(capability_policy["default_growth"] == "capability_or_skill", "new professional depth must default to Capability/Skill")
    require(capability_policy["expert_promotion_requires_adr"] is True, "Capability -> Expert promotion must require ADR")
    require(len(capability_policy["expert_promotion_criteria"]) >= 6, "Expert promotion gate is underspecified")

    execution = domain["execution"]
    assurance = domain["assurance"]
    require(execution["runtime_binding"] == "not_frozen", "execution runtime must remain replaceable")
    require(execution["responsibility_separation_required"] is True, "execution responsibility separation must remain required")
    require(assurance["independent_from_execution"] is True, "Assurance must remain independent from execution")
    require(assurance["responsibilities"]["verification"]["self_approval_by_implementation"] is False, "implementation must not self-approve Verification")
    require(
        assurance["responsibilities"]["review"]["independent_from_domain_decision_and_execution"] is True,
        "Independent Review must remain separate from domain decision and execution",
    )
    require(assurance["responsibilities"]["evidence"]["source_of_truth_stays_at_source"] is True, "Source of Truth must stay at source")

    high_level_modes = domain["workflow_semantics"]["frozen_high_level_modes"]
    require(high_level_modes == ["single_domain", "multi_domain", "diagnostic", "review"], "high-level workflow semantics drift")
    require(domain["workflow_semantics"]["concrete_workflows_not_frozen"] is True, "concrete workflow count must remain evolvable")
    require(domain["workflow_semantics"]["minimal_required_path"] is True, "workflow must use minimum necessary path")

    require(domain["cross_domain_collaboration"]["model"] == "claim-evidence-driven", "cross-domain collaboration must be claim/evidence driven")
    required_objects = {"claim", "hypothesis", "evidence", "finding", "decision", "verification", "closure"}
    require(set(domain["cross_domain_collaboration"]["shared_objects"]) == required_objects, "cross-domain shared-object contract drift")
    require(domain["knowledge"]["source_of_truth_policy"] == "stays_at_source", "knowledge authority policy drift")
    require(domain["knowledge"]["knowledge_provider_binding"] == "not_frozen", "knowledge provider must remain replaceable")

    legacy_ids = {legacy["team_lead"]["id"]}
    legacy_ids.update(item["id"] for item in legacy["experts"])
    require(len(legacy_ids) == 8, f"legacy compatibility source expected 8 identities, got {len(legacy_ids)}")

    mapped = mapping["legacy_identities"]
    mapped_ids = [item["legacy_id"] for item in mapped]
    require(len(mapped_ids) == 8, f"compatibility mapping must cover exactly 8 legacy identities, got {len(mapped_ids)}")
    require(set(mapped_ids) == legacy_ids, f"legacy compatibility mapping mismatch: expected {sorted(legacy_ids)}, got {sorted(mapped_ids)}")
    require(len(mapped_ids) == len(set(mapped_ids)), "duplicate legacy identity mapping")

    allowed_target_kinds = {"role", "capability-routing", "capability", "assurance", "method-set", "criteria-set"}
    for item in mapped:
        bindings = item.get("target_bindings", [])
        require(bindings, f"legacy identity has no target binding: {item['legacy_id']}")
        for binding in bindings:
            require(binding["kind"] in allowed_target_kinds, f"unknown target binding kind: {item['legacy_id']} -> {binding['kind']}")
        if item.get("owner_expert"):
            require(item["owner_expert"] == "embedded-system-expert", f"legacy embedded capability must be owned by embedded-system-expert: {item['legacy_id']}")

    verification_mapping = next(item for item in mapped if item["legacy_id"] == "verification-expert")
    review_mapping = next(item for item in mapped if item["legacy_id"] == "embedded-review-governor")
    require({b["kind"] for b in verification_mapping["target_bindings"]} >= {"assurance", "method-set"}, "Verification migration must preserve assurance responsibility and methods")
    require({b["kind"] for b in review_mapping["target_bindings"]} >= {"assurance", "criteria-set"}, "Review migration must preserve assurance responsibility and review criteria")

    invariants = set(mapping["migration_invariants"])
    require("no-verification-self-approval-regression" in invariants, "missing Verification independence migration invariant")
    require("no-review-independence-regression" in invariants, "missing Review independence migration invariant")
    require("no-provider-binding-regression" in invariants, "missing provider-neutral migration invariant")
    require("source-of-truth-stays-at-source" in invariants, "missing knowledge authority migration invariant")

    compatibility = domain["legacy_compatibility"]
    require(compatibility["mode"] == "shadow", "first migration stage must remain shadow mode")
    require(compatibility["legacy_machine_contract_preserved"] is True, "legacy machine contract must remain preserved during phase 1")
    require(compatibility["direct_big_bang_removal_forbidden"] is True, "big-bang removal must remain forbidden")

    adr_text = adr_path.read_text(encoding="utf-8")
    required_terms = [
        "领域（Domain）",
        "能力域（Capability）",
        "编排平面（Orchestration Plane）",
        "可信保障平面（Assurance Plane）",
        "运行时（Runtime）",
        "契约（Contract）",
        "渐进式披露 / 按需加载",
    ]
    for term in required_terms:
        require(term in adr_text, f"ADR-004 missing Chinese/English terminology pair: {term}")

    print(
        "edge-foundation architecture validation PASS: "
        f"{len(expert_ids)} Domain Experts, {len(embedded_capabilities)} embedded core Capabilities, "
        f"{len(mapped_ids)}/8 legacy identities mapped, provider-neutral orchestration/runtime, independent Assurance"
    )


if __name__ == "__main__":
    main()
