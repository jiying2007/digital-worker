#!/usr/bin/env python3
"""Validate one runtime/evaluation-owned Skill invocation receipt against canonical Skill contracts."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
SCHEMA = ROOT / "schemas" / "skill-invocation-receipt.v1.schema.json"
PILOT_SCHEMA = ROOT / "schemas" / "pilot-run.v1.schema.json"
SKILLS = EDGE / "skills.yaml"
ACTION_POLICY = EDGE / "runtime" / "action-policy.yaml"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_json(instance: dict, schema_path: Path) -> None:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(instance)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def skill_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    require(text.startswith("---\n"), f"Skill frontmatter missing: {path.relative_to(ROOT)}")
    parts = text.split("---", 2)
    require(len(parts) >= 3, f"Skill frontmatter malformed: {path.relative_to(ROOT)}")
    value = yaml.safe_load(parts[1])
    require(isinstance(value, dict), f"Skill frontmatter is not an object: {path.relative_to(ROOT)}")
    return value


def action_rank(level: str) -> int:
    match = re.match(r"^A([0-7])_", level)
    require(match is not None, f"invalid action level: {level}")
    return int(match.group(1))


def validate_receipt(receipt_path: Path, pilot_run_path: Path | None = None) -> dict:
    receipt = load_json(receipt_path)
    validate_json(receipt, SCHEMA)

    registry = load_yaml(SKILLS)
    by_id = {item["id"]: item for item in registry["skills"]}
    skill_id = receipt["skill_id"]
    require(skill_id in by_id, f"unregistered Skill invocation: {skill_id}")
    item = by_id[skill_id]
    contract_path = (EDGE / item["path"]).resolve()
    require(contract_path.is_file() and EDGE.resolve() in contract_path.parents, f"invalid canonical Skill path: {skill_id}")
    fm = skill_frontmatter(contract_path)

    frozen = receipt["skill_contract"]
    require(frozen["version"] == str(fm["version"]), f"Skill version drift: {skill_id}")
    require(frozen["path"] == item["path"], f"Skill path drift: {skill_id}")
    require(frozen["sha256"] == sha256(contract_path), f"Skill contract SHA256 mismatch: {skill_id}")
    require(frozen["owner_kind"] == item["owner_kind"] == fm["owner_kind"], f"Skill owner_kind drift: {skill_id}")
    require(frozen["owner"] == item["owner_id"] == fm["owner"], f"Skill owner drift: {skill_id}")
    require(frozen["max_action_level"] == fm["max_action_level"], f"Skill action ceiling drift: {skill_id}")

    policy = load_yaml(ACTION_POLICY)
    require(receipt["action_level"] in policy["levels"], f"action level not in canonical action policy: {receipt['action_level']}")
    require(frozen["max_action_level"] in policy["levels"], f"Skill ceiling not in canonical action policy: {skill_id}")
    require(action_rank(receipt["action_level"]) <= action_rank(frozen["max_action_level"]), f"Skill action ceiling exceeded: {skill_id}")

    if receipt["source_type"] == "real":
        require(receipt["attestation"]["producer"] == "runtime-binding", "real Skill receipt requires runtime-binding attestation")
        require(bool(receipt["runtime_binding"].get("execution_identity")), "real Skill receipt requires runtime execution_identity")

    if pilot_run_path is not None:
        pilot = load_json(pilot_run_path)
        validate_json(pilot, PILOT_SCHEMA)
        require(receipt["run_id"] == pilot["run_id"], "Skill receipt/pilot run_id mismatch")
        require(receipt["work_item_id"] == pilot["work_item_id"], "Skill receipt/pilot work_item_id mismatch")
        require(receipt["source_type"] == pilot["source_type"], "Skill receipt/pilot source_type mismatch")

    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--pilot-run", type=Path)
    args = parser.parse_args()
    receipt = validate_receipt(args.receipt, args.pilot_run)
    print(
        "skill invocation receipt PASS: "
        f"invocation={receipt['invocation_id']} skill={receipt['skill_id']} "
        f"source={receipt['source_type']} status={receipt['result']['status']}"
    )


if __name__ == "__main__":
    main()
