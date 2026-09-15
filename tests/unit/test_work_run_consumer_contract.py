from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "config" / "integrations" / "cross-repo-lock.json"
CATALOG = ROOT / "contracts" / "catalog.json"
REUSE_SCHEMA = ROOT / "schemas" / "knowledge-reuse-evidence.v1.schema.json"
VERIFICATION = ROOT / "domains" / "edge-foundation" / "assurance" / "verification.yaml"
REVIEW = ROOT / "domains" / "edge-foundation" / "assurance" / "review.yaml"


class WorkRunConsumerContractTests(unittest.TestCase):
    def test_codex_bootstrap_12_and_work_run_handoff_are_promoted(self) -> None:
        lock = json.loads(LOCK.read_text(encoding="utf-8"))
        codex = lock["runtime_bindings"]["codex"]
        self.assertEqual(codex["commit"], "729c54192ae9dc69a8a4d7ecf913c1069c0a1ddf")
        self.assertEqual(codex["contract_version"], "2.1")
        self.assertEqual(codex["session_bootstrap_contract_version"], "1.2")
        self.assertEqual(
            codex["session_bootstrap_contract_canonical_sha256"],
            "d60b577b9cb3908cdbe29a6f1637858201f6ee392f55a20933cb85c411ef0de0",
        )
        self.assertIn("WORK_RUN", codex["validation"])
        self.assertIn("RECEIPT_V2", codex["validation"])

        rules = lock["rules"]
        for key in (
            "formal_mode_requires_authoritative_work_run_identity_from_engineering_task_package",
            "formal_execution_source_set_binds_work_item_run_and_package_identity",
            "runtime_receipt_v2_must_reuse_frozen_work_run_and_source_set_identity",
            "formal_assurance_run_id_must_match_frozen_run_identity",
        ):
            self.assertTrue(rules[key], key)

    def test_knowledge_route_promotion_is_not_regressed_by_codex_promotion(self) -> None:
        lock = json.loads(LOCK.read_text(encoding="utf-8"))
        knowledge = lock["providers"]["knowledge_control_plane"]
        self.assertEqual(knowledge["contract_version"], "1.2")
        self.assertIn("ROUTE_REGISTERED", knowledge["validation"])
        self.assertIn("REUSE_PENDING", knowledge["validation"])
        self.assertTrue(lock["rules"]["governed_knowledge_route_registration_does_not_imply_real_reuse"])
        self.assertTrue(lock["rules"]["knowledge_closed_loop_requires_real_reuse_evidence"])

    def test_e3_reuse_gate_from_current_main_coexists_with_work_run_promotion(self) -> None:
        self.assertTrue(REUSE_SCHEMA.is_file())
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in catalog["contracts"]}
        reuse = by_id["knowledge-reuse-evidence"]
        self.assertEqual(reuse["version"], "1")
        self.assertEqual(reuse["path"], "schemas/knowledge-reuse-evidence.v1.schema.json")
        self.assertEqual(reuse["compatibility"], "optional-fail-closed-v1")

    def test_assurance_policies_bind_report_run_to_frozen_work_run(self) -> None:
        for path in (VERIFICATION, REVIEW):
            policy = yaml.safe_load(path.read_text(encoding="utf-8"))
            formal = policy["formal_provenance"]
            self.assertEqual(
                formal["exact_bindings"]["run_id"],
                "session-bootstrap.work_identity.run_id",
            )
            self.assertIn("run_id", formal["required_fields"])
            self.assertTrue(policy["rules"]["formal_report_run_id_must_match_frozen_work_run_identity"])


if __name__ == "__main__":
    unittest.main()
