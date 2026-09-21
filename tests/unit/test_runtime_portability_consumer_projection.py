from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "config" / "integrations" / "cross-repo-lock.json"
CAPABILITY = ROOT / "config" / "integrations" / "provider-capability-matrix.yaml"
POLICY = ROOT / "manifests" / "runtime-r2-qualification-policy.json"


def test_runtime_eval_is_optional_observer_not_r2_decision_authority() -> None:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    runtime_eval = lock["providers"]["runtime_practice_eval"]

    assert runtime_eval["repository"] == "jiying2007/llm_agent"
    assert re.fullmatch(r"[0-9a-f]{40}", runtime_eval["commit"])
    assert runtime_eval["role"] == "optional-evolution-observer"
    assert runtime_eval["qualification_authority"] == "jiying2007/digital-worker"
    assert runtime_eval["qualification_policy"] == "manifests/runtime-r2-qualification-policy.json"
    assert runtime_eval["runtime_portability_evidence_level"] == "R2-periodic-real-provider-substitution"
    assert runtime_eval["runtime_portability_status"] == "periodic-qualification-policy-active-current-evidence-blocked"

    for retired in (
        "runtime_portability_certifier",
        "runtime_portability_certifier_test",
        "runtime_portability_qualification_manifest",
        "runtime_portability_cli_contract",
    ):
        assert retired not in runtime_eval

    rules = lock["rules"]
    assert rules["terminal_replaceability_requires_r2_real_provider_substitution"] is True
    assert rules["r1_binding_conformance_is_not_terminal_replaceability"] is True
    assert rules["repository_closure_requires_r2"] is False
    assert rules["product_release_requires_r2"] is False
    assert rules["runtime_binding_r1_required"] is True
    assert rules["runtime_portability_qualification_requires_r2"] is True
    assert rules["r2_is_periodic_qualification"] is True
    assert rules["r2_failure_does_not_invalidate_repository_health"] is True


def test_capability_projection_keeps_r2_claim_gated_without_root_certifier() -> None:
    capability = yaml.safe_load(CAPABILITY.read_text(encoding="utf-8"))
    runtime_eval = capability["roles"]["runtime_practice_eval"]
    caps = runtime_eval["capabilities"]

    assert runtime_eval["evidence"] == {
        "identity_ref": "config/integrations/cross-repo-lock.json#/providers/runtime_practice_eval",
        "checkout_verification": "permanent-digital-worker-ci",
    }
    assert runtime_eval["decision"] == "optional-evolution-observer"
    assert caps["runtime_binding_comparison"] == "periodic-r2-observer"
    assert caps["exact_release_source_set_comparison"] == "periodic-r2-observer"
    assert caps["r2_qualification_authority"] == "digital-worker-independent-verifier"
    assert caps["r2_real_provider_evidence"] == "current-campaign-blocked"
    assert caps["terminal_replaceability"] == "claim-gated-by-fresh-r2"
    assert caps["production_runtime"] == "unsupported-by-design"
    assert "runtime_portability_certifier" not in caps
    assert "runtime_portability_certifier_readiness" not in caps

    rules = capability["rules"]
    assert rules["repository_closure_requires_r2"] is False
    assert rules["product_release_requires_r2"] is False
    assert rules["runtime_binding_r1_required"] is True
    assert rules["runtime_portability_qualification_requires_r2"] is True
    assert rules["r2_is_periodic_qualification"] is True
    assert rules["r2_failure_does_not_invalidate_repository_health"] is True


def test_machine_policy_defines_periodic_claim_freshness_boundary() -> None:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    assert policy["cadence"]["period"] == "quarterly"
    assert policy["cadence"]["recommended_max_age_days"] == 120
    assert policy["scope"]["repository_closure_blocking"] is False
    assert policy["scope"]["product_release_blocking"] is False
    assert policy["scope"]["runtime_portability_claim_requires_r2"] is True
    assert policy["campaign"]["independent_human_review_required"] is False
    assert policy["campaign"]["root_certifier_required"] is False
    assert policy["governance"]["failed_campaigns_are_valid_evidence"] is True
