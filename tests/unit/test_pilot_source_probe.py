#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "embedded_pilot_source_probe", ROOT / "scripts" / "embedded_pilot_source_probe.py"
)
assert SPEC and SPEC.loader
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class PilotSourceProbeTests(unittest.TestCase):
    def _repo(self, root: Path) -> Path:
        repo = root / "source"
        repo.mkdir()
        subprocess.run(["git", "init", str(repo)], check=True, capture_output=True, text=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test User"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
        (repo / "tracked.txt").write_text("baseline\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "tracked.txt"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-m", "baseline"], check=True, capture_output=True, text=True)
        return repo

    def test_clean_repo_records_exact_head_without_promotion_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            report = probe.build_report(repo, [])

            self.assertRegex(report["source_identity"]["head_sha"], r"^[0-9a-f]{40}$")
            self.assertTrue(report["source_identity"]["working_tree_clean"])
            self.assertTrue(report["source_identity_ready"])
            self.assertFalse(report["promotion_eligible"])
            self.assertIn("phase3_evidence", report["not_authoritative_for"])
            self.assertIn("canonical_routing_switch", report["not_authoritative_for"])

    def test_dirty_repo_is_not_source_identity_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            (repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
            report = probe.build_report(repo, [])

            self.assertFalse(report["source_identity"]["working_tree_clean"])
            self.assertFalse(report["source_identity_ready"])
            self.assertGreater(report["source_identity"]["dirty_entry_count"], 0)
            self.assertRegex(report["source_identity"]["dirty_status_sha256"], r"^[0-9a-f]{64}$")
            self.assertFalse(report["promotion_eligible"])

    def test_evidence_file_is_hashed_without_claiming_material_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self._repo(root)
            log = root / "ubifs.log"
            log.write_bytes(b"UBIFS error: test fixture\n")

            report = probe.build_report(repo, [("ubifs_log", log)])
            item = report["evidence_files"][0]

            self.assertEqual(item["kind"], "ubifs_log")
            self.assertEqual(item["size"], len(b"UBIFS error: test fixture\n"))
            self.assertEqual(item["sha256"], probe.sha256_file(log))
            self.assertIn("material_readiness", report["not_authoritative_for"])
            self.assertFalse(report["promotion_eligible"])

    def test_duplicate_evidence_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            probe.parse_evidence(["log=/tmp/a", "log=/tmp/b"])


if __name__ == "__main__":
    unittest.main()
