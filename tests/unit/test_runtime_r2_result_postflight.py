from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/runtime_r2_result_postflight.py"
SCHEMA = ROOT / "schemas/runtime-r2-host-verifier.v1.schema.json"

spec = importlib.util.spec_from_file_location("runtime_r2_result_postflight_test", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

BASE = "a" * 40
BLOB = "b" * 40
PACKAGE = "ota_pkg_v1.1.21.tar.gz"
PACKAGE_BYTES = b"test"
PACKAGE_SHA = hashlib.sha256(PACKAGE_BYTES).hexdigest()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def plan() -> dict:
    return {
        "controlled_task": {
            "repo_root": "jiying2007/ota_download_test",
            "exact_base_commit": BASE,
            "artifact_identity": {
                "repository": "jiying2007/ota_download_test",
                "source_commit": BASE,
                "source_blob_sha": BLOB,
                "path": PACKAGE,
                "size_bytes": len(PACKAGE_BYTES),
                "sha256": PACKAGE_SHA,
            },
            "host_verifier_contract": {
                "descriptor_path": ".r2/host-verifier.json",
                "schema": "digital-worker-runtime-r2-host-verifier/v1",
                "schema_ref": "schemas/runtime-r2-host-verifier.v1.schema.json",
                "schema_sha256": sha(SCHEMA),
                "replay_self_contained": True,
                "git_metadata_required": False,
                "descriptor_shape": {
                    "top_level_fields": ["schema", "replay_self_contained", "steps"],
                    "step_fields": ["kind", "entrypoint", "args"],
                    "allowed_kinds": ["python", "shell", "unittest"],
                },
            },
        }
    }


def make_tree(root: Path, descriptor: dict, verifier_source: str = "print('ok')\n") -> Path:
    tree = root / "tree"
    (tree / ".r2").mkdir(parents=True)
    (tree / "tools").mkdir(parents=True)
    (tree / PACKAGE).write_bytes(PACKAGE_BYTES)
    (tree / "SHA256SUMS.txt").write_text(f"{PACKAGE_SHA}  {PACKAGE}\n", encoding="utf-8")
    write_json(
        tree / "artifact-identity.json",
        {
            "repository": "jiying2007/ota_download_test",
            "source_commit": BASE,
            "source_blob_sha": BLOB,
            "path": PACKAGE,
            "size_bytes": len(PACKAGE_BYTES),
            "sha256": PACKAGE_SHA,
        },
    )
    write_json(tree / ".r2/host-verifier.json", descriptor)
    (tree / "tools/verify.py").write_text(verifier_source, encoding="utf-8")
    return tree


def archive_tree(tree: Path, archive: Path) -> None:
    with tarfile.open(archive, "w:gz") as tf:
        for path in sorted(x for x in tree.rglob("*") if x.is_file()):
            tf.add(path, arcname=path.relative_to(tree).as_posix())


class RuntimeR2ResultPostflightTests(unittest.TestCase):
    def test_replay_self_contained_result_passes(self) -> None:
        descriptor = {
            "schema": "digital-worker-runtime-r2-host-verifier/v1",
            "replay_self_contained": True,
            "steps": [
                {
                    "kind": "python",
                    "entrypoint": "tools/verify.py",
                    "args": [],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp_value:
            tmp = Path(tmp_value)
            frozen = tmp / "plan.json"
            write_json(frozen, plan())
            tree = make_tree(tmp, descriptor)
            archive = tmp / "result.tar.gz"
            archive_tree(tree, archive)
            out = tmp / "out"
            receipt = module.run_postflight(frozen, archive, out)
            self.assertEqual(receipt["status"], "pass")
            self.assertTrue(receipt["replay_self_contained"])
            self.assertFalse(receipt["git_metadata_present"])
            self.assertFalse(receipt["verification_pass_claimed"])
            self.assertTrue((out / "result-postflight-host.log").is_file())
            self.assertTrue((out / "result-postflight-ota.log").is_file())

    def test_descriptor_extra_field_fails_closed(self) -> None:
        descriptor = {
            "schema": "digital-worker-runtime-r2-host-verifier/v1",
            "working_directory": ".",
            "steps": [
                {
                    "id": "verify-frozen-artifact",
                    "kind": "python",
                    "command": ["python3", "tools/verify.py"],
                    "receipt": ".r2/host-verifier-receipt.json",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp_value:
            tmp = Path(tmp_value)
            frozen = tmp / "plan.json"
            write_json(frozen, plan())
            tree = make_tree(tmp, descriptor)
            archive = tmp / "result.tar.gz"
            archive_tree(tree, archive)
            with self.assertRaisesRegex(
                module.PostflightError,
                "schema validation failed",
            ):
                module.run_postflight(frozen, archive, tmp / "out")

    def test_declared_python_verifier_failure_fails_closed(self) -> None:
        descriptor = {
            "schema": "digital-worker-runtime-r2-host-verifier/v1",
            "replay_self_contained": True,
            "steps": [
                {
                    "kind": "python",
                    "entrypoint": "tools/verify.py",
                    "args": [],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp_value:
            tmp = Path(tmp_value)
            frozen = tmp / "plan.json"
            write_json(frozen, plan())
            tree = make_tree(tmp, descriptor, "if True print('broken')\n")
            archive = tmp / "result.tar.gz"
            archive_tree(tree, archive)
            with self.assertRaisesRegex(
                module.PostflightError,
                "verification command failed",
            ):
                module.run_postflight(frozen, archive, tmp / "out")


if __name__ == "__main__":
    unittest.main()
