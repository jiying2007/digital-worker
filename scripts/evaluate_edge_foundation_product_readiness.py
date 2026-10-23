#!/usr/bin/env python3
"""Aggregate canonical Edge Foundation Pilot receipts into product-readiness status."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
from evaluate_edge_foundation_pilot import build_receipt
from embedded_pilot import safe_ref
from pilot_support import load_json, load_yaml, validate_json, validation_scope, error_result
EDGE = ROOT / "domains" / "edge-foundation"
PILOT_ROOT = EDGE / "pilot"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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


@validation_scope
def evaluate(receipt_paths: list[Path]) -> dict:
    domain = load_yaml(EDGE / "domain.yaml")
    pilot_plan = load_yaml(PILOT_ROOT / "pilot-plan.yaml")
    receipt_schema = ROOT / "schemas" / "edge-foundation-pilot-receipt.v1.schema.json"
    require(domain["execution"]["authority"] == "canonical", "product readiness requires canonical target execution")
    require(domain["execution"]["legacy_compatibility_removed"] is True, "legacy compatibility must stay removed")
    require(domain["product_readiness"]["requires_real_pilot_evidence"] is True, "real Pilot evidence requirement disabled")
    require(domain["product_readiness"]["synthetic_pilot_counts"] is False, "synthetic Pilot evidence must remain excluded")
    require(domain["product_readiness"]["controls_routing_authority"] is False, "product readiness must not control routing authority")
    require(domain["product_readiness"]["blocking_scope"] == "product-readiness-only", "product readiness blocker scope drift")
    require(domain["product_readiness"]["development_blocking"] is False, "product readiness must not block development")
    require(domain["product_readiness"]["integration_blocking"] is False, "product readiness must not block integration")
    require(domain["product_readiness"]["control_plane_blocking"] is False, "product readiness must not block the control plane")

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
    safety_blockers: list[str] = []

    for path in receipt_paths:
        receipt = load_json(path)
        validate_json(receipt, receipt_schema)
        if receipt["source_type"] == "real":
            evidence = receipt.get("evidence")
            require(isinstance(evidence, dict), "real receipt must bind its source Run")
            run_path = (path.parent / evidence["pilot_run_ref"]).resolve()
            require(run_path.is_file(), "receipt source Run is missing")
            require(hashlib.sha256(run_path.read_bytes()).hexdigest() == evidence["pilot_run_sha256"],
                    "receipt source Run digest mismatch")
            source_run = load_json(run_path)
            result_path = safe_ref(run_path.parent, source_run["pilot_result_ref"]) if source_run.get("pilot_result_ref") else None
            rebuilt = build_receipt(run_path, result_path, receipt["cross_domain"]["trigger"], receipt_dir=path.parent)
            require(receipt == rebuilt, "receipt does not match recomputed frozen evidence")
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
        if receipt["source_type"] == "real" and receipt["eligibility_checks"]["run_completed"]:
            for check in ("no_unauthorized_actions", "no_incorrect_pass", "audit_trace_complete"):
                if not receipt["eligibility_checks"][check]:
                    safety_blockers.append(f"safety-violation:{run_id}:{check}")
        if not recomputed_eligible:
            continue
        require(receipt["source_type"] == "real", f"eligible receipt must be real: {run_id}")
        require(receipt["pilot_result_evaluated"] is True, f"eligible receipt must evaluate result: {run_id}")
        require(receipt["pilot_outcome"] == "PASS", f"eligible receipt must PASS: {run_id}")
        coverage[track]["eligible_count"] += 1
        coverage[track]["run_ids"].append(run_id)
        eligible_run_ids.append(run_id)

    blockers: list[str] = sorted(safety_blockers)
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
        "operational_status": "eligible_for_productionization_review" if ready else "product_readiness_in_progress",
        "blocking_scope": "none" if ready else "product-readiness-only",
        "development_blocking": False,
        "integration_blocking": False,
        "control_plane_blocking": False,
        "product_readiness_blocking": not ready,
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
    parser.add_argument("--json", action="store_true", help="Emit exactly one JSON document on stdout")
    args = parser.parse_args()
    result = evaluate(collect_receipts(args.receipt_dir, args.receipt))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        from embedded_pilot import write_derived_json
        write_derived_json(args.output, result)
    if not args.output or args.json:
        print(rendered, end="")
    if not args.json:
        print(
        "edge-foundation product readiness: "
        f"status={result['status']} operational_status={result['operational_status']} "
        f"receipts={result['receipts_scanned']} eligible={result['eligible_real_receipts']} "
        f"qualification_blockers={len(result['blockers'])}"
    )
    if args.require_ready and not result["eligible_for_product_review"]:
        raise SystemExit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        result, code = error_result(exc)
        print(json.dumps(result, ensure_ascii=False), file=sys.stdout if "--json" in sys.argv else sys.stderr)
        raise SystemExit(code)
