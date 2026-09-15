#!/usr/bin/env python3
"""Validate terminal Edge Foundation semantics and canonical reference integrity."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
DOMAIN_PATH = EDGE / "domain.yaml"

ACTIVE_TEXT_ROOTS = [
    ROOT / "README.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "runbooks",
    ROOT / "docs" / "strategy",
    ROOT / "嵌入式系统专家团-核心参考",
    EDGE,
]
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".txt", ".toml"}

RETIRED_PATHS = [
    ROOT / "expert-groups" / "embedded-system",
    EDGE / "compatibility",
    EDGE / "routing-shadow.yaml",
    ROOT / "docs" / "runbooks" / "edge-foundation-canonical-switch.md",
    ROOT / "scripts" / "evaluate_edge_foundation_phase3_readiness.py",
    ROOT / "scripts" / "generate_edge_foundation_canonical_switch_plan.py",
]

FORBIDDEN_ACTIVE_SEMANTICS = [
    "canonical_routing_switched=false",
    "canonical_routing_switched = false",
    "legacy-embedded-1plus7",
    "phase3-readiness",
    "edge-foundation-phase3-review-package",
    "generate_edge_foundation_canonical_switch_plan.py",
    "evaluate_edge_foundation_phase3_readiness.py",
    "compatibility/embedded-1plus7-mapping.yaml",
    "expert-groups" + "/embedded-system/",
]

EXPECTED_PRODUCT_READINESS_EVALUATOR = "../../scripts/evaluate_edge_foundation_product_readiness.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_domain() -> dict:
    return yaml.safe_load(DOMAIN_PATH.read_text(encoding="utf-8"))


def resolve_edge_ref(value: str) -> Path:
    return (EDGE / value).resolve()


def require_ref(label: str, value: str) -> None:
    target = resolve_edge_ref(value)
    require(target.exists(), f"canonical reference is missing: {label} -> {value} ({target})")


def validate_contract_references(domain: dict) -> None:
    require(domain["status"] == "canonical-v1", "Edge Foundation status must remain canonical-v1")
    require(domain["execution"]["authority"] == "canonical", "execution authority must remain canonical")
    require(domain["execution"]["legacy_compatibility_removed"] is True, "legacy compatibility must remain removed")
    require(domain["execution"]["zero_live_legacy_reference_required"] is True, "zero-live legacy ratchet must remain required")
    require(domain["target_assets"]["execution_surface"] == "canonical", "target execution surface must remain canonical")
    require(domain["target_assets"]["legacy_compatibility_removed"] is True, "target assets must remain legacy-free")
    require(domain["product_readiness"]["controls_routing_authority"] is False, "product readiness must not control routing authority")
    require(domain["product_readiness"]["requires_real_pilot_evidence"] is True, "product readiness must require real Pilot evidence")
    require(domain["product_readiness"]["synthetic_pilot_counts"] is False, "synthetic Pilot evidence must remain excluded")
    require(
        domain["product_readiness"]["evaluator"] == EXPECTED_PRODUCT_READINESS_EVALUATOR,
        "product readiness evaluator drifted from canonical target-only evaluator",
    )

    refs = {
        "canonical_adr": domain["canonical_adr"],
        "source_material": domain["source_material"],
        "coordination_role.contract": domain["coordination_role"]["contract"],
        "embedded-system-expert.contract": next(
            item["contract"] for item in domain["experts"] if item["id"] == "embedded-system-expert"
        ),
        "execution.routing": domain["execution"]["routing"],
        "execution.runtime_policy": domain["execution"]["runtime_policy"],
        "execution.workflow": domain["execution"]["workflow"],
        "execution.action_policy": domain["execution"]["action_policy"],
        "execution.material_policy": domain["execution"]["material_policy"],
        "assurance.verification.contract": domain["assurance"]["responsibilities"]["verification"]["contract"],
        "assurance.review.contract": domain["assurance"]["responsibilities"]["review"]["contract"],
        "target_assets.skill_registry": domain["target_assets"]["skill_registry"],
        "target_assets.gate_policy": domain["target_assets"]["gate_policy"],
        "target_assets.evaluation_cases": domain["target_assets"]["evaluation_cases"],
        "target_assets.knowledge_registry": domain["target_assets"]["knowledge_registry"],
        "target_assets.pilot_runtime": domain["target_assets"]["pilot_runtime"],
        "target_assets.pilot_assets": domain["target_assets"]["pilot_assets"],
        "target_assets.schema_root": domain["target_assets"]["schema_root"],
        "target_assets.template_root": domain["target_assets"]["template_root"],
        "knowledge.local_registry": domain["knowledge"]["local_registry"],
        "product_readiness.evaluator": domain["product_readiness"]["evaluator"],
        "product_readiness.pilot_plan": domain["product_readiness"]["pilot_plan"],
    }
    for label, value in refs.items():
        require_ref(label, value)


def iter_active_text_files(root: Path):
    if root.is_file():
        yield root
        return
    if not root.exists():
        return
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def validate_retirement_is_physical() -> None:
    for path in RETIRED_PATHS:
        require(not path.exists(), f"retired migration/legacy surface reappeared: {path.relative_to(ROOT)}")


def validate_active_semantics() -> None:
    violations: list[str] = []
    for root in ACTIVE_TEXT_ROOTS:
        for path in iter_active_text_files(root):
            text = path.read_text(encoding="utf-8", errors="replace")
            for token in FORBIDDEN_ACTIVE_SEMANTICS:
                if token in text:
                    violations.append(f"{path.relative_to(ROOT)} contains retired semantic token: {token}")
    if violations:
        raise AssertionError("retired migration semantics detected in active surfaces:\n- " + "\n- ".join(sorted(violations)))


def main() -> None:
    domain = load_domain()
    validate_contract_references(domain)
    validate_retirement_is_physical()
    validate_active_semantics()
    print("terminal Edge Foundation consistency PASS")


if __name__ == "__main__":
    main()
