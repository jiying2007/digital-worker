import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "reports/runtime-r2/freeze/R2-FEATURE-PCR02-OTA-001/freeze-receipt.json"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class RuntimeR2FreezeLedgerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = json.loads(RECEIPT.read_text(encoding="utf-8"))

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

        text = RECEIPT.read_text(encoding="utf-8").lower()
        for forbidden in (
            '"verification_status": "pass"',
            '"independent_review_status": "pass"',
            '"r2_qualified": true',
            '"provider_execution_authorized": true',
        ):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
