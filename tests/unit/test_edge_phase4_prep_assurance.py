from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DOMAIN = ROOT / "domains" / "edge-foundation" / "domain.yaml"


class EdgePhase4PrepAssuranceTest(unittest.TestCase):
    def test_target_assurance_validator_passes(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/validate_edge_foundation_assurance.py"],
            cwd=ROOT,
            check=True,
        )

    def test_domain_binds_verification_and_review_contracts(self) -> None:
        domain = yaml.safe_load(DOMAIN.read_text(encoding="utf-8"))
        responsibilities = domain["assurance"]["responsibilities"]
        self.assertEqual(responsibilities["verification"]["contract"], "assurance/verification.yaml")
        self.assertFalse(responsibilities["verification"]["self_approval_by_implementation"])
        self.assertEqual(responsibilities["review"]["contract"], "assurance/review.yaml")
        self.assertTrue(responsibilities["review"]["independent_from_domain_decision_and_execution"])
        self.assertFalse(domain["migration"]["canonical_routing_switched"])


if __name__ == "__main__":
    unittest.main()
