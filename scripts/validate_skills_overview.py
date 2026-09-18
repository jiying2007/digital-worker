#!/usr/bin/env python3
"""Fail-closed synchronization for the root reviewer-facing SKILLS.md."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
OVERVIEW = ROOT / "SKILLS.md"
REGISTRY = EDGE / "skills.yaml"

LEGACY_IDS = {
    "embedded-system-team-lead",
    "embedded-architecture-expert",
    "linux-bsp-expert",
    "mcu-rtos-expert",
    "driver-component-expert",
    "debug-reliability-expert",
    "verification-expert",
    "embedded-review-governor",
}

CANDIDATES = {
    "power-state-analysis",
    "ota-bootloader-analysis",
    "watchdog-reset-analysis",
    "device-substitution-qualification",
    "production-calibration-test-analysis",
    "long-run-soak-analysis",
    "latency-jitter-analysis",
    "kernel-config-diff-review",
    "flash-ecc-badblock-analysis",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    require(OVERVIEW.is_file(), "root SKILLS.md is missing")
    text = OVERVIEW.read_text(encoding="utf-8")
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    skills = registry["skills"]

    require(len(skills) == 23, "canonical Skill registry baseline drift")
    for item in skills:
        for marker in [item["id"], item["owner_id"], item["path"]]:
            require(marker in text, f"SKILLS.md missing canonical registry marker: {item['id']} -> {marker}")

    for candidate in CANDIDATES:
        require(candidate in text, f"SKILLS.md missing planning candidate: {candidate}")

    required_markers = [
        "reviewer-facing index",
        "不是第二份 Skill Registry",
        "23 个 canonical Skill",
        "Total Skill evaluation cases",
        "46",
        "Skill definition ≠ Skill maturity",
        "Skill maturity ≠ Product readiness",
        "Candidate Skill 规划池（非 canonical）",
        "Skill Evaluation Plan",
        "Skill Invocation Receipt",
        "Skill Evaluation Receipt",
        "Skill Evaluation Summary",
        "portability_proven = false",
        "product_readiness_inherited = false",
        "仍统一保持 DEFINED",
    ]
    for marker in required_markers:
        require(marker in text, f"SKILLS.md missing review boundary marker: {marker}")

    leaked = sorted(identity for identity in LEGACY_IDS if identity in text)
    require(not leaked, f"legacy Expert identity leaked into SKILLS.md: {leaked}")

    print("SKILLS overview validation PASS: 23 canonical Skills / 9 non-canonical candidates / evidence-bound maturity semantics")


if __name__ == "__main__":
    main()
