#!/usr/bin/env python3
"""Fail-closed checks for the provider-neutral AI R&D architecture baseline."""
from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
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
    core_arch = CORE / "02-架构设计/01 总体架构设计.md"
    core_boundary = CORE / "02-架构设计/02 系统边界与控制面.md"
    domain_path = EDGE / "domain.yaml"
    runtime_path = EDGE / "runtime/workflow.yaml"

    for path in [workflow_doc, adr1, adr2, adr3, core_arch, core_boundary, domain_path, runtime_path]:
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
    require("Provider-neutral" in text(core_arch), "human architecture guide must explain provider-neutral behavior")
    require("Knowledge Source" in text(core_boundary) and "Knowledge Provider" in text(core_boundary), "human boundary guide must separate knowledge sources/providers")

    domain = load_yaml(domain_path)
    require(domain["architecture_model"] == "provider-neutral", "Edge Foundation architecture_model must remain provider-neutral")
    require(domain["runtime_topology"] == "not_frozen", "runtime topology must remain replaceable")
    require(domain["orchestration"]["provider_binding"] == "not_frozen", "orchestration provider must remain unfrozen")
    require(domain["orchestration"]["implementation_binding"] == "not_frozen", "orchestration implementation must remain unfrozen")
    require(domain["coordination_role"]["runtime_binding"] == "not_frozen", "coordination runtime must remain unfrozen")
    require(domain["knowledge"]["source_of_truth_policy"] == "stays_at_source", "knowledge Source of Truth policy drift")
    require(domain["knowledge"]["knowledge_provider_binding"] == "not_frozen", "knowledge provider must remain unfrozen")
    require(domain["execution"]["authority"] == "canonical", "provider-neutral validation expects canonical target execution")
    require(domain["execution"]["responsibility_separation_required"] is True, "execution responsibility separation disabled")

    forbidden_assumptions = set(domain["orchestration"]["forbidden_assumptions"])
    require({"workbuddy-is-required", "one-expert-equals-one-agent", "capability-equals-agent"} <= forbidden_assumptions, "provider/runtime decoupling invariant drift")

    forbidden_machine_tokens = {"engineer-plus-codex", "direct_workbuddy_control", "human_canonical_store", "ai_retrieval_layer"}
    violations: list[str] = []
    scan_roots = [EDGE, ROOT / "contracts", ROOT / "config/integrations"]
    for scan_root in scan_roots:
        for path in scan_root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".yaml", ".yml", ".json", ".py"}:
                continue
            content = text(path)
            for token in forbidden_machine_tokens:
                if token in content:
                    violations.append(f"{path.relative_to(ROOT)} -> {token}")
    require(not violations, "provider-specific active residue found: " + "; ".join(violations))

    print("provider-neutral architecture validation PASS: canonical Edge Foundation contracts and human architecture remain provider-independent")


if __name__ == "__main__":
    main()
