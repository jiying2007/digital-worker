#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "config" / "integrations" / "cross-repo-lock.json"
CAPABILITY = ROOT / "config" / "integrations" / "provider-capability-matrix.yaml"
OWNERSHIP = ROOT / "contracts" / "cross-repo" / "embedded-ai-operating-system.yaml"
IDENTITY = ROOT / "contracts" / "cross-repo" / "identity-envelope.yaml"
HARVEST = ROOT / "contracts" / "cross-repo" / "knowledge-harvest-handoff.yaml"
STRATEGY = ROOT / "docs" / "strategy" / "four-repo-ai-operating-system.md"
QUICKSTART = ROOT / "docs" / "runbooks" / "embedded-closed-loop-quickstart.md"
SKILLS = ROOT / "expert-groups" / "embedded-system" / "config" / "p0-skills.yaml"
MATRIX = ROOT / "expert-groups" / "embedded-system" / "config" / "skill-ownership-matrix.yaml"
ADAPTER = ROOT / "scripts" / "embedded_knowledge.py"


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def main() -> None:
    for path in [LOCK, CAPABILITY, OWNERSHIP, IDENTITY, HARVEST, STRATEGY, QUICKSTART, SKILLS, MATRIX, ADAPTER]:
        require(path.is_file(), f"missing cross-repo asset: {path.relative_to(ROOT)}")

    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    require(lock["architecture_provider_selection"] == "not_frozen", "provider choice must remain not_frozen")
    expected = {
        "knowledge_control_plane": "jiying2007/knowledge-hub",
        "agent_asset_control_plane": "jiying2007/agent-dev-kit",
        "runtime_practice_eval": "jiying2007/llm_agent",
    }
    for key, repo in expected.items():
        provider = lock["providers"].get(key, {})
        require(provider.get("repository") == repo, f"wrong provider repository for {key}")
        require(re.fullmatch(r"[0-9a-f]{40}", provider.get("commit", "")) is not None, f"{key} must pin exact commit")
        require(provider.get("contract_version") == "1.0", f"{key} contract version must be explicit")
        require(provider.get("validation"), f"{key} validation state must be explicit")
        require("PASS" not in provider.get("validation", "") or "BLOCKED" not in provider.get("validation", ""), f"ambiguous provider validation: {key}")
    require(lock["rules"]["runtime_output_is_not_verification_pass"] is True, "runtime output must never imply verification PASS")
    require(lock["rules"]["source_of_truth_stays_at_source"] is True, "source authority rule must remain enabled")

    ownership = yaml.safe_load(OWNERSHIP.read_text(encoding="utf-8"))
    require(ownership["planes"]["digital-worker"]["role"] == "rd-operating-model", "digital-worker role drift")
    require(ownership["planes"]["knowledge-hub"]["role"] == "knowledge-control-plane", "knowledge-hub role drift")
    require(ownership["planes"]["agent-dev-kit"]["role"] == "agent-asset-control-plane", "ADK role drift")
    require(ownership["planes"]["llm_agent"]["role"] == "practice-and-runtime-evaluation-lab", "llm_agent role drift")
    require(ownership["planes"]["knowledge-hub"]["write_from_digital_worker"] == "proposal-only", "knowledge writes must remain proposal-only")

    capability = yaml.safe_load(CAPABILITY.read_text(encoding="utf-8"))
    require(capability["provider_selection"] == "not_frozen", "capability matrix must not freeze provider choice")
    require(capability["rules"]["no_poc_evidence_no_pass"] is True, "provider matrix must be evidence-first")
    require(capability["roles"]["knowledge_control_plane"]["capabilities"]["digital_worker_project_route"] == "pending-governed-registration", "Knowledge Hub route gap must remain explicit until proven")
    require(capability["roles"]["runtime_practice_eval"]["capabilities"]["production_runtime"] == "unsupported-by-design", "llm_agent must not become production runtime")

    p0 = yaml.safe_load(SKILLS.read_text(encoding="utf-8"))["skills"]
    matrix = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    p0_ids = {item["id"] for item in p0}
    decisions = matrix["decisions"]
    matrix_ids = {item["id"] for item in decisions}
    require(matrix_ids == p0_ids, f"skill ownership matrix must cover all P0 skills: missing={sorted(p0_ids-matrix_ids)} extra={sorted(matrix_ids-p0_ids)}")
    allowed = {"KEEP_DOMAIN_CONTRACT", "WRAP_ADK", "ADK_REUSE_CANDIDATE"}
    require(all(item["decision"] in allowed for item in decisions), "invalid skill ownership decision")
    require(matrix["promotion_rule"]["require_real_pilot_evidence"] is True, "skill replacement requires real pilot evidence")
    require(matrix["promotion_rule"]["auto_remove_domain_skill"] is False, "domain skills must not auto-remove")
    require(any(item["decision"] == "WRAP_ADK" for item in decisions), "matrix must contain at least one concrete ADK wrapper candidate")
    require(any(item["decision"] == "KEEP_DOMAIN_CONTRACT" for item in decisions), "matrix must preserve domain-only semantics")

    identity = yaml.safe_load(IDENTITY.read_text(encoding="utf-8"))
    require(identity["knowledge_context"]["provider"] == "knowledge-hub", "identity envelope knowledge provider drift")
    require(identity["agent_assets"]["provider"] == "agent-dev-kit", "identity envelope ADK provider drift")
    require(identity["runtime"]["evaluator"] == "llm_agent", "identity envelope runtime evaluator drift")

    harvest = yaml.safe_load(HARVEST.read_text(encoding="utf-8"))
    require(harvest["to"] == "knowledge-hub", "Knowledge Harvest must route to Knowledge Hub")
    require(harvest["adapter"]["digital_worker_must_not_reimplement_provider_schema"] is True, "digital-worker must not fork Knowledge Hub proposal schema")
    require(harvest["hard_rules"]["direct_active_write"] is False, "Knowledge Harvest must not directly write active knowledge")
    require(harvest["hard_rules"]["owner_review_required"] is True, "Knowledge promotion requires owner review")

    adapter = ADAPTER.read_text(encoding="utf-8")
    for token in ["knowledge-context.sh", "knowledge-evidence-pack.sh", "knowledge-action-check.sh", "knowledge-proposal-route.sh", "bootstrap-local-catalog", "KNOWLEDGE_HUB_ROOT"]:
        require(token in adapter, f"knowledge adapter missing required surface: {token}")
    for forbidden in ["~/.codex", "~/.claude", "~/.config/opencode"]:
        require(forbidden not in adapter, f"digital-worker must not own runtime-specific path: {forbidden}")

    strategy = STRATEGY.read_text(encoding="utf-8")
    for token in ["R&D Operating Model", "Knowledge Control Plane", "Agent Asset Control Plane", "Practice/Runtime Evaluation Lab", "route-pending"]:
        require(token in strategy, f"four-repo strategy missing boundary marker: {token}")

    quickstart = QUICKSTART.read_text(encoding="utf-8")
    for token in ["KNOWLEDGE_HUB_ROOT", "embedded_knowledge.py context", "embedded_knowledge.py evidence-pack", "bootstrap-local-catalog", "identity-envelope.yaml"]:
        require(token in quickstart, f"quickstart missing integrated workflow marker: {token}")

    print("cross-repo integration validation PASS: ownership, exact pins, capability evidence, skill matrix, identity envelope, Knowledge Hub adapter/handoff")


if __name__ == "__main__":
    main()
