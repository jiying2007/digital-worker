#!/usr/bin/env python3
"""Validate P02-P06 responsibility migration into Embedded System Expert capabilities."""
from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
CAP_ROOT = EDGE / "experts" / "embedded-system" / "capabilities"
LEGACY = ROOT / "expert-groups" / "embedded-system"


def load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    domain_path = EDGE / "domain.yaml"
    expert_path = EDGE / "experts" / "embedded-system" / "expert.yaml"
    mapping_path = EDGE / "compatibility" / "embedded-1plus7-mapping.yaml"
    legacy_group_path = LEGACY / "expert-group.yaml"

    target_specs = {
        "embedded.architecture": (CAP_ROOT / "architecture.yaml", LEGACY / "contracts" / "experts" / "architecture.io.yaml"),
        "embedded.linux-bsp": (CAP_ROOT / "linux-bsp.yaml", LEGACY / "contracts" / "experts" / "linux-bsp.io.yaml"),
        "embedded.mcu-rtos": (CAP_ROOT / "mcu-rtos.yaml", LEGACY / "contracts" / "experts" / "mcu-rtos.io.yaml"),
        "embedded.driver-component": (CAP_ROOT / "driver-component.yaml", LEGACY / "contracts" / "experts" / "driver-component.io.yaml"),
        "embedded.debug-reliability": (CAP_ROOT / "debug-reliability.yaml", LEGACY / "contracts" / "experts" / "debug-reliability.io.yaml"),
    }
    for path in [domain_path, expert_path, mapping_path, legacy_group_path, *(p for pair in target_specs.values() for p in pair)]:
        require(path.is_file(), f"missing capability migration asset: {path.relative_to(ROOT)}")

    domain = load(domain_path)
    expert = load(expert_path)
    mapping = load(mapping_path)
    legacy_group = load(legacy_group_path)

    embedded_domain = next(item for item in domain["experts"] if item["id"] == "embedded-system-expert")
    require(embedded_domain["contract"] == "experts/embedded-system/expert.yaml", "Embedded Expert contract pointer drift")
    require(set(embedded_domain["capabilities"]) == set(target_specs), "domain capability set drift")
    require(expert["id"] == "embedded-system-expert" and expert["kind"] == "expert", "Embedded Expert target contract identity drift")
    require(expert["status"] == "phase4-prep-target", "Embedded Expert prep status drift")
    require(expert["ownership_authority"] == "canonical", "Embedded Expert responsibility must be canonical")
    require(expert["runtime_topology"] == "not_frozen", "Embedded Expert runtime topology must not freeze")
    require(set(expert["capability_contracts"]) == set(target_specs), "Embedded Expert capability contract registry drift")
    require(expert["rules"]["expert_is_not_agent"] is True, "Expert must not become Agent identity")
    require(expert["rules"]["expert_count_is_not_worker_count"] is True, "Expert count must not imply worker count")

    legacy_ids = {legacy_group["team_lead"]["id"], *(item["id"] for item in legacy_group["experts"])}
    static_handoff_map = {
        "embedded-system-team-lead": {"edge-coordination"},
        "embedded-architecture-expert": {"embedded.architecture"},
        "linux-bsp-expert": {"embedded.linux-bsp"},
        "mcu-rtos-expert": {"embedded.mcu-rtos"},
        "driver-component-expert": {"embedded.driver-component"},
        "debug-reliability-expert": {"embedded.debug-reliability"},
        "verification-expert": {"assurance.verification"},
        "embedded-review-governor": {"assurance.review"},
    }
    require(set(static_handoff_map) == legacy_ids, "capability handoff map must cover exact legacy identity set")

    mapping_by_id = {item["legacy_id"]: item for item in mapping["legacy_identities"]}
    require(set(mapping_by_id) == legacy_ids, "compatibility mapping identity set drift")
    for legacy_id, targets in static_handoff_map.items():
        item = mapping_by_id[legacy_id]
        mapped_tokens: set[str] = set()
        for binding in item["target_bindings"]:
            kind = binding["kind"]
            target_id = binding["id"]
            if kind == "role":
                mapped_tokens.add(target_id)
            elif kind == "capability":
                mapped_tokens.add(target_id)
            elif kind == "assurance":
                mapped_tokens.add(f"assurance.{target_id}")
        if legacy_id == "embedded-system-team-lead":
            require("edge-coordination" in mapped_tokens, "Team Lead must map to edge-coordination")
        elif legacy_id in {"verification-expert", "embedded-review-governor"}:
            require(targets.issubset(mapped_tokens), f"Assurance handoff mapping drift: {legacy_id}")
        else:
            require(targets.issubset(mapped_tokens), f"Capability handoff mapping drift: {legacy_id}")

    for capability_id, (target_path, legacy_path) in target_specs.items():
        target = load(target_path)
        legacy = load(legacy_path)
        require(target["id"] == capability_id, f"Capability id drift: {capability_id}")
        require(target["kind"] == "capability", f"Capability kind drift: {capability_id}")
        require(target["owner_expert"] == "embedded-system-expert", f"Capability owner Expert drift: {capability_id}")
        require(target["status"] == "phase4-prep-target", f"Capability prep status drift: {capability_id}")
        require(target["ownership_authority"] == "canonical", f"Capability responsibility must be canonical: {capability_id}")
        require(target["execution_surface"] == "legacy-compatible", f"legacy execution adapter must remain active: {capability_id}")
        adapter = (target_path.parent / target["legacy_execution_adapter"]).resolve()
        require(adapter == legacy_path.resolve(), f"legacy adapter pointer drift: {capability_id}")
        for key in ["consumes", "produces", "constraints"]:
            require(target[key] == legacy[key], f"Capability I/O semantic drift: {capability_id}.{key}")

        target_text = target_path.read_text(encoding="utf-8")
        leaked = sorted(identity for identity in legacy_ids if identity in target_text)
        require(not leaked, f"legacy Expert identity leaked into target Capability {capability_id}: {leaked}")

        expected_handoffs: set[str] = set()
        for legacy_handoff in legacy["hands_off_to"]:
            expected_handoffs.update(static_handoff_map[legacy_handoff])
        require(set(target["hands_off_to"]) == expected_handoffs, f"Capability handoff semantic drift: {capability_id}: expected={sorted(expected_handoffs)} got={sorted(target['hands_off_to'])}")
        require(target["rules"]["capability_is_not_agent"] is True, f"Capability became Agent identity: {capability_id}")
        require(target["rules"]["capability_is_not_domain_expert"] is True, f"Capability became Domain Expert: {capability_id}")
        require(target["rules"]["legacy_expert_identity_forbidden"] is True, f"legacy identity not forbidden: {capability_id}")
        require(target["rules"]["execution_adapter_does_not_define_responsibility"] is True, f"legacy adapter still defines responsibility: {capability_id}")

    print("edge-foundation capability validation PASS: P02-P06 migrated 5/5 to Embedded System Expert Capability contracts with exact I/O/constraint and mapped-handoff preservation")


if __name__ == "__main__":
    main()
