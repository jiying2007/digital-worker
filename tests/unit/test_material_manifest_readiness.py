#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scaffold = load_module("embedded_pilot_scaffold", ROOT / "scripts" / "embedded_pilot_scaffold.py")
validator = load_module("validate_material_manifest", ROOT / "scripts" / "validate_material_manifest.py")


class MaterialManifestReadinessTests(unittest.TestCase):
    def _debug_manifest(self):
        run = {
            "run_id": "REAL-DEBUG-001",
            "pilot_track": "debug",
            "repo_root": "firmware/pcr02",
            "base_commit": "0123456789abcdef0123456789abcdef01234567",
        }
        task = {
            "target_board": None,
            "required_verification": {
                "host": "required",
                "cross_build": "required",
                "sil": "optional",
                "hil": "not_applicable",
                "release": "not_applicable",
            },
        }
        return scaffold.build_material_manifest(run, task)

    def test_debug_scaffold_models_reproduction_or_log(self):
        manifest = self._debug_manifest()
        by_kind = {item["kind"]: item for item in manifest["items"]}
        self.assertIn("reproduction", by_kind)
        self.assertIn("log", by_kind)
        self.assertFalse(by_kind["reproduction"]["required"])
        self.assertFalse(by_kind["log"]["required"])
        self.assertIn("reproduction_or_log", manifest["missing_critical"])
        self.assertIn("test_environment", manifest["missing_critical"])
        self.assertEqual(manifest["readiness"], "BLOCKED")

    def test_authoritative_log_alone_can_satisfy_debug_alternative(self):
        manifest = self._debug_manifest()
        by_kind = {item["kind"]: item for item in manifest["items"]}
        by_kind["log"].update(
            status="available",
            source="field-dmesg.log",
            version="sha256:fixture-log",
            evidence_ref="evidence/field-dmesg.log",
        )
        by_kind["test_environment"].update(
            status="available",
            source="PCR02-real-device",
            version="fixture-env",
            evidence_ref="evidence/test-environment.json",
        )
        manifest["missing_critical"] = []
        manifest["readiness"] = "READY"
        result = validator.validate_manifest(manifest, "debug", require_terminal_ready=True)
        self.assertTrue(result["terminal_acceptable"])
        self.assertEqual(result["blockers"], [])

    def test_blocked_manifest_is_rejected_for_terminal_evidence(self):
        manifest = self._debug_manifest()
        with self.assertRaisesRegex(AssertionError, "cannot use BLOCKED material manifest"):
            validator.validate_manifest(manifest, "debug", require_terminal_ready=True)

    def test_existing_ready_fixture_is_terminal_acceptable(self):
        manifest = json.loads((ROOT / "tests" / "fixtures" / "material-manifest.valid.json").read_text(encoding="utf-8"))
        result = validator.validate_manifest(manifest, "feature", require_terminal_ready=True)
        self.assertEqual(result["readiness"], "READY")
        self.assertTrue(result["terminal_acceptable"])


if __name__ == "__main__":
    unittest.main()
