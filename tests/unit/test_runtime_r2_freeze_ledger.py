import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HISTORICAL_RECEIPT = ROOT / "reports/runtime-r2/freeze/R2-FEATURE-PCR02-OTA-001/freeze-receipt.json"
CURRENT_RECEIPT = ROOT / "reports/runtime-r2/freeze/R2-FEATURE-PCR02-OTA-001/freeze-receipt-35493819124.json"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class RuntimeR2FreezeLedgerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(HISTORICAL_RECEIPT.read_text(encoding="utf-8"))
        cls.current = json.loads(CURRENT_RECEIPT.read_text(encoding="utf-8"))

    def test_real_freeze_identity_is_immutable_and_exact(self):
        v = self.value
        self.assertEqual(v["schema"], "digital-worker-runtime-r2-freeze-receipt/v1")
        self.assertEqual(v["status"], "frozen-awaiting-independent-runtime-executions")
        self.assertEqual(v["campaign_id"], "R2-FEATURE-PCR02-OTA-001")

        src = v["source_evidence"]
        self.assertEqual(src["repository"], "jiying2007/digital-worker")
        self.assertEqual(src["workflow"], ".github/workflows/runtime-r2-freeze.yml")
        self.assertEqual(src["workflow_run_id"], "35300117234")
        self.assertEqual(src["workflow_run_attempt"], 1)
        self.assertEqual(src["event"], "workflow_dispatch")
        self.assertEqual(src["conclusion"], "success")
        self.assertRegex(src["head_sha"], SHA40)

        frozen = v["frozen_identity"]
        self.assertEqual(frozen["digital_worker_commit"], src["head_sha"])
        self.assertRegex(frozen["frozen_inputs_sha256"], SHA256)
        self.assertEqual(frozen["target_repository"], "jiying2007/ota_download_test")
        self.assertRegex(frozen["target_base_commit"], SHA40)
        self.assertEqual(frozen["adk_release"]["version"], "5.1.1")
        self.assertRegex(frozen["adk_release"]["commit"], SHA40)
        self.assertRegex(frozen["adk_release"]["artifact_sha256"], SHA256)
        self.assertEqual(set(frozen["runtime_bindings"]), {"codex", "claude-code"})
        for binding in frozen["runtime_bindings"].values():
            self.assertRegex(binding["commit"], SHA40)

    def test_receipt_binds_original_actions_artifact_without_replacing_it(self):
        artifact = self.value["artifact"]
        self.assertEqual(artifact["id"], "10530010120")
        self.assertEqual(artifact["name"], "runtime-r2-freeze-35300117234")
        self.assertEqual(artifact["size_in_bytes"], 4106)
        self.assertEqual(
            artifact["digest"],
            "sha256:7dc5a77f330463298aa95984b373a5675509a53689a45dcb2499e2ba117a3e98",
        )
        self.assertRegex(artifact["campaign_json_sha256"], SHA256)
        self.assertRegex(artifact["frozen_plan_json_sha256"], SHA256)
        self.assertLess(artifact["created_at"], artifact["expires_at"])

        boundary = self.value["authority_boundary"]
        self.assertIs(boundary["source_artifact_is_authoritative"], True)
        self.assertIs(boundary["tracked_receipt_is_derived_audit_anchor_only"], True)

    def test_freeze_receipt_cannot_claim_runtime_or_verification_authority(self):
        boundary = self.value["authority_boundary"]
        self.assertIs(boundary["provider_execution_authorized"], False)
        self.assertEqual(boundary["verification_status"], "pending")
        self.assertEqual(boundary["independent_review_status"], "pending")
        self.assertIs(boundary["r2_qualified"], False)

        text = HISTORICAL_RECEIPT.read_text(encoding="utf-8").lower()
        for forbidden in (
            '"verification_status": "pass"',
            '"independent_review_status": "pass"',
            '"r2_qualified": true',
            '"provider_execution_authorized": true',
        ):
            self.assertNotIn(forbidden, text)

    def test_current_adk_704_freeze_is_run_scoped_and_exact(self):
        historical = self.value
        current = self.current
        self.assertNotEqual(
            historical["source_evidence"]["workflow_run_id"],
            current["source_evidence"]["workflow_run_id"],
        )
        self.assertEqual(current["schema"], "digital-worker-runtime-r2-freeze-receipt/v1")
        self.assertEqual(current["status"], "frozen-awaiting-independent-runtime-executions")
        self.assertEqual(current["campaign_id"], "R2-FEATURE-PCR02-OTA-001")

        src = current["source_evidence"]
        self.assertEqual(src["workflow_run_id"], "35493819124")
        self.assertEqual(src["workflow_run_attempt"], 1)
        self.assertEqual(src["event"], "workflow_dispatch")
        self.assertEqual(src["head_sha"], "fdd6d8423517847ed9695c87e1a1a68e55b292e7")
        self.assertEqual(src["conclusion"], "success")

        artifact = current["artifact"]
        self.assertEqual(artifact["id"], "10600136622")
        self.assertEqual(artifact["name"], "runtime-r2-freeze-35493819124")
        self.assertEqual(artifact["size_in_bytes"], 4111)
        self.assertEqual(
            artifact["digest"],
            "sha256:e5fb5f8fd246b7892b08aabba5157b03a23f90404c7f63d9dbba0765baf4e984",
        )
        self.assertEqual(
            artifact["campaign_json_sha256"],
            "d8c272d9309abafb56400df4c3bce9ce6d063959d6772e9db225ec071ac88f59",
        )
        self.assertEqual(
            artifact["frozen_plan_json_sha256"],
            "06f2297f830f8cf0d0bd780bec47b20915569964e819c775a281b86875835517",
        )

        frozen = current["frozen_identity"]
        self.assertEqual(
            frozen["frozen_inputs_sha256"],
            "378fa49d74194618cfa7adac9929504275ad2fc2f9d17dcf3d7289a3eb804c56",
        )
        self.assertEqual(frozen["target_repository"], "jiying2007/ota_download_test")
        self.assertEqual(
            frozen["target_base_commit"],
            "eeb926bd1fff75d2a5d5abb9f0ede9c8f582cc6d",
        )
        adk = frozen["adk_release"]
        self.assertEqual(adk["version"], "7.0.4")
        self.assertEqual(adk["commit"], "1d6c28e89eb98a4af5ac978707730783f0c84437")
        self.assertEqual(adk["tree"], "c5b8fa7b11a81597ac2c7cd6fb44d7abf9605137")
        self.assertEqual(adk["manifest_blob"], "a5e5963545318c4a4498cda0d49d10f08c5f6412")
        self.assertEqual(
            adk["artifact_sha256"],
            "497e44ec83d2506c8721019aeca979965127b481203f33387806c51c0d1aff68",
        )
        self.assertEqual(
            frozen["runtime_bindings"]["codex"]["commit"],
            "79acb193cef381b4c8b72f00e0af15f87e32765c",
        )
        self.assertEqual(
            frozen["runtime_bindings"]["claude-code"]["commit"],
            "fba4551aa4a2abe5f74cff3c60e8318961b36add",
        )

        boundary = current["authority_boundary"]
        self.assertFalse(boundary["provider_execution_authorized"])
        self.assertEqual(boundary["verification_status"], "pending")
        self.assertEqual(boundary["independent_review_status"], "pending")
        self.assertFalse(boundary["r2_qualified"])
        self.assertTrue(boundary["historical_freeze_receipt_preserved"])

        text = CURRENT_RECEIPT.read_text(encoding="utf-8").lower()
        for forbidden in (
            '"verification_status": "pass"',
            '"independent_review_status": "pass"',
            '"r2_qualified": true',
            '"provider_execution_authorized": true',
        ):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
