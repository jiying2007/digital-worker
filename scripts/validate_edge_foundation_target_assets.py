#!/usr/bin/env python3
"""Validate canonical Edge Foundation target assets without a duplicated legacy Golden dataset."""
from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
LEGACY = ROOT / "expert-groups" / "embedded-system"


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
    routing = load(EDGE / "routing-shadow.yaml")
    legacy_group = load(LEGACY / "expert-group.yaml")
    legacy_skills = load(LEGACY / "config/p0-skills.yaml")
    legacy_gates = load(LEGACY / "config/gate-policy.yaml")

    require(domain["migration"]["canonical_routing_switched"] is False, "target-asset prep must not switch canonical routing")
    require(skills["ownership_authority"] == "canonical", "target Skill ownership must be canonical")
    require(gates["ownership_authority"] == "canonical", "target Gate ownership must be canonical")
    require(cases["status"] == "phase4-prep-target", "target Golden Cases status drift")
    require(cases["canonical_routing_switched"] is False, "target Golden Cases must not imply canonical switch")

    legacy_ids = {legacy_group["team_lead"]["id"], *(item["id"] for item in legacy_group["experts"])}
    for path in [EDGE / "skills.yaml", EDGE / "gate-policy.yaml", EDGE / "evaluation/golden-cases.yaml"]:
        text = path.read_text(encoding="utf-8")
        leaked = sorted(identity for identity in legacy_ids if identity in text)
        require(not leaked, f"legacy identity leaked into target asset {path.relative_to(ROOT)}: {leaked}")

    expert_ids = {item["id"] for item in domain["experts"]}
    require(expert_ids == {"structure-expert", "hardware-expert", "embedded-system-expert"}, "target Domain Expert set drift")
    embedded = next(item for item in domain["experts"] if item["id"] == "embedded-system-expert")
    capability_ids = set(embedded["capabilities"])
    assurance_ids = set(domain["assurance"]["responsibilities"])
    role_ids = {domain["coordination_role"]["id"]}

    legacy_skill_ids = {item["id"] for item in legacy_skills["skills"]}
    target_skill_by_id = {item["id"]: item for item in skills["skills"]}
    require(len(target_skill_by_id) == len(skills["skills"]), "duplicate target Skill IDs")
    require(set(target_skill_by_id) == legacy_skill_ids, "target Skill registry must cover current execution Skill set exactly")
    require(len(target_skill_by_id) == 23, f"expected current 23 Skill baseline, got {len(target_skill_by_id)}")
    for skill_id, item in target_skill_by_id.items():
        kind, owner = item["owner_kind"], item["owner_id"]
        if kind == "role":
            require(owner in role_ids, f"unknown Role owner: {skill_id} -> {owner}")
        elif kind == "capability":
            require(owner in capability_ids, f"unknown Capability owner: {skill_id} -> {owner}")
        elif kind == "assurance":
            require(owner in assurance_ids, f"unknown Assurance owner: {skill_id} -> {owner}")
        else:
            raise AssertionError(f"unsupported target Skill owner kind: {skill_id} -> {kind}")
        resolved = ((EDGE / "skills.yaml").parent / item["path"]).resolve()
        require(resolved.is_file() and ROOT.resolve() in resolved.parents, f"target Skill implementation path invalid: {skill_id}")

    target_gate_ids = set(gates["gates"])
    legacy_gate_ids = set(legacy_gates["gates"])
    require(target_gate_ids == legacy_gate_ids == {"gate.k", "gate.m", "gate.0", "gate.t", "gate.e", "gate.v", "gate.r", "gate.c"}, "Gate baseline drift")
    require(gates["failure_policy"] == legacy_gates["failure_policy"], "Gate failure policy drift during ownership migration")
    for gate_id, gate in gates["gates"].items():
        require(gate["name"] == legacy_gates["gates"][gate_id]["name"], f"Gate name drift: {gate_id}")
        kind, owner = gate["owner_kind"], gate["owner_id"]
        if kind == "role":
            require(owner in role_ids, f"unknown Gate Role owner: {gate_id}")
        elif kind == "assurance":
            require(owner in assurance_ids, f"unknown Gate Assurance owner: {gate_id}")
        elif kind == "routed-expert":
            require(owner == "routed-domain-expert", f"technical Gate owner drift: {gate_id}")
        else:
            raise AssertionError(f"unsupported Gate owner kind: {gate_id} -> {kind}")

    target_cases = cases["cases"]
    expected_case_ids = {
        "GC-BOOT-001", "GC-KPANIC-001", "GC-HARDFAULT-001", "GC-NAND-001",
        "GC-UBIFS-001", "GC-DMA-001", "GC-RTOS-001", "GC-LINKER-001",
        "GC-DRIVER-001", "GC-BRINGUP-001", "GC-REVIEW-001", "GC-OTA-001",
    }
    case_by_id = {item["id"]: item for item in target_cases}
    require(len(case_by_id) == len(target_cases), "duplicate target Golden Case IDs")
    require(set(case_by_id) == expected_case_ids, f"target Golden Case ID drift: {sorted(case_by_id)}")
    for case_id, case in case_by_id.items():
        task_type = case["task_type"]
        require(task_type in routing["routing"], f"Golden Case task type not routed: {case_id}")
        route = routing["routing"][task_type]
        require(case["target_mode"] == route["target_mode"], f"Golden Case target mode drift: {case_id}")
        require(case["expected_experts"] == route.get("primary_experts", []), f"Golden Case Expert drift: {case_id}")
        require(set(route.get("capabilities", [])).issubset(set(case.get("expected_capabilities", []))), f"Golden Case drops routed Capability: {case_id}")
        require(set(case.get("expected_capabilities", [])).issubset(capability_ids), f"Golden Case unknown Capability: {case_id}")
        require(case["required_assurance"] == route.get("assurance", []), f"Golden Case Assurance drift: {case_id}")
        require(set(case["expected_experts"]).issubset(expert_ids), f"Golden Case unknown target Expert: {case_id}")
        legacy_mode = case["legacy_execution_mode"]
        require(legacy_mode in routing["legacy_mode_translation"], f"Golden Case unknown comparison mode: {case_id}")
        translated = routing["legacy_mode_translation"][legacy_mode]
        require(translated in set(route.get("allowed_target_modes", [route["target_mode"]])), f"Golden Case comparison mode no longer maps to target: {case_id}")
        for key in ["required_evidence", "expected_gate_behavior", "forbidden_claims", "success_signals"]:
            require(case.get(key), f"Golden Case missing safety/evidence field: {case_id}.{key}")

    legacy_pointer = LEGACY / "tests/golden-cases.yaml"
    require(legacy_pointer.is_file(), "legacy Golden location must remain an explicit retirement pointer during compatibility stage")
    pointer = load(legacy_pointer)
    require(pointer.get("retired") is True and "cases" not in pointer, "legacy Golden location must not contain a second Golden dataset")
    require(pointer.get("authority") == "../../../domains/edge-foundation/evaluation/golden-cases.yaml", "legacy Golden pointer authority drift")

    require(skills["rules"]["legacy_expert_identity_as_owner_forbidden"] is True, "legacy Skill owner must remain forbidden")
    require(gates["rules"]["engineering_not_equal_verification"] is True, "Engineering/Verification separation drift")
    require(gates["rules"]["verification_not_equal_review"] is True, "Verification/Review separation drift")
    require(cases["rules"]["legacy_expert_identity_forbidden"] is True, "target Golden Cases must reject legacy identity")

    print(
        "edge-foundation target assets PASS: "
        f"{len(target_skill_by_id)} Skills, {len(target_gate_ids)} Gates, {len(target_cases)} canonical Golden Cases; "
        "legacy Golden data copy retired; canonical execution unchanged"
    )


if __name__ == "__main__":
    main()
