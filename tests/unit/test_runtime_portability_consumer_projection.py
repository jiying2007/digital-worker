from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "config" / "integrations" / "cross-repo-lock.json"
CAPABILITY = ROOT / "config" / "integrations" / "provider-capability-matrix.yaml"


def test_pinned_runtime_eval_exposes_dual_r1_and_r2_certifier_without_qualifying_r2() -> None:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    runtime_eval = lock["providers"]["runtime_practice_eval"]

    # This is a consumer projection of the already pinned provider commit; do not
    # turn R1 source-set readiness or certifier readiness into fabricated R2 evidence.
    assert runtime_eval["repository"] == "jiying2007/llm_agent"
    assert runtime_eval["commit"] == "04ec33d8bf1c42e8bd6b3530407372d5a1c2715b"
    assert runtime_eval["contract_version"] == "1.3"
    assert runtime_eval["contract_canonical_sha256"] == "8a22d73149d38177f7cdcb29a955d6245905d09edfdc34974f5af2c81a9b6873"
    assert runtime_eval["runtime_portability_certifier"] == "tools/control_plane/runtime_portability.py"
    assert runtime_eval["runtime_portability_certifier_test"] == "tests/test_runtime_portability_certifier.sh"
    assert runtime_eval["runtime_portability_qualification_manifest"] == "manifests/long_term_asset_qualification.json"
    assert runtime_eval["runtime_portability_cli_contract"] == "tools/control_plane/cli.py"
    assert runtime_eval["runtime_portability_evidence_level"] == "R2-real-provider-substitution"
    assert runtime_eval["runtime_portability_status"] == "certifier-ready-real-evidence-pending"

    validation = runtime_eval["validation"]
    for marker in (
        "R1_CODEX_CLAUDE",
        "R2_POLICY",
        "R2_CERTIFIER_READY",
        "REAL_EVIDENCE_PENDING",
        "BLOCKER_PRESERVED",
    ):
        assert marker in validation

    claude = lock["runtime_bindings"]["claude-code"]
    assert claude["commit"] == "8cd87956507f9dbde0438c9135493c96f3b2d318"
    assert claude["runtime_readiness"] == "SOURCE_SET_READY_R1"
    assert claude["verified_runtime_execution_receipt"] == "PENDING"
    assert claude["r2_real_provider_substitution"] == "PENDING"

    assert lock["rules"]["terminal_replaceability_requires_r2_real_provider_substitution"] is True
    assert lock["rules"]["r1_binding_conformance_is_not_terminal_replaceability"] is True
    assert lock["rules"]["r2_certifier_readiness_does_not_imply_terminal_replaceability"] is True


def test_capability_projection_keeps_policy_certifier_and_real_evidence_separate() -> None:
    capability = yaml.safe_load(CAPABILITY.read_text(encoding="utf-8"))
    runtime_eval = capability["roles"]["runtime_practice_eval"]
    caps = runtime_eval["capabilities"]

    assert runtime_eval["evidence"] == {
        "identity_ref": "config/integrations/cross-repo-lock.json#/providers/runtime_practice_eval",
        "checkout_verification": "permanent-digital-worker-ci",
    }
    assert caps["runtime_binding_comparison"] == "r2-policy-ready"
    assert caps["exact_release_source_set_comparison"] == "r2-policy-ready"
    assert caps["runtime_portability_certifier"] == "native-fail-closed"
    assert caps["runtime_portability_certifier_readiness"] == "certifier-ready-real-evidence-pending"
    assert caps["r2_real_provider_evidence"] == "pending-external-evidence"
    assert caps["terminal_replaceability"] == "blocked-until-r2-real-provider-evidence"
    assert caps["production_runtime"] == "unsupported-by-design"
    assert capability["rules"]["r2_certifier_readiness_does_not_imply_terminal_replaceability"] is True
