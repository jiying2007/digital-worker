from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DOMAIN = ROOT / "domains" / "edge-foundation" / "domain.yaml"
SCOPE = ROOT / "expert-groups" / "embedded-system" / "compatibility-scope.yaml"


class EdgePhase4PrepLegacyScopeTest(unittest.TestCase):
    def test_legacy_scope_validator_passes(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/validate_edge_foundation_legacy_scope.py"],
            cwd=ROOT,
            check=True,
        )

    def test_legacy_surface_has_no_canonical_ownership(self) -> None:
        domain = yaml.safe_load(DOMAIN.read_text(encoding="utf-8"))
        scope = yaml.safe_load(SCOPE.read_text(encoding="utf-8"))
        self.assertEqual(domain["migration"]["legacy_scope"], "../../expert-groups/embedded-system/compatibility-scope.yaml")
        self.assertEqual(scope["status"], "execution-adapter-only")
        self.assertFalse(scope["canonical_ownership"])
        self.assertFalse(scope["canonical_routing_switched"])
        self.assertTrue(scope["rules"]["physical_removal_before_canonical_switch_forbidden"])


if __name__ == "__main__":
    unittest.main()
