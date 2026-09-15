#!/usr/bin/env python3
"""Canonical Edge Foundation Pilot CLI using target runtime assets.

The implementation is temporarily shared with embedded_pilot.py while all data,
schemas and routing inputs come from domains/edge-foundation. This wrapper exists
only to migrate execution without duplicating lifecycle logic.
"""
from pathlib import Path
import embedded_pilot as impl

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "domains" / "edge-foundation"

impl.EMB = EDGE
impl.PILOT_DIR = EDGE / "pilot"
impl.PLAN = impl.PILOT_DIR / "pilot-plan.yaml"
impl.REQUIREMENTS = impl.PILOT_DIR / "artifact-requirements.yaml"
impl.TASK_MODES = EDGE / "runtime" / "task-modes.yaml"
impl.REF_SCHEMAS = {
    "engineering_task_package_ref": EDGE / "schemas" / "engineering-task-package.schema.json",
    "delivery_receipt_ref": ROOT / "schemas" / "delivery-receipt.v1.schema.json",
    "verification_report_ref": EDGE / "schemas" / "verification-report.schema.json",
    "review_report_ref": EDGE / "schemas" / "review-report.schema.json",
    "pilot_result_ref": ROOT / "schemas" / "pilot-result.v1.schema.json",
}
impl.MATERIAL_VALIDATOR = ROOT / "scripts" / "validate_edge_material_manifest.py"

if __name__ == "__main__":
    impl.main()
