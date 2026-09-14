#!/usr/bin/env python3
"""Fail-closed drift validation for the embedded expert overview workbook.

The XLSX is a human view. It must stay synchronized with canonical machine
contracts and the concise human annotation source; it never becomes a second
source of truth.
"""
from __future__ import annotations

import subprocess
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "嵌入式系统专家团-核心参考"
OVERVIEW = CORE / "00-总览"
XLSX = OVERVIEW / "嵌入式系统专家团-架构与运行总览.xlsx"
HUMAN = OVERVIEW / "overview-human.yaml"
EMB = ROOT / "expert-groups" / "embedded-system"

EXPECTED_SHEETS = [
    "00 总览",
    "01 专家与职责",
    "02 任务路由矩阵",
    "03 串并行与Gate",
    "04 Artifact与Evidence",
    "05 权限与Verification",
    "06 跨团队RACI",
    "07 术语与任务走查",
]
SOURCE_PATHS = [
    "expert-groups/embedded-system/expert-group.yaml",
    "expert-groups/embedded-system/config/task-modes.yaml",
    "expert-groups/embedded-system/config/workflow.yaml",
    "expert-groups/embedded-system/config/gate-policy.yaml",
    "expert-groups/embedded-system/config/action-policy.yaml",
    "expert-groups/embedded-system/config/p0-skills.yaml",
    "嵌入式系统专家团-核心参考/00-总览/overview-human.yaml",
]
NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
OFFICE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", str(ROOT / path)], text=True).strip()


def _shared_strings(zf: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.findall(".//x:t", NS)) for si in root.findall("x:si", NS)]


def _sheet_map(zf: zipfile.ZipFile) -> tuple[list[str], dict[str, str]]:
    book = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    targets = {node.attrib["Id"]: node.attrib["Target"] for node in rels.findall("r:Relationship", REL_NS)}
    names: list[str] = []
    mapping: dict[str, str] = {}
    for sheet in book.findall("x:sheets/x:sheet", NS):
        name = sheet.attrib["name"]
        rid = sheet.attrib[f"{{{OFFICE_REL}}}id"]
        target = targets[rid].lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        names.append(name)
        mapping[name] = target
    return names, mapping


def _cells(zf: zipfile.ZipFile, xml_path: str, shared: list[str]) -> dict[str, str]:
    root = ET.fromstring(zf.read(xml_path))
    cells: dict[str, str] = {}
    for cell in root.findall(".//x:c", NS):
        ref = cell.attrib.get("r", "")
        typ = cell.attrib.get("t")
        if typ == "inlineStr":
            value = "".join(t.text or "" for t in cell.findall(".//x:t", NS))
        else:
            node = cell.find("x:v", NS)
            value = "" if node is None or node.text is None else node.text
            if typ == "s" and value:
                value = shared[int(value)]
        cells[ref] = value
    return cells


def main() -> None:
    require(XLSX.is_file(), f"missing embedded overview workbook: {XLSX.relative_to(ROOT)}")
    require(HUMAN.is_file(), f"missing embedded overview human source: {HUMAN.relative_to(ROOT)}")
    human = yaml.safe_load(HUMAN.read_text(encoding="utf-8"))
    require(human["schema_version"] == 1, "unexpected overview-human schema_version")

    with zipfile.ZipFile(XLSX) as zf:
        shared = _shared_strings(zf)
        sheet_names, sheet_xml = _sheet_map(zf)
        require(sheet_names == EXPECTED_SHEETS, f"overview workbook sheet drift: {sheet_names}")
        sheets = {name: _cells(zf, sheet_xml[name], shared) for name in sheet_names}

    overview = sheets["00 总览"]
    expected_kpis = {"A7": "8", "D7": "23", "G7": "14", "J7": "7", "A10": "8", "D10": "8", "G10": "7"}
    for ref, expected in expected_kpis.items():
        require(overview.get(ref) == expected, f"overview KPI drift at {ref}: {overview.get(ref)} != {expected}")
    overview_text = "\n".join(overview.values())
    for marker in ["v0.7.0", "provider-neutral", "E2 Engineering Closed Loop", "Production Ready = NO", "SOURCE_SNAPSHOT"]:
        require(marker in overview_text, f"overview missing baseline marker: {marker}")

    for path in SOURCE_PATHS:
        actual = git_blob(path)
        require(path in overview_text, f"workbook source snapshot missing path: {path}")
        require(actual in overview_text, f"workbook source snapshot stale for {path}: expected blob {actual}")

    expert_group = yaml.safe_load((EMB / "expert-group.yaml").read_text(encoding="utf-8"))
    roles_text = "\n".join(sheets["01 专家与职责"].values())
    role_ids = [expert_group["team_lead"]["id"]] + [item["id"] for item in expert_group["experts"]]
    require(len(role_ids) == 8, f"expected 1+7 roles, got {len(role_ids)}")
    for role_id in role_ids:
        require(role_id in roles_text, f"overview role missing: {role_id}")

    skill_doc = yaml.safe_load((EMB / "config/p0-skills.yaml").read_text(encoding="utf-8"))
    skill_ids = [item["id"] for item in skill_doc["skills"]]
    require(len(skill_ids) == 23, f"expected 23 P0 skills, got {len(skill_ids)}")
    for skill_id in skill_ids:
        require(skill_id in roles_text, f"overview skill missing: {skill_id}")

    task_doc = yaml.safe_load((EMB / "config/task-modes.yaml").read_text(encoding="utf-8"))
    task_text = "\n".join(sheets["02 任务路由矩阵"].values())
    require(len(task_doc["routing"]) == 14, f"expected 14 task types, got {len(task_doc['routing'])}")
    require(len(task_doc["workflow_modes"]) == 7, f"expected 7 workflow modes, got {len(task_doc['workflow_modes'])}")
    for task_type, cfg in task_doc["routing"].items():
        require(task_type in task_text, f"overview task missing: {task_type}")
        require(cfg["default_mode"] in task_text, f"overview default mode missing for {task_type}")
        for mode in cfg["allowed_modes"]:
            require(mode in task_text, f"overview allowed mode missing for {task_type}: {mode}")
    for mode in task_doc["workflow_modes"]:
        require(mode in task_text, f"overview mode missing: {mode}")

    gate_text = "\n".join(sheets["03 串并行与Gate"].values())
    for gate in expert_group["core_gates"]:
        require(gate in gate_text, f"overview gate missing: {gate}")

    action_doc = yaml.safe_load((EMB / "config/action-policy.yaml").read_text(encoding="utf-8"))
    action_text = "\n".join(sheets["05 权限与Verification"].values())
    for action in action_doc["levels"]:
        require(action in action_text, f"overview action level missing: {action}")
    for layer in expert_group["verification_layers"]:
        require(layer in action_text, f"overview verification layer missing: {layer}")

    require("Excel 是视图，不是第二个 SSOT" in overview_text, "overview must state that XLSX is not a second SSOT")
    print("embedded overview workbook PASS: 8 sheets synchronized with 1+7 / 23 skills / 14 tasks / 7 modes / 8 gates / A0-A7 / 7 verification layers")


if __name__ == "__main__":
    main()
