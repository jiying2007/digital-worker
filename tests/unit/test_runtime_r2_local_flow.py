from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = "eeb926bd1fff75d2a5d5abb9f0ede9c8f582cc6d"
PACKAGE_PATH = "ota_pkg_v1.1.21.tar.gz"
PACKAGE_BYTES = b"test"
PACKAGE_SHA = hashlib.sha256(PACKAGE_BYTES).hexdigest()
PACKAGE_BLOB = "b" * 40


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evidence = load_module("runtime_r2_evidence_local_flow", ROOT / "scripts/runtime_r2_evidence.py")
intake = load_module("runtime_r2_intake_local_flow", ROOT / "scripts/runtime_r2_intake.py")
verify = load_module("runtime_r2_local_verify_local_flow", ROOT / "scripts/runtime_r2_local_verify.py")


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: Path) -> str:
    rows = []
    for path in sorted(x for x in root.rglob("*") if x.is_file() and ".git" not in x.parts):
        rows.append((path.relative_to(root).as_posix(), sha(path)))
    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


def current_head() -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()


def build_plan() -> dict:
    plan = evidence.build_plan(ROOT, digital_worker_commit=current_head(), target_head=BASE, target_clean=True)
    identity = {
        "repository": "jiying2007/ota_download_test",
        "source_commit": BASE,
        "source_blob_sha": PACKAGE_BLOB,
        "path": PACKAGE_PATH,
        "size_bytes": len(PACKAGE_BYTES),
        "sha256": PACKAGE_SHA,
    }
    plan["controlled_task"]["artifact_identity"] = identity
    plan["controlled_task"]["artifact_identity_contract"] = {
        "ref": "fixture/r2-artifact-identity.v1.json",
        "sha256": "a" * 64,
    }
    plan["engineering_task_package"]["artifact_identity"] = identity
    plan["engineering_task_package"]["artifact_identity_contract_ref"] = "fixture/r2-artifact-identity.v1.json"
    plan["engineering_task_package"]["artifact_identity_contract_sha256"] = "a" * 64
    plan["comparison_source_set"]["artifact_identity"] = identity
    plan["frozen_inputs_sha256"] = evidence._digest(plan["controlled_task"])
    return plan


def freeze(root: Path, plan: dict) -> Path:
    out = root / "freeze"
    out.mkdir()
    write_json(out / "frozen-plan.json", plan)
    write_json(
        out / "campaign.json",
        {
            "schema": "digital-worker-runtime-r2-campaign/v1",
            "campaign_id": plan["controlled_task"]["run_id"],
            "status": "frozen-awaiting-independent-runtime-executions",
            "digital_worker_commit": current_head(),
            "freeze_workflow_run_id": "12345",
            "frozen_inputs_sha256": plan["frozen_inputs_sha256"],
            "target_repository": "jiying2007/ota_download_test",
            "target_base_commit": BASE,
            "runtime_bindings": plan["runtime_bindings"],
            "runtime_execution": {
                "mode": "runtime-owned-local-terminal",
                "runbook": "docs/runbooks/runtime-r2-local-terminal.md",
                "adapters": {
                    "codex": "scripts/runtime-r2-local.sh",
                    "claude-code": "control/scripts/runtime-r2-local.sh",
                },
                "runtime_home_mode": "shared-user-home",
                "credential_state_in_evidence": False,
                "github_provider_credentials_required": False,
                "provider_credentials_must_not_enter_github": True,
            },
            "provider_credentials_held_by_digital_worker": False,
            "provider_execution_authorized": False,
            "verification_status": "pending",
            "independent_review_status": "pending",
        },
    )
    return out


