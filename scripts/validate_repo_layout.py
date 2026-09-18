#!/usr/bin/env python3
"""Validate terminal digital-worker repository layout."""
from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
CORE = ROOT / "嵌入式系统专家团-核心参考"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    required_files = [
        ROOT / "README.md",
        ROOT / "SKILLS.md",
        EDGE / "domain.yaml",
        EDGE / "coordination.yaml",
        EDGE / "routing.yaml",
        EDGE / "gate-policy.yaml",
        EDGE / "skills.yaml",
        EDGE / "runtime/task-modes.yaml",
        EDGE / "runtime/workflow.yaml",
        EDGE / "runtime/action-policy.yaml",
        EDGE / "runtime/material-requirements.yaml",
        EDGE / "pilot/pilot-plan.yaml",
        EDGE / "knowledge/registry.yaml",
        EDGE / "evaluation/golden-cases.yaml",
        EDGE / "evaluation/skill-evaluation-plan.yaml",
        EDGE / "assurance/verification.yaml",
        EDGE / "assurance/review.yaml",
        CORE / "README.md",
    ]
    for path in required_files:
        require(path.is_file(), f"required terminal asset missing: {path.relative_to(ROOT)}")
    require(not (ROOT / "expert-groups" / "embedded-system").exists(), "retired embedded legacy tree must be absent")
    require(not (EDGE / "compatibility").exists(), "retired 1+7 compatibility mapping must be absent")
    require(not (EDGE / "routing-shadow.yaml").exists(), "migration shadow routing must be absent")

    domain = yaml.safe_load((EDGE / "domain.yaml").read_text(encoding="utf-8"))
    require(domain["status"] == "canonical-v1", "domain must be canonical-v1")
    require(domain["execution"]["authority"] == "canonical", "target execution authority must be canonical")
    require(domain["execution"]["legacy_compatibility_removed"] is True, "legacy compatibility removal must be explicit")
    require(domain["product_readiness"]["controls_routing_authority"] is False, "product readiness must be decoupled from routing")

    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    skills_overview = (ROOT / "SKILLS.md").read_text(encoding="utf-8")
    for marker in ["Edge Foundation", "canonical", "Product readiness"]:
        require(marker.lower() in root_readme.lower(), f"root README missing terminal marker: {marker}")
    require("SKILLS.md" in root_readme, "root README must link the Skill review index")
    require("23 个 canonical Skill" in skills_overview and "仍统一保持 DEFINED" in skills_overview, "root SKILLS review baseline drift")

    require(len(list((EDGE / "skills").glob("*/SKILL.md"))) == 23, "target Skill tree must contain exactly 23 current Skill contracts")
    require(len(list((EDGE / "experts/embedded-system/capabilities").glob("*.yaml"))) == 5, "Embedded System Expert must contain exactly five current Capability contracts")
    print("repository layout validation PASS: canonical Edge Foundation runtime is self-contained; retired embedded compatibility tree absent")


if __name__ == "__main__":
    main()
