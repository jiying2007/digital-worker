from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
EDGE = ROOT / "domains" / "edge-foundation"
VALIDATOR = ROOT / "scripts" / "validate_skill_invocation_receipt.py"
PILOT = ROOT / "scripts" / "embedded_pilot.py"
TASK_BRIEF = ROOT / "tests" / "fixtures" / "task-brief.valid.json"


def canonical_skill(skill_id: str) -> tuple[dict, dict, Path]:
    registry = yaml.safe_load((EDGE / "skills.yaml").read_text(encoding="utf-8"))
    item = next(value for value in registry["skills"] if value["id"] == skill_id)
    path = EDGE / item["path"]
    text = path.read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(text.split("---", 2)[1])
    return item, frontmatter, path


def make_receipt(run_id="SKILL-RUN-001", work_item_id="WI-SKILL-001", source_type="synthetic", **overrides):
    item, fm, contract_path = canonical_skill("boot-chain-analysis")
    receipt = {
        "schema_version": 1,
        "invocation_id": "INV-BOOT-001",
        "run_id": run_id,
        "work_item_id": work_item_id,
        "source_type": source_type,
        "skill_id": "boot-chain-analysis",
        "skill_contract": {
            "version": str(fm["version"]),
            "path": item["path"],
            "sha256": hashlib.sha256(contract_path.read_bytes()).hexdigest(),
            "owner_kind": item["owner_kind"],
            "owner": item["owner_id"],
            "max_action_level": fm["max_action_level"],
        },
        "runtime_binding": {
            "provider": "synthetic-test",
            "runtime_id": "runtime-test-1",
            "version": "1",
            "execution_identity": "exec-test-1" if source_type == "real" else None,
        },
        "action_level": "A2_GENERATE",
        "inputs": [{"ref": "evidence://boot-log", "kind": "boot-log", "sha256": None}],
        "outputs": [{"ref": "artifact://technical-analysis", "kind": "technical-analysis", "sha256": "0" * 64}],
        "result": {"status": "COMPLETED", "summary": "synthetic test", "block_reason": None},
        "started_at": "2026-09-18T00:00:00+00:00",
        "finished_at": "2026-09-18T00:01:00+00:00",
        "attestation": {
            "producer": "runtime-binding" if source_type == "real" else "evaluation-harness",
            "evidence_ref": "runtime-evidence://exec-test-1",
            "generated_at": "2026-09-18T00:01:01+00:00",
        },
    }
    for key, value in overrides.items():
        receipt[key] = value
    return receipt


