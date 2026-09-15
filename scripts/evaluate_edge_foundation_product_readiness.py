#!/usr/bin/env python3
"""Aggregate canonical Edge Foundation Pilot receipts into product-readiness status."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"
PILOT_ROOT = EDGE / "pilot"


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


def collect_receipts(receipt_dir: Path | None, explicit: list[Path]) -> list[Path]:
    paths = list(explicit)
    if receipt_dir is not None and receipt_dir.exists():
        paths.extend(receipt_dir.rglob("edge-foundation-pilot-receipt.json"))
    dedup: dict[str, Path] = {}
    for path in paths:
        resolved = path.resolve()
        require(resolved.is_file(), f"Pilot receipt does not exist: {path}")
        dedup[str(resolved)] = resolved
    return [dedup[key] for key in sorted(dedup)]


def evaluate(receipt_paths: list[Path]) -> dict:
    domain = load_yaml(EDGE / "domain.yaml")
    pilot_plan = load_yaml(PILOT_ROOT / "pilot-plan.yaml")
    receipt_schema = ROOT / "schemas" / "edge-foundation-pilot-receipt.v1.schema.json"
    require(domain["execution"]["authority"] == "canonical", "product readiness requires canonical target execution")
    require(domain["execution"]["legacy_compatibility_removed"] is True, "legacy compatibility must stay removed")
    require(domain["product_readiness"]["requires_real_pilot_evidence"] is True, "real Pilot evidence requirement disabled")
    require(domain["product_readiness"]["synthetic_pilot_counts"] is False, "synthetic Pilot evidence must remain excluded")
    require(domain["product_readiness"]["controls_routing_authority"] is False, "product readiness must not control routing authority")

    known_experts = {item["id"] for item in domain["experts"]}
    embedded = next(item for item in domain["experts"] if item["id"] == "embedded-system-expert")
    known_capabilities = set(embedded.get("capabilities", []))
    tracks = pilot_plan["tracks"]
    required_tracks = list(tracks)
    coverage = {
        track: {"minimum_required": int(cfg["minimum_real_completed_runs"]), "eligible_count": 0, "run_ids": []}
        for track, cfg in tracks.items()
    }
    run_ids: set[str] = set()
    eligible_run_ids: list[str] = []

    for path in receipt_paths:
        receipt = load_json(path)
        validate_json(receipt, receipt_schema)
        run_id = receipt["run_id"]
        require(run_id not in run_ids, f"duplicate Pilot receipt run_id: {run_id}")
        run_ids.add(run_id)
        require(receipt["routing_authority"] == "edge-foundation", f"receipt routing authority drift: {run_id}")
        require(receipt["canonical_routing"] is True, f"receipt must use canonical routing: {run_id}")
        require(set(receipt["target_experts"]) <= known_experts, f"receipt references unknown Expert: {run_id}")
        require(set(receipt["target_capabilities"]) <= known_capabilities, f"receipt references unknown Capability: {run_id}")
        recomputed_eligible = all(receipt["eligibility_checks"].values())
        require(receipt["product_readiness_eligible"] is recomputed_eligible, f"receipt eligibility drift: {run_id}")
        track = receipt["pilot_track"]
        require(track in tracks, f"receipt uses unknown Pilot track: {run_id} -> {track}")
        require(receipt["task_type"] in tracks[track]["candidate_task_types"], f"receipt task type does not belong to track: {run_id}")
        if not recomputed_eligible:
            continue
        require(receipt["source_type"] == "real", f"eligible receipt must be real: {run_id}")
        require(receipt["pilot_result_evaluated"] is True, f"eligible receipt must evaluate result: {run_id}")
        require(receipt["pilot_outcome"] == "PASS", f"eligible receipt must PASS: {run_id}")
        coverage[track]["eligible_count"] += 1
        coverage[track]["run_ids"].append(run_id)
        eligible_run_ids.append(run_id)

    blockers: list[str] = []
    for track in required_tracks:
        item = coverage[track]
        item["run_ids"].sort()
        if item["eligible_count"] < item["minimum_required"]:
            blockers.append(f"track-{track}-needs-{item['minimum_required']}-eligible-real-run(s)-has-{item['eligible_count']}")

    promotion = pilot_plan["promotion_gate"]
    minimum_total = int(promotion["minimum_total_real_completed_runs"])
    if len(eligible_run_ids) < minimum_total:
        blockers.append(f"total-eligible-real-runs-needs-{minimum_total}-has-{len(eligible_run_ids)}")
    require(promotion["require_each_track"] is True, "product readiness requires each track")
    require(promotion["incorrect_pass_rate_must_equal"] == 0.0, "incorrect PASS threshold must remain zero")
    require(promotion["unauthorized_actions_must_equal"] == 0, "unauthorized action threshold must remain zero")
    require(promotion["audit_trace_completeness_must_equal"] == 1.0, "audit trace completeness threshold must remain 1.0")

    eligible_run_ids.sort()
    ready = not blockers
    result = {
        "schema_version": 1,
        "status": "ELIGIBLE_FOR_PRODUCTIONIZATION_REVIEW" if ready else "BLOCKED",
        "eligible_for_product_review": ready,
        "routing_authority": "edge-foundation",
        "canonical_routing": True,
        "promotion_gate_source": "domains/edge-foundation/pilot/pilot-plan.yaml",
        "required_tracks": required_tracks,
        "track_coverage": coverage,
        "receipts_scanned": len(receipt_paths),
        "eligible_real_receipts": len(eligible_run_ids),
        "evidence_run_ids": eligible_run_ids,
        "blockers": blockers,
    }
    validate_json(result, ROOT / "schemas" / "edge-foundation-product-readiness.v1.schema.json")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt-dir", type=Path, default=PILOT_ROOT / "runs")
    parser.add_argument("--receipt", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    result = evaluate(collect_receipts(args.receipt_dir, args.receipt))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    print(
        "edge-foundation product readiness: "
        f"status={result['status']} receipts={result['receipts_scanned']} "
        f"eligible={result['eligible_real_receipts']} blockers={len(result['blockers'])}"
    )
    if args.require_ready and not result["eligible_for_product_review"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
