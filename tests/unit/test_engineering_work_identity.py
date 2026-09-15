from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "domains" / "edge-foundation" / "schemas" / "engineering-task-package.schema.json"
CURRENT_PACKAGE = ROOT / "tests" / "fixtures" / "engineering-task-package.valid.json"
CURRENT_TASK = ROOT / "tests" / "fixtures" / "task-brief.valid.json"
HISTORICAL_PACKAGE = (
    ROOT
    / "domains"
    / "edge-foundation"
    / "pilot"
    / "evidence"
    / "FEATURE-PCR02-OTA-001"
    / "engineering-task-package.json"
)


class EngineeringWorkIdentityTests(unittest.TestCase):
    def test_additive_schema_keeps_retained_real_package_valid(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        historical = json.loads(HISTORICAL_PACKAGE.read_text(encoding="utf-8"))
        jsonschema.validate(instance=historical, schema=schema)
        self.assertNotIn("work_item_id", historical)

    def test_current_package_threads_authoritative_work_and_run_identity(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        package = json.loads(CURRENT_PACKAGE.read_text(encoding="utf-8"))
        task = json.loads(CURRENT_TASK.read_text(encoding="utf-8"))
        jsonschema.validate(instance=package, schema=schema)
        self.assertEqual(package["work_item_id"], task["work_item_id"])
        self.assertTrue(package["run_id"].strip())

    def test_work_item_id_is_additive_not_globally_required(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertIn("work_item_id", schema["properties"])
        self.assertNotIn("work_item_id", schema["required"])
        self.assertEqual(schema["properties"]["work_item_id"]["minLength"], 1)
        self.assertEqual(schema["properties"]["run_id"]["minLength"], 1)


if __name__ == "__main__":
    unittest.main()
