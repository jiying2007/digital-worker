from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = (
    ROOT
    / "domains"
    / "edge-foundation"
    / "pilot"
    / "evidence"
    / "KNOWLEDGE-E3-PROVIDER-GAP-SNAPSHOT-001"
    / "provider-gap-snapshot.json"
)
INVENTORY = (
    ROOT
    / "domains"
    / "edge-foundation"
    / "pilot"
    / "evidence"
    / "KNOWLEDGE-E3-SOURCE-INVENTORY-001"
    / "source-inventory.json"
)
LOCK = ROOT / "config" / "integrations" / "cross-repo-lock.json"


class KnowledgeProviderGapAuthorityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        self.inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        self.lock = json.loads(LOCK.read_text(encoding="utf-8"))

    def test_snapshot_uses_exact_pinned_provider_identity(self) -> None:
        provider = self.snapshot["knowledge_provider"]
        authoritative = self.lock["providers"]["knowledge_control_plane"]

        for key in (
            "repository",
            "commit",
            "contract",
            "contract_version",
            "contract_canonical_sha256",
        ):
            self.assertEqual(provider[key], authoritative[key])

    def test_authority_ledger_remains_external_closure_required(self) -> None:
        ledger = self.snapshot["authority_ledger"]
        gaps = {item["id"]: item for item in self.snapshot["required_open_external_gaps"]}

        self.assertEqual(ledger["path"], "registry/knowledge-platform-p5-p10.json")
        self.assertEqual(
            ledger["blob_sha"], "447dbf7add8a16ad023bfe28c378f84e03453450"
        )
        self.assertEqual(ledger["implementation_status"], "qualified")
        self.assertEqual(ledger["adoption_status"], "external-closure-required")
        self.assertEqual(ledger["source_integration_adoption_status"], "provider-pilot-required")
        self.assertFalse(ledger["hub_credentials"])
        self.assertEqual(gaps["connector-provider-pilot"]["status"], "open")
        self.assertIn("ACL/tombstone", gaps["connector-provider-pilot"]["reason"])
        self.assertEqual(gaps["real-adoption-evidence"]["status"], "open")

    def test_digital_worker_synchronizes_claim_scope_without_closing_provider_gaps(self) -> None:
        alignment = self.snapshot["digital_worker_alignment"]

        self.assertEqual(alignment["status"], "consistent-open")
        self.assertTrue(alignment["provider_gap_claim_scope_synchronized"])
        self.assertFalse(alignment["provider_gaps_mirrored_as_local_qualification"])
        self.assertFalse(alignment["provider_gap_closure_claimed"])
        self.assertFalse(alignment["acl_negative_real_evidence_available_to_close_issue_16"])
        self.assertEqual(
            alignment["remaining_local_issue_16_requirement"],
            "acl-negative-real-evidence",
        )

    def test_inventory_now_has_one_honest_local_open_requirement(self) -> None:
        provider = self.inventory["provider_authority_snapshot"]
        progress = self.inventory["progress"]

        self.assertEqual(provider["status"], "synchronized-open")
        self.assertFalse(provider["provider_gap_closure_claimed"])
        self.assertEqual(
            self.inventory["open_requirements"], ["acl-negative-real-evidence"]
        )
        self.assertEqual(progress["provider_gap_claim_scope"], "synchronized-open")
        self.assertFalse(progress["issue_16_complete"])
        self.assertFalse(progress["knowledge_provider_qualification"])
        self.assertFalse(progress["terminal_maturity"])

    def test_snapshot_does_not_overclaim_external_closure(self) -> None:
        does_not_imply = set(self.snapshot["does_not_imply"])
        for claim in {
            "provider-gap-closure",
            "connector-provider-pilot-closure",
            "acl-negative-evidence-complete",
            "knowledge-provider-qualification",
            "issue-16-complete",
            "product-readiness",
            "terminal-maturity",
        }:
            self.assertIn(claim, does_not_imply)


if __name__ == "__main__":
    unittest.main()
