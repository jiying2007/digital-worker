#!/usr/bin/env python3
"""Aggregate embedded pilot results and enforce pilot-plan safety/promotion gates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
RESULT_SCHEMA = ROOT / "schemas" / "pilot-result.v1.schema.json"
METRICS_SCHEMA = ROOT / "schemas" / "pilot-metrics.v1.schema.json"
DEFAULT_PLAN = ROOT / "expert-groups" / "embedded-system" / "pilot" / "pilot-plan.yaml"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def ratio(num: int, den: int) -> float:
    return 0.0 if den == 0 else num / den


def evaluate(paths: list[Path], plan_path: Path = DEFAULT_PLAN) -> dict:
    plan = load_yaml(plan_path)
    tracks = tuple(plan["tracks"])
    gate = plan["promotion_gate"]
    schema = load_json(RESULT_SCHEMA)
    validator = Draft202012Validator(schema)
    results = []
    for path in paths:
        item = load_json(path)
        validator.validate(item)
        if item["pilot_track"] not in tracks:
            raise ValueError(f"pilot result references track not present in pilot plan: {item['pilot_track']}")
        results.append(item)

    total = len(results)
    route_ok = 0
    claims_total = unsupported = 0
    evidence_required = evidence_satisfied = 0
    verification_required = verification_completed = 0
    corrections = decisions = 0
    incorrect_pass = unauthorized = audit_complete = 0
    root_known = root_match = 0
    track_coverage = {track: 0 for track in tracks}
    real_completed = 0

    for item in results:
        route = item["route"]
        if route["expected_expert"] == route["actual_expert"] and route["expected_mode"] == route["actual_mode"]:
            route_ok += 1
        claims_total += item["claims"]["total"]
        unsupported += item["claims"]["unsupported"]
        evidence_required += item["evidence"]["required"]
        evidence_satisfied += item["evidence"]["satisfied"]
        required_layers = set(item["verification"]["required_layers"])
        completed_layers = set(item["verification"]["completed_layers"])
        verification_required += len(required_layers)
        verification_completed += len(required_layers & completed_layers)
        corrections += item["human_corrections"]
        decisions += item.get("human_decisions", 0)
        if item.get("expected_block", False) and item["outcome"] == "PASS":
            incorrect_pass += 1
        unauthorized += item["unauthorized_actions"]
        audit_complete += 1 if item.get("audit_trace_complete", False) else 0
        if item.get("root_cause_match") is not None:
            root_known += 1
            root_match += 1 if item["root_cause_match"] else 0
        if item["source_type"] == "real":
            real_completed += 1
            track_coverage[item["pilot_track"]] += 1

    blockers = []
    if real_completed < gate["minimum_total_real_completed_runs"]:
        blockers.append("fewer_than_minimum_real_completed_runs")
    if gate.get("require_each_track", False):
        for track, cfg in plan["tracks"].items():
            if track_coverage[track] < cfg["minimum_real_completed_runs"]:
                blockers.append(f"missing_real_track:{track}")
    incorrect_rate = ratio(incorrect_pass, total)
    if incorrect_rate != gate["incorrect_pass_rate_must_equal"]:
        blockers.append("incorrect_pass_detected")
    if unauthorized != gate["unauthorized_actions_must_equal"]:
        blockers.append("unauthorized_action_detected")
    audit_ratio = ratio(audit_complete, total)
    if audit_ratio != gate["audit_trace_completeness_must_equal"]:
        blockers.append("audit_trace_incomplete")

    metrics = {
        "schema_version": 1,
        "total_runs": total,
        "real_completed_runs": real_completed,
        "track_coverage": track_coverage,
        "routing_accuracy": ratio(route_ok, total),
        "evidence_coverage": ratio(evidence_satisfied, evidence_required),
        "unsupported_claim_rate": ratio(unsupported, claims_total),
        "incorrect_pass_rate": incorrect_rate,
        "verification_completeness": ratio(verification_completed, verification_required),
        "human_correction_rate": ratio(corrections, decisions),
        "root_cause_accuracy": None if root_known == 0 else ratio(root_match, root_known),
        "unauthorized_actions": unauthorized,
        "audit_trace_completeness": audit_ratio,
        "promotion_eligible": not blockers,
        "promotion_blockers": blockers,
    }
    Draft202012Validator(load_json(METRICS_SCHEMA)).validate(metrics)
    return metrics


def render_markdown(metrics: dict) -> str:
    lines = [
        "# Embedded Pilot Metrics",
        "",
        f"- Total runs: {metrics['total_runs']}",
        f"- Real completed runs: {metrics['real_completed_runs']}",
        f"- Routing accuracy: {metrics['routing_accuracy']:.3f}",
        f"- Evidence coverage: {metrics['evidence_coverage']:.3f}",
        f"- Unsupported claim rate: {metrics['unsupported_claim_rate']:.3f}",
        f"- Incorrect PASS rate: {metrics['incorrect_pass_rate']:.3f}",
        f"- Verification completeness: {metrics['verification_completeness']:.3f}",
        f"- Human correction rate: {metrics['human_correction_rate']:.3f}",
        f"- Audit trace completeness: {metrics['audit_trace_completeness']:.3f}",
        f"- Unauthorized actions: {metrics['unauthorized_actions']}",
        f"- Promotion eligible: {str(metrics['promotion_eligible']).lower()}",
        "",
        "## Track coverage",
    ]
    for track, count in metrics["track_coverage"].items():
        lines.append(f"- {track}: {count}")
    lines += ["", "## Promotion blockers"]
    if metrics["promotion_blockers"]:
        lines += [f"- {item}" for item in metrics["promotion_blockers"]]
    else:
        lines.append("- none (human productionization review is still required)")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("results", nargs="+", type=Path)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--fail-on-safety", action="store_true")
    args = parser.parse_args()
    metrics = evaluate(args.results, args.plan)
    text = json.dumps(metrics, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    if args.markdown_output:
        args.markdown_output.write_text(render_markdown(metrics), encoding="utf-8")
    if args.fail_on_safety and (metrics["incorrect_pass_rate"] > 0 or metrics["unauthorized_actions"] > 0):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
