#!/usr/bin/env python3
"""Validate canonical Edge Foundation routing against runtime policy and Golden Cases."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"


def load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    domain = load(EDGE / "domain.yaml")
    routing = load(EDGE / "routing.yaml")
    runtime = load(EDGE / "runtime/task-modes.yaml")
    golden = load(EDGE / "evaluation/golden-cases.yaml")
    require(routing["canonical_routing"] is True, "routing must be canonical")
    require(domain["execution"]["routing"] == "routing.yaml", "domain routing authority pointer drift")
    require(set(routing["routing"]) == set(runtime["routing"]), "runtime/canonical task taxonomy drift")
    expert_ids = {item["id"] for item in domain["experts"]}
    caps = set(next(item for item in domain["experts"] if item["id"] == "embedded-system-expert")["capabilities"])
    cross_candidates = []
    for task_type, route in routing["routing"].items():
        require(set(route.get("primary_experts", [])) <= expert_ids, f"unknown Expert in route: {task_type}")
        require(set(route.get("capabilities", [])) <= caps, f"unknown Capability in route: {task_type}")
        mode = runtime["routing"][task_type]["default_mode"]
        responsibility_mode = routing["runtime_mode_to_responsibility_mode"][mode]
        allowed = set(route.get("allowed_target_modes", [route["target_mode"]]))
        require(responsibility_mode in allowed, f"default runtime mode does not map to allowed responsibility mode: {task_type}")
        if route.get("cross_domain_escalation"):
            cross_candidates.append(task_type)
    for case in golden["cases"]:
        route = routing["routing"][case["task_type"]]
        require(case["target_mode"] == route["target_mode"], f"Golden mode drift: {case['id']}")
        require(case["expected_experts"] == route.get("primary_experts", []), f"Golden Expert drift: {case['id']}")
        require(case["required_assurance"] == route.get("assurance", []), f"Golden Assurance drift: {case['id']}")
    report = {
        "schema_version": 1,
        "status": "PASS",
        "canonical_routing": True,
        "task_types": len(routing["routing"]),
        "golden_cases": len(golden["cases"]),
        "cross_domain_candidates": sorted(cross_candidates),
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"edge-foundation routing validation PASS: {report['task_types']} task types, {report['golden_cases']} Golden Cases, canonical target routing")


if __name__ == "__main__":
    main()