def result_tree(root: Path, runtime: str) -> tuple[Path, str]:
    tree = root / f"{runtime}-result"
    (tree / "artifacts").mkdir(parents=True)
    (tree / "scripts").mkdir(parents=True)
    (tree / ".r2").mkdir(parents=True)
    (tree / PACKAGE_PATH).write_bytes(PACKAGE_BYTES)
    (tree / "SHA256SUMS.txt").write_text(
        f"{PACKAGE_SHA}  {PACKAGE_PATH}\n",
        encoding="utf-8",
    )
    write_json(
        tree / "artifacts/pcr02-ota-v1.1.21.identity.json",
        {
            "schema_version": 1,
            "artifact": {
                "repository": "jiying2007/ota_download_test",
                "source_commit": BASE,
                "source_blob_sha": PACKAGE_BLOB,
                "path": PACKAGE_PATH,
                "size_bytes": len(PACKAGE_BYTES),
                "sha256": PACKAGE_SHA,
            },
            "runtime_note": runtime,
        },
    )
    if runtime == "claude-code":
        (tree / "verify_artifact.py").write_text(
            "from pathlib import Path\n"
            "import hashlib\n"
            "package = Path('ota_pkg_v1.1.21.tar.gz')\n"
            "expected = '" + PACKAGE_SHA + "'\n"
            "actual = hashlib.sha256(package.read_bytes()).hexdigest()\n"
            "raise SystemExit(0 if actual == expected else 1)\n",
            encoding="utf-8",
        )
        steps = [
            {
                "kind": "python",
                "entrypoint": "verify_artifact.py",
                "args": [],
            }
        ]
    else:
        (tree / "scripts/verify_pcr02_ota_identity.sh").write_text(
            "#!/usr/bin/env bash\nset -euo pipefail\nsha256sum -c SHA256SUMS.txt\n",
            encoding="utf-8",
        )
        steps = [
            {
                "kind": "shell",
                "entrypoint": "scripts/verify_pcr02_ota_identity.sh",
                "args": [],
            }
        ]
    write_json(
        tree / ".r2/host-verifier.json",
        {
            "schema": "digital-worker-runtime-r2-host-verifier/v1",
            "replay_self_contained": True,
            "steps": steps,
        },
    )
    digest = tree_digest(tree)
    archive = root / f"{runtime}-result-tree.tar.gz"
    with tarfile.open(archive, "w:gz") as tf:
        for path in sorted(x for x in tree.rglob("*") if x.is_file()):
            tf.add(path, arcname=path.relative_to(tree).as_posix())
    return archive, digest


def codex_native(plan: dict, digest: str, postflight_sha: str) -> dict:
    controlled = plan["controlled_task"]
    binding = plan["runtime_bindings"]["codex"]
    return {
        "schema_version": 2,
        "work_item_id": controlled["work_item_id"],
        "run_id": controlled["run_id"],
        "execution_source_set_identity": controlled["runtime_source_set_identity_ref"],
        "digital_worker_governance_identity": controlled["digital_worker_governance_identity_ref"].removeprefix("sha256:"),
        "runtime_binding": {
            "repository": "jiying2007/codex",
            "commit": binding["commit"],
            "target": "codex-cli",
            "runtime_profile": "default",
            "runtime_host": "local-terminal",
            "source_set_identity_ref": "sha256:" + "3" * 64,
            "runtime_distribution_identity_ref": "sha256:" + "4" * 64,
        },
        "agent_assets": {
            "provider_repository": plan["adk_release_identity"]["repository"],
            "release_version": plan["adk_release_identity"]["version"],
            "release_tag": plan["adk_release_identity"]["tag"],
            "release_commit": plan["adk_release_identity"]["commit"],
            "asset_profile": controlled["adk_asset_profile"],
            "source_set_identity": "sha256:" + "3" * 64,
        },
        "runtime": {"provider": "openai", "cli_version": "test", "model": "test"},
        "permissions": {"sandbox": "workspace-write", "approval": "explicit-local-operator-execution"},
        "repository": {
            "repository": "jiying2007/ota_download_test",
            "base_commit": controlled["exact_base_commit"],
            "result_commit": None,
        },
        "execution": {"status": "completed", "runtime_local_gates": ["host"]},
        "evidence_refs": [
            "worktree-result:sha256:" + digest,
            "replay-postflight:sha256:" + postflight_sha,
        ],
    }


def claude_native(plan: dict, digest: str, postflight_sha: str) -> dict:
    binding = plan["runtime_bindings"]["claude-code"]
    return {
        "schema_version": 2,
        "status": "completed",
        "runtime": "claude-code",
        "frozen_inputs_sha256": plan["frozen_inputs_sha256"],
        "verification_pass_claimed": False,
        "runtime_identity": {
            "runtime_binding_repository": "jiying2007/claude",
            "runtime_binding_commit": binding["commit"],
            "runtime_target": "claude-code",
            "runtime_profile": "solo-dev",
            "runtime_host": "local-terminal",
            "runtime_provider": "anthropic",
            "runtime_version": "test",
            "runtime_source_set_identity_ref": "sha256:" + "5" * 64,
            "runtime_distribution_identity_ref": "sha256:" + "6" * 64,
        },
        "execution": {
            "started_at": "2026-09-20T00:00:00Z",
            "completed_at": "2026-09-20T00:01:00Z",
            "result_identity_ref": "sha256:" + "7" * 64,
            "source_identity_ref": plan["controlled_task"]["runtime_source_set_identity_ref"],
            "exit_code": 0,
            "summary": "test",
        },
        "evidence_refs": [
            "worktree-result:sha256:" + digest,
            "replay-postflight:sha256:" + postflight_sha,
        ],
    }


