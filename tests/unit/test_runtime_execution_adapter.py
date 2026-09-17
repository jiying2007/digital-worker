from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import runtime_execution_adapter as adapter


ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = ROOT / "config/integrations/runtime-execution-profiles.json"
SCRIPT_PATH = ROOT / "scripts/runtime_execution_adapter.py"


class RuntimeExecutionAdapterTests(unittest.TestCase):
    def test_default_development_path_is_native_codex_cli(self) -> None:
        registry = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(registry["default_development_profile"], "codex-cli-native")
        profile = registry["profiles"]["codex-cli-native"]
        self.assertEqual(profile["runtime"], "codex")
        self.assertEqual(profile["executor"], "native-cli")
        self.assertEqual(profile["credential_mode"], "runtime-managed-session")
        self.assertEqual(profile["endpoint_mode"], "runtime-managed")
        self.assertFalse(profile["verification_authority"])

    def test_core_contract_does_not_bind_vendor_api_key_names(self) -> None:
        text = PROFILE_PATH.read_text(encoding="utf-8") + SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertNotIn("OPENAI_API_KEY", text)
        self.assertNotIn("ANTHROPIC_API_KEY", text)
        self.assertIn("credential_material_must_not_enter_execution_receipts", text)
        self.assertIn("credential_material_recorded", text)

    def _git_repo(self, root: Path) -> str:
        subprocess.run(["git", "init", "--quiet", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "Runtime Test"], check=True)
        (root / "README.md").write_text("fixture\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "--quiet", "-m", "fixture"], check=True)
        return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()

    def _fake_codex(self, bindir: Path) -> None:
        path = bindir / "codex"
        path.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "if [ \"${1:-}\" = \"--version\" ]; then echo 'codex-cli 9.9.9'; exit 0; fi\n"
            "if [ \"${1:-}\" != \"exec\" ]; then exit 64; fi\n"
            "cat\n",
            encoding="utf-8",
        )
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def test_native_codex_execution_reuses_runtime_session_without_secret_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work = root / "work"
            work.mkdir()
            self._git_repo(work)
            bindir = root / "bin"
            bindir.mkdir()
            self._fake_codex(bindir)
            prompt = root / "prompt.txt"
            prompt.write_text("hello native codex\n", encoding="utf-8")
            output = root / "out.txt"
            receipt = root / "receipt.json"
            env = {
                "PATH": str(bindir) + os.pathsep + os.environ.get("PATH", ""),
                "OPENAI_API_KEY": "must-not-be-recorded",
                "ANTHROPIC_API_KEY": "must-not-be-recorded-either",
            }
            with mock.patch.dict(os.environ, env, clear=False):
                rc = adapter.main(
                    [
                        "run",
                        "--working-directory",
                        str(work),
                        "--prompt-file",
                        str(prompt),
                        "--output",
                        str(output),
                        "--receipt",
                        str(receipt),
                    ]
                )
            self.assertEqual(rc, 0)
            self.assertEqual(output.read_text(encoding="utf-8"), "hello native codex\n")
            value = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(value["runtime"], "codex")
            self.assertEqual(value["runtime_version"], "codex-cli 9.9.9")
            self.assertEqual(value["transport"]["credential_mode"], "runtime-managed-session")
            self.assertFalse(value["transport"]["credential_material_recorded"])
            raw = receipt.read_text(encoding="utf-8")
            self.assertNotIn("must-not-be-recorded", raw)

    def test_formal_mode_requires_exact_identity_and_clean_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work = root / "work"
            work.mkdir()
            head = self._git_repo(work)
            bindir = root / "bin"
            bindir.mkdir()
            self._fake_codex(bindir)
            prompt = root / "prompt.txt"
            prompt.write_text("formal\n", encoding="utf-8")
            output = root / "out.txt"
            receipt = root / "receipt.json"
            with mock.patch.dict(
                os.environ,
                {"PATH": str(bindir) + os.pathsep + os.environ.get("PATH", "")},
                clear=False,
            ):
                rc = adapter.main(
                    [
                        "run",
                        "--formal",
                        "--expected-head",
                        head,
                        "--source-set-identity",
                        "sha256:" + "1" * 64,
                        "--distribution-identity",
                        "sha256:" + "2" * 64,
                        "--working-directory",
                        str(work),
                        "--prompt-file",
                        str(prompt),
                        "--output",
                        str(output),
                        "--receipt",
                        str(receipt),
                    ]
                )
            self.assertEqual(rc, 0)
            value = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertTrue(value["formal_identity"]["formal"])
            self.assertEqual(value["formal_identity"]["expected_head"], head)


if __name__ == "__main__":
    unittest.main()
