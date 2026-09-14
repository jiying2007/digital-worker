#!/usr/bin/env python3
"""Fail-closed synchronization and content-ownership checks for embedded human views."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "嵌入式系统专家团-核心参考"
ORG = CORE / "01-数字组织与岗位"
OVERVIEW = ORG / "01 数字员工组织与运行总览.md"
POSITIONS = ORG / "03 数字岗位与能力模型.md"
HUMAN = ORG / "human-view.yaml"
SKILL_MAP = CORE / "05-工程交付/01 Skill能力地图.md"
TASK_MATRIX = CORE / "03-流程与运行/05 任务类型运行矩阵.md"
WORKFLOW_GUIDE = CORE / "03-流程与运行/01 任务生命周期与Gate.md"
VERIFICATION_GUIDE = CORE / "03-流程与运行/04 验证评审发布与异常恢复.md"
ACTION_GUIDE = CORE / "06-治理与评审/02 权限安全风险与例外.md"
CORE_README = CORE / "README.md"
EMB = ROOT / "expert-groups" / "embedded-system"


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def compact(value: object) -> str:
    text = str(value)
    for token in ["`", "*", "“", "”", '"', "‘", "’"]:
        text = text.replace(token, "")
    return "".join(text.split())


def contains_compact(text: str, value: object) -> bool:
    return compact(value) in compact(text)


def main() -> None:
    for path in [OVERVIEW, POSITIONS, HUMAN, SKILL_MAP, TASK_MATRIX, WORKFLOW_GUIDE, VERIFICATION_GUIDE, ACTION_GUIDE, CORE_README]:
        require(path.is_file(), f"missing human-view asset: {path.relative_to(ROOT)}")

    forbidden = [
        CORE / "00-总览",
        CORE / "00-评审入口",
        ROOT / ".github/workflows/materialize-embedded-overview-once.yml",
        ROOT / "scripts/validate_embedded_overview_workbook.py",
        ROOT / "tests/unit/test_embedded_overview_workbook.py",
        EMB / "positions",
        EMB / "config/positions.yaml",
        EMB / "config/position-model.yaml",
    ]
    require(not any(p.exists() for p in forbidden), "legacy overview/workbook or parallel Position SSOT residue must stay absent")

    overview = OVERVIEW.read_text(encoding="utf-8")
    positions_text = POSITIONS.read_text(encoding="utf-8")
    skill_map = SKILL_MAP.read_text(encoding="utf-8")
    task_matrix = TASK_MATRIX.read_text(encoding="utf-8")
    workflow_guide = WORKFLOW_GUIDE.read_text(encoding="utf-8")
    verification_guide = VERIFICATION_GUIDE.read_text(encoding="utf-8")
    action_guide = ACTION_GUIDE.read_text(encoding="utf-8")
    core_readme = CORE_README.read_text(encoding="utf-8")
    human_text = HUMAN.read_text(encoding="utf-8")
    human = yaml.safe_load(human_text)

    require(human.get("schema_version") == 2, "human-view must use schema_version 2 after content convergence")
    require(human.get("view_version") == "2.0.0", "unexpected human-view version")
    require(human.get("status") == "operational-human-view", "unexpected human-view status")
    require("workbook" not in human_text.lower(), "human-view must not retain workbook-era naming")
    for stale_key in ["roles", "task_labels", "task_guidance", "artifacts", "cross_team_roles", "cross_team_raci", "terms", "walkthrough"]:
        require(stale_key not in human, f"human-view must not mirror non-position content: {stale_key}")

    require("唯一第一入口" in core_readme, "root README must remain the single human entry")
    for marker in ["人类总览视图", "不是第二个 SSOT", "1 名主理人 + 7 个专业角色", "23 个 P0 Skill", "14 类 task type", "7 种 workflow mode", "K / M / 0 / T / E / V / R / C", "A0-A7", "7 层", "E2 Engineering Closed Loop", "Production Ready"]:
        require(contains_compact(overview, marker), f"slim overview missing stable marker: {marker}")

    expert_group = yaml.safe_load((EMB / "expert-group.yaml").read_text(encoding="utf-8"))
    require(expert_group["version"] == "0.7.0", "unexpected embedded expert-group version")
    require(expert_group["architecture_model"] == "provider-neutral", "human views assume provider-neutral architecture")
    role_ids = [expert_group["team_lead"]["id"]] + [item["id"] for item in expert_group["experts"]]
    require(len(role_ids) == 8, f"expected 1+7 roles, got {len(role_ids)}")

    modules = human.get("modules", {})
    positions = human.get("positions", {})
    require(set(modules) == {f"M{i}" for i in range(1, 7)}, f"expected M1-M6 modules, got {sorted(modules)}")
    require(set(positions) == set(role_ids), "digital positions must map 1:1 to existing Agent definitions")
    position_ids = [item["position_id"] for item in positions.values()]
    require(set(position_ids) == {f"P{i:02d}" for i in range(1, 9)} and len(position_ids) == 8, "expected unique P01-P08")

    members: list[str] = []
    for module_id, item in modules.items():
        for field in ["name", "positioning", "work_content", "work_requirements", "positions"]:
            require(item.get(field), f"module annotation missing {field}: {module_id}")
        require(contains_compact(positions_text, module_id), f"position model missing module: {module_id}")
        require(contains_compact(positions_text, item["name"]), f"position model module-name drift: {module_id}")
        for role_id in item["positions"]:
            require(role_id in role_ids, f"module references unknown Agent: {module_id} -> {role_id}")
            members.append(role_id)
    require(Counter(members) == Counter(role_ids), "M1-M6 must cover each Agent exactly once")

    for role_id, item in positions.items():
        require(item["module"] in modules, f"position references unknown module: {role_id}")
        require(role_id in modules[item["module"]]["positions"], f"position/module membership drift: {role_id}")
        for field in [
            "position_id", "name", "module", "positioning", "objective", "responsibilities", "work_content",
            "work_requirements", "inputs", "outputs", "collaboration", "boundaries", "qualification_focus", "real_world_analogy",
        ]:
            require(item.get(field), f"position annotation missing {field}: {role_id}")
        for value in [role_id, item["position_id"], item["name"], item["module"], item["real_world_analogy"]]:
            require(contains_compact(positions_text, value), f"position model identity drift: {role_id} -> {value}")

    require((EMB / expert_group["team_lead"]["contract"]).is_file(), "team-lead I/O contract missing")
    for expert in expert_group["experts"]:
        require((EMB / expert["contract"]).is_file(), f"expert I/O contract missing: {expert['id']}")

    skills = yaml.safe_load((EMB / "config/p0-skills.yaml").read_text(encoding="utf-8"))["skills"]
    require(len(skills) == 23, f"expected 23 P0 skills, got {len(skills)}")
    skill_counts = Counter(item["owner"] for item in skills)
    for item in skills:
        require(item["owner"] in role_ids, f"skill owner not in 1+7 roles: {item['id']}")
        require(item["id"] in skill_map, f"Skill capability map missing registered skill: {item['id']}")
    for role_id, count in skill_counts.items():
        row = next((line for line in positions_text.splitlines() if line.startswith("|P") and f"`{role_id}`" in line), None)
        require(row is not None, f"position summary row missing Agent: {role_id}")
        require(f"|{count}|" in row, f"position summary Skill count drift: {role_id} expected {count}")

    # Content-ownership rule: overview/position docs summarize capabilities but do not mirror machine registries.
    duplicated_overview_skills = [item["id"] for item in skills if item["id"] in overview]
    duplicated_position_skills = [item["id"] for item in skills if item["id"] in positions_text]
    require(not duplicated_overview_skills, f"overview must not duplicate Skill IDs: {duplicated_overview_skills}")
    require(not duplicated_position_skills, f"position model must link to Skill map instead of duplicating Skill IDs: {duplicated_position_skills}")

    task_doc = yaml.safe_load((EMB / "config/task-modes.yaml").read_text(encoding="utf-8"))
    routing, modes = task_doc["routing"], task_doc["workflow_modes"]
    require(len(routing) == 14 and len(modes) == 7, "expected 14 task types / 7 workflow modes")
    for task_type, cfg in routing.items():
        row = next((line for line in task_matrix.splitlines() if line.startswith(f"|`{task_type}`|")), None)
        require(row is not None, f"task matrix missing task type: {task_type}")
        require(cfg["default_mode"] in row, f"task matrix default mode drift: {task_type}")
        for mode in cfg["allowed_modes"]:
            require(mode in row, f"task matrix allowed mode drift: {task_type} -> {mode}")
    require(not [task for task in routing if task in overview], "overview must not mirror the 14-row task matrix")

    workflow = yaml.safe_load((EMB / "config/workflow.yaml").read_text(encoding="utf-8"))
    for gate in expert_group["core_gates"]:
        gate_name = gate.split(".", 1)[1].upper() if "." in gate else gate.upper()
        require(f"Gate {gate_name}" in workflow_guide, f"workflow guide missing human-readable core gate: {gate}")
    require("任务生命周期与 Gate" in overview, "overview must link to the detailed Gate source")

    action_doc = yaml.safe_load((EMB / "config/action-policy.yaml").read_text(encoding="utf-8"))
    require(len(action_doc["levels"]) == 8, "expected A0-A7 action policy")
    for action_id in action_doc["levels"]:
        human_level = action_id.split("_", 1)[0]
        require(f"|{human_level}|" in action_guide, f"action governance guide missing human-readable level: {action_id}")
    require(not [action_id for action_id in action_doc["levels"] if action_id in overview], "overview must not mirror the detailed action table")
    require("A6_DEVICE_WRITE" in positions_text and "A7_RELEASE" in positions_text, "position qualification model must preserve A6/A7 human boundary")

    layers = expert_group["verification_layers"]
    require(len(layers) == 7, "expected 7 verification layers")
    for layer in layers:
        require(layer in verification_guide, f"verification flow guide missing layer: {layer}")
    require(not [layer for layer in layers if layer in overview], "overview must not mirror the detailed verification-layer table")
    for marker in ["device_verified", "hil_verified", "release_verified", "禁止跨层推导"]:
        require(contains_compact(positions_text, marker), f"position model missing verification boundary: {marker}")

    for metric in expert_group["evaluation"]["primary_metrics"]:
        require(metric in positions_text, f"position performance model missing machine metric: {metric}")
    require(expert_group["evaluation"]["safety_priority_metric"] in positions_text, "position model missing safety-priority metric")

    for marker in [
        "不是招聘 JD", "Position = 数字岗位", "Agent    = 承担岗位的数字员工",
        "Skill    = 数字员工掌握的岗位技能", "不声明任何岗位已经达到完全替代人工",
    ]:
        require(contains_compact(positions_text, marker), f"position governance marker missing: {marker}")
    for marker in ["数字任职资格模型", "岗位替代", "positions.yaml"]:
        require(marker in positions_text, f"position governance marker missing: {marker}")

    for link_marker in [
        "数字岗位与能力模型", "Skill 能力地图", "任务类型运行矩阵", "任务生命周期与 Gate",
        "权限、安全、风险与例外", "验证、评审、发布与异常恢复", "身份证据与知识架构",
    ]:
        require(link_marker in overview, f"slim overview missing canonical detail link: {link_marker}")

    print(
        "embedded human views PASS: 6 modules / 8 positions synchronized with 1+7 Agents; "
        "detail ownership converged to Skill/Task/Gate/Action/Verification canonical human guides"
    )


if __name__ == "__main__":
    main()
