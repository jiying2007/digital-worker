#!/usr/bin/env python3
"""Validate Edge Coordination responsibility migration from the legacy Team Lead adapter."""
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
    target_path = EDGE / "coordination.yaml"
    mapping_path = EDGE / "compatibility" / "embedded-1plus7-mapping.yaml"
    legacy_path = LEGACY / "contracts" / "experts" / "team-lead.io.yaml"
    legacy_group_path = LEGACY / "expert-group.yaml"

    for path in [domain_path, target_path, mapping_path, legacy_path, legacy_group_path]:
        require(path.is_file(), f"missing Coordination asset: {path.relative_to(ROOT)}")

    domain = load(domain_path)
    target = load(target_path)
    mapping = load(mapping_path)
    legacy = load(legacy_path)
    legacy_group = load(legacy_group_path)

    require(domain["migration"]["canonical_routing_switched"] is False, "Coordination prep must not switch canonical routing")
    require(domain["coordination_role"]["id"] == "edge-coordination", "domain Coordination role identity drift")
    require(domain["coordination_role"]["contract"] == "coordination.yaml", "domain Coordination contract pointer drift")
    require(domain["coordination_role"]["is_domain_expert"] is False, "Coordination role must not become a Domain Expert")

    legacy_ids = {legacy_group["team_lead"]["id"], *(item["id"] for item in legacy_group["experts"])}
    target_text = target_path.read_text(encoding="utf-8")
    leaked = sorted(identity for identity in legacy_ids if identity in target_text)
    require(not leaked, f"legacy expert identity leaked into target Coordination contract: {leaked}")

    require(target["id"] == "edge-coordination" and target["kind"] == "role", "target Coordination identity/kind drift")
    require(target["status"] == "phase4-prep-target", "target Coordination prep status drift")
    require(target["ownership_authority"] == "canonical", "target Coordination responsibility must be canonical")
    require(target["execution_surface"] == "legacy-compatible", "legacy Team Lead adapter must remain active during prep")
    adapter = (target_path.parent / target["legacy_execution_adapter"]).resolve()
    require(adapter == legacy_path.resolve(), "legacy Team Lead adapter pointer drift")

    for key in ["consumes", "produces", "produces_when_applicable", "constraints"]:
        require(target[key] == legacy[key], f"Coordination semantic drift: {key}")

    expected_responsibilities = set(domain["coordination_role"]["responsibilities"])
    require(set(target["responsibilities"]) == expected_responsibilities, "Coordination responsibility set disagrees with domain contract")

    mappings = {item["legacy_id"]: item for item in mapping["legacy_identities"]}
    legacy_handoffs = set(legacy["hands_off_to"])
    require(legacy_handoffs == set(legacy_ids) - {legacy_group["team_lead"]["id"]}, "legacy Team Lead handoff set drift")
    require(legacy_handoffs.issubset(mappings), "legacy Team Lead handoff missing compatibility mapping")

    collapsed_targets: set[str] = set()
    for legacy_id in legacy_handoffs:
        item = mappings[legacy_id]
        target_bindings = item["target_bindings"]
        if item.get("owner_expert") == "embedded-system-expert" or any(binding.get("kind") == "capability" for binding in target_bindings):
            collapsed_targets.add("embedded-system-expert")
        for binding in target_bindings:
            if binding.get("kind") == "assurance":
                collapsed_targets.add(f"assurance.{binding['id']}")

    require(collapsed_targets == {"embedded-system-expert", "assurance.verification", "assurance.review"}, f"unexpected collapsed legacy handoff mapping: {sorted(collapsed_targets)}")
    require(set(target["hands_off_to"]) == collapsed_targets, "target Coordination handoff does not exactly cover mapped legacy responsibilities")

    require(target["rules"]["legacy_expert_identity_forbidden"] is True, "Coordination must forbid legacy expert identity")
    require(target["rules"]["coordination_is_not_domain_expert"] is True, "Coordination must remain a Role")
    require(target["rules"]["coordination_is_not_agent"] is True, "Coordination role must not imply one Agent")
    require(target["rules"]["domain_conclusion_substitution_forbidden"] is True, "Coordination must not substitute professional conclusions")
    require(target["rules"]["implementation_verification_review_separation_required"] is True, "Coordination must preserve assurance separation")
    require(target["rules"]["execution_adapter_does_not_define_responsibility"] is True, "legacy adapter must not define target responsibility")

    print("edge-foundation Coordination validation PASS: Team Lead responsibility de-legacy to edge-coordination with exact I/O/constraint preservation and mapped handoffs")


if __name__ == "__main__":
    main()