def runtime_dir(root: Path, runtime: str, plan: dict) -> Path:
    out = root / runtime
    out.mkdir()
    archive, digest = result_tree(root, runtime)
    target_archive = out / "result-tree.tar.gz"
    target_archive.write_bytes(archive.read_bytes())
    write_json(
        out / "result-postflight.json",
        {
            "schema": "digital-worker-runtime-r2-result-postflight/v1",
            "status": "pass",
            "replay_self_contained": True,
            "git_metadata_present": False,
            "descriptor_path": ".r2/host-verifier.json",
            "descriptor_schema": "digital-worker-runtime-r2-host-verifier/v1",
            "result_archive_sha256": sha(target_archive),
            "host_log_sha256": "a" * 64,
            "ota_log_sha256": "b" * 64,
            "verification_pass_claimed": False,
            "domain_verification_pass_claimed": False,
            "r2_qualified": False,
        },
    )
    postflight_sha = sha(out / "result-postflight.json")
    write_json(
        out / "provider-authorization.json",
        {
            "schema": f"{runtime}-r2-provider-authorization/v1",
            "authorized": True,
            "authorization_mode": "explicit-local-operator-execution",
            "actor": f"local-test-{runtime}",
            "runtime_host": "local-terminal",
            "runtime_home_mode": "shared-user-home",
            **(
                {
                    "execution_context_mode": "frozen-project-local",
                    "user_setting_source_loaded": False,
                }
                if runtime == "claude-code"
                else {}
            ),
            "credential_state_in_evidence": False,
            "frozen_inputs_sha256": plan["frozen_inputs_sha256"],
            "verification_or_release_authority": False,
            "github_provider_credential_used": False,
        },
    )
    if runtime == "codex":
        write_json(out / "codex-native.json", codex_native(plan, digest, postflight_sha))
        (out / "codex-events.jsonl").write_text("{}\n", encoding="utf-8")
        (out / "codex-final.txt").write_text("done\n", encoding="utf-8")
    else:
        write_json(out / "claude-native-validated.json", claude_native(plan, digest, postflight_sha))
        write_json(out / "claude-execution.json", {"status": "completed"})
    return out


