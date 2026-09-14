#!/usr/bin/env python3
"""Fail-closed synchronization checks for the embedded expert overview.

The Markdown overview is a human view over canonical machine contracts plus
concise human annotations. It must not become a second source of truth.
"""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "嵌入式系统专家团-核心参考"
OVERVIEW_DIR = CORE / "00-总览"
OVERVIEW = OVERVIEW_DIR / "00 架构与运行总览.md"
HUMAN = OVERVIEW_DIR / "overview-human.yaml"
EMB = ROOT / "expert-groups" / "embedded-system"


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def row_for(text: str, key: str) -> str:
    prefix = f"|`{key}`|"
    for line in text.splitlines():
        if line.replace(" ", "").startswith(prefix):
            return line
    raise AssertionError(f"overview row missing: {key}")


def compact(value: object) -> str:
    return "".join(str(value).replace("`", "").split())


def contains_compact(text: str, value: object) -> bool:
    return compact(value) in compact(text)


def main() -> None:
    require(OVERVIEW.is_file(), f"missing overview: {OVERVIEW.relative_to(ROOT)}")
    require(HUMAN.is_file(), f"missing human annotation source: {HUMAN.relative_to(ROOT)}")

    # The abandoned XLSX path must not become an active compatibility layer.
    forbidden_paths = [
        OVERVIEW_DIR / "嵌入式系统专家团-架构与运行总览.xlsx",
        ROOT / ".github/workflows/materialize-embedded-overview-once.yml",
        ROOT / "scripts/validate_embedded_overview_workbook.py",
        ROOT / "tests/unit/test_embedded_overview_workbook.py",
    ]
    require(not any(path.exists() for path in forbidden_paths), "XLSX/workbook residue must stay removed from the active path")

    text = OVERVIEW.read_text(encoding="utf-8")
    human_text = HUMAN.read_text(encoding="utf-8")
    human = yaml.safe_load(human_text)
    require(human["schema_version"] == 1, "unexpected overview-human schema_version")
    require(human.get("overview_view_version") == "1.0.0", "unexpected overview view version")
    require(human.get("status") == "operational-overview", "overview-human must remain operational-overview")
    require("workbook" not in human_text.lower(), "overview-human must not retain workbook-era naming")

    for marker in [
        "1 名主理人 + 7 个专业角色",
        "23",
        "14",
        "7",
        "K / M / 0 / T / E / V / R / C",
        "A0-A7",
        "E2 Engineering Closed Loop",
        "Production Ready",
        "视图，不是第二个 SSOT",
    ]:
        require(marker in text, f"overview baseline marker missing: {marker}")

    expert_group = yaml.safe_load((EMB / "expert-group.yaml").read_text(encoding="utf-8"))
    require(expert_group["version"] == "0.7.0", "unexpected embedded expert-group version")
    require(expert_group["architecture_model"] == "provider-neutral", "overview assumes provider-neutral baseline")

    # 1+7 role identity plus stable human labels/positioning.
    role_ids = [expert_group["team_lead"]["id"]] + [item["id"] for item in expert_group["experts"]]
    require(len(role_ids) == 8, f"expected 1+7 roles, got {len(role_ids)}")
    require(set(role_ids) == set(human["roles"]), "overview-human role set drift")
    for role_id in role_ids:
        item = human["roles"][role_id]
        for value in [role_id, item["name"], item["positioning"], item["inputs"], item["outputs"]]:
            require(contains_compact(text, value), f"overview role annotation drift: {role_id} -> {value}")
        # Responsibilities and boundaries are deliberately concise in the view;
        # require several stable fragments rather than byte-for-byte prose equality.
        resp_fragments = [frag for frag in str(item["responsibilities"]).split("；") if frag][:3]
        boundary_fragments = [frag for frag in str(item["boundaries"]).split("；") if frag][:1]
        for frag in resp_fragments + boundary_fragments:
            require(contains_compact(text, frag), f"overview role responsibility/boundary drift: {role_id} -> {frag}")

    skills = yaml.safe_load((EMB / "config/p0-skills.yaml").read_text(encoding="utf-8"))["skills"]
    require(len(skills) == 23, f"expected 23 P0 skills, got {len(skills)}")
    for item in skills:
        require(item["id"] in text, f"overview skill missing: {item['id']}")
        require(item["owner"] in role_ids, f"skill owner not in 1+7 roles: {item['id']}")

    # Task type / mode routing is checked row-by-row, not only by token presence.
    task_doc = yaml.safe_load((EMB / "config/task-modes.yaml").read_text(encoding="utf-8"))
    routing = task_doc["routing"]
    modes = task_doc["workflow_modes"]
    require(len(routing) == 14, f"expected 14 task types, got {len(routing)}")
    require(len(modes) == 7, f"expected 7 workflow modes, got {len(modes)}")
    require(set(routing) == set(human["task_labels"]) == set(human["task_guidance"]), "overview-human task set drift")
    for task_type, cfg in routing.items():
        row = row_for(text, task_type)
        require(cfg["default_mode"] in row, f"overview default mode drift: {task_type}")
        for mode in cfg["allowed_modes"]:
            require(mode in row, f"overview allowed mode drift: {task_type} -> {mode}")
        for expert_id in cfg["primary_experts"]:
            human_name = human["roles"][expert_id]["name"]
            require(human_name in row, f"overview primary expert drift: {task_type} -> {expert_id}")
        guide = human["task_guidance"][task_type]
        require(contains_compact(row, guide["artifact"]), f"overview artifact guidance drift: {task_type}")
        require(contains_compact(row, guide["verification"]), f"overview verification guidance drift: {task_type}")
    for mode, cfg in modes.items():
        require(mode in text and cfg["description"] in text, f"overview workflow mode drift: {mode}")

    workflow = yaml.safe_load((EMB / "config/workflow.yaml").read_text(encoding="utf-8"))
    for stage in workflow["stages"]:
        require(stage["id"] in text, f"overview stage missing: {stage['id']}")
        require(stage["name"] in text, f"overview stage name missing: {stage['id']}")
        require(stage["output"] in text, f"overview stage output missing: {stage['id']} -> {stage['output']}")
    for gate in expert_group["core_gates"]:
        require(gate in text, f"overview core gate missing: {gate}")

    action_doc = yaml.safe_load((EMB / "config/action-policy.yaml").read_text(encoding="utf-8"))
    require(len(action_doc["levels"]) == 8, "expected A0-A7 action policy")
    for action_id in action_doc["levels"]:
        require(action_id in text, f"overview action missing: {action_id}")
    for action_id in expert_group["autonomy"]["human_approval_required"]:
        require("human-approval-required" in row_for(text, action_id), f"overview human approval drift: {action_id}")
    require(len(expert_group["verification_layers"]) == 7, "expected 7 verification layers")
    for layer in expert_group["verification_layers"]:
        require(layer in text, f"overview verification layer missing: {layer}")
    require("forbid_cross_layer_inference = true" in text, "overview must preserve no cross-layer inference rule")

    for artifact in human["artifacts"]:
        for value in [artifact["name"], artifact["question"], artifact["schema"]]:
            require(contains_compact(text, value), f"overview artifact annotation drift: {artifact['name']} -> {value}")

    for role in human["cross_team_roles"]:
        require(contains_compact(text, role), f"overview cross-team role missing: {role}")
    for activity in human["cross_team_raci"]:
        require(contains_compact(text, activity[0]), f"overview RACI activity missing: {activity[0]}")

    for term in human["terms"]:
        # Formal term and boundary warning are the stable parts; middle wording may be editorially condensed.
        require(contains_compact(text, term[0]), f"overview term missing: {term[0]}")
        require(contains_compact(text, term[-1]), f"overview term boundary drift: {term[0]}")
    for step in human["walkthrough"]:
        for value in step[1:]:
            require(contains_compact(text, value), f"overview walkthrough drift at step {step[0]} -> {value}")

    overview_readme = (OVERVIEW_DIR / "README.md").read_text(encoding="utf-8")
    core_readme = (CORE / "README.md").read_text(encoding="utf-8")
    for entry in [overview_readme, core_readme]:
        require("00 架构与运行总览.md" in entry, "overview entry must point to Markdown total view")
        require(".xlsx" not in entry.lower(), "active entry must not depend on XLSX")
    require("Excel 可以很好地展示横向矩阵" in overview_readme, "overview README must explain the format decision")

    print("embedded overview PASS: Markdown total view synchronized with 1+7 / 23 skills / 14 tasks / 7 modes / 8 gates / A0-A7 / 7 verification layers")


if __name__ == "__main__":
    main()
