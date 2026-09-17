from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "evaluate_edge_foundation_product_readiness.py"
SCHEMA = ROOT / "schemas" / "edge-foundation-product-readiness.v1.schema.json"
DOMAIN = ROOT / "domains" / "edge-foundation" / "domain.yaml"


def load_module():
    spec = importlib.util.spec_from_file_location("edge_product_readiness", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load product-readiness evaluator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProductReadinessBlockingScopeTests(unittest.TestCase):
    def test_domain_declares_product_only_blocking_scope(self) -> None:
        text = DOMAIN.read_text(encoding="utf-8")
        self.assertIn("blocking_scope: product-readiness-only", text)
        self.assertIn("development_blocking: false", text)
        self.assertIn("integration_blocking: false", text)
        self.assertIn("control_plane_blocking: false", text)

    def test_zero_receipt_state_is_fail_closed_but_not_iteration_blocking(self) -> None:
        module = load_module()
        result = module.evaluate([])
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["operational_status"], "product_readiness_in_progress")
        self.assertEqual(result["blocking_scope"], "product-readiness-only")
        self.assertFalse(result["development_blocking"])
        self.assertFalse(result["integration_blocking"])
        self.assertFalse(result["control_plane_blocking"])
        self.assertTrue(result["product_readiness_blocking"])
        self.assertFalse(result["eligible_for_product_review"])
        self.assertTrue(result["blockers"])

    def test_schema_enforces_scoped_blocked_and_ready_semantics(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        blocked = load_module().evaluate([])
        Draft202012Validator(schema).validate(blocked)

        bad = dict(blocked)
        bad["integration_blocking"] = True
        with self.assertRaises(Exception):
            Draft202012Validator(schema).validate(bad)

        bad_scope = dict(blocked)
        bad_scope["blocking_scope"] = "none"
        with self.assertRaises(Exception):
            Draft202012Validator(schema).validate(bad_scope)


if __name__ == "__main__":
    unittest.main()
