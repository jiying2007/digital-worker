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
STRATEGY = ROOT / "docs" / "strategy" / "ai-rd-target-operating-model.md"
LEGACY_STRATEGY = ROOT / "docs" / "strategy" / "four-control-planes-runtime-bindings.md"
QUICKSTART = ROOT / "docs" / "runbooks" / "embedded-closed-loop-quickstart.md"
SKILLS = ROOT / "expert-groups" / "embedded-system" / "config" / "p0-skills.yaml"
MATRIX = ROOT / "expert-groups" / "embedded-system" / "config" / "skill-ownership-matrix.yaml"
ADAPTER = ROOT / "scripts" / "embedded_knowledge.py"


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def exact_sha(value: str | None) -> bool:
    return re.fullmatch(r"[0-9a-f]{40}", value or "") is not None


def digest(value: str | None) -> bool:
    return re.fullmatch(r"[0-9a-f]{64}", value or "") is not None


def main() -> None:
    for path in [LOCK, CAPABILITY, OWNERSHIP, IDENTITY, HARVEST, STRATEGY, LEGACY_STRATEGY, QUICKSTART, SKILLS, MATRIX, ADAPTER]:
        require(path.is_file(), f"missing cross-repo asset: {path.relative_to(ROOT)}")

    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    require(lock["schema_version"] == 3, "cross-repo lock must use trust-closure schema v3")
    require(lock["architecture_model"] == "four-control-planes-plus-replaceable-runtime-bindings", "architecture model drift")
    require(lock["architecture_provider_selection"] == "not_frozen", "provider choice must remain not_frozen")

    expected = {
        "knowledge_control_plane": ("jiying2007/knowledge-hub", "1.0"),
        "agent_asset_control_plane": ("jiying2007/agent-dev-kit", "1.0"),
        "runtime_practice_eval": ("jiying2007/llm_agent", "1.1"),
    }
    for key, (repo, contract_version) in expected.items():
        provider = lock["providers"].get(key, {})
        require(provider.get("repository") == repo, f"wrong provider repository for {key}")
        require(exact_sha(provider.get("commit")), f"{key} must pin exact commit")
        require(provider.get("contract_version") == contract_version, f"wrong contract version for {key}")
        require(digest(provider.get("contract_canonical_sha256")), f"{key} must pin canonical contract SHA256")
        require(provider.get("validation"), f"{key} validation state must be explicit")

    adk = lock["providers"]["agent_asset_control_plane"]
    require(digest(adk.get("runtime_binding_contract_canonical_sha256")), "ADK runtime-binding contract digest missing")

    codex = lock["runtime_bindings"].get("codex", {})
    require(codex.get("repository") == "jiying2007/codex", "Codex Runtime Binding repository drift")
    require(exact_sha(codex.get("commit")), "Codex Runtime Binding must pin exact commit")
    require(digest(codex.get("contract_canonical_sha256")), "Codex Runtime Binding contract digest missing")
    require(codex.get("runtime_target") == "codex-cli", "Codex target drift")
    require(codex.get("required_asset_profile") == "embedded-fullstack", "Codex must consume the ADK embedded-fullstack Asset Profile")
    require(codex.get("execution_receipt_schema") == "schemas/runtime-execution-receipt.schema.json", "Codex receipt schema missing")
    require("BLOCKED" in codex.get("validation", ""), "current Codex lock must stay fail-closed until the versioned source-set migration is promoted")
    require(adk.get("asset_bundle_hash") is None, "current legacy lock must not fabricate an ADK asset bundle identity")

    rules = lock["rules"]
    for key in [
        "contract_digest_required",
        "source_of_truth_stays_at_source",
        "provider_failure_must_not_be_reported_as_pass",
        "asset_profile_must_be_separate_from_runtime_profile",
        "runtime_local_gate_is_not_domain_gate",
        "runtime_output_is_not_verification_pass",
        "runtime_execution_receipt_must_not_contain_verification_pass",
        "pin_freshness_does_not_imply_compatibility",
        "pin_promotion_requires_checkout_verification",
    ]:
        require(rules[key] is True, f"required 4+N rule disabled: {key}")

    ownership = yaml.safe_load(OWNERSHIP.read_text(encoding="utf-8"))
    require(ownership["architecture_model"] == "four-control-planes-plus-replaceable-runtime-bindings", "ownership architecture drift")
    require(ownership["planes"]["digital-worker"]["role"] == "rd-operating-model", "digital-worker role drift")
    require(ownership["planes"]["knowledge-hub"]["role"] == "knowledge-control-plane", "knowledge-hub role drift")
    require(ownership["planes"]["agent-dev-kit"]["role"] == "agent-asset-control-plane", "ADK role drift")
    require(ownership["planes"]["llm_agent"]["role"] == "practice-and-runtime-evaluation-lab", "llm_agent role drift")
    require(ownership["runtime_bindings"]["candidates"]["codex"]["runtime_target"] == "codex-cli", "Codex candidate missing")
    require("domain-verification-pass" in ownership["runtime_bindings"]["contract"]["must_not_own"], "Runtime Binding must not own verification PASS")

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

    identity = yaml.safe_load(IDENTITY.read_text(encoding="utf-8"))
    require(identity["knowledge_context"]["provider"] == "knowledge-hub", "identity envelope knowledge provider drift")
    require(identity["agent_assets"]["provider"] == "agent-dev-kit", "identity envelope ADK provider drift")
    require(identity["runtime_evaluation"]["evaluator"] == "llm_agent", "identity envelope runtime evaluator drift")
    for key in ["repository", "commit", "runtime_target", "runtime_profile", "runtime_host", "execution_receipt_ref"]:
        require(key in identity["runtime_binding"], f"runtime binding identity missing {key}")
    require(any("must not contain verification_pass" in rule for rule in identity["rules"]), "receipt must explicitly reject verification_pass")

    harvest = yaml.safe_load(HARVEST.read_text(encoding="utf-8"))
    require(harvest["to"] == "knowledge-hub", "Knowledge Harvest must route to Knowledge Hub")
    require(harvest["adapter"]["digital_worker_must_not_reimplement_provider_schema"] is True, "digital-worker must not fork Knowledge Hub proposal schema")
    require(harvest["hard_rules"]["direct_active_write"] is False, "Knowledge Harvest must not directly write active knowledge")
    require(harvest["hard_rules"]["owner_review_required"] is True, "Knowledge promotion requires owner review")

    adapter = ADAPTER.read_text(encoding="utf-8")
    for token in ["knowledge-context.sh", "knowledge-evidence-pack.sh", "knowledge-action-check.sh", "knowledge-proposal-route.sh", "bootstrap-local-catalog", "KNOWLEDGE_HUB_ROOT", "BLOCKED_PROVIDER_IDENTITY_MISMATCH"]:
        require(token in adapter, f"knowledge adapter missing required surface: {token}")
    for forbidden in ["~/.codex", "~/.claude", "~/.config/opencode"]:
        require(forbidden not in adapter, f"digital-worker must not own runtime-specific path: {forbidden}")

    strategy = STRATEGY.read_text(encoding="utf-8")
    for token in [
        "4 个稳定控制面",
        "N 个可替换 Runtime Binding",
        "jiying2007/codex",
        "Thin Session Bootstrap",
        "L0 — Quick Assist",
        "L1 — Governed Engineering",
        "L2 — Formal Evidence",
        "Asset Profile",
        "Runtime Profile",
        "Execution Receipt",
        "exact-source-set",
    ]:
        require(token in strategy, f"target operating model missing marker: {token}")
    require("asset_bundle_hash / BLOCKED_ASSET_BUNDLE_IDENTITY" in strategy, "target operating model must document the legacy bundle migration boundary")
    require("target-baseline / frozen-for-implementation" in strategy, "target operating model status drift")

    legacy_strategy = LEGACY_STRATEGY.read_text(encoding="utf-8")
    require("Status: `superseded`" in legacy_strategy, "transitional 4+N strategy must remain superseded")
    require("ai-rd-target-operating-model.md" in legacy_strategy, "superseded strategy must point to final target baseline")

    quickstart = QUICKSTART.read_text(encoding="utf-8")
    for token in ["KNOWLEDGE_HUB_ROOT", "embedded_knowledge.py context", "embedded_knowledge.py evidence-pack", "identity-envelope.yaml"]:
        require(token in quickstart, f"quickstart missing integrated workflow marker: {token}")

    print("cross-repo integration validation PASS: final target operating model indexed; current machine locks remain fail-closed pending versioned source-set migration")


if __name__ == "__main__":
    main()
