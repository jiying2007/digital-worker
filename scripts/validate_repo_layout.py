#!/usr/bin/env python3
"""Fail-closed repository layout and canonical-path validation."""
from __future__ import annotations

from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    canonical_workflow = ROOT / "研发中心AI数字员工研发流程规划.md"
    archived_v1 = ROOT / "docs/archive/研发中心AI数字员工研发流程规划_V1.md"
    source_root = ROOT / "docs/source-materials"
    adr3 = ROOT / "docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md"
    adr4 = ROOT / "docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md"
    domain = ROOT / "domains/edge-foundation/domain.yaml"
    mapping = ROOT / "domains/edge-foundation/compatibility/embedded-1plus7-mapping.yaml"
    pilot_runbook = ROOT / "docs/runbooks/embedded-pilot.md"

    for path, message in [
        (canonical_workflow, "missing canonical R&D workflow"),
        (archived_v1, "missing archived V1 workflow"),
        (adr3, "missing provider-neutral target architecture ADR-003"),
        (adr4, "missing Edge Foundation target architecture ADR-004"),
        (domain, "missing Edge Foundation domain contract"),
        (mapping, "missing legacy identity bridge"),
        (pilot_runbook, "missing canonical embedded Pilot runbook"),
    ]:
        require(path.is_file(), message)

    require((source_root / "研发中心AI数字员工办公体系改造方案（预案）.docx").is_file(), "missing office source material")
    require((source_root / "端侧底座专家团创建.docx").is_file(), "missing edge-foundation source material")
    require((source_root / "硬件电路/硬件电路开发模块（举例）.docx").is_file(), "missing hardware source material")

    root_docx = sorted(path.name for path in ROOT.glob("*.docx"))
    require(not root_docx, f"raw docx files are forbidden at repository root: {root_docx}")
    versioned_active = sorted(path.name for path in ROOT.glob("*.md") if re.search(r"_V\d+\.md$", path.name, re.IGNORECASE))
    require(not versioned_active, f"versioned active markdown is forbidden at repository root: {versioned_active}")

    # Removed transition/review residue must not reappear as active parallel sources.
    removed_paths = [
        "硬件电路-举例",
        "docs/architecture/embedded-system-expert-team-v1.md",
        "docs/review",
        "docs/strategy/four-control-planes-runtime-bindings.md",
        "docs/strategy/four-repo-ai-operating-system.md",
        "docs/strategy/pilot-material-terminal-gate.md",
    ]
    for rel in removed_paths:
        require(not (ROOT / rel).exists(), f"superseded active residue must stay removed: {rel}")

    workflow_text = canonical_workflow.read_text(encoding="utf-8")
    require(workflow_text.startswith("# 研发中心 AI 数字员工研发流程规划\n"), "canonical workflow title must be unversioned")
    require("- 文档版本：3" in workflow_text, "canonical workflow must carry document version 3 metadata")
    require("docs/archive/" in workflow_text, "canonical workflow must preserve historical archive policy")
    require("ADR-003" in workflow_text, "canonical workflow must reference ADR-003")

    root_readme = read("README.md")
    for marker in [
        "研发中心AI数字员工研发流程规划.md",
        "ADR-003",
        "ADR-004",
        "legacy compatibility surface",
        "canonical_routing_switched=false",
        "Debug",
        "Feature",
        "Review / Release",
    ]:
        require(marker in root_readme, f"root README missing current architecture/status marker: {marker}")
    for stale in ["review-ready", "phase-2-dual-evaluation", "no real task bound yet"]:
        require(stale not in root_readme, f"stale root README status returned: {stale}")

    core_readme = read("嵌入式系统专家团-核心参考/README.md")
    for marker in ["运行参考（Operational Reference）", "ADR-004", "legacy", "canonical_routing_switched=false", "真实 Pilot"]:
        require(marker in core_readme, f"embedded core reference missing current marker: {marker}")
    for stale in ["review-ready", "phase-2-dual-evaluation", "real Pilot evidence（当前 blocker）"]:
        require(stale not in core_readme, f"stale core-reference status returned: {stale}")

    embedded_readme = read("expert-groups/embedded-system/README.md")
    require("Legacy Compatibility Surface" in embedded_readme, "embedded machine README must identify the legacy compatibility surface")
    require("canonical_routing_switched = false" in embedded_readme, "embedded machine README must preserve unswitched routing boundary")
    require("1+7 核心专家" not in embedded_readme, "embedded machine README must not present 1+7 as target expert organization")

    runbook_text = pilot_runbook.read_text(encoding="utf-8")
    for marker in [
        "task-brief v1",
        "material_manifest",
        "reproduction OR authoritative log",
        "Verification",
        "Independent Review",
        "edge-shadow",
        "phase3-readiness",
        "compatibility mapping",
    ]:
        require(marker in runbook_text, f"Pilot runbook missing converged operational marker: {marker}")

    expert_group = yaml.safe_load(read("expert-groups/embedded-system/expert-group.yaml"))
    ssot = expert_group["ssot"]
    require(ssot.get("external_repositories") == "reference_only", "external repository policy must use canonical reference_only field")
    require("external_repositories_are_dependencies" not in ssot, "legacy dependency boolean must stay removed")
    require("external_repositories_are_reference_only" not in ssot, "legacy reference boolean must stay removed")
    require("../../研发中心AI数字员工研发流程规划.md" in expert_group["upstream_contracts"], "expert group must reference canonical workflow path")

    ownership = yaml.safe_load(read("expert-groups/embedded-system/contracts/cross-team/edge-foundation-ownership.yaml"))
    require(ownership["source_reference"] == "../../../../docs/source-materials/端侧底座专家团创建.docx", "edge ownership must point to canonical source-materials path")
    resolved_source = (ROOT / "expert-groups/embedded-system/contracts/cross-team" / ownership["source_reference"]).resolve()
    require(resolved_source == (source_root / "端侧底座专家团创建.docx").resolve(), "edge ownership source path resolves incorrectly")
    require(resolved_source.is_file(), "edge ownership source material is missing")

    forbidden_tokens = [
        "研发中心AI数字员工研发流程规划_V2.md",
        "docs/architecture/embedded-system-expert-team-v1.md",
        "docs/strategy/pilot-material-terminal-gate.md",
    ]
    text_suffixes = {".md", ".yaml", ".yml", ".json", ".py"}
    violations: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in text_suffixes:
            continue
        if path.resolve() == SELF or ROOT / "docs/archive" in path.parents:
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            if token in text:
                violations.append(f"{path.relative_to(ROOT)} -> {token}")
    require(not violations, "stale canonical-path references found: " + "; ".join(violations))

    print("repository layout validation PASS: target/compatibility boundaries are explicit and superseded active residue is absent")


if __name__ == "__main__":
    main()
