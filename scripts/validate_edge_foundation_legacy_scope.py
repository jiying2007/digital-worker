#!/usr/bin/env python3
"""Validate that the legacy embedded surface is execution/rollback compatibility only."""
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
    scope_path = LEGACY / "compatibility-scope.yaml"
    group_path = LEGACY / "expert-group.yaml"
    domain_path = EDGE / "domain.yaml"
    evaluator_path = ROOT / "scripts" / "evaluate_edge_foundation_shadow.py"
    legacy_golden_path = LEGACY / "tests" / "golden-cases.yaml"
    target_golden_path = EDGE / "evaluation" / "golden-cases.yaml"

    for path in [scope_path, group_path, domain_path, evaluator_path, legacy_golden_path, target_golden_path]:
        require(path.is_file(), f"missing legacy-scope asset: {path.relative_to(ROOT)}")

    scope = load(scope_path)
    group = load(group_path)
    domain = load(domain_path)

    require(scope["status"] == "execution-adapter-only", "legacy scope status drift")
    require(scope["canonical_ownership"] is False, "legacy surface must not retain canonical ownership")
    require(scope["canonical_routing_switched"] is False, "legacy scope must reflect unswitched canonical routing")
    require(scope["canonical_routing_switched"] == domain["migration"]["canonical_routing_switched"], "legacy scope routing state disagrees with target domain")
    require(group["semantic_lifecycle"]["status"] == "legacy-compatibility-surface", "legacy expert-group lifecycle drift")
    require(group["semantic_lifecycle"]["direct_removal_forbidden"] is True, "physical removal must remain blocked before switch")
    require(group["semantic_lifecycle"]["no_new_legacy_expert_roles"] is True, "new legacy Expert roles must remain forbidden")

    expected_targets = {
        "domain": EDGE / "domain.yaml",
        "coordination": EDGE / "coordination.yaml",
        "embedded_expert": EDGE / "experts" / "embedded-system" / "expert.yaml",
        "skill_ownership": EDGE / "skills.yaml",
        "gate_ownership": EDGE / "gate-policy.yaml",
        "verification": EDGE / "assurance" / "verification.yaml",
        "review": EDGE / "assurance" / "review.yaml",
        "evaluation": target_golden_path,
        "identity_mapping": EDGE / "compatibility" / "embedded-1plus7-mapping.yaml",
    }
    for key, expected in expected_targets.items():
        resolved = (scope_path.parent / scope["canonical_target"][key]).resolve()
        require(resolved == expected.resolve(), f"legacy scope target pointer drift: {key}")
        require(resolved.is_file(), f"legacy scope target missing: {key}")

    expected_legacy_modes = {
        "expert_group": ("expert-group.yaml", "execution-and-rollback-adapter"),
        "expert_io": ("contracts/experts", "execution-adapter-only"),
        "skill_registry": ("config/p0-skills.yaml", "execution-registry-mirror"),
        "gate_policy": ("config/gate-policy.yaml", "execution-policy-mirror"),
        "golden_cases": ("tests/golden-cases.yaml", "retired-pointer-to-target-authority"),
        "task_modes": ("config/task-modes.yaml", "canonical-execution-until-switch"),
    }
    for key, (rel, mode) in expected_legacy_modes.items():
        item = scope["legacy_assets"][key]
        require(item["path"] == rel, f"legacy asset path drift: {key}")
        require(item["mode"] == mode, f"legacy asset mode drift: {key}")
        require((LEGACY / rel).exists(), f"legacy execution/compatibility asset missing before switch: {key}")

    rules = scope["rules"]
    for key in [
        "no_new_legacy_expert_identity",
        "no_new_canonical_ownership_in_legacy_surface",
        "target_assets_must_not_depend_on_legacy_identity",
        "legacy_execution_semantics_must_remain_regression_tested_until_switch",
        "target_evaluation_is_only_golden_case_authority",
        "legacy_golden_dataset_forbidden",
        "legacy_golden_path_may_only_be_retired_pointer",
        "physical_removal_before_canonical_switch_forbidden",
        "phase4_deprecation_after_switch_and_soak",
        "phase5_physical_removal_after_zero-live-reference-proof",
    ]:
        require(rules[key] is True, f"legacy scope safety rule disabled: {key}")

    legacy_golden = load(legacy_golden_path)
    require(legacy_golden.get("retired") is True, "legacy Golden path must be a retired pointer")
    require("cases" not in legacy_golden, "legacy Golden dataset must stay physically absent")
    authority = (legacy_golden_path.parent / legacy_golden["authority"]).resolve()
    require(authority == target_golden_path.resolve(), "legacy Golden pointer must resolve to target authority")
    require(authority.is_file(), "target Golden authority missing")

    target_golden = load(target_golden_path)
    require(len(target_golden.get("cases", [])) == 12, "target Golden authority must keep current 12-case baseline")
    require(target_golden["rules"]["legacy_expert_identity_forbidden"] is True, "target Golden authority must reject legacy Expert identity")

    evaluator_text = evaluator_path.read_text(encoding="utf-8")
    require('DOMAIN_ROOT / "evaluation" / "golden-cases.yaml"' in evaluator_text, "shadow evaluator must use target Golden Cases")
    require('LEGACY_ROOT / "tests" / "golden-cases.yaml"' not in evaluator_text, "shadow evaluator must not use legacy Golden path as evaluation authority")
    require('LEGACY_ROOT / "config" / "task-modes.yaml"' in evaluator_text, "legacy task modes must remain the execution input before canonical switch")

    print(
        "edge-foundation legacy scope validation PASS: execution/rollback adapters remain bounded; "
        "target ownership/evaluation is canonical; legacy Golden path is pointer-only; physical removal remains gated"
    )


if __name__ == "__main__":
    main()
