from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DOMAIN = ROOT / "domains" / "edge-foundation" / "domain.yaml"


class EdgePhase4PrepCoordinationTest(unittest.TestCase):
    def test_target_coordination_validator_passes(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/validate_edge_foundation_coordination.py"],
            cwd=ROOT,
            check=True,
        )

    def test_domain_binds_coordination_role_contract(self) -> None:
        domain = yaml.safe_load(DOMAIN.read_text(encoding="utf-8"))
        role = domain["coordination_role"]
        self.assertEqual(role["id"], "edge-coordination")
        self.assertEqual(role["contract"], "coordination.yaml")
        self.assertFalse(role["is_domain_expert"])
        self.assertFalse(domain["migration"]["canonical_routing_switched"])


if __name__ == "__main__":
    unittest.main()
