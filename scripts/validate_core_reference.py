#!/usr/bin/env python3
"""Fail-closed validation for the human-facing embedded-system core reference."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "嵌入式系统专家团-核心参考"
EMB = ROOT / "expert-groups" / "embedded-system"


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def read(rel: str) -> str:
    return (CORE / rel).read_text(encoding="utf-8")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_json(instance_path: Path, schema_path: Path) -> dict:
    schema = load_json(schema_path)
    instance = load_json(instance_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(instance)
    return instance


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
    required = [
        "README.md",
        "00-总览/README.md",
        "00-总览/00 架构与运行总览.md",
        "00-总览/01 数字岗位与能力模型.md",
        "00-评审入口/01 评审说明与决策清单.md",
        "00-评审入口/02 术语与缩写.md",
        "01-架构设计/01 总体架构设计.md",
        "01-架构设计/02 系统边界与控制面.md",
        "01-架构设计/03 身份证据与知识架构.md",
        "01-架构设计/04 质量属性与非功能约束.md",
        "02-流程与运行/01 任务生命周期与Gate.md",
        "02-流程与运行/02 Debug问题闭环流程.md",
        "02-流程与运行/03 功能开发Bring-up与多仓协同.md",
        "02-流程与运行/04 验证评审发布与异常恢复.md",
        "02-流程与运行/05 任务类型运行矩阵.md",
        "03-角色与领域/01 组织模型职责与RACI.md",
        "03-角色与领域/02 跨团队RACI.md",
        "03-角色与领域/03 嵌入式架构领域指南.md",
        "03-角色与领域/04 Linux BSP领域指南.md",
        "03-角色与领域/05 MCU RTOS领域指南.md",
        "03-角色与领域/06 驱动与组件领域指南.md",
        "03-角色与领域/07 调试与可靠性领域指南.md",
        "03-角色与领域/08 验证领域指南.md",
        "03-角色与领域/09 独立审查领域指南.md",
        "04-工程交付/01 Skill能力地图.md",
        "04-工程交付/02 工程交接Runtime与关键产物.md",
        "04-工程交付/03 完整任务产物样例.md",
        "05-治理与评测/01 权限安全风险与例外.md",
        "05-治理与评测/02 Pilot指标成熟度与生产化.md",
        "05-治理与评测/03 架构取舍与演进原则.md",
        "06-案例/01 UBIFS只读问题走查.md",
        "06-案例/02 多仓功能与OTA发布走查.md",
        "06-案例/03 MCU HardFault与RTOS并发走查.md",
        "06-案例/04 新板Bring-up走查.md",
        "06-案例/05 器件替代兼容性走查.md",
    ]
    for rel in required:
        path = CORE / rel
        require(path.is_file(), f"missing core reference: {rel}")
        require(len(path.read_text(encoding="utf-8").strip()) >= 500, f"core reference too thin: {rel}")

    index = read("README.md")
    require("operational reference" in index, "core reference must declare operational reference status")
    require("v0.7.0" in index, "core reference must declare v0.7.0")
    require("iterative-development" in index, "core reference must state current repository stage")
    require("01 数字岗位与能力模型.md" in index, "core reference must expose digital position model")

    expert_group = yaml.safe_load((EMB / "expert-group.yaml").read_text(encoding="utf-8"))
    require(expert_group["version"] == "0.7.0", "unexpected embedded expert-group version")
    require(expert_group["architecture_model"] == "provider-neutral", "embedded architecture must remain provider-neutral")
    require(len(expert_group["experts"]) == 7, "human reference assumes 1+7 expert organization")

    skill_registry = yaml.safe_load((EMB / "config/p0-skills.yaml").read_text(encoding="utf-8"))
    skills = [item["id"] for item in skill_registry["skills"]]
    require(len(skills) == 23, f"expected 23 P0 skills, got {len(skills)}")
    skill_doc = read("04-工程交付/01 Skill能力地图.md")
    missing_skills = [skill for skill in skills if skill not in skill_doc]
    require(not missing_skills, f"skill map missing registered skills: {missing_skills}")

    position_doc = read("00-总览/01 数字岗位与能力模型.md")
    for marker in [
        "不是招聘 JD",
        "6 个职能模块 + 8 个数字岗位",
        "Position = 数字岗位",
        "Agent    = 承担岗位的数字员工",
        "Skill    = 数字员工掌握的岗位技能",
        "数字任职资格模型",
        "岗位替代",
        "positions.yaml",
        "不声明任何岗位已经达到完全替代人工",
    ]:
        require(marker in position_doc, f"digital position model missing marker: {marker}")
    for position_id in [f"P{i:02d}" for i in range(1, 9)]:
        require(position_id in position_doc, f"digital position model missing {position_id}")
    for module_id in [f"M{i}" for i in range(1, 7)]:
        require(module_id in position_doc, f"digital position model missing {module_id}")
    missing_position_skills = [skill for skill in skills if skill not in position_doc]
    require(not missing_position_skills, f"digital position model missing registered skills: {missing_position_skills}")

    architecture = read("01-架构设计/01 总体架构设计.md")
    require("1+7" in architecture, "architecture must explain 1+7 organization")
    require("Provider-neutral" in architecture, "architecture must explain provider-neutral behavior")
    require("四个稳定控制面 + N 个 Runtime Binding" in architecture, "architecture must explain control-plane model")

    identity = read("01-架构设计/03 身份证据与知识架构.md")
    require("Source of Truth stays at source" in identity, "identity/knowledge doc must retain source authority rule")
    require("Acceptance → Evidence" in identity, "identity/knowledge doc must explain acceptance-evidence mapping")

    workflow = read("02-流程与运行/01 任务生命周期与Gate.md")
    for gate in ["Gate K", "Gate M", "Gate 0", "Gate T", "Gate E", "Gate V", "Gate R", "Gate C"]:
        require(gate in workflow, f"workflow doc missing {gate}")

    # The human routing matrix must cover every machine task type and its allowed modes.
    matrix_text = read("02-流程与运行/05 任务类型运行矩阵.md")
    routing = yaml.safe_load((EMB / "config/task-modes.yaml").read_text(encoding="utf-8"))["routing"]
    require(len(routing) == 14, f"expected 14 task types, got {len(routing)}")
    for task_type, cfg in routing.items():
        row = next((line for line in matrix_text.splitlines() if line.startswith(f"|`{task_type}`|")), None)
        require(row is not None, f"task matrix missing task type: {task_type}")
        require(cfg["default_mode"] in row, f"task matrix default mode drift for {task_type}")
        for mode in cfg["allowed_modes"]:
            require(mode in row, f"task matrix allowed mode drift for {task_type}: {mode}")

    safety = read("05-治理与评测/01 权限安全风险与例外.md")
    for level in [f"A{i}" for i in range(8)]:
        require(level in safety, f"safety doc missing {level}")

    pilot = read("05-治理与评测/02 Pilot指标成熟度与生产化.md")
    for marker in ["incorrect_pass_rate = 0", "unauthorized_actions = 0", "audit_trace_completeness = 1.0", "E2 Engineering Closed Loop", "E3 Knowledge Closed Loop"]:
        require(marker in pilot, f"pilot/maturity doc missing marker: {marker}")

    review = read("00-评审入口/01 评审说明与决策清单.md")
    for decision in [f"D{i:02d}" for i in range(1, 11)]:
        require(decision in review, f"review guide missing decision: {decision}")
    for evidence_id in [f"E{i:02d}" for i in range(1, 9)]:
        require(evidence_id in review, f"review guide missing evidence register entry: {evidence_id}")

    # Human-readable artifact chain has a machine-validated sample set.
    example = CORE / "04-工程交付/examples/ubifs-run"
    schema_map = {
        "task-brief.json": ROOT / "schemas/task-brief.v1.schema.json",
        "material-manifest.json": EMB / "schemas/material-manifest.schema.json",
        "task-charter.json": EMB / "schemas/task-charter.schema.json",
        "routing-decision.json": EMB / "schemas/routing-decision.schema.json",
        "technical-analysis.json": EMB / "schemas/technical-analysis.schema.json",
        "hypothesis-registry.json": EMB / "schemas/hypothesis-registry.schema.json",
        "technical-decision.json": EMB / "schemas/technical-decision.schema.json",
        "engineering-task-package.json": EMB / "schemas/engineering-task-package.schema.json",
        "delivery-receipt.json": ROOT / "schemas/delivery-receipt.v1.schema.json",
        "verification-report.json": EMB / "schemas/verification-report.schema.json",
        "review-report.json": EMB / "schemas/review-report.schema.json",
        "deliverable-manifest.json": EMB / "schemas/deliverable-manifest.schema.json",
    }
    docs = {name: validate_json(example / name, schema) for name, schema in schema_map.items()}
    run_id = "EXAMPLE-UBIFS-001"
    for name in ["material-manifest.json", "task-charter.json", "routing-decision.json", "technical-analysis.json", "hypothesis-registry.json", "technical-decision.json", "engineering-task-package.json", "verification-report.json", "review-report.json", "deliverable-manifest.json"]:
        require(docs[name].get("run_id") == run_id, f"example run_id drift: {name}")
    work_item = docs["task-brief.json"]["work_item_id"]
    require(docs["delivery-receipt.json"]["work_item_id"] == work_item, "example work_item identity drift")
    base = docs["task-brief.json"]["base_branch_or_commit"]
    require(docs["engineering-task-package.json"]["base_commit"] == base, "example package base drift")
    require(docs["delivery-receipt.json"]["base_commit"] == base, "example receipt base drift")
    acceptance = (example / "acceptance-evidence-matrix.md").read_text(encoding="utf-8")
    harvest = (example / "knowledge-harvest.md").read_text(encoding="utf-8")
    require(run_id in acceptance and "PASS" in acceptance, "example acceptance/evidence matrix invalid")
    require(run_id in harvest and "KNOWLEDGE_CANDIDATE" in harvest, "example knowledge harvest invalid")

    validate_links()

    # Superseded combined/flat documents and parallel human/machine sources must not come back.
    forbidden_paths = [
        CORE / "03-角色与领域/02 架构LinuxBSPMCURTOS与驱动领域指南.md",
        CORE / "03-角色与领域/03 调试验证与独立评审领域指南.md",
        EMB / "positions",
        EMB / "config/positions.yaml",
        EMB / "config/position-model.yaml",
    ]
    require(not any(path.exists() for path in forbidden_paths), "superseded or parallel Position sources must stay removed")
    stale_root_files = [path.name for path in CORE.glob("[0-9][0-9] *.md")]
    require(not stale_root_files, f"legacy flat core-reference files must be removed: {stale_root_files}")
    require(not (ROOT / "docs/review").exists(), "legacy docs/review pack must be removed")

    forbidden = ["review-ready", "01~16 已统一", "v0.6.0"]
    violations = []
    for path in CORE.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                violations.append(f"{path.relative_to(ROOT)} -> {token}")
    require(not violations, "stale core-reference wording found: " + "; ".join(violations))

    print("core reference validation PASS: digital position model + 14 task types + 7 modes + split domain guides + valid artifact chain + links + v0.7.0 baseline")


if __name__ == "__main__":
    main()