class RuntimeR2LocalFlowTests(unittest.TestCase):
    def test_local_intake_and_domain_verification_complete_without_github_provider_attestation(self) -> None:
        plan = build_plan()
        with tempfile.TemporaryDirectory() as tmp_value:
            tmp = Path(tmp_value)
            freeze_dir = freeze(tmp, plan)
            codex_dir = runtime_dir(tmp, "codex", plan)
            claude_dir = runtime_dir(tmp, "claude-code", plan)

            intake_out = tmp / "intake"
            collection = intake.intake(ROOT, freeze_dir, codex_dir, claude_dir, intake_out)
            self.assertEqual(collection["schema"], "digital-worker-runtime-r2-local-intake/v1")
            self.assertEqual(collection["execution_venue"], "local-terminal")
            self.assertEqual(collection["runtime_home_mode"], "shared-user-home")
            self.assertFalse(collection["credential_state_in_evidence"])
            self.assertFalse(collection["github_provider_credentials_required"])
            self.assertEqual(set(collection["execution_receipts"]), {"codex", "claude-code"})
            self.assertEqual(
                collection["provider_execution_evidence"]["codex"]["runtime_binding_commit"],
                plan["runtime_bindings"]["codex"]["commit"],
            )
            codex_evidence = collection["provider_execution_evidence"]["codex"]
            self.assertRegex(codex_evidence["replay_postflight_sha256"], r"^[0-9a-f]{64}$")
            claude_evidence = collection["provider_execution_evidence"]["claude-code"]
            self.assertEqual(claude_evidence["execution_context_mode"], "frozen-project-local")
            self.assertFalse(claude_evidence["user_setting_source_loaded"])
            self.assertRegex(claude_evidence["replay_postflight_sha256"], r"^[0-9a-f]{64}$")

            verify_out = tmp / "verification"
            report = verify.verify_local_r2(
                ROOT,
                freeze_dir,
                codex_dir,
                claude_dir,
                verify_out,
                "local-verifier:test",
            )
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["verification_execution_venue"], "local-terminal")
            self.assertEqual(report["runtime_home_mode"], "shared-user-home")
            self.assertFalse(report["credential_state_in_evidence"])
            self.assertFalse(report["github_provider_credentials_required"])
            self.assertFalse(report["verification_pass_claimed_by_runtime"])
            self.assertEqual(report["independent_review_status"], "pending")
            self.assertEqual(set(report["provider_execution_evidence"]), {"codex", "claude-code"})

    def test_native_host_verification_executes_declared_python_step(self) -> None:
        plan = build_plan()
        with tempfile.TemporaryDirectory() as tmp_value:
            tmp = Path(tmp_value)
            tree = tmp / "tree"
            (tree / ".r2").mkdir(parents=True)
            (tree / "verify_artifact.py").write_text(
                "print('python verifier pass')\n",
                encoding="utf-8",
            )
            write_json(
                tree / ".r2/host-verifier.json",
                {
                    "schema": "digital-worker-runtime-r2-host-verifier/v1",
                    "replay_self_contained": True,
                    "steps": [
                        {
                            "kind": "python",
                            "entrypoint": "verify_artifact.py",
                            "args": [],
                        }
                    ],
                },
            )
            log = tmp / "host.log"
            verify._run_native_host_verification(tree, log, plan)
            text = log.read_text(encoding="utf-8")
            self.assertIn("verify_artifact.py", text)
            self.assertIn("[exit=0]", text)

    def test_native_host_verification_rejects_missing_descriptor(self) -> None:
        plan = build_plan()
        with tempfile.TemporaryDirectory() as tmp_value:
            tmp = Path(tmp_value)
            tree = tmp / "tree"
            tree.mkdir()
            log = tmp / "host.log"
            with self.assertRaisesRegex(
                verify.VerificationError,
                "missing host verifier descriptor",
            ):
                verify._run_native_host_verification(tree, log, plan)

    def test_local_intake_rejects_claude_user_setting_source(self) -> None:
        plan = build_plan()
        with tempfile.TemporaryDirectory() as tmp_value:
            tmp = Path(tmp_value)
            freeze_dir = freeze(tmp, plan)
            codex_dir = runtime_dir(tmp, "codex", plan)
            claude_dir = runtime_dir(tmp, "claude-code", plan)
            auth_path = claude_dir / "provider-authorization.json"
            auth = json.loads(auth_path.read_text(encoding="utf-8"))
            auth["user_setting_source_loaded"] = True
            write_json(auth_path, auth)
            with self.assertRaisesRegex(
                intake.IntakeError,
                "user setting source must not enter controlled R2 execution",
            ):
                intake.intake(ROOT, freeze_dir, codex_dir, claude_dir, tmp / "bad-intake")

    def test_domain_verification_rejects_manifest_missing_source_identity(self) -> None:
        plan = build_plan()
        with tempfile.TemporaryDirectory() as tmp_value:
            tmp = Path(tmp_value)
            freeze_dir = freeze(tmp, plan)
            codex_dir = runtime_dir(tmp, "codex", plan)
            claude_dir = runtime_dir(tmp, "claude-code", plan)

            with tarfile.open(codex_dir / "result-tree.tar.gz", "r:gz") as tf:
                tree = tmp / "bad-codex"
                tf.extractall(tree)
            manifest = tree / "artifacts/pcr02-ota-v1.1.21.identity.json"
            value = json.loads(manifest.read_text(encoding="utf-8"))
            del value["artifact"]["source_blob_sha"]
            write_json(manifest, value)

            archive = codex_dir / "result-tree.tar.gz"
            with tarfile.open(archive, "w:gz") as tf:
                for path in sorted(x for x in tree.rglob("*") if x.is_file()):
                    tf.add(path, arcname=path.relative_to(tree).as_posix())

            native = json.loads((codex_dir / "codex-native.json").read_text(encoding="utf-8"))
            replay_refs = [
                item
                for item in native["evidence_refs"]
                if item.startswith("replay-postflight:sha256:")
            ]
            native["evidence_refs"] = [
                "worktree-result:sha256:" + tree_digest(tree),
                *replay_refs,
            ]
            write_json(codex_dir / "codex-native.json", native)

            verify_out = tmp / "verification-bad"
            with self.assertRaisesRegex(
                verify.VerificationError,
                "no machine-readable identity JSON binds frozen",
            ):
                verify.verify_local_r2(
                    ROOT,
                    freeze_dir,
                    codex_dir,
                    claude_dir,
                    verify_out,
                    "local-verifier:test",
                )


if __name__ == "__main__":
    unittest.main()
