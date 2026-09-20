from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "private_provider_proof.py"
PROOF = ROOT / "config" / "integrations" / "proofs" / "knowledge-control-plane-51e4f816.json"

spec = importlib.util.spec_from_file_location("private_provider_proof", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PrivateProviderProofTests(unittest.TestCase):
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
