#!/usr/bin/env python3
"""Validate target Verification/Review Assurance contracts against legacy execution adapters."""
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
    verification_path = EDGE / "assurance" / "verification.yaml"
    review_path = EDGE / "assurance" / "review.yaml"
    legacy_verification_path = LEGACY / "contracts" / "experts" / "verification.io.yaml"
    legacy_review_path = LEGACY / "contracts" / "experts" / "review-governor.io.yaml"
    legacy_group_path = LEGACY / "expert-group.yaml"

    for path in [domain_path, verification_path, review_path, legacy_verification_path, legacy_review_path, legacy_group_path]:
        require(path.is_file(), f"missing Assurance asset: {path.relative_to(ROOT)}")

    domain = load(domain_path)
    verification = load(verification_path)
    review = load(review_path)
    legacy_verification = load(legacy_verification_path)
    legacy_review = load(legacy_review_path)
    legacy_group = load(legacy_group_path)

    require(domain["migration"]["canonical_routing_switched"] is False, "Assurance prep must not switch canonical routing")
    require(domain["assurance"]["independent_from_execution"] is True, "Assurance independence drift")
    require(domain["assurance"]["responsibilities"]["verification"]["contract"] == "assurance/verification.yaml", "Verification contract pointer drift")
    require(domain["assurance"]["responsibilities"]["review"]["contract"] == "assurance/review.yaml", "Review contract pointer drift")

    legacy_ids = {legacy_group["team_lead"]["id"], *(item["id"] for item in legacy_group["experts"])}
    for path in [verification_path, review_path]:
        text = path.read_text(encoding="utf-8")
        leaked = sorted(identity for identity in legacy_ids if identity in text)
        require(not leaked, f"legacy expert identity leaked into target Assurance contract {path.relative_to(ROOT)}: {leaked}")

    for target, legacy, label in [
        (verification, legacy_verification, "Verification"),
        (review, legacy_review, "Review"),
    ]:
        require(target["kind"] == "assurance", f"{label} must be Assurance")
        require(target["status"] == "phase4-prep-target", f"{label} prep status drift")
        require(target["ownership_authority"] == "canonical", f"{label} target responsibility must be canonical")
        require(target["execution_surface"] == "legacy-compatible", f"{label} legacy execution adapter must remain active during prep")
        require(target["consumes"] == legacy["consumes"], f"{label} consumes semantic drift")
        require(target["produces"] == legacy["produces"], f"{label} produces semantic drift")
        require(target["constraints"] == legacy["constraints"], f"{label} constraints semantic drift")
        adapter = (EDGE / target["legacy_execution_adapter"]).resolve()
        require(adapter == (legacy_verification_path if label == "Verification" else legacy_review_path).resolve(), f"{label} legacy adapter pointer drift")
        require(target["rules"]["legacy_expert_identity_forbidden"] is True, f"{label} must forbid legacy expert identity")
        require(target["rules"]["execution_adapter_does_not_define_responsibility"] is True, f"{label} adapter must not define responsibility")
        require(target["rules"]["evidence_source_of_truth_stays_at_source"] is True, f"{label} evidence authority drift")

    require(verification["hands_off_to"] == ["edge-coordination", "assurance.review"], "Verification target handoff drift")
    require(review["hands_off_to"] == ["edge-coordination"], "Review target handoff drift")
    require(verification["independence"]["implementation_may_self_approve"] is False, "implementation self-verification regression")
    require(verification["independence"]["runtime_local_pass_is_verification_pass"] is False, "runtime-local PASS must not become Verification PASS")
    require(verification["independence"]["verification_pass_is_release_approval"] is False, "Verification PASS must not become release approval")
    require(review["independence"]["independent_from_domain_decision"] is True, "Review/domain independence drift")
    require(review["independence"]["independent_from_implementation"] is True, "Review/implementation independence drift")
    require(review["independence"]["implementation_ci_may_self_approve_review"] is False, "implementation CI must not self-approve Review")
    require(review["release_authority"]["review_is_release_approval"] is False, "Review must not become release approval")
    require(review["release_authority"]["human_release_gate_required"] is True, "human release gate must remain required")

    print("edge-foundation Assurance validation PASS: Verification and Independent Review responsibilities de-legacy without semantic or independence regression")


if __name__ == "__main__":
    main()