class SkillInvocationReceiptTest(unittest.TestCase):
    def validate(self, receipt: dict, pilot_run: Path | None = None) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            command = [sys.executable, str(VALIDATOR), str(path)]
            if pilot_run is not None:
                command.extend(["--pilot-run", str(pilot_run)])
            return subprocess.run(command, capture_output=True, text=True)

    def test_valid_synthetic_receipt_passes(self):
        completed = self.validate(make_receipt())
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)

    def test_contract_hash_drift_fails(self):
        receipt = make_receipt()
        receipt["skill_contract"]["sha256"] = "f" * 64
        completed = self.validate(receipt)
        self.assertNotEqual(completed.returncode, 0)

    def test_action_above_skill_ceiling_fails(self):
        receipt = make_receipt()
        receipt["action_level"] = "A3_MODIFY_WORKTREE"
        completed = self.validate(receipt)
        self.assertNotEqual(completed.returncode, 0)

    def test_real_receipt_requires_runtime_attestation(self):
        receipt = make_receipt(source_type="real")
        receipt["attestation"]["producer"] = "evaluation-harness"
        completed = self.validate(receipt)
        self.assertNotEqual(completed.returncode, 0)

    def test_blocked_receipt_requires_reason(self):
        receipt = make_receipt()
        receipt["outputs"] = []
        receipt["result"] = {"status": "BLOCKED", "summary": "blocked", "block_reason": None}
        completed = self.validate(receipt)
        self.assertNotEqual(completed.returncode, 0)

    def test_complete_freezes_skill_receipt_into_evidence_bundle(self):
        fixtures = ROOT / "tests" / "fixtures"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "CI-PILOT-001"
            init = subprocess.run(
                [
                    sys.executable, str(PILOT), "init",
                    "--run-id", "CI-PILOT-001",
                    "--track", "feature",
                    "--source-type", "synthetic",
                    "--task-type", "feature_development",
                    "--workflow-mode", "short_chain",
                    "--human-owner", "ci",
                    "--task-brief", str(TASK_BRIEF),
                    "--repo-root", "firmware/main",
                    "--base-commit", "0123456789abcdef0123456789abcdef01234567",
                    "--output-root", str(root),
                ],
                capture_output=True, text=True,
            )
            self.assertEqual(init.returncode, 0, init.stderr or init.stdout)
            pilot_run = json.loads((run_dir / "pilot-run.json").read_text(encoding="utf-8"))
            receipt = make_receipt(
                run_id=pilot_run["run_id"],
                work_item_id=pilot_run["work_item_id"],
                source_type=pilot_run["source_type"],
            )
            receipt_source = root / "skill-receipt.json"
            receipt_source.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            complete = subprocess.run(
                [
                    sys.executable, str(PILOT), "complete", str(run_dir),
                    "--engineering-task-package", str(fixtures / "engineering-task-package.valid.json"),
                    "--delivery-receipt", str(fixtures / "delivery-receipt.valid.json"),
                    "--verification-report", str(fixtures / "verification-report.valid.json"),
                    "--pilot-result", str(fixtures / "pilot-result.feature.valid.json"),
                    "--skill-invocation", str(receipt_source),
                    "--extra", f"material_manifest={fixtures / 'material-manifest.valid.json'}",
                    "--extra", f"acceptance_evidence_matrix={fixtures / 'acceptance-evidence-matrix.valid.md'}",
                    "--extra", f"knowledge_harvest={fixtures / 'knowledge-harvest.valid.md'}",
                ],
                capture_output=True, text=True,
            )
            self.assertEqual(complete.returncode, 0, complete.stderr or complete.stdout)
            completed_run = json.loads((run_dir / "pilot-run.json").read_text(encoding="utf-8"))
            self.assertEqual(completed_run["status"], "completed")
            self.assertEqual(len(completed_run["skill_invocation_refs"]), 1)
            skill_ref = completed_run["skill_invocation_refs"][0]
            self.assertTrue((run_dir / skill_ref).is_file())
            bundle = json.loads((run_dir / "evidence-bundle.json").read_text(encoding="utf-8"))
            matching = [item for item in bundle["artifacts"] if item["path"] == skill_ref]
            self.assertEqual(len(matching), 1)
            self.assertEqual(matching[0]["kind"], "skill_invocation:boot-chain-analysis")
            self.assertEqual(matching[0]["sha256"], hashlib.sha256((run_dir / skill_ref).read_bytes()).hexdigest())

    def test_pilot_run_validates_attached_skill_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init = subprocess.run(
                [
                    sys.executable, str(PILOT), "init",
                    "--run-id", "CI-SKILL-INV-001",
                    "--track", "feature",
                    "--source-type", "synthetic",
                    "--task-type", "feature_development",
                    "--workflow-mode", "short_chain",
                    "--human-owner", "ci",
                    "--task-brief", str(TASK_BRIEF),
                    "--repo-root", "firmware/main",
                    "--base-commit", "0123456789abcdef0123456789abcdef01234567",
                    "--output-root", str(root),
                ],
                capture_output=True, text=True,
            )
            self.assertEqual(init.returncode, 0, init.stderr or init.stdout)
            run_dir = root / "CI-SKILL-INV-001"
            pilot_run = json.loads((run_dir / "pilot-run.json").read_text(encoding="utf-8"))
            receipt = make_receipt(
                run_id=pilot_run["run_id"],
                work_item_id=pilot_run["work_item_id"],
                source_type=pilot_run["source_type"],
            )
            skill_dir = run_dir / "skill-invocations"
            skill_dir.mkdir()
            receipt_path = skill_dir / "01-boot-chain-analysis.json"
            receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            pilot_run["skill_invocation_refs"] = ["skill-invocations/01-boot-chain-analysis.json"]
            (run_dir / "pilot-run.json").write_text(json.dumps(pilot_run, indent=2) + "\n", encoding="utf-8")

            completed = subprocess.run(
                [sys.executable, str(PILOT), "validate", str(run_dir)],
                capture_output=True, text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)

            receipt["skill_contract"]["sha256"] = "e" * 64
            receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            rejected = subprocess.run(
                [sys.executable, str(PILOT), "validate", str(run_dir)],
                capture_output=True, text=True,
            )
            self.assertNotEqual(rejected.returncode, 0)


if __name__ == "__main__":
    unittest.main()
