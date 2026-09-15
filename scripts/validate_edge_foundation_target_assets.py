#!/usr/bin/env python3
"""Validate Phase-4-prep target assets without changing canonical execution."""
from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
LEGACY = ROOT / "expert-groups" / "embedded-system"


def load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    domain_path = EDGE / "domain.yaml"
    skills_path = EDGE / "skills.yaml"
    gates_path = EDGE / "gate-policy.yaml"
    cases_path = EDGE / "evaluation" / "golden-cases.yaml"
    routing_path = EDGE / "routing-shadow.yaml"
    legacy_group_path = LEGACY / "expert-group.yaml"
    legacy_skills_path = LEGACY / "config" / "p0-skills.yaml"
    legacy_gates_path = LEGACY / "config" / "gate-policy.yaml"
    legacy_cases_path = LEGACY / "tests" / "golden-cases.yaml"

    for path in [
        domain_path, skills_path, gates_path, cases_path, routing_path,
        legacy_group_path, legacy_skills_path, legacy_gates_path, legacy_cases_path,
    ]:
        require(path.is_file(), f"missing Phase-4-prep asset: {path.relative_to(ROOT)}")

    domain = load(domain_path)
    skills = load(skills_path)
    gates = load(gates_path)
    cases = load(cases_path)
    routing = load(routing_path)
    legacy_group = load(legacy_group_path)
    legacy_skills = load(legacy_skills_path)
    legacy_gates = load(legacy_gates_path)
    legacy_cases = load(legacy_cases_path)

    require(domain["migration"]["canonical_routing_switched"] is False, "Phase-4-prep must not switch canonical routing")
    require(skills["status"] == "phase4-prep-target" and skills["ownership_authority"] == "canonical", "target Skill ownership must be canonical")
    require(gates["status"] == "phase4-prep-target" and gates["ownership_authority"] == "canonical", "target Gate ownership must be canonical")
    require(cases["status"] == "phase4-prep-target", "target Golden Cases must declare Phase-4-prep status")
    require(cases["canonical_routing_switched"] is False, "target Golden Cases must not imply canonical routing switch")

    legacy_ids = {legacy_group["team_lead"]["id"], *(item["id"] for item in legacy_group["experts"])}
    for path in [skills_path, gates_path, cases_path]:
        text = path.read_text(encoding="utf-8")
        leaked = sorted(identity for identity in legacy_ids if identity in text)
        require(not leaked, f"legacy expert identity leaked into target asset {path.relative_to(ROOT)}: {leaked}")

    expert_ids = {item["id"] for item in domain["experts"]}
    embedded = next(item for item in domain["experts"] if item["id"] == "embedded-system-expert")
    capability_ids = set(embedded["capabilities"])
    assurance_ids = set(domain["assurance"]["responsibilities"])
    role_ids = {domain["coordination_role"]["id"]}

    legacy_skill_by_id = {item["id"]: item for item in legacy_skills["skills"]}
    target_skill_by_id = {item["id"]: item for item in skills["skills"]}
    require(len(target_skill_by_id) == len(skills["skills"]), "duplicate target Skill IDs")
    require(set(target_skill_by_id) == set(legacy_skill_by_id), "target Skill registry must cover legacy execution Skill set exactly during prep")
    require(len(target_skill_by_id) == 23, f"expected current 23-Skill baseline during prep, got {len(target_skill_by_id)}")

    for skill_id, item in target_skill_by_id.items():
        owner_kind = item["owner_kind"]
        owner_id = item["owner_id"]
        if owner_kind == "role":
            require(owner_id in role_ids, f"unknown target Role owner: {skill_id} -> {owner_id}")
        elif owner_kind == "capability":
            require(owner_id in capability_ids, f"unknown target Capability owner: {skill_id} -> {owner_id}")
        elif owner_kind == "assurance":
            require(owner_id in assurance_ids, f"unknown target Assurance owner: {skill_id} -> {owner_id}")
        else:
            raise AssertionError(f"unsupported target Skill owner kind: {skill_id} -> {owner_kind}")
        resolved = (skills_path.parent / item["path"]).resolve()
        require(ROOT.resolve() in resolved.parents, f"target Skill path escapes repository: {skill_id}")
        require(resolved.is_file(), f"target Skill implementation path missing: {skill_id} -> {resolved.relative_to(ROOT)}")

    target_gate_ids = set(gates["gates"])
    legacy_gate_ids = set(legacy_gates["gates"])
    require(target_gate_ids == legacy_gate_ids, "target Gate set must preserve all current Gate IDs")
    require(target_gate_ids == {"gate.k", "gate.m", "gate.0", "gate.t", "gate.e", "gate.v", "gate.r", "gate.c"}, "unexpected Gate baseline")
    require(gates["failure_policy"] == legacy_gates["failure_policy"], "Gate failure policy changed during ownership migration")

    for gate_id, target in gates["gates"].items():
        legacy = legacy_gates["gates"][gate_id]
        require(target["name"] == legacy["name"], f"Gate name drift: {gate_id}")
        for key in ["pass_when", "dimensions", "auto_check", "human_decision_on_degradation"]:
            if key in legacy:
                require(target.get(key) == legacy[key], f"Gate semantic drift: {gate_id}.{key}")
        kind = target["owner_kind"]
        owner = target["owner_id"]
        if kind == "role":
            require(owner in role_ids, f"unknown Gate Role owner: {gate_id} -> {owner}")
        elif kind == "assurance":
            require(owner in assurance_ids, f"unknown Gate Assurance owner: {gate_id} -> {owner}")
        elif kind == "routed-expert":
            require(owner == "routed-domain-expert", f"technical Gate must remain routed-expert owned: {gate_id}")
        else:
            raise AssertionError(f"unsupported Gate owner kind: {gate_id} -> {kind}")

    legacy_case_by_id = {case["id"]: case for case in legacy_cases["cases"]}
    target_case_by_id = {case["id"]: case for case in cases["cases"]}
    require(len(target_case_by_id) == len(cases["cases"]), "duplicate target Golden Case IDs")
    require(set(target_case_by_id) == set(legacy_case_by_id), "target Golden Cases must cover current legacy evaluation set exactly")
    require(len(target_case_by_id) == 12, f"expected current 12 Golden Cases during prep, got {len(target_case_by_id)}")

    for case_id, target in target_case_by_id.items():
        legacy = legacy_case_by_id[case_id]
        route = routing["routing"][target["task_type"]]
        require(target["task_type"] == legacy["task_type"], f"Golden Case task type drift: {case_id}")
        require(target["legacy_execution_mode"] == legacy["workflow_mode"], f"Golden Case legacy execution mode drift: {case_id}")
        require(target["target_mode"] == route["target_mode"], f"Golden Case target mode disagrees with routing shadow: {case_id}")
        require(target["expected_experts"] == route["primary_experts"], f"Golden Case Expert expectation disagrees with routing shadow: {case_id}")
        require(set(route.get("capabilities", [])).issubset(set(target["expected_capabilities"])), f"Golden Case drops routed Capability: {case_id}")
        require(set(target["expected_capabilities"]).issubset(capability_ids), f"Golden Case contains unknown Capability: {case_id}")
        require(target["required_assurance"] == route["assurance"], f"Golden Case Assurance expectation disagrees with routing shadow: {case_id}")
        require(set(target["expected_experts"]).issubset(expert_ids), f"Golden Case contains unknown target Expert: {case_id}")
        for key in ["required_evidence", "expected_gate_behavior", "forbidden_claims", "success_signals"]:
            require(target[key] == legacy[key], f"Golden Case evidence/safety semantic drift: {case_id}.{key}")

    require(skills["rules"]["legacy_expert_identity_as_owner_forbidden"] is True, "legacy Skill ownership must be forbidden")
    require(gates["rules"]["legacy_expert_identity_as_owner_forbidden"] is True, "legacy Gate ownership must be forbidden")
    require(gates["rules"]["engineering_not_equal_verification"] is True, "Engineering/Verification separation must be preserved")
    require(gates["rules"]["verification_not_equal_review"] is True, "Verification/Review separation must be preserved")
    require(cases["rules"]["legacy_expert_identity_forbidden"] is True, "Golden Cases must reject legacy expert identities")

    print(
        "edge-foundation target asset validation PASS: "
        f"{len(target_skill_by_id)} Skills re-owned to Role/Capability/Assurance, "
        f"{len(target_gate_ids)} Gates re-owned without semantic drift, "
        f"{len(target_case_by_id)} Golden Cases migrated to Expert/Capability/Assurance semantics, "
        "canonical execution unchanged"
    )


if __name__ == "__main__":
    main()
