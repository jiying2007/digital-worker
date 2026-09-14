from __future__ import annotations

import subprocess
import sys
import unittest


class EmbeddedOverviewWorkbookTest(unittest.TestCase):
    def test_workbook_is_synchronized_with_machine_contracts(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/validate_embedded_overview_workbook.py"],
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
