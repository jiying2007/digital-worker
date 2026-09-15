from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DOMAIN = ROOT / "domains" / "edge-foundation" / "domain.yaml"
EXPERT = ROOT / "domains" / "edge-foundation" / "experts" / "embedded-system" / "expert.yaml"


class EdgePhase4PrepCapabilitiesTest(unittest.TestCase):
    def test_target_capability_validator_passes(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/validate_edge_foundation_capabilities.py"],
            cwd=ROOT,
            check=True,
        )

    def test_embedded_expert_owns_exact_capability_contract_set(self) -> None:
        domain = yaml.safe_load(DOMAIN.read_text(encoding="utf-8"))
        expert = yaml.safe_load(EXPERT.read_text(encoding="utf-8"))
        embedded = next(item for item in domain["experts"] if item["id"] == "embedded-system-expert")
        self.assertEqual(embedded["contract"], "experts/embedded-system/expert.yaml")
        self.assertEqual(set(embedded["capabilities"]), set(expert["capability_contracts"]))
        self.assertEqual(len(expert["capability_contracts"]), 5)
        self.assertTrue(expert["rules"]["expert_is_not_agent"])
        self.assertFalse(domain["migration"]["canonical_routing_switched"])


if __name__ == "__main__":
    unittest.main()
