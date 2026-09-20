from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "runtime_r2_evidence.py"
BASE = "eeb926bd1fff75d2a5d5abb9f0ede9c8f582cc6d"
DW = "a" * 40
CODEX_COMMIT = "79acb193cef381b4c8b72f00e0af15f87e32765c"
CLAUDE_COMMIT = "fba4551aa4a2abe5f74cff3c60e8318961b36add"
ADK_VERSION = "7.0.4"
ADK_COMMIT = "1d6c28e89eb98a4af5ac978707730783f0c84437"
ADK_ARTIFACT_SHA256 = "497e44ec83d2506c8721019aeca979965127b481203f33387806c51c0d1aff68"

spec = importlib.util.spec_from_file_location("runtime_r2_evidence", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def canonical_digest(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def build_plan() -> dict:
    return module.build_plan(ROOT, digital_worker_commit=DW, target_head=BASE, target_clean=True)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def codex_native(plan: dict) -> dict:
    controlled = plan["controlled_task"]
    return {
        "schema_version": 2,
        "work_item_id": controlled["work_item_id"],
        "run_id": controlled["run_id"],
        "execution_source_set_identity": "sha256:" + "1" * 64,
        "digital_worker_governance_identity": "2" * 64,
        "runtime_binding": {
            "repository": "jiying2007/codex",
            "commit": CODEX_COMMIT,
            "target": "codex-cli",
            "runtime_profile": "default",
            "runtime_host": "github-hosted",
            "source_set_identity_ref": "sha256:" + "3" * 64,
            "runtime_distribution_identity_ref": "sha256:" + "4" * 64,
        },
        "agent_assets": {
            "provider_repository": plan["adk_release_identity"]["repository"],
            "release_version": plan["adk_release_identity"]["version"],
            "release_tag": plan["adk_release_identity"]["tag"],
            "release_commit": plan["adk_release_identity"]["commit"],
            "asset_profile": "embedded-fullstack",
            "source_set_identity": "exact-release-source-blobs",
        },
        "runtime": {
            "provider": "openai",
            "cli_version": "codex-cli-test",
            "model": "test-model",
        },
        "permissions": {"sandbox": "workspace-write", "approval": "never"},
        "repository": {
            "repository": "jiying2007/ota_download_test",
            "base_commit": controlled["exact_base_commit"],
            "result_commit": None,
        },
        "execution": {"status": "completed", "runtime_local_gates": ["host"]},
        "evidence_refs": ["provider-run:test"],
    }


def claude_native(plan: dict) -> dict:
    return {
        "schema_version": 2,
        "status": "completed",
        "runtime": "claude-code",
        "frozen_inputs_sha256": plan["frozen_inputs_sha256"],
        "verification_pass_claimed": False,
        "runtime_identity": {
            "runtime_binding_repository": "jiying2007/claude",
            "runtime_binding_commit": CLAUDE_COMMIT,
            "runtime_target": "claude-code",
            "runtime_profile": "solo-dev",
            "runtime_host": "github-hosted",
            "runtime_provider": "anthropic",
            "runtime_version": "claude-code-test",
            "runtime_source_set_identity_ref": "sha256:" + "5" * 64,
            "runtime_distribution_identity_ref": "sha256:" + "6" * 64,
        },
        "execution": {
            "started_at": "2026-09-17T00:00:00Z",
            "completed_at": "2026-09-17T00:01:00Z",
            "result_identity_ref": "sha256:" + "7" * 64,
            "source_identity_ref": None,
            "exit_code": 0,
            "summary": "test",
        },
        "evidence_refs": ["provider-run:test"],
    }


class RuntimeR2EvidenceTests(unittest.TestCase):
    def test_build_plan_freezes_real_feature_pilot_without_authorizing_provider_run(self) -> None:
        plan = build_plan()
        self.assertEqual(plan["schema"], "digital-worker-runtime-r2-plan/v1")
        self.assertEqual(plan["status"], "ready-for-manual-provider-execution")
        self.assertFalse(plan["provider_execution_authorized"])
        self.assertFalse(plan["automatic_execution_enabled"])
        controlled = plan["controlled_task"]
        self.assertEqual(controlled["work_item_id"], "PCR02-OTA-ARTIFACT-IDENTITY-V1.1.21")
        self.assertEqual(controlled["run_id"], "R2-FEATURE-PCR02-OTA-001")
        self.assertEqual(controlled["exact_base_commit"], BASE)
        self.assertIs(controlled["dirty_baseline"], False)
        self.assertEqual(controlled["workflow_mode"], "short_chain")
        self.assertTrue(controlled["digital_worker_governance_identity_ref"].startswith("sha256:"))
        self.assertTrue(controlled["knowledge_context_fingerprint"].startswith("sha256:"))
        self.assertTrue(controlled["runtime_source_set_identity_ref"].startswith("sha256:"))
        self.assertEqual(plan["frozen_inputs_sha256"], canonical_digest(controlled))
        self.assertEqual(controlled["adk_release_identity_ref"], "manifests/r2_frozen_adk_release.lock.json")
        self.assertEqual(plan["adk_release_identity"]["commit"], ADK_COMMIT)
        self.assertEqual(plan["adk_release_identity"]["version"], ADK_VERSION)
        self.assertEqual(plan["adk_release_identity"]["artifact_sha256"], ADK_ARTIFACT_SHA256)
        self.assertEqual(plan["runtime_bindings"]["codex"]["commit"], CODEX_COMMIT)
        self.assertEqual(plan["runtime_bindings"]["claude-code"]["commit"], CLAUDE_COMMIT)
        generic = json.loads((ROOT / "config/integrations/cross-repo-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(generic["providers"]["agent_asset_control_plane"]["release_baseline"]["version"], "5.1.1")
        self.assertNotEqual(
            generic["providers"]["agent_asset_control_plane"]["release_baseline"]["commit"],
            plan["adk_release_identity"]["commit"],
        )

    def test_build_plan_rejects_wrong_or_dirty_target_baseline(self) -> None:
        with self.assertRaisesRegex(module.R2EvidenceError, "target checkout HEAD mismatch"):
            module.build_plan(ROOT, digital_worker_commit=DW, target_head="0" * 40, target_clean=True)
        with self.assertRaisesRegex(module.R2EvidenceError, "clean exact-base"):
            module.build_plan(ROOT, digital_worker_commit=DW, target_head=BASE, target_clean=False)

    def test_codex_native_receipt_projects_to_portable_receipt_bound_to_native_sha(self) -> None:
        plan = build_plan()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            plan_path = tmp / "plan.json"
            native_path = tmp / "codex-native.json"
            write_json(plan_path, plan)
            write_json(native_path, codex_native(plan))
            result = module.project_receipt(ROOT, runtime="codex", native_receipt=native_path, frozen_plan=plan_path)
            self.assertEqual(result["runtime"], "codex")
            self.assertEqual(result["frozen_inputs_sha256"], plan["frozen_inputs_sha256"])
            self.assertFalse(result["verification_pass_claimed"])
            identity = result["runtime_identity"]
            self.assertEqual(identity["runtime_binding_repository"], "https://github.com/jiying2007/codex.git")
            self.assertEqual(identity["runtime_binding_commit"], CODEX_COMMIT)
            self.assertEqual(identity["runtime_target"], "codex-cli")
            self.assertEqual(result["native_receipt"]["sha256"], hashlib.sha256(native_path.read_bytes()).hexdigest())

    def test_codex_projection_rejects_frozen_work_run_or_base_drift(self) -> None:
        plan = build_plan()
        for field, bad in (("work_item_id", "other"), ("run_id", "other")):
            native = codex_native(plan)
            native[field] = bad
            with tempfile.TemporaryDirectory() as tmp:
                tmp = Path(tmp)
                plan_path = tmp / "plan.json"
                native_path = tmp / "native.json"
                write_json(plan_path, plan)
                write_json(native_path, native)
                with self.assertRaises(module.R2EvidenceError):
                    module.project_receipt(ROOT, runtime="codex", native_receipt=native_path, frozen_plan=plan_path)
        native = codex_native(plan)
        native["repository"]["base_commit"] = "0" * 40
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            plan_path = tmp / "plan.json"
            native_path = tmp / "native.json"
            write_json(plan_path, plan)
            write_json(native_path, native)
            with self.assertRaisesRegex(module.R2EvidenceError, "base commit"):
                module.project_receipt(ROOT, runtime="codex", native_receipt=native_path, frozen_plan=plan_path)

    def test_claude_native_receipt_projects_canonical_repository_identity(self) -> None:
        plan = build_plan()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            plan_path = tmp / "plan.json"
            native_path = tmp / "claude-native.json"
            write_json(plan_path, plan)
            write_json(native_path, claude_native(plan))
            result = module.project_receipt(ROOT, runtime="claude-code", native_receipt=native_path, frozen_plan=plan_path)
            self.assertEqual(result["runtime_identity"]["runtime_binding_repository"], "https://github.com/jiying2007/claude.git")
            self.assertEqual(result["runtime_identity"]["runtime_binding_commit"], CLAUDE_COMMIT)
            self.assertEqual(result["frozen_inputs_sha256"], plan["frozen_inputs_sha256"])

    def test_forbidden_runtime_decision_claim_fails_closed(self) -> None:
        plan = build_plan()
        native = claude_native(plan)
        native["verification_status"] = "pass"
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            plan_path = tmp / "plan.json"
            native_path = tmp / "native.json"
            write_json(plan_path, plan)
            write_json(native_path, native)
            with self.assertRaisesRegex(module.R2EvidenceError, "forbidden"):
                module.project_receipt(ROOT, runtime="claude-code", native_receipt=native_path, frozen_plan=plan_path)


if __name__ == "__main__":
    unittest.main()
