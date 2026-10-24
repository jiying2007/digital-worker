from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
SCRIPT = ROOT / "scripts" / "private_provider_proof.py"
PROOF = ROOT / "config" / "integrations" / "proofs" / "knowledge-control-plane-51e4f816.json"

spec = importlib.util.spec_from_file_location("private_provider_proof", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PrivateProviderProofTests(unittest.TestCase):
    def run_without_agent(self, callback):
        actual_run = module.subprocess.run
        commands = []

        def unavailable_agent(args, **kwargs):
            commands.append(args)
            # Exercise the actual GPG binary with an agent that cannot start;
            # neither a mock success nor an ambient user's agent can help.
            return actual_run([args[0], "--agent-program", "/nonexistent/dw-unavailable-gpg-agent", *args[1:]], **kwargs)

        with patch.object(module.subprocess, "run", side_effect=unavailable_agent):
            result = callback()
        self.assertEqual(len(commands), 2)
        self.assertTrue(all("--no-autostart" in command for command in commands))
        return result

    def test_public_key_proof_verifies_with_agent_unavailable(self) -> None:
        result = self.run_without_agent(lambda: self.verify(PROOF))
        self.assertEqual(result["status"], "PASS")

    def test_agent_unavailable_does_not_allow_invalid_signature(self) -> None:
        value = json.loads(PROOF.read_text(encoding="utf-8"))
        signature = value["commit_signature"]
        signature["payload"] += "tampered message\n"
        headers, message = signature["payload"].split("\n\n", 1)
        commit_object = headers + "\ngpgsig " + signature["signature"].replace("\n", "\n ") + "\n\n" + message
        value["commit"] = module._git_hash("commit", commit_object.encode("utf-8"))

        def verify_invalid():
            with self.assertRaisesRegex(module.ProofError, "commit signature verification failed.*gpg exit"):
                module._verify_signature(value, ROOT)

        self.run_without_agent(verify_invalid)

    def test_import_failure_preserves_bounded_redacted_diagnostic_and_stops(self) -> None:
        diagnostic = "x" * 5000 + "\ngpg: import failed https://user:secret@example.invalid/key?token=secret#fragment"
        failure = module.subprocess.CompletedProcess(["gpg"], 2, diagnostic)
        with patch.object(module.subprocess, "run", return_value=failure) as command:
            with self.assertRaises(module.ProofError) as caught:
                self.verify(PROOF)
        message = str(caught.exception)
        self.assertIn("unable to import private-provider trust key (gpg exit 2)", message)
        self.assertIn("gpg: import failed https://example.invalid/key", message)
        self.assertNotIn("secret", message)
        self.assertLess(len(message), 4200)
        self.assertEqual(command.call_count, 1)

    def test_verification_failure_preserves_diagnostic_and_never_qualifies(self) -> None:
        imported = module.subprocess.CompletedProcess(["gpg"], 0, "imported")
        failed = module.subprocess.CompletedProcess(["gpg"], 2, "gpg: Can't check signature: No public key")
        with patch.object(module.subprocess, "run", side_effect=[imported, failed]) as command:
            with self.assertRaisesRegex(module.ProofError, "gpg exit 2.*No public key"):
                self.verify(PROOF)
        self.assertEqual(command.call_count, 2)

    def test_signed_proof_cannot_be_relabelled_to_another_commit(self) -> None:
        value = json.loads(PROOF.read_text(encoding="utf-8"))
        value["commit"] = "0" * 40
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "proof.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(module.ProofError, "commit object SHA"):
                module.verify_proof(
                    root=ROOT, proof_path=path, expected_repository=value["repository"],
                    expected_commit=value["commit"], expected_contract_path=value["contract_path"],
                    expected_contract_version=value["contract_version"],
                    expected_contract_digest=value["contract_canonical_sha256"],
                )

    def test_proof_cannot_select_its_own_trust_key(self) -> None:
        value = json.loads(PROOF.read_text(encoding="utf-8"))
        value["commit_signature"]["trust_key_path"] = "/tmp/untrusted-key.asc"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "proof.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(module.ProofError, "configured trust anchor"):
                self.verify(path)

    def verify(self, path: Path):
        return module.verify_proof(
            root=ROOT,
            proof_path=path,
            expected_repository="jiying2007/knowledge-hub",
            expected_commit="51e4f8166657d9d082f523335d350d0e8c2890a9",
            expected_contract_path="registry/integrations/digital-worker.json",
            expected_contract_version="1.2",
            expected_contract_digest="7e67ff9f19ef8a1bc627e589d888fcf8370297c7ceafa26e8d65d9d0630c3d11",
        )

    def test_real_private_provider_proof_verifies_offline(self) -> None:
        result = self.verify(PROOF)
        self.assertEqual("PASS", result["status"])
        self.assertEqual("signed-git-object-proof", result["verification_mode"])
        self.assertFalse(result["provider_network_accessed"])
        self.assertEqual(
            "968479A1AFF927E37D1A566BB5690EEEBB952194",
            result["signer_key_fingerprint"],
        )
        self.assertEqual(
            "e4d67e7704a353beb723d211ad7aa2770d646abe",
            result["contract_blob_sha"],
        )

    def test_contract_snapshot_tamper_fails_closed(self) -> None:
        value = json.loads(PROOF.read_text(encoding="utf-8"))
        value["contract_text"] += " "
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "proof.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises(module.ProofError):
                self.verify(path)

    def test_tree_proof_tamper_fails_closed(self) -> None:
        value = json.loads(PROOF.read_text(encoding="utf-8"))
        value["trees"][0]["entries"][0]["sha"] = "0" * 40
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "proof.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises(module.ProofError):
                self.verify(path)

    def test_signer_identity_tamper_fails_closed(self) -> None:
        value = json.loads(PROOF.read_text(encoding="utf-8"))
        value["commit_signature"]["signer_key_fingerprint"] = "0" * 40
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "proof.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaises(module.ProofError):
                self.verify(path)


if __name__ == "__main__":
    unittest.main()
