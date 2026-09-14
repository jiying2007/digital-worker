from __future__ import annotations

import importlib.util
import inspect
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("embedded_pilot_material_gate", ROOT / "scripts" / "embedded_pilot.py")
assert SPEC and SPEC.loader
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


def write_manifest(path: Path, *, readiness: str, log_status: str, reproduction_status: str, missing: list[str]) -> None:
    value = {
        "run_id": "RUN-MATERIAL-001",
        "items": [
            {"kind": "repo", "required": True, "status": "available", "source": "firmware/main"},
            {"kind": "base_commit", "required": True, "status": "available", "version": "0123456789abcdef0123456789abcdef01234567"},
            {"kind": "reproduction", "required": False, "status": reproduction_status},
            {"kind": "log", "required": False, "status": log_status},
        ],
        "readiness": readiness,
        "missing_critical": missing,
        "degradation_approved_by": None,
    }
    path.write_text(json.dumps(value), encoding="utf-8")


class PilotMaterialTerminalGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.run = {
            "run_id": "RUN-MATERIAL-001",
            "pilot_track": "debug",
            "extra_artifact_refs": {"material_manifest": "material-manifest.json"},
        }

    def test_blocked_manifest_is_allowed_while_running_but_rejected_for_terminal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_manifest(
                root / "material-manifest.json",
                readiness="BLOCKED",
                log_status="missing",
                reproduction_status="missing",
                missing=["reproduction_or_log"],
            )
            pilot.validate_material_manifest_ref(root, self.run, require_terminal_ready=False)
            with self.assertRaisesRegex(ValueError, "terminal Pilot evidence cannot use BLOCKED material manifest"):
                pilot.validate_material_manifest_ref(root, self.run, require_terminal_ready=True)

    def test_authoritative_log_only_debug_manifest_is_terminal_acceptable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_manifest(
                root / "material-manifest.json",
                readiness="READY",
                log_status="available",
                reproduction_status="missing",
                missing=[],
            )
            pilot.validate_material_manifest_ref(root, self.run, require_terminal_ready=True)

    def test_complete_and_completed_validate_both_ratchet_terminal_gate(self):
        complete_source = inspect.getsource(pilot.cmd_complete)
        validate_source = inspect.getsource(pilot.validate_run_dir)
        self.assertIn("validate_material_manifest_ref(run_dir, run, require_terminal_ready=True)", complete_source)
        self.assertIn('require_terminal_ready=run["status"] == "completed"', validate_source)


if __name__ == "__main__":
    unittest.main()
