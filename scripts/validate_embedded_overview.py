#!/usr/bin/env python3
"""Fail-closed synchronization checks for embedded human overview and digital positions."""
from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "嵌入式系统专家团-核心参考"
OVERVIEW_DIR = CORE / "00-总览"
OVERVIEW = OVERVIEW_DIR / "00 架构与运行总览.md"
POSITIONS = OVERVIEW_DIR / "01 数字岗位与能力模型.md"
HUMAN = OVERVIEW_DIR / "overview-human.yaml"
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


def row_for(text: str, key: str) -> str:
    prefix = f"|`{key}`|"
    for line in text.splitlines():
        if line.replace(" ", "").startswith(prefix):
            return line
    raise AssertionError(f"overview row missing: {key}")


def main() -> None:
    require(OVERVIEW.is_file(), f"missing overview: {OVERVIEW.relative_to(ROOT)}")
    require(POSITIONS.is_file(), f"missing digital position model: {POSITIONS.relative_to(ROOT)}")
    require(HUMAN.is_file(), f"missing human annotation source: {HUMAN.relative_to(ROOT)}")

    forbidden = [
        OVERVIEW_DIR / "嵌入式系统专家团-架构与运行总览.xlsx",
        ROOT / ".github/workflows/materialize-embedded-overview-once.yml",
        ROOT / "scripts/validate_embedded_overview_workbook.py",
        ROOT / "tests/unit/test_embedded_overview_workbook.py",
        EMB / "positions",
        EMB / "config/positions.yaml",
        EMB / "config/position-model.yaml",
    ]
    require(not any(p.exists() for p in forbidden), "workbook or parallel Position SSOT residue must stay absent")

    text = OVERVIEW.read_text(encoding="utf-8")
    position_text = POSITIONS.read_text(encoding="utf-8")
    human_text = HUMAN.read_text(encoding="utf-8")
    human = yaml.safe_load(human_text)
    require(human["schema_version"] == 1, "unexpected overview-human schema_version")
    require(human.get("overview_view_version") == "1.1.0", "unexpected overview view version")
    require(human.get("status") == "operational-overview", "overview-human must remain operational-overview")
    require("workbook" not in human_text.lower(), "overview-human must not retain workbook-era naming")

    for marker in ["1 名主理人 + 7 个专业角色", "E2 Engineering Closed Loop", "Production Ready", "人类总览视图", "第二个 SSOT"]:
        require(contains_compact(text, marker), f"overview baseline marker missing: {marker}")
    for marker in ["23", "14", "7", "K / M / 0 / T / E / V / R / C", "A0-A7"]:
        require(marker in text, f"overview baseline marker missing: {marker}")

    expert_group = yaml.safe_load((EMB / "expert-group.yaml").read_text(encoding="utf-8"))
    require(expert_group["version"] == "0.7.0", "unexpected embedded expert-group version")
    require(expert_group["architecture_model"] == "provider-neutral", "overview assumes provider-neutral baseline")

    role_ids = [expert_group["team_lead"]["id"]] + [x["id"] for x in expert_group["experts"]]
    require(len(role_ids) == 8, f"expected 1+7 roles, got {len(role_ids)}")
    require(set(role_ids) == set(human["roles"]), "overview-human role set drift")
    for role_id in role_ids:
        item = human["roles"][role_id]
        for value in [role_id, item["name"], item["positioning"], item["inputs"], item["outputs"]]:
            require(contains_compact(text, value), f"overview role annotation drift: {role_id} -> {value}")
        boundary = str(item["boundaries"]).split("；", 1)[0]
        require(contains_compact(text, boundary), f"overview role boundary drift: {role_id} -> {boundary}")

    modules = human.get("modules", {})
    positions = human.get("positions", {})
    require(set(modules) == {f"M{i}" for i in range(1, 7)}, f"expected M1-M6 modules, got {sorted(modules)}")
    require(set(positions) == set(role_ids), "digital positions must map 1:1 to the existing 1+7 Agent definitions")
    position_ids = [item["position_id"] for item in positions.values()]
    require(len(position_ids) == len(set(position_ids)) == 8, "digital position IDs must be unique")
    require(set(position_ids) == {f"P{i:02d}" for i in range(1, 9)}, f"expected P01-P08 positions, got {sorted(position_ids)}")

    module_members: list[str] = []
    for module_id, item in modules.items():
        for field in ["name", "positioning", "work_content", "work_requirements"]:
            require(item.get(field), f"module annotation missing {field}: {module_id}")
        require(contains_compact(position_text, module_id), f"position doc missing module ID: {module_id}")
        require(contains_compact(position_text, item["name"]), f"position doc module name drift: {module_id}")
        require(contains_compact(position_text, item["positioning"]), f"position doc module positioning drift: {module_id}")
        for role_id in item["positions"]:
            require(role_id in role_ids, f"module references unknown Agent: {module_id} -> {role_id}")
            module_members.append(role_id)
    require(sorted(module_members) == sorted(role_ids), "M1-M6 must cover every Agent exactly once")

    for role_id, item in positions.items():
        require(item["module"] in modules, f"position references unknown module: {role_id}")
        require(role_id in modules[item["module"]]["positions"], f"position/module membership drift: {role_id}")
        for field in ["position_id", "name", "objective", "work_content", "work_requirements", "qualification_focus", "real_world_analogy"]:
            require(item.get(field), f"position annotation missing {field}: {role_id}")
        for value in [role_id, item["position_id"], item["name"], item["module"], item["real_world_analogy"]]:
            require(contains_compact(position_text, value), f"position doc identity drift: {role_id} -> {value}")

    require((EMB / expert_group["team_lead"]["contract"]).is_file(), "team-lead I/O contract missing")
    for expert in expert_group["experts"]:
        require((EMB / expert["contract"]).is_file(), f"expert I/O contract missing: {expert['id']}")

    skills = yaml.safe_load((EMB / "config/p0-skills.yaml").read_text(encoding="utf-8"))["skills"]
    require(len(skills) == 23, f"expected 23 P0 skills, got {len(skills)}")
    skills_by_owner: dict[str, list[str]] = {role_id: [] for role_id in role_ids}
    for item in skills:
        require(item["id"] in text, f"overview skill missing: {item['id']}")
        require(item["owner"] in role_ids, f"skill owner not in 1+7 roles: {item['id']}")
        require(item["id"] in position_text, f"digital position model skill missing: {item['id']}")
        skills_by_owner[item["owner"]].append(item["id"])
    for role_id, owned_skills in skills_by_owner.items():
        require(owned_skills, f"digital position has no registered P0 Skill: {role_id}")
        require(role_id in positions, f"skill owner lacks digital position: {role_id}")

    task_doc = yaml.safe_load((EMB / "config/task-modes.yaml").read_text(encoding="utf-8"))
    routing, modes = task_doc["routing"], task_doc["workflow_modes"]
    require(len(routing) == 14, f"expected 14 task types, got {len(routing)}")
    require(len(modes) == 7, f"expected 7 workflow modes, got {len(modes)}")
    require(set(routing) == set(human["task_labels"]) == set(human["task_guidance"]), "overview-human task set drift")
    for task_type, cfg in routing.items():
        row = row_for(text, task_type)
        require(cfg["default_mode"] in row, f"overview default mode drift: {task_type}")
        for mode in cfg["allowed_modes"]:
            require(mode in row, f"overview allowed mode drift: {task_type} -> {mode}")
        for expert_id in cfg["primary_experts"]:
            require(expert_id in human["roles"], f"routing expert missing from overview role model: {task_type} -> {expert_id}")
            require(expert_id in positions, f"routing expert missing from digital position model: {task_type} -> {expert_id}")
        guide = human["task_guidance"][task_type]
        require(contains_compact(row, guide["artifact"]), f"overview artifact guidance drift: {task_type}")
        require(contains_compact(row, guide["verification"]), f"overview verification guidance drift: {task_type}")
    for mode, cfg in modes.items():
        require(mode in text and contains_compact(text, cfg["description"]), f"overview workflow mode drift: {mode}")

    workflow = yaml.safe_load((EMB / "config/workflow.yaml").read_text(encoding="utf-8"))
    for stage in workflow["stages"]:
        require(stage["id"] in text, f"overview stage missing: {stage['id']}")
        require(stage["name"] in text, f"overview stage name missing: {stage['id']}")
        require(stage["output"] in text, f"overview stage output missing: {stage['id']} -> {stage['output']}")
    for gate in expert_group["core_gates"]:
        require(gate in text, f"overview core gate missing: {gate}")
    for marker in ["K/M/0/T/E/V/R/C", "Task Type", "Workflow Mode", "Agent Routing"]:
        require(contains_compact(position_text, marker), f"digital position model must preserve machine-routing boundary: {marker}")

    action_doc = yaml.safe_load((EMB / "config/action-policy.yaml").read_text(encoding="utf-8"))
    require(len(action_doc["levels"]) == 8, "expected A0-A7 action policy")
    for action_id in action_doc["levels"]:
        require(action_id in text, f"overview action missing: {action_id}")
    for action_id in expert_group["autonomy"]["human_approval_required"]:
        require("human-approval-required" in row_for(text, action_id), f"overview human approval drift: {action_id}")
    require(contains_compact(position_text, "A0-A7"), "position model must state A0-A7 authority boundary")
    require(contains_compact(position_text, "A6_DEVICE_WRITE"), "position model must preserve A6 human boundary")
    require(contains_compact(position_text, "A7_RELEASE"), "position model must preserve A7 human boundary")

    require(len(expert_group["verification_layers"]) == 7, "expected 7 verification layers")
    for layer in expert_group["verification_layers"]:
        require(layer in text, f"overview verification layer missing: {layer}")
    for marker in ["Verification Layer", "device_verified", "hil_verified", "release_verified", "禁止跨层推导"]:
        require(contains_compact(position_text, marker), f"digital position verification boundary missing: {marker}")
    require("forbid_cross_layer_inference = true" in text, "overview must preserve no cross-layer inference rule")

    for metric in expert_group["evaluation"]["primary_metrics"]:
        require(metric in position_text, f"digital position performance model missing machine metric: {metric}")
    require(expert_group["evaluation"]["safety_priority_metric"] in position_text, "position model missing safety priority metric")
    for marker in ["不是招聘 JD", "Position = 数字岗位", "Agent    = 承担岗位的数字员工", "Skill    = 数字员工掌握的岗位技能", "不声明任何岗位已经达到完全替代人工"]:
        require(contains_compact(position_text, marker), f"digital position governance marker missing: {marker}")

    for artifact in human["artifacts"]:
        for value in [artifact["name"], artifact["question"], artifact["schema"]]:
            require(contains_compact(text, value), f"overview artifact annotation drift: {artifact['name']} -> {value}")
    for role in human["cross_team_roles"]:
        require(contains_compact(text, role), f"overview cross-team role missing: {role}")
    for activity in human["cross_team_raci"]:
        require(contains_compact(text, activity[0]), f"overview RACI activity missing: {activity[0]}")
    for term in human["terms"]:
        require(contains_compact(text, term[0]), f"overview term missing: {term[0]}")
        require(contains_compact(text, term[-1]), f"overview term boundary drift: {term[0]}")
    for step in human["walkthrough"]:
        for value in step[1:]:
            require(contains_compact(text, value), f"overview walkthrough drift at step {step[0]} -> {value}")

    overview_readme = (OVERVIEW_DIR / "README.md").read_text(encoding="utf-8")
    core_readme = (CORE / "README.md").read_text(encoding="utf-8")
    for entry in [overview_readme, core_readme]:
        require("00 架构与运行总览.md" in entry, "overview entry must point to Markdown total view")
        require("01 数字岗位与能力模型.md" in entry, "overview entry must point to digital position model")
        require(".xlsx" not in entry.lower(), "active entry must not depend on XLSX")
    require("Excel 可以很好地展示横向矩阵" in overview_readme, "overview README must explain the format decision")
    require("positions.yaml" in overview_readme and "不是新的执行配置" in overview_readme, "overview README must forbid parallel Position SSOT")

    print("embedded overview PASS: 6 modules / 8 digital positions synchronized with 1+7 Agents / 23 skills / 14 tasks / 7 modes / 8 gates / A0-A7 / 7 verification layers")


if __name__ == "__main__":
    main()
