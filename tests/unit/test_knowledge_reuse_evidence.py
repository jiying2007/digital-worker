from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "evaluate_knowledge_reuse_evidence.py"
SPEC = importlib.util.spec_from_file_location("knowledge_reuse_evaluator", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def valid_payload() -> dict:
    lock = json.loads((ROOT / "config/integrations/cross-repo-lock.json").read_text(encoding="utf-8"))
    provider = lock["providers"]["knowledge_control_plane"]
    return {
        "schema_version": 1,
        "work_item_id": "WORK-E3-001",
        "run_id": "RUN-E3-001",
        "source_type": "real",
        "evidence_origin": "real-run",
        "observed_at": "2026-09-15T15:45:00Z",
        "knowledge_provider": {
            "repository": provider["repository"],
            "commit": provider["commit"],
            "contract": provider["contract"],
            "contract_version": provider["contract_version"],
            "contract_canonical_sha256": provider["contract_canonical_sha256"],
            "context_fingerprint": "a" * 64,
        },
        "reuse_items": [
            {
                "knowledge_id": "embedded.spi-nand.ubifs-readonly-001",
                "source_real": True,
                "authority_ref": "authority://project-source/ssc305",
                "source_ref": "git://project/ssc305/docs/ubi-ubifs.md",
                "version_or_revision": "0123456789abcdef0123456789abcdef01234567",
                "acl_state": "allowed",
                "acl_evidence_refs": ["receipt://knowledge/acl/001"],
                "freshness_state": "fresh",
                "freshness_evidence_refs": ["receipt://knowledge/freshness/001"],
                "conflict_state": "none",
                "provenance_ref": "receipt://knowledge/provenance/001",
                "actual_use_refs": ["claim://RUN-E3-001/root-cause-1"],
            }
        ],
        "knowledge_harvest_ref": "working/knowledge-harvest.md",
    }


class KnowledgeReuseEvidenceTests(unittest.TestCase):
    def test_structurally_complete_real_reuse_is_eligible(self):
        receipt = MODULE.evaluate(valid_payload())
        self.assertEqual(receipt["status"], "ELIGIBLE")
        self.assertTrue(receipt["e3_knowledge_reuse_eligible"])
        self.assertEqual(receipt["blockers"], [])
        self.assertIn("product-readiness", receipt["does_not_imply"])

    def test_controlled_fixture_cannot_close_e3(self):
        payload = valid_payload()
        payload["evidence_origin"] = "controlled-fixture"
        receipt = MODULE.evaluate(payload)
        self.assertFalse(receipt["e3_knowledge_reuse_eligible"])
        self.assertIn("controlled-fixture-not-eligible", receipt["blockers"])

    def test_synthetic_run_cannot_close_e3(self):
        payload = valid_payload()
        payload["source_type"] = "synthetic"
        receipt = MODULE.evaluate(payload)
        self.assertFalse(receipt["e3_knowledge_reuse_eligible"])
        self.assertIn("synthetic-source-not-eligible", receipt["blockers"])

    def test_provider_identity_drift_fails_closed(self):
        payload = valid_payload()
        payload["knowledge_provider"]["commit"] = "f" * 40
        receipt = MODULE.evaluate(payload)
        self.assertFalse(receipt["e3_knowledge_reuse_eligible"])
        self.assertIn("knowledge-provider-identity-mismatch:commit", receipt["blockers"])

    def test_acl_freshness_conflict_and_nonreal_source_fail_closed(self):
        cases = [
            ("source_real", False, "reuse-item-1:source-not-real"),
            ("acl_state", "unresolved", "reuse-item-1:acl-not-allowed"),
            ("freshness_state", "stale", "reuse-item-1:freshness-not-fresh"),
            ("conflict_state", "detected", "reuse-item-1:authority-conflict-unresolved"),
        ]
        for field, value, blocker in cases:
            with self.subTest(field=field):
                payload = copy.deepcopy(valid_payload())
                payload["reuse_items"][0][field] = value
                receipt = MODULE.evaluate(payload)
                self.assertFalse(receipt["e3_knowledge_reuse_eligible"])
                self.assertIn(blocker, receipt["blockers"])


if __name__ == "__main__":
    unittest.main()
