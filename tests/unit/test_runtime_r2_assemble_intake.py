from __future__ import annotations

import hashlib
import importlib.util
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSEMBLER = ROOT / "scripts/runtime_r2_assemble_intake.py"
EVIDENCE = ROOT / "scripts/runtime_r2_evidence.py"
BASE = "eeb926bd1fff75d2a5d5abb9f0ede9c8f582cc6d"
DW = "a" * 40


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


module = load_module("runtime_r2_assemble_intake", ASSEMBLER)
evidence = load_module("runtime_r2_evidence_for_assemble", EVIDENCE)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plan() -> dict:
    return evidence.build_plan(ROOT, digital_worker_commit=DW, target_head=BASE, target_clean=True)


def freeze_dir(root: Path, p: dict) -> Path:
    out = root / "freeze"
    out.mkdir()
    write_json(out / "frozen-plan.json", p)
    write_json(
        out / "campaign.json",
        {
            "schema": "digital-worker-runtime-r2-campaign/v1",
            "campaign_id": p["controlled_task"]["run_id"],
            "status": "frozen-awaiting-independent-runtime-executions",
            "digital_worker_commit": DW,
            "freeze_workflow_run_id": "12345",
            "frozen_inputs_sha256": p["frozen_inputs_sha256"],
            "target_repository": "jiying2007/ota_download_test",
            "target_base_commit": BASE,
            "runtime_bindings": p["runtime_bindings"],
            "runtime_execution_workflows": {
                "codex": "jiying2007/codex/.github/workflows/runtime-r2-provider-execution.yml",
                "claude-code": "jiying2007/claude/.github/workflows/runtime-r2-provider-execution.yml",
            },
            "provider_credentials_held_by_digital_worker": False,
            "provider_execution_authorized": False,
            "verification_status": "pending",
            "independent_review_status": "pending",
        },
    )
    return out


def subject(root: Path, runtime: str, p: dict, *, repository: str | None = None, plan_override: dict | None = None) -> tuple[Path, Path]:
    bundle = root / (runtime + "-bundle")
    bundle.mkdir()
    selected_plan = plan_override or p
    write_json(bundle / "frozen-plan.json", selected_plan)
    expected_repo = "jiying2007/codex" if runtime == "codex" else "jiying2007/claude"
    write_json(
        bundle / "bundle-manifest.json",
        {
            "schema": runtime + "-r2-evidence-bundle/v1",
            "runtime": runtime,
            "status": "provider-execution-completed-pending-digital-worker-verification",
            "workflow_repository": repository or expected_repo,
            "workflow_sha": ("1" if runtime == "codex" else "2") * 40,
            "workflow_run_id": "9001" if runtime == "codex" else "9002",
            "verification_pass_claimed": False,
            "r2_qualified": False,
            "files": [],
        },
    )
    archive = root / (runtime + "-evidence.tar.gz")
    with tarfile.open(archive, "w:gz") as tf:
        tf.add(bundle / "frozen-plan.json", arcname="./frozen-plan.json")
        tf.add(bundle / "bundle-manifest.json", arcname="./bundle-manifest.json")
    attestation = root / (runtime + "-attestation.json")
    write_json(attestation, {"mediaType": "application/vnd.dev.sigstore.bundle+json;version=0.3", "test": True})
    return archive, attestation


class RuntimeR2AssembleIntakeTests(unittest.TestCase):
    def test_assembles_tracked_intake_campaign_without_manual_identity_copying(self) -> None:
        p = plan()
        with tempfile.TemporaryDirectory() as tmp_value:
            tmp = Path(tmp_value)
            freeze = freeze_dir(tmp, p)
            codex_subject, codex_attestation = subject(tmp, "codex", p)
            claude_subject, claude_attestation = subject(tmp, "claude-code", p)
            fake_root = tmp / "repo"
            out = fake_root / "reports/runtime-r2/intake/R2-FEATURE-PCR02-OTA-001"
            result = module.assemble(
                fake_root,
                freeze,
                codex_subject,
                codex_attestation,
                claude_subject,
                claude_attestation,
                out,
            )
            self.assertEqual(result["schema"], "digital-worker-runtime-r2-intake/v1")
            self.assertEqual(result["campaign_id"], "R2-FEATURE-PCR02-OTA-001")
            self.assertEqual(result["frozen_inputs_sha256"], p["frozen_inputs_sha256"])
            self.assertFalse(result["r2_qualified"])
            self.assertEqual(result["runtime_evidence"]["codex"]["workflow_run_id"], "9001")
            self.assertEqual(result["runtime_evidence"]["claude-code"]["workflow_run_id"], "9002")
            self.assertEqual(result["runtime_evidence"]["codex"]["subject_sha256"], sha(out / "codex-evidence.tar.gz"))
            self.assertEqual(result["runtime_evidence"]["claude-code"]["attestation_sha256"], sha(out / "claude-code-attestation.json"))
            self.assertEqual((out / "frozen-plan.json").read_bytes(), (freeze / "frozen-plan.json").read_bytes())

    def test_rejects_subject_with_different_frozen_plan(self) -> None:
        p = plan()
        bad = json.loads(json.dumps(p))
        bad["controlled_task"]["workflow_mode"] = "tampered"
        with tempfile.TemporaryDirectory() as tmp_value:
            tmp = Path(tmp_value)
            freeze = freeze_dir(tmp, p)
            codex_subject, codex_attestation = subject(tmp, "codex", p, plan_override=bad)
            claude_subject, claude_attestation = subject(tmp, "claude-code", p)
            out = tmp / "repo/reports/runtime-r2/intake/campaign"
            with self.assertRaisesRegex(module.AssembleError, "not byte-identical"):
                module.assemble(tmp / "repo", freeze, codex_subject, codex_attestation, claude_subject, claude_attestation, out)

    def test_rejects_runtime_owned_subject_from_wrong_repository(self) -> None:
        p = plan()
        with tempfile.TemporaryDirectory() as tmp_value:
            tmp = Path(tmp_value)
            freeze = freeze_dir(tmp, p)
            codex_subject, codex_attestation = subject(tmp, "codex", p, repository="other/repo")
            claude_subject, claude_attestation = subject(tmp, "claude-code", p)
            out = tmp / "repo/reports/runtime-r2/intake/campaign"
            with self.assertRaisesRegex(module.AssembleError, "workflow repository mismatch"):
                module.assemble(tmp / "repo", freeze, codex_subject, codex_attestation, claude_subject, claude_attestation, out)

    def test_rejects_output_outside_tracked_intake_root(self) -> None:
        p = plan()
        with tempfile.TemporaryDirectory() as tmp_value:
            tmp = Path(tmp_value)
            freeze = freeze_dir(tmp, p)
            codex_subject, codex_attestation = subject(tmp, "codex", p)
            claude_subject, claude_attestation = subject(tmp, "claude-code", p)
            with self.assertRaisesRegex(module.AssembleError, "reports/runtime-r2/intake"):
                module.assemble(
                    tmp / "repo",
                    freeze,
                    codex_subject,
                    codex_attestation,
                    claude_subject,
                    claude_attestation,
                    tmp / "outside",
                )


if __name__ == "__main__":
    unittest.main()
