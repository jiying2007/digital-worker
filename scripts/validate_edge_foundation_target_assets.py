#!/usr/bin/env python3
"""Validate canonical Edge Foundation target assets."""
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
    skills = load(EDGE / "skills.yaml")
    gates = load(EDGE / "gate-policy.yaml")
    cases = load(EDGE / "evaluation/golden-cases.yaml")
    skill_evaluation = load(EDGE / "evaluation/skill-evaluation-plan.yaml")
    routing = load(EDGE / "routing.yaml")
    runtime = load(EDGE / "runtime/task-modes.yaml")

    require(domain["execution"]["authority"] == "canonical", "execution authority must be canonical")
    require(domain["execution"]["legacy_compatibility_removed"] is True, "legacy compatibility must be removed")
    require(skills["ownership_authority"] == "canonical" and skills["execution_surface"] == "target", "Skill registry must be canonical target")
    require(gates["ownership_authority"] == "canonical" and gates["execution_surface"] == "canonical", "Gate policy must be canonical target")
    require(cases["status"] == "canonical" and cases["canonical_routing"] is True, "Golden Cases must be canonical")
    require(skill_evaluation["status"] == "canonical-plan", "Skill evaluation plan must be canonical-plan")
    require(set(skill_evaluation["skills"]) == {item["id"] for item in skills["skills"]}, "Skill evaluation plan/registry drift")
    require(routing["canonical_routing"] is True and routing["status"] == "canonical", "routing must be canonical")

    expert_ids = {item["id"] for item in domain["experts"]}
    require(expert_ids == {"structure-expert", "hardware-expert", "embedded-system-expert"}, "Domain Expert set drift")
    embedded = next(item for item in domain["experts"] if item["id"] == "embedded-system-expert")
    capability_ids = set(embedded["capabilities"])
    assurance_ids = set(domain["assurance"]["responsibilities"])
    role_ids = {domain["coordination_role"]["id"]}

    for path in [EDGE / "skills.yaml", EDGE / "gate-policy.yaml", EDGE / "evaluation/golden-cases.yaml", EDGE / "evaluation/skill-evaluation-plan.yaml", EDGE / "routing.yaml"]:
        text = path.read_text(encoding="utf-8")
        leaked = sorted(identity for identity in LEGACY_IDS if identity in text)
        require(not leaked, f"legacy identity leaked into target asset {path.relative_to(ROOT)}: {leaked}")

    skill_by_id = {item["id"]: item for item in skills["skills"]}
    require(len(skill_by_id) == 23 == len(skills["skills"]), "expected exactly 23 registered Skills")
    for skill_id, item in skill_by_id.items():
        kind, owner = item["owner_kind"], item["owner_id"]
        if kind == "role":
            require(owner in role_ids, f"unknown Role owner: {skill_id} -> {owner}")
        elif kind == "capability":
            require(owner in capability_ids, f"unknown Capability owner: {skill_id} -> {owner}")
        elif kind == "assurance":
            require(owner in assurance_ids, f"unknown Assurance owner: {skill_id} -> {owner}")
        else:
            raise AssertionError(f"unsupported Skill owner kind: {skill_id} -> {kind}")
        resolved = (EDGE / item["path"]).resolve()
        require(resolved.is_file() and EDGE.resolve() in resolved.parents, f"Skill path is not target-local: {skill_id}")
        skill_text = resolved.read_text(encoding="utf-8")
        required_sections = [
            "## Purpose",
            "## Use When",
            "## Do Not Use For",
            "## Required Inputs",
            "## Optional Inputs",
            "## Method",
            "## Outputs",
            "## Evidence Rules",
            "## BLOCK Conditions",
            "## Verification / Review Handoff",
            "## Evaluation",
            "## Known Limits / Change Notes",
        ]
        for heading in required_sections:
            require(heading in skill_text, f"Skill contract incomplete: {skill_id} missing {heading}")
        for frontmatter_marker in [
            f"id: {skill_id}",
            f"owner_kind: {kind}",
            f"owner: {owner}",
            "max_action_level: A2_GENERATE",
            "inputs:",
            "outputs:",
        ]:
            require(frontmatter_marker in skill_text, f"Skill frontmatter drift: {skill_id} missing {frontmatter_marker}")
        require(len(skill_text.strip()) >= 2200, f"Skill contract too thin for review-grade definition: {skill_id}")

    expected_gates = {"gate.k", "gate.m", "gate.0", "gate.t", "gate.e", "gate.v", "gate.r", "gate.c"}
    require(set(gates["gates"]) == expected_gates, "Gate set drift")
    for gate_id, gate in gates["gates"].items():
        kind, owner = gate["owner_kind"], gate["owner_id"]
        if kind == "role": require(owner in role_ids, f"unknown Gate Role owner: {gate_id}")
        elif kind == "assurance": require(owner in assurance_ids, f"unknown Gate Assurance owner: {gate_id}")
        elif kind == "routed-expert": require(owner == "routed-domain-expert", f"Technical Gate owner drift: {gate_id}")
        else: raise AssertionError(f"unsupported Gate owner kind: {gate_id} -> {kind}")

    runtime_routes = runtime["routing"]
    routes = routing["routing"]
    require(set(routes) == set(runtime_routes) and len(routes) == 14, "routing/runtime task taxonomy drift")
    for task_type, route in routes.items():
        require(set(route.get("primary_experts", [])) <= expert_ids, f"route references unknown Expert: {task_type}")
        require(set(route.get("capabilities", [])) <= capability_ids, f"route references unknown Capability: {task_type}")
        require(set(route.get("assurance", [])) <= assurance_ids, f"route references unknown Assurance: {task_type}")

    expected_case_ids = {"GC-BOOT-001", "GC-KPANIC-001", "GC-HARDFAULT-001", "GC-NAND-001", "GC-UBIFS-001", "GC-DMA-001", "GC-RTOS-001", "GC-LINKER-001", "GC-DRIVER-001", "GC-BRINGUP-001", "GC-REVIEW-001", "GC-OTA-001"}
    case_by_id = {item["id"]: item for item in cases["cases"]}
    require(set(case_by_id) == expected_case_ids and len(case_by_id) == 12, "Golden Case set drift")
    for case_id, case in case_by_id.items():
        route = routes[case["task_type"]]
        require(case["target_mode"] == route["target_mode"], f"Golden target mode drift: {case_id}")
        require(case["expected_experts"] == route.get("primary_experts", []), f"Golden Expert drift: {case_id}")
        require(set(route.get("capabilities", [])).issubset(set(case.get("expected_capabilities", []))), f"Golden drops routed Capability: {case_id}")
        require(set(case.get("expected_capabilities", [])) <= capability_ids, f"Golden unknown Capability: {case_id}")
        require(case["required_assurance"] == route.get("assurance", []), f"Golden Assurance drift: {case_id}")
        for key in ["required_evidence", "expected_gate_behavior", "forbidden_claims", "success_signals"]:
            require(case.get(key), f"Golden Case missing safety/evidence field: {case_id}.{key}")

    print(f"edge-foundation target assets PASS: 3 Experts / {len(capability_ids)} Capabilities / {len(skill_by_id)} Skills / {len(expected_gates)} Gates / {len(case_by_id)} Golden Cases / canonical routing")


if __name__ == "__main__":
    main()
