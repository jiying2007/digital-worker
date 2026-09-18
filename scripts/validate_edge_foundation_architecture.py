#!/usr/bin/env python3
"""Validate the canonical Edge Foundation responsibility and execution architecture."""
from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
LEGACY_IDS = {
    "embedded-system-team-lead", "embedded-architecture-expert", "linux-bsp-expert",
    "mcu-rtos-expert", "driver-component-expert", "debug-reliability-expert",
    "verification-expert", "embedded-review-governor",
}


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    domain = load(EDGE / "domain.yaml")
    require(domain["status"] == "canonical-v1", "Edge Foundation must be canonical-v1")
    require(domain["architecture_model"] == "provider-neutral", "architecture must remain provider-neutral")
    require(domain["responsibility_model"] == "contract-first", "responsibility model drift")

    experts = {item["id"]: item for item in domain["experts"]}
    require(set(experts) == {"structure-expert", "hardware-expert", "embedded-system-expert"}, "Edge Foundation must have exactly three Domain Experts")
    embedded = experts["embedded-system-expert"]
    expected_caps = {"embedded.architecture", "embedded.linux-bsp", "embedded.mcu-rtos", "embedded.driver-component", "embedded.debug-reliability"}
    require(set(embedded["capabilities"]) == expected_caps, "Embedded Capability set drift")
    require(domain["coordination_role"]["id"] == "edge-coordination", "Edge Coordination Role drift")
    require(domain["coordination_role"]["is_domain_expert"] is False, "Edge Coordination must not become a Domain Expert")

    assurance = domain["assurance"]
    require(assurance["independent_from_execution"] is True, "Assurance must remain independent from execution")
    require({"verification", "review", "evidence", "evaluation"} <= set(assurance["responsibilities"]), "Assurance responsibility set drift")
    require(assurance["responsibilities"]["verification"]["self_approval_by_implementation"] is False, "implementation self-verification forbidden")
    require(assurance["responsibilities"]["review"]["independent_from_domain_decision_and_execution"] is True, "Independent Review boundary drift")

    execution = domain["execution"]
    require(execution["authority"] == "canonical", "target execution must be canonical")
    require(execution["routing"] == "routing.yaml", "canonical routing pointer drift")
    require(execution["runtime_policy"] == "runtime/task-modes.yaml", "runtime policy pointer drift")
    require(execution["legacy_compatibility_removed"] is True, "legacy compatibility removal must remain terminal")
    require(execution["zero_live_legacy_reference_required"] is True, "zero-live-reference ratchet disabled")

    assets = domain["target_assets"]
    require(assets["ownership_authority"] == "canonical" and assets["execution_surface"] == "canonical", "target assets must be canonical")
    require(assets["legacy_compatibility_removed"] is True, "target assets must not depend on legacy compatibility")
    for key in ["skill_registry", "gate_policy", "evaluation_cases", "skill_evaluation_plan", "knowledge_registry", "pilot_runtime", "pilot_assets", "schema_root", "template_root"]:
        require(assets.get(key), f"target asset pointer missing: {key}")

    readiness = domain["product_readiness"]
    require(readiness["requires_real_pilot_evidence"] is True, "real product Pilot evidence requirement disabled")
    require(readiness["synthetic_pilot_counts"] is False, "synthetic Pilot must not count")
    require(readiness["controls_routing_authority"] is False, "product readiness must not control routing authority")

    target_files = [
        EDGE / "domain.yaml", EDGE / "coordination.yaml", EDGE / "routing.yaml", EDGE / "gate-policy.yaml",
        EDGE / "skills.yaml", EDGE / "assurance/verification.yaml", EDGE / "assurance/review.yaml",
        EDGE / "evaluation/golden-cases.yaml", EDGE / "evaluation/skill-evaluation-plan.yaml",
        *sorted((EDGE / "experts/embedded-system/capabilities").glob("*.yaml")),
    ]
    for path in target_files:
        require(path.is_file(), f"target contract missing: {path.relative_to(ROOT)}")
        text = path.read_text(encoding="utf-8")
        leaked = sorted(item for item in LEGACY_IDS if item in text)
        require(not leaked, f"legacy Expert identity leaked into target contract {path.relative_to(ROOT)}: {leaked}")

    print("edge-foundation architecture validation PASS: canonical 3 Domain Experts / 5 Embedded Capabilities / target execution / independent Assurance / product readiness decoupled")


if __name__ == "__main__":
    main()
