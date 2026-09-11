#!/usr/bin/env python3
"""Fail-closed validation for the architecture review readiness pack."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "review"


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def text(name: str) -> str:
    path = REVIEW / name
    require(path.is_file(), f"missing review file: {path}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    index = text("README.md")
    pre = text("architecture-review-pre-read.md")
    decisions = text("architecture-review-decision-matrix.md")
    gaps = text("architecture-review-evidence-gaps.md")
    raci = text("architecture-review-raci.md")
    walks = text("architecture-review-walkthroughs.md")

    require("review-candidate" in index, "review pack must declare review-candidate status")
    require("Production Ready" in index and "不评" in index, "review scope/non-goal boundary missing")
    require("Provider-neutral" in pre or "Provider-neutral" in index, "provider-neutral baseline missing")

    missing_decisions = [f"D{i:02d}" for i in range(1, 13) if f"D{i:02d}" not in decisions]
    require(not missing_decisions, f"missing review decisions: {missing_decisions}")

    missing_gaps = [f"A{i:03d}" for i in range(1, 13) if f"A{i:03d}" not in gaps]
    require(not missing_gaps, f"missing evidence gaps: {missing_gaps}")

    for role in ["Embedded Engineering Owner", "AI/Platform Owner", "Knowledge Owner", "Verification/HIL Owner", "IT/Security", "Release Owner"]:
        require(role in raci, f"missing RACI role: {role}")

    for case in ["Walkthrough A", "Walkthrough B", "Walkthrough C"]:
        require(case in walks, f"missing walkthrough: {case}")

    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs_readme = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    core_readme = (ROOT / "嵌入式系统专家团-核心参考" / "README.md").read_text(encoding="utf-8")
    require("docs/review/" in root_readme, "root README must link review pack")
    require("review/" in docs_readme, "docs README must index review directory")
    require("docs/review/" in core_readme, "core reference must link review pack")

    print("architecture review readiness validation PASS: 12 decisions, 12 gaps, RACI and 3 walkthroughs present")


if __name__ == "__main__":
    main()
