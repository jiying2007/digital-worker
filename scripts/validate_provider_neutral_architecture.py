#!/usr/bin/env python3
"""Fail-closed checks for the provider-neutral AI R&D architecture baseline."""
from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
EMB = ROOT / "expert-groups" / "embedded-system"
CORE = ROOT / "嵌入式系统专家团-核心参考"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_yaml(path: Path):
    return yaml.safe_load(text(path))


def main() -> None:
    workflow_doc = ROOT / "研发中心AI数字员工研发流程规划.md"
    adr1 = ROOT / "docs/adr/ADR-001-workbuddy-codex-integration-boundary.md"
    adr2 = ROOT / "docs/adr/ADR-002-embedded-system-expert-team-architecture.md"
    adr3 = ROOT / "docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md"
    core_arch = CORE / "01-架构设计/01 总体架构设计.md"
    core_boundary = CORE / "01-架构设计/02 系统边界与控制面.md"

    for path in [workflow_doc, adr1, adr2, adr3, core_arch, core_boundary]:
        require(path.is_file(), f"missing architecture asset: {path.relative_to(ROOT)}")

    workflow_text = text(workflow_doc)
    require("- 文档版本：3" in workflow_text, "canonical R&D workflow must be document version 3")
    require("Provider 可替换，Contract 稳定" in workflow_text, "canonical workflow must state provider-neutral principle")
    require("Knowledge Source" in workflow_text and "Knowledge Provider" in workflow_text, "canonical workflow must separate knowledge source/provider")
    require("Engineering Agent Runtime" in workflow_text, "canonical workflow must use Engineering Agent Runtime abstraction")

    require("- Status: superseded-in-part" in text(adr1), "ADR-001 must be superseded-in-part")
    require("ADR-003" in text(adr1), "ADR-001 must point to ADR-003")
    require("ADR-003-provider-neutral-ai-rd-target-architecture.md" in text(adr2), "ADR-002 must relate to ADR-003")
    require("Provider-neutral" in text(adr3), "provider-neutral architecture declaration missing")
    require("- Status: proposed-for-review" in text(adr3), "ADR-003 status must remain truthful until formally accepted")
    require("Provider-neutral" in text(core_arch), "human architecture guide must explain provider-neutral behavior")
    require("Knowledge Source" in text(core_boundary) and "Knowledge Provider" in text(core_boundary), "human boundary guide must separate knowledge sources/providers")

    expert_group = load_yaml(EMB / "expert-group.yaml")
    require(expert_group.get("architecture_model") == "provider-neutral", "expert-group architecture_model must be provider-neutral")
    require(expert_group["ssot"].get("provider_binding") == "not_frozen", "expert-group provider binding must remain not_frozen")
    require(expert_group["engineering_runtime"].get("execution_role") == "engineer-plus-engineering-agent", "engineering runtime role must be provider-neutral")
    require(expert_group["engineering_runtime"].get("provider_selection") == "not_frozen", "engineering runtime provider selection must remain not_frozen")
    require(expert_group["knowledge"].get("source_of_truth_policy") == "stays_at_source", "knowledge source-of-truth policy must stay_at_source")
    require(expert_group["knowledge"].get("provider_selection") == "not_frozen", "knowledge provider selection must remain not_frozen")

    workflow = load_yaml(EMB / "config/workflow.yaml")
    require(workflow.get("architecture_model") == "provider-neutral", "embedded workflow must be provider-neutral")
    execution = next(stage for stage in workflow["stages"] if stage["id"] == "phase.execution")
    require(execution.get("owner") == "engineer-plus-engineering-agent", "phase.execution owner must be provider-neutral")
    require(execution.get("runtime_provider") == "selectable", "phase.execution runtime provider must be selectable")
    require(execution.get("interaction_provider_direct_control") == "forbidden_by_default", "direct interaction-provider control must be forbidden by default")

    handoff = load_yaml(EMB / "contracts/engineering-handoff.yaml")
    exec_handoff = handoff["stages"]["engineering_execution"]
    require(exec_handoff.get("executor_role") == "engineer-plus-engineering-agent", "engineering handoff executor role must be provider-neutral")
    require(exec_handoff.get("runtime_provider") == "selectable", "engineering handoff runtime provider must be selectable")

    forbidden_machine_tokens = {"engineer-plus-codex", "direct_workbuddy_control", "human_canonical_store", "ai_retrieval_layer"}
    violations: list[str] = []
    for path in EMB.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".yaml", ".yml", ".json", ".py"}:
            continue
        content = text(path)
        for token in forbidden_machine_tokens:
            if token in content:
                violations.append(f"{path.relative_to(ROOT)} -> {token}")
    require(not violations, "provider-specific compatibility residue found: " + "; ".join(violations))

    print("provider-neutral architecture validation PASS: machine contracts and human architecture guide remain provider-independent")


if __name__ == "__main__":
    main()
