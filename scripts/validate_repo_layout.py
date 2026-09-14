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
    core = ROOT / "嵌入式系统专家团-核心参考"

    require(canonical_workflow.is_file(), "missing canonical R&D workflow")
    require(archived_v1.is_file(), "missing archived V1 workflow")
    require(adr3.is_file(), "missing provider-neutral target architecture ADR-003")
    require((source_root / "研发中心AI数字员工办公体系改造方案（预案）.docx").is_file(), "missing office source material")
    require((source_root / "端侧底座专家团创建.docx").is_file(), "missing edge-foundation source material")
    require((source_root / "硬件电路/硬件电路开发模块（举例）.docx").is_file(), "missing hardware source material")

    root_docx = sorted(path.name for path in ROOT.glob("*.docx"))
    require(not root_docx, f"raw docx files are forbidden at repository root: {root_docx}")
    versioned_active = sorted(path.name for path in ROOT.glob("*.md") if re.search(r"_V\d+\.md$", path.name, re.IGNORECASE))
    require(not versioned_active, f"versioned active markdown is forbidden at repository root: {versioned_active}")
    require(not (ROOT / "硬件电路-举例").exists(), "legacy hardware example directory must not return to root")
    require(not (ROOT / "docs/architecture/embedded-system-expert-team-v1.md").exists(), "superseded embedded architecture V1 must stay removed")
    require(not (ROOT / "docs/review").exists(), "superseded docs/review pack must stay removed")
    require(not (ROOT / "docs/strategy/four-control-planes-runtime-bindings.md").exists(), "superseded control-plane transition strategy must stay removed")
    require(not (ROOT / "docs/strategy/four-repo-ai-operating-system.md").exists(), "superseded four-repo transition strategy must stay removed")

    workflow_text = canonical_workflow.read_text(encoding="utf-8")
    require(workflow_text.startswith("# 研发中心 AI 数字员工研发流程规划\n"), "canonical workflow title must be unversioned")
    require("- 文档版本：3" in workflow_text, "canonical workflow must carry document version 3 metadata")
    require("docs/archive/" in workflow_text, "canonical workflow must preserve historical archive policy")
    require("ADR-003" in workflow_text, "canonical workflow must reference ADR-003")

    root_readme = read("README.md")
    require("研发中心AI数字员工研发流程规划.md" in root_readme, "root README must link canonical workflow")
    require("ADR-003" in root_readme, "root README must expose provider-neutral ADR-003")
    require("operational-reference" in root_readme, "root README must expose operational core-reference status")
    require("review-ready" not in root_readme, "stale review-ready status is forbidden in root README")

    core_readme = read("嵌入式系统专家团-核心参考/README.md")
    require("运行参考（operational reference）" in core_readme, "embedded core reference must be operational reference")
    require("review-ready" not in core_readme, "review-era status must not remain in core reference index")

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

    forbidden_tokens = ["研发中心AI数字员工研发流程规划_V2.md", "docs/architecture/embedded-system-expert-team-v1.md"]
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

    print("repository layout validation PASS: active docs are converged and superseded review/strategy residue is absent")


if __name__ == "__main__":
    main()
