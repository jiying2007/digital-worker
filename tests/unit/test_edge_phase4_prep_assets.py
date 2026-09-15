from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DOMAIN = ROOT / "domains" / "edge-foundation" / "domain.yaml"


class EdgePhase4PrepAssetsTest(unittest.TestCase):
    def test_target_asset_validator_passes(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/validate_edge_foundation_target_assets.py"],
            cwd=ROOT,
            check=True,
        )

    def test_domain_registers_canonical_target_assets(self) -> None:
        domain = yaml.safe_load(DOMAIN.read_text(encoding="utf-8"))
        assets = domain["target_assets"]
        self.assertEqual(assets["ownership_authority"], "canonical")
        self.assertEqual(assets["execution_surface"], "legacy-compatible")
        self.assertEqual(assets["skill_registry"], "skills.yaml")
        self.assertEqual(assets["gate_policy"], "gate-policy.yaml")
        self.assertEqual(assets["evaluation_cases"], "evaluation/golden-cases.yaml")
        self.assertTrue(assets["legacy_expert_identity_in_target_assets_forbidden"])
        self.assertTrue(assets["physical_asset_move_deferred_until_canonical_switch"])
        self.assertFalse(domain["migration"]["canonical_routing_switched"])


if __name__ == "__main__":
    unittest.main()
