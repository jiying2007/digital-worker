#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
LOCK = ROOT / "config" / "integrations" / "cross-repo-lock.json"
CAPABILITY = ROOT / "config" / "integrations" / "provider-capability-matrix.yaml"
OWNERSHIP = ROOT / "contracts" / "cross-repo" / "embedded-ai-operating-system.yaml"
IDENTITY = ROOT / "contracts" / "cross-repo" / "identity-envelope.yaml"
HARVEST = ROOT / "contracts" / "cross-repo" / "knowledge-harvest-handoff.yaml"
STRATEGY = ROOT / "docs" / "strategy" / "ai-rd-target-operating-model.md"
QUICKSTART = ROOT / "docs" / "runbooks" / "embedded-closed-loop-quickstart.md"
SKILLS = EDGE / "skills.yaml"
ADAPTER = ROOT / "scripts" / "embedded_knowledge.py"


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def exact_sha(value: str | None) -> bool:
    return re.fullmatch(r"[0-9a-f]{40}", value or "") is not None


def digest(value: str | None) -> bool:
    return re.fullmatch(r"[0-9a-f]{64}", value or "") is not None


def main() -> None:
    for path in [LOCK, CAPABILITY, OWNERSHIP, IDENTITY, HARVEST, STRATEGY, QUICKSTART, SKILLS, ADAPTER]:
        require(path.is_file(), f"missing cross-repo asset: {path.relative_to(ROOT)}")

    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    require(lock["schema_version"] == 4, "cross-repo lock must use terminal source-set schema v4")
    require(lock["status"] == "source-set-integrated", "cross-repo lock status drift")
    require(lock["architecture_model"] == "four-control-planes-plus-replaceable-runtime-bindings", "architecture model drift")
    require(lock["architecture_provider_selection"] == "not_frozen", "provider choice must remain not_frozen")

    expected = {
        "knowledge_control_plane": ("jiying2007/knowledge-hub", "1.0"),
        "agent_asset_control_plane": ("jiying2007/agent-dev-kit", "2.0"),
        "runtime_practice_eval": ("jiying2007/llm_agent", "1.2"),
    }
    for key, (repo, contract_version) in expected.items():
        provider = lock["providers"].get(key, {})
        require(provider.get("repository") == repo, f"wrong provider repository for {key}")
        require(exact_sha(provider.get("commit")), f"{key} must pin exact commit")
        require(provider.get("contract_version") == contract_version, f"wrong contract version for {key}")
        require(digest(provider.get("contract_canonical_sha256")), f"{key} must pin canonical contract SHA256")
        require(provider.get("validation"), f"{key} validation state must be explicit")

    adk = lock["providers"]["agent_asset_control_plane"]
    require(adk.get("runtime_binding_contract_version") == "2.0", "ADK runtime-binding contract version drift")
    require(digest(adk.get("runtime_binding_contract_canonical_sha256")), "ADK runtime-binding contract digest missing")
    require(adk.get("required_asset_profile") == "embedded-fullstack", "ADK required asset profile drift")
    require(adk.get("delivery_mode") == "exact-source-set-reference", "ADK delivery mode drift")
    require("SOURCE_SET_READY" in adk.get("validation", ""), "ADK source-set handoff must be promoted")
    baseline = adk.get("release_baseline", {})
    require(baseline.get("version") == "5.1.0", "ADK release version drift")
    require(baseline.get("tag") == "v5.1.0", "ADK release tag drift")
    require(exact_sha(baseline.get("commit")), "ADK release commit must be exact")
    require(exact_sha(baseline.get("tree")), "ADK release tree must be exact")
    require(exact_sha(baseline.get("manifest_blob")), "ADK manifest blob must be exact")
    require(digest(baseline.get("release_artifact_sha256")), "ADK release artifact digest missing")

    codex = lock["runtime_bindings"].get("codex", {})
    require(codex.get("repository") == "jiying2007/codex", "Codex Runtime Binding repository drift")
    require(exact_sha(codex.get("commit")), "Codex Runtime Binding must pin exact commit")
    require(codex.get("contract_version") == "2.0", "Codex Runtime Binding contract version drift")
    require(digest(codex.get("contract_canonical_sha256")), "Codex Runtime Binding contract digest missing")
    require(codex.get("runtime_target") == "codex-cli", "Codex target drift")
    require(codex.get("required_asset_profile") == "embedded-fullstack", "Codex must consume the ADK embedded-fullstack Asset Profile")
    require(codex.get("source_identity_mode") == "exact-release-source-blobs", "Codex source identity mode drift")
    require(codex.get("runtime_readiness") == "SOURCE_SET_BOUND", "Codex source-set readiness drift")
    require(codex.get("session_bootstrap_contract_version") == "1.0", "Codex Session Bootstrap version drift")
    require(digest(codex.get("session_bootstrap_contract_canonical_sha256")), "Codex Session Bootstrap digest missing")
    require(codex.get("execution_receipt_schema") == "schemas/runtime-execution-receipt.schema.json", "Codex receipt schema missing")
    require("SOURCE_SET_BOUND" in codex.get("validation", ""), "Codex source-set binding must be promoted")
    require("runtime_profile_examples" not in codex, "digital-worker lock must not mirror mutable Codex runtime profile examples")

    rendered_lock = json.dumps(lock, ensure_ascii=False, sort_keys=True)
    for retired in ('"asset_bundle_hash"', "BLOCKED_ASSET_BUNDLE_IDENTITY", "5.0.0-rc.2", "provider-produced bundle", "token-lean"):
        require(retired not in rendered_lock, f"retired active lock token returned: {retired}")

    rules = lock["rules"]
    for key in [
        "contract_digest_required", "source_of_truth_stays_at_source", "provider_failure_must_not_be_reported_as_pass",
        "asset_profile_must_be_separate_from_runtime_profile", "immutable_adk_release_required", "exact_source_set_identity_required",
        "runtime_distribution_identity_required_when_executed", "monolithic_runtime_bundle_not_required_identity",
        "formal_mode_requires_exact_pinned_knowledge", "runtime_local_gate_is_not_domain_gate",
        "runtime_output_is_not_verification_pass", "runtime_execution_receipt_must_not_contain_verification_pass",
        "pin_freshness_does_not_imply_compatibility", "pin_promotion_requires_checkout_verification",
    ]:
        require(rules[key] is True, f"required source-set rule disabled: {key}")

    ownership = yaml.safe_load(OWNERSHIP.read_text(encoding="utf-8"))
    require(ownership["schema_version"] == 3, "ownership contract must use source-set schema v3")
    require(ownership["architecture_model"] == "four-control-planes-plus-replaceable-runtime-bindings", "ownership architecture drift")

    projection = ownership.get("projection_semantics", {})
    require(projection.get("repository_responsibility_projection") is True, "ownership model must be marked as a repository responsibility projection")
    require(projection.get("not_equal_authority_architecture_planes") is True, "repository responsibility projection must not imply equal-authority architecture planes")
    require(
        projection.get("canonical_semantic_ownership_authority")
        == "docs/adr/ADR-005-cross-repo-semantic-ownership-and-evidence-federation.md",
        "semantic ownership authority must remain ADR-005",
    )

    artifact_semantics = ownership.get("artifact_semantics", {})
    require(artifact_semantics.get("authority_kinds") == ["contract", "fact", "decision"], "artifact authority kinds drift")
    require(artifact_semantics.get("evidence_layers") == ["fact", "receipt", "report", "qualification"], "artifact evidence layers drift")
    require(artifact_semantics.get("decision_authority_is_orthogonal_to_evidence_layer") is True, "Decision Authority must remain orthogonal to evidence layer")
    require(artifact_semantics.get("classification_is_artifact_level_not_producer_inferred") is True, "authority/evidence classification must stay artifact-level")

    qualification_isolation = ownership.get("qualification_isolation", {})
    require(
        set(qualification_isolation.get("states", []))
        == {
            "product-readiness",
            "terminal-maturity",
            "runtime-qualification",
            "adk-release-qualification",
            "knowledge-provider-qualification",
        },
        "qualification isolation state set drift",
    )
    require(qualification_isolation.get("cross_state_pass_inheritance") == "forbidden", "qualification PASS inheritance must remain forbidden")

    require(ownership["planes"]["digital-worker"]["role"] == "rd-operating-model", "digital-worker role drift")
    require("expert-identity-and-routing" in ownership["planes"]["digital-worker"]["owns"], "digital-worker domain responsibility ownership missing")
    require("domain-workflow-and-gates" in ownership["planes"]["digital-worker"]["owns"], "digital-worker domain workflow ownership missing")
    require(ownership["planes"]["knowledge-hub"]["role"] == "knowledge-control-plane", "knowledge-hub role drift")
    require(ownership["planes"]["agent-dev-kit"]["role"] == "agent-asset-control-plane", "ADK role drift")
    require("reusable-skills" in ownership["planes"]["agent-dev-kit"]["owns"], "ADK reusable Skill ownership missing")
    require("immutable-release-identity" in ownership["planes"]["agent-dev-kit"]["owns"], "ADK immutable release ownership missing")
    require("exact-source-set-handoff-contract" in ownership["planes"]["agent-dev-kit"]["owns"], "ADK source-set handoff ownership missing")
    require(ownership["planes"]["llm_agent"]["role"] == "practice-and-runtime-evaluation-lab", "llm_agent role drift")
    require(ownership["runtime_bindings"]["candidates"]["codex"]["runtime_target"] == "codex-cli", "Codex candidate missing")
    require(ownership["runtime_bindings"]["candidates"]["codex"]["status"] == "source-set-bound", "Codex candidate source-set status drift")
    require(ownership["runtime_bindings"]["candidates"]["codex"]["session_bootstrap"] == "active", "Codex Session Bootstrap not active")
    require("domain-verification-pass" in ownership["runtime_bindings"]["contract"]["must_not_own"], "Runtime Binding must not own Verification PASS")
    require("reusable-agent-skill-source-of-truth" in ownership["runtime_bindings"]["contract"]["must_not_own"], "Runtime Binding must not own reusable Skill SoT")

    capability = yaml.safe_load(CAPABILITY.read_text(encoding="utf-8"))
    require(capability["schema_version"] == 3, "capability matrix must use source-set schema v3")
    require(capability["provider_selection"] == "not_frozen", "capability matrix must not freeze provider choice")
    require(capability["rules"]["no_poc_evidence_no_pass"] is True, "provider matrix must be evidence-first")
    require(capability["roles"]["knowledge_control_plane"]["capabilities"]["digital_worker_project_route"] == "pending-governed-registration", "Knowledge Hub route gap must remain explicit until proven")
    require(capability["roles"]["agent_asset_control_plane"]["capabilities"]["exact_source_set_handoff"] == "native", "ADK source-set capability missing")
    require(capability["roles"]["runtime_binding"]["candidates"]["codex"]["operational_readiness"] == "SOURCE_SET_BOUND", "Codex operational source-set readiness drift")
    require(capability["roles"]["runtime_binding"]["candidates"]["codex"]["capabilities"]["thin_session_bootstrap_l0_l1_l2"] == "native", "Codex thin bootstrap capability missing")
    require(capability["roles"]["runtime_practice_eval"]["capabilities"]["production_runtime"] == "unsupported-by-design", "llm_agent must not become production runtime")

    # Domain Skill contracts are canonical in digital-worker; reusable generic Skill assets may be sourced from ADK,
    # but runtime/provider ownership must never rewrite domain Role/Capability/Assurance ownership.
    skills_doc = yaml.safe_load(SKILLS.read_text(encoding="utf-8"))
    require(skills_doc["ownership_authority"] == "canonical", "target Skill ownership must remain canonical")
    require(skills_doc["execution_surface"] == "target", "target Skill execution surface drift")
    require(skills_doc["rules"]["physical_skill_location_is_canonical"] is True, "target Skill physical location must remain canonical")
    require(skills_doc["rules"]["skill_frontmatter_owner_must_match_registry"] is True, "Skill owner/frontmatter consistency ratchet disabled")
    skills = skills_doc["skills"]
    require(len(skills) == 23, f"current canonical Skill baseline must contain 23 entries, got {len(skills)}")
    require(len({item["id"] for item in skills}) == len(skills), "duplicate canonical Skill IDs")
    require({item["owner_kind"] for item in skills} <= {"role", "capability", "assurance"}, "canonical Skills may only be owned by Role/Capability/Assurance")
    for item in skills:
        path = (EDGE / item["path"]).resolve()
        require(path.is_file() and EDGE.resolve() in path.parents, f"canonical Skill path invalid: {item['id']}")

    identity = yaml.safe_load(IDENTITY.read_text(encoding="utf-8"))
    require(identity["schema_version"] == 3, "identity envelope must use source-set schema v3")

    governance = identity.get("digital_worker_governance", {})
    require(governance.get("provider") == "digital-worker", "identity envelope Digital Worker provider drift")
    require(governance.get("repository") == "jiying2007/digital-worker", "identity envelope Digital Worker repository drift")
    for key in [
        "provider_commit", "contract_catalog_ref", "contract_catalog_digest", "selected_domain_refs",
        "selected_routing_refs", "materially_used_domain_skills",
    ]:
        require(key in governance, f"Digital Worker governance identity missing {key}")

    require(identity["knowledge_context"]["provider"] == "knowledge-hub", "identity envelope knowledge provider drift")
    require(identity["agent_assets"]["provider"] == "agent-dev-kit", "identity envelope ADK provider drift")
    require("release_identity" in identity["agent_assets"], "identity envelope immutable release identity missing")
    require("source_set_ref" in identity["agent_assets"], "identity envelope source-set ref missing")
    require(identity["runtime_evaluation"]["evaluator"] == "llm_agent", "identity envelope runtime evaluator drift")
    for key in [
        "repository", "commit", "runtime_target", "runtime_profile", "runtime_host",
        "source_set_identity_ref", "runtime_distribution_identity_ref", "session_bootstrap_ref", "execution_receipt_ref",
    ]:
        require(key in identity["runtime_binding"], f"runtime binding identity missing {key}")

    escalation = identity.get("governance_escalation", {})
    for key in [
        "from_level", "to_level", "escalation_reason", "prior_context_disposition",
        "new_execution_source_set_ref", "new_session_bootstrap_ref", "formal_evidence_start_ref",
    ]:
        require(key in escalation, f"governance escalation provenance missing {key}")

    require("reports" in identity.get("verification", {}), "identity envelope Verification provenance refs missing")
    require("reports" in identity.get("review", {}), "identity envelope Review provenance refs missing")
    require(
        set(identity.get("qualification_refs", {}))
        == {
            "product_readiness_ref",
            "terminal_maturity_ref",
            "runtime_qualification_ref",
            "adk_release_qualification_ref",
            "knowledge_provider_qualification_ref",
        },
        "identity envelope orthogonal qualification refs drift",
    )

    identity_text = IDENTITY.read_text(encoding="utf-8")
    require("asset_bundle_hash" not in identity_text, "identity envelope must not retain bundle-era identity")
    identity_rules = "\n".join(identity["rules"])
    for marker in [
        "exact Digital Worker provider commit",
        "L1 to L2 governance escalation requires a new exact Execution Source Set",
        "formal Verification and Review reports bind exact Execution Source Set",
        "must not be silently reused",
        "orthogonal states and never inherit PASS",
        "must not contain verification_pass",
    ]:
        require(marker in identity_rules, f"identity envelope missing Stage 1 rule marker: {marker}")

    harvest = yaml.safe_load(HARVEST.read_text(encoding="utf-8"))
    require(harvest["to"] == "knowledge-hub", "Knowledge Harvest must route to Knowledge Hub")
    require(harvest["adapter"]["digital_worker_must_not_reimplement_provider_schema"] is True, "digital-worker must not fork Knowledge Hub proposal schema")
    require(harvest["hard_rules"]["direct_active_write"] is False, "Knowledge Harvest must not directly write active knowledge")
    require(harvest["hard_rules"]["owner_review_required"] is True, "Knowledge promotion requires owner review")

    adapter = ADAPTER.read_text(encoding="utf-8")
    for token in [
        "knowledge-context.sh", "knowledge-evidence-pack.sh", "knowledge-action-check.sh", "knowledge-proposal-route.sh",
        "bootstrap-local-catalog", "KNOWLEDGE_HUB_ROOT", "BLOCKED_PROVIDER_IDENTITY_MISMATCH",
    ]:
        require(token in adapter, f"knowledge adapter missing required surface: {token}")
    for forbidden in ["~/.codex", "~/.claude", "~/.config/opencode"]:
        require(forbidden not in adapter, f"digital-worker must not own runtime-specific path: {forbidden}")

    strategy = STRATEGY.read_text(encoding="utf-8")
    for token in [
        "4 个稳定 repository responsibility/control roles", "repository responsibility model", "不等于 ADR-003 的 architecture plane",
        "N 个可替换 Runtime Binding", "jiying2007/codex", "Thin Session Bootstrap",
        "L0 — Quick Assist", "L1 — Governed Engineering", "L2 — Formal Evidence",
        "Asset Profile", "Runtime Profile", "Execution Receipt", "exact-source-set",
    ]:
        require(token in strategy, f"target operating model missing marker: {token}")
    require("target-baseline / frozen-for-implementation" in strategy, "target operating model status drift")

    quickstart = QUICKSTART.read_text(encoding="utf-8")
    for token in [
        "session-bootstrap.sh", "L2 / formal-evidence", "SOURCE_SET_BOUND", "exact-source-set-reference",
        "runtime distribution identity", "KNOWLEDGE_HUB_ROOT", "edge_knowledge.py context",
        "edge_knowledge.py evidence-pack", "identity-envelope.yaml", "default (runtime-owned)",
    ]:
        require(token in quickstart, f"quickstart missing integrated source-set workflow marker: {token}")
    for retired in [
        "provider-produced bundle hash", "BLOCKED_ASSET_BUNDLE_IDENTITY", "ADK Asset Profile / bundle identity",
        "token-lean", "--runtime-profile",
    ]:
        require(retired not in quickstart, f"quickstart retained retired runtime marker: {retired}")

    print(
        "cross-repo integration validation PASS: exact provider pins/digests, repository-responsibility projection, "
        "artifact-level authority/evidence semantics, Stage 1 governance/decision provenance, canonical domain Skills, "
        "ADK reusable-asset boundary, thin Session Bootstrap, exact source-set and fail-closed Runtime boundaries"
    )


if __name__ == "__main__":
    main()
