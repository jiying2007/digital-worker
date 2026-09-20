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
    return evidence.build_plan(ROOT, digital_worker_commit=current_head(), target_head=BASE, target_clean=True)


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
    (tree / "tests").mkdir(parents=True)
    (tree / "tests/test_smoke.py").write_text(
        "import unittest\n\nclass Smoke(unittest.TestCase):\n    def test_ok(self): self.assertTrue(True)\n",
        encoding="utf-8",
    )
    (tree / "verify_ota_manifest.py").write_text(
        "import argparse\np=argparse.ArgumentParser(); p.add_argument('--manifest'); p.parse_args()\n",
        encoding="utf-8",
    )
    write_json(tree / "ota-manifest.v1.json", {"runtime": runtime})
    digest = tree_digest(tree)
    archive = root / f"{runtime}-result-tree.tar.gz"
    with tarfile.open(archive, "w:gz") as tf:
        for path in sorted(x for x in tree.rglob("*") if x.is_file()):
            tf.add(path, arcname=path.relative_to(tree).as_posix())
    return archive, digest


def codex_native(plan: dict, digest: str) -> dict:
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
        "evidence_refs": ["worktree-result:sha256:" + digest],
    }


def claude_native(plan: dict, digest: str) -> dict:
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
        "evidence_refs": ["worktree-result:sha256:" + digest],
    }


def runtime_dir(root: Path, runtime: str, plan: dict) -> Path:
    out = root / runtime
    out.mkdir()
    archive, digest = result_tree(root, runtime)
    target_archive = out / "result-tree.tar.gz"
    target_archive.write_bytes(archive.read_bytes())
    write_json(
        out / "provider-authorization.json",
        {
            "schema": f"{runtime}-r2-provider-authorization/v1",
            "authorized": True,
            "authorization_mode": "explicit-local-operator-execution",
            "actor": f"local-test-{runtime}",
            "runtime_host": "local-terminal",
            "frozen_inputs_sha256": plan["frozen_inputs_sha256"],
            "verification_or_release_authority": False,
            "github_provider_credential_used": False,
        },
    )
    if runtime == "codex":
        write_json(out / "codex-native.json", codex_native(plan, digest))
        (out / "codex-events.jsonl").write_text("{}\n", encoding="utf-8")
        (out / "codex-final.txt").write_text("done\n", encoding="utf-8")
    else:
        write_json(out / "claude-native-validated.json", claude_native(plan, digest))
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
            self.assertFalse(collection["github_provider_credentials_required"])
            self.assertEqual(set(collection["execution_receipts"]), {"codex", "claude-code"})
            self.assertEqual(
                collection["provider_execution_evidence"]["codex"]["runtime_binding_commit"],
                plan["runtime_bindings"]["codex"]["commit"],
            )

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
            self.assertFalse(report["github_provider_credentials_required"])
            self.assertFalse(report["verification_pass_claimed_by_runtime"])
            self.assertEqual(report["independent_review_status"], "pending")
            self.assertEqual(set(report["provider_execution_evidence"]), {"codex", "claude-code"})


if __name__ == "__main__":
    unittest.main()
