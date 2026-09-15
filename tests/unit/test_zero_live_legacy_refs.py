from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ZeroLiveLegacyRefsTest(unittest.TestCase):
    def test_active_surfaces_do_not_reference_retired_legacy_tree(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/validate_zero_live_legacy_refs.py"],
            cwd=ROOT,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
