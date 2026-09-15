#!/usr/bin/env python3
"""Fail-closed validation for the target-first embedded core reference."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "嵌入式系统专家团-核心参考"
EDGE = ROOT / "domains" / "edge-foundation"
LEGACY = ROOT / "expert-groups" / "embedded-system"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def read(rel: str) -> str:
    return (CORE / rel).read_text(encoding="utf-8")


def validate_links() -> None:
    pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    broken: list[str] = []
    for doc in CORE.rglob("*.md"):
        for raw in pattern.findall(doc.read_text(encoding="utf-8")):
            target = raw.strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = unquote(target.split("#", 1)[0])
            if not target:
                continue
            resolved = (doc.parent / target).resolve()
            if ROOT.resolve() not in resolved.parents and resolved != ROOT.resolve():
                broken.append(f"{doc.relative_to(ROOT)} -> escapes repo: {raw}")
            elif not resolved.exists():
                broken.append(f"{doc.relative_to(ROOT)} -> missing: {raw}")
    require(not broken, "broken core-reference links: " + "; ".join(broken))


def main() -> None:
    expected_top_dirs = {
        "01-责任模型与协作",
        "02-架构设计",
        "03-流程与运行",
        "04-专业能力",
        "05-工程交付",
        "06-治理与评审",
        "07-案例",
        "附录",
    }
    actual_top_dirs = {p.name for p in CORE.iterdir() if p.is_dir()}
    require(actual_top_dirs == expected_top_dirs, f"core information architecture drift: {sorted(actual_top_dirs)}")
    require(not (CORE / "01-数字组织与岗位").exists(), "legacy digital-position directory must stay removed")

    required = [
        "README.md",
        "01-责任模型与协作/01 责任模型总览.md",
        "01-责任模型与协作/02 责任协作与RACI.md",
        "01-责任模型与协作/03 跨域协作与边界.md",
        "02-架构设计/01 总体架构设计.md",
        "02-架构设计/02 系统边界与控制面.md",
        "02-架构设计/03 身份证据与知识架构.md",
        "02-架构设计/04 质量属性与非功能约束.md",
        "03-流程与运行/01 任务生命周期与Gate.md",
        "03-流程与运行/02 Debug问题闭环流程.md",
        "03-流程与运行/03 功能开发Bring-up与多仓协同.md",
        "03-流程与运行/04 验证评审发布与异常恢复.md",
        "03-流程与运行/05 任务类型运行矩阵.md",
        "04-专业能力/01 嵌入式架构能力域指南.md",
        "04-专业能力/02 Linux BSP能力域指南.md",
        "04-专业能力/03 MCU RTOS能力域指南.md",
        "04-专业能力/04 驱动与组件能力域指南.md",
        "04-专业能力/05 调试与可靠性能力域指南.md",
        "05-工程交付/01 Skill能力地图.md",
        "05-工程交付/02 工程交接Runtime与关键产物.md",
        "05-工程交付/03 完整任务产物样例.md",
        "06-治理与评审/01 评审说明与决策清单.md",
        "06-治理与评审/02 权限安全风险与例外.md",
        "06-治理与评审/03 Pilot指标成熟度与生产化.md",
        "06-治理与评审/04 架构取舍与演进原则.md",
        "06-治理与评审/05 Verification责任与证据.md",
        "06-治理与评审/06 Independent Review与发布边界.md",
        "07-案例/01 UBIFS只读问题走查.md",
        "07-案例/02 多仓功能与OTA发布走查.md",
        "07-案例/03 MCU HardFault与RTOS并发走查.md",
        "07-案例/04 新板Bring-up走查.md",
        "07-案例/05 器件替代兼容性走查.md",
        "附录/术语与缩写.md",
    ]
    for rel in required:
        path = CORE / rel
        require(path.is_file(), f"missing core reference: {rel}")
        if path.suffix == ".md":
            require(len(path.read_text(encoding="utf-8").strip()) >= 350, f"core reference too thin: {rel}")

    domain = load_yaml(EDGE / "domain.yaml")
    experts = {item["id"]: item for item in domain["experts"]}
    require(set(experts) == {"structure-expert", "hardware-expert", "embedded-system-expert"}, "core reference requires exactly three Edge Domain Experts")
    embedded_caps = set(experts["embedded-system-expert"]["capabilities"])
    expected_caps = {
        "embedded.architecture",
        "embedded.linux-bsp",
        "embedded.mcu-rtos",
        "embedded.driver-component",
        "embedded.debug-reliability",
    }
    require(embedded_caps == expected_caps, f"Embedded Capability set drift: {sorted(embedded_caps)}")
    require(domain["coordination_role"]["id"] == "edge-coordination", "Edge Coordination role drift")
    require(set(domain["assurance"]["responsibilities"]) == {"verification", "review"}, "Assurance responsibility drift")
    require(domain["migration"]["canonical_routing_switched"] is False, "core reference validator assumes canonical routing remains unswitched")

    index = read("README.md")
    for marker in ["运行参考（Operational Reference）", "唯一第一入口", "ADR-004", "iterative-development", "canonical_routing_switched=false"]:
        require(marker in index, f"core README missing target marker: {marker}")
    for marker in ["Structure Expert", "Hardware Expert", "Embedded System Expert", "Edge Coordination Role", "Verification", "Independent Review"]:
        require(marker in index, f"core README missing responsibility marker: {marker}")

    responsibility = read("01-责任模型与协作/01 责任模型总览.md")
    for expert_id in experts:
        require(expert_id in responsibility, f"responsibility overview missing Expert id: {expert_id}")
    for capability_id in sorted(expected_caps):
        require(capability_id in responsibility, f"responsibility overview missing Capability id: {capability_id}")

    capability_files = sorted((CORE / "04-专业能力").glob("*.md"))
    require(len(capability_files) == 5, f"04-专业能力 must contain exactly five Embedded Capability guides, got {len(capability_files)}")
    for path in capability_files:
        text = path.read_text(encoding="utf-8")
        for heading in ["## 1. 领域定位", "## 2. 典型任务", "## 3. 必要输入", "## 4. 分析方法", "## 5. Evidence 要求", "## 6. 输出", "## 7. 协作与交接", "## 8. 常见错误", "## 9. BLOCK 条件"]:
            require(heading in text, f"Capability guide template drift: {path.relative_to(ROOT)} missing {heading}")
    professional_text = "\n".join(path.read_text(encoding="utf-8") for path in capability_files)
    require("Verification 属于 Assurance" not in professional_text, "Verification must not be reintroduced as Embedded Capability")

    skills = load_yaml(EDGE / "skills.yaml")["skills"]
    require(len(skills) == 23, f"expected current 23 Skill baseline, got {len(skills)}")
    skill_map = read("05-工程交付/01 Skill能力地图.md")
    for item in skills:
        require(item["id"] in skill_map, f"Skill map missing target Skill: {item['id']}")
        require(item["owner_id"] in skill_map, f"Skill map missing target owner: {item['id']} -> {item['owner_id']}")

    shadow = load_yaml(EDGE / "routing-shadow.yaml")
    matrix = read("03-流程与运行/05 任务类型运行矩阵.md")
    require(len(shadow["routing"]) == 14, "expected 14 target task routes")
    for task_type, route in shadow["routing"].items():
        row = next((line for line in matrix.splitlines() if line.startswith(f"| `{task_type}` |")), None)
        require(row is not None, f"target task matrix missing: {task_type}")
        require(route["target_mode"] in row, f"target mode drift in task matrix: {task_type}")
        for capability in route.get("capabilities", []):
            require(capability.removeprefix("embedded.") in row or capability in row, f"target Capability missing from task matrix: {task_type} -> {capability}")
        for assurance in route.get("assurance", []):
            require(assurance in row, f"Assurance missing from task matrix: {task_type} -> {assurance}")

    gate_policy = load_yaml(EDGE / "gate-policy.yaml")
    workflow_text = read("03-流程与运行/01 任务生命周期与Gate.md")
    for gate_id in gate_policy["gates"]:
        human = gate_id.split(".", 1)[1].upper()
        require(f"Gate {human}" in workflow_text, f"workflow guide missing target Gate: {gate_id}")

    golden = load_yaml(EDGE / "evaluation/golden-cases.yaml")
    case_ids = [item["id"] for item in golden["cases"]]
    require(len(case_ids) == 12 and len(case_ids) == len(set(case_ids)), "target Golden Case baseline must contain 12 unique cases")
    require(golden["rules"]["legacy_expert_identity_forbidden"] is True, "target Golden Cases must reject legacy identities")

    legacy_group = load_yaml(LEGACY / "expert-group.yaml")
    legacy_ids = {legacy_group["team_lead"]["id"], *(item["id"] for item in legacy_group["experts"])}
    forbidden_hits: list[str] = []
    p_pattern = re.compile(r"\bP0[1-8]\b")
    for path in list(CORE.rglob("*.md")) + list(CORE.rglob("*.yaml")) + list(CORE.rglob("*.yml")):
        text = path.read_text(encoding="utf-8")
        for legacy_id in sorted(legacy_ids):
            if legacy_id in text:
                forbidden_hits.append(f"{path.relative_to(ROOT)} -> {legacy_id}")
        if p_pattern.search(text):
            forbidden_hits.append(f"{path.relative_to(ROOT)} -> P01-P08")
        for token in ["1+7", "数字岗位", "human-view.yaml"]:
            if token in text:
                forbidden_hits.append(f"{path.relative_to(ROOT)} -> {token}")
    require(not forbidden_hits, "legacy organization semantics leaked into core reference: " + "; ".join(sorted(set(forbidden_hits))))

    legacy_golden = LEGACY / "tests/golden-cases.yaml"
    if legacy_golden.exists():
        pointer = load_yaml(legacy_golden)
        require(pointer.get("retired") is True, "legacy Golden path may only remain as retired pointer")
        require("cases" not in pointer, "legacy Golden path must not contain a second case dataset")
        require(pointer.get("authority") == "../../../domains/edge-foundation/evaluation/golden-cases.yaml", "legacy Golden pointer must resolve to target authority")

    validate_links()
    print("core reference validation PASS: target-first 3 Experts / 5 Embedded Capabilities / Assurance model; legacy organization leakage forbidden")


if __name__ == "__main__":
    main()
