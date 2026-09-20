#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

PROOF_SCHEMA = "digital-worker-private-provider-git-proof/v1"


class ProofError(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _git_hash(kind: str, payload: bytes) -> str:
    header = f"{kind} {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _tree_hash(entries: list[dict[str, Any]]) -> str:
    body = bytearray()
    for entry in entries:
        mode = str(entry.get("mode", ""))
        path = str(entry.get("path", ""))
        sha = str(entry.get("sha", ""))
        if not mode or not path or len(sha) != 40:
            raise ProofError("tree proof entry is incomplete")
        if mode.startswith("0"):
            mode = mode.lstrip("0") or "0"
        try:
            raw_sha = bytes.fromhex(sha)
        except ValueError as exc:
            raise ProofError("tree proof entry SHA is invalid") from exc
        body.extend(mode.encode("ascii"))
        body.extend(b" ")
        body.extend(path.encode("utf-8"))
        body.extend(b"\0")
        body.extend(raw_sha)
    return _git_hash("tree", bytes(body))


def _verify_signature(proof: dict[str, Any], root: Path) -> dict[str, Any]:
    signature = proof.get("commit_signature")
    if not isinstance(signature, dict):
        raise ProofError("commit_signature is missing")
    if signature.get("verified_by_github") is not True or signature.get("reason") != "valid":
        raise ProofError("captured GitHub commit verification is not valid")
    fingerprint = str(signature.get("signer_key_fingerprint", "")).upper()
    if len(fingerprint) != 40:
        raise ProofError("signer key fingerprint is invalid")
    trust_path = root / str(signature.get("trust_key_path", ""))
    if not trust_path.is_file():
        raise ProofError("private-provider trust key is missing")
    payload = signature.get("payload")
    detached = signature.get("signature")
    if not isinstance(payload, str) or not payload or not isinstance(detached, str) or not detached:
        raise ProofError("commit signature payload is incomplete")
    gpg = shutil.which("gpg")
    if not gpg:
        raise ProofError("gpg is required for private-provider proof verification")
    with tempfile.TemporaryDirectory(prefix="dw-private-provider-proof-") as tmp:
        tmp_root = Path(tmp)
        home = tmp_root / "gnupg"
        home.mkdir(mode=0o700)
        payload_path = tmp_root / "payload.txt"
        signature_path = tmp_root / "signature.asc"
        payload_path.write_text(payload, encoding="utf-8")
        signature_path.write_text(detached, encoding="utf-8")
        env = dict(os.environ)
        env["GNUPGHOME"] = str(home)
        imported = subprocess.run(
            [gpg, "--batch", "--import", str(trust_path)],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if imported.returncode != 0:
            raise ProofError("unable to import private-provider trust key")
        verified = subprocess.run(
            [gpg, "--batch", "--status-fd=1", "--verify", str(signature_path), str(payload_path)],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if verified.returncode != 0 or "[GNUPG:] GOODSIG " not in verified.stdout:
            raise ProofError("private-provider commit signature verification failed")
        valid_lines = [line for line in verified.stdout.splitlines() if line.startswith("[GNUPG:] VALIDSIG ")]
        if not valid_lines or fingerprint not in valid_lines[0].upper():
            raise ProofError("private-provider commit signer fingerprint mismatch")
    return {"fingerprint": fingerprint, "payload": payload}


def verify_proof(
    *,
    root: Path,
    proof_path: Path,
    expected_repository: str,
    expected_commit: str,
    expected_contract_path: str,
    expected_contract_version: str,
    expected_contract_digest: str,
) -> dict[str, Any]:
    try:
        proof = json.loads(proof_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProofError("private-provider proof is unreadable") from exc
    if not isinstance(proof, dict) or proof.get("schema") != PROOF_SCHEMA:
        raise ProofError("private-provider proof schema is unsupported")
    expected = {
        "repository": expected_repository,
        "commit": expected_commit,
        "contract_path": expected_contract_path,
        "contract_version": str(expected_contract_version),
        "contract_canonical_sha256": expected_contract_digest,
    }
    for field, value in expected.items():
        if str(proof.get(field)) != str(value):
            raise ProofError(f"private-provider proof {field} drift")

    boundary = proof.get("boundary")
    required_boundary = {
        "evidence_snapshot_only": True,
        "source_of_truth_stays_at_source": True,
        "provider_network_access_required_at_verification_time": False,
        "provider_mutation_permitted": False,
    }
    if not isinstance(boundary, dict) or any(boundary.get(k) is not v for k, v in required_boundary.items()):
        raise ProofError("private-provider proof authority boundary is invalid")

    signature = _verify_signature(proof, root)
    trees = proof.get("trees")
    if not isinstance(trees, list) or not trees:
        raise ProofError("private-provider tree proof is missing")
    computed: dict[str, str] = {}
    tree_docs: dict[str, dict[str, Any]] = {}
    for tree in trees:
        if not isinstance(tree, dict) or not isinstance(tree.get("entries"), list):
            raise ProofError("private-provider tree proof is invalid")
        prefix = str(tree.get("path_prefix", ""))
        actual = _tree_hash(tree["entries"])
        expected_sha = str(tree.get("sha", ""))
        if actual != expected_sha:
            raise ProofError(f"private-provider tree SHA mismatch: {prefix or '<root>'}")
        computed[prefix] = actual
        tree_docs[prefix] = tree

    payload_lines = signature["payload"].splitlines()
    if not payload_lines or payload_lines[0] != f"tree {computed.get('', '')}":
        raise ProofError("signed commit payload is not bound to the verified root tree")

    components = expected_contract_path.split("/")
    if len(components) < 2:
        raise ProofError("private-provider contract path must be nested")
    prefix = ""
    for component in components[:-1]:
        parent = tree_docs.get(prefix)
        if parent is None:
            raise ProofError(f"tree proof missing parent prefix: {prefix}")
        entry = next(
            (item for item in parent["entries"] if item.get("path") == component and item.get("type") == "tree"),
            None,
        )
        next_prefix = component if not prefix else f"{prefix}/{component}"
        if not isinstance(entry, dict) or entry.get("sha") != computed.get(next_prefix):
            raise ProofError(f"tree proof path binding mismatch: {next_prefix}")
        prefix = next_prefix

    leaf_tree = tree_docs.get(prefix)
    if leaf_tree is None:
        raise ProofError("private-provider leaf tree is missing")
    leaf_name = components[-1]
    leaf = next(
        (item for item in leaf_tree["entries"] if item.get("path") == leaf_name and item.get("type") == "blob"),
        None,
    )
    if not isinstance(leaf, dict):
        raise ProofError("private-provider contract blob entry is missing")

    contract_text = proof.get("contract_text")
    if not isinstance(contract_text, str):
        raise ProofError("private-provider contract snapshot is missing")
    blob_sha = _git_hash("blob", contract_text.encode("utf-8"))
    if blob_sha != proof.get("contract_blob_sha") or blob_sha != leaf.get("sha"):
        raise ProofError("private-provider contract blob SHA mismatch")
    try:
        contract = json.loads(contract_text)
    except json.JSONDecodeError as exc:
        raise ProofError("private-provider contract snapshot is invalid JSON") from exc
    if str(contract.get("contract_version")) != str(expected_contract_version):
        raise ProofError("private-provider contract version mismatch")
    canonical_sha256 = hashlib.sha256(_canonical(contract)).hexdigest()
    if canonical_sha256 != expected_contract_digest:
        raise ProofError("private-provider canonical contract digest mismatch")

    return {
        "schema": "digital-worker-private-provider-proof-check/v1",
        "status": "PASS",
        "repository": expected_repository,
        "commit": expected_commit,
        "contract": expected_contract_path,
        "contract_version": str(expected_contract_version),
        "contract_canonical_sha256": canonical_sha256,
        "contract_blob_sha": blob_sha,
        "root_tree_sha": computed[""],
        "signer_key_fingerprint": signature["fingerprint"],
        "verification_mode": "signed-git-object-proof",
        "provider_network_accessed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a signed offline Git object proof for a private provider contract")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--contract-version", required=True)
    parser.add_argument("--contract-digest", required=True)
    parser.add_argument("--summary-json", action="store_true")
    args = parser.parse_args()
    try:
        result = verify_proof(
            root=args.root.resolve(),
            proof_path=args.proof.resolve(),
            expected_repository=args.repository,
            expected_commit=args.commit,
            expected_contract_path=args.contract,
            expected_contract_version=args.contract_version,
            expected_contract_digest=args.contract_digest,
        )
        rc = 0
    except ProofError as exc:
        result = {"schema": "digital-worker-private-provider-proof-check/v1", "status": "FAIL", "error": str(exc)}
        rc = 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) if args.summary_json else json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
