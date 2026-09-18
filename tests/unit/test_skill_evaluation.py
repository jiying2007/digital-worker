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
EVALUATOR = ROOT / "scripts" / "evaluate_skill_case.py"
MATURITY_EVALUATOR = ROOT / "scripts" / "evaluate_skill_maturity.py"
PLAN_VALIDATOR = ROOT / "scripts" / "validate_skill_evaluation_plan.py"


def canonical_skill(skill_id: str) -> tuple[dict, dict, Path]:
    registry = yaml.safe_load((EDGE / "skills.yaml").read_text(encoding="utf-8"))
    item = next(value for value in registry["skills"] if value["id"] == skill_id)
    path = EDGE / item["path"]
    frontmatter = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
    return item, frontmatter, path


def invocation(status: str = "COMPLETED", runtime_id: str = "skill-eval-harness-v1") -> dict:
    item, fm, contract_path = canonical_skill("boot-chain-analysis")
    outputs = []
    block_reason = None
    if status == "COMPLETED":
        outputs = [{
            "ref": "artifact://boot-analysis",
            "kind": "technical-analysis",
            "sha256": "1" * 64,
        }]
    elif status == "BLOCKED":
        block_reason = "target firmware identity does not match the supplied boot log"
    return {
        "schema_version": 1,
        "invocation_id": f"INV-BOOT-{status}",
        "run_id": "EVAL-RUN-BOOT-001",
        "work_item_id": "EVAL-WI-BOOT-001",
        "source_type": "synthetic",
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
            "provider": "evaluation-harness",
            "runtime_id": runtime_id,
            "version": "1",
            "execution_identity": None,
        },
        "action_level": "A2_GENERATE",
        "inputs": [{"ref": "fixture://boot-materials", "kind": "boot-materials", "sha256": None}],
        "outputs": outputs,
        "result": {"status": status, "summary": "synthetic evaluation fixture", "block_reason": block_reason},
        "started_at": "2026-09-18T00:00:00+00:00",
        "finished_at": "2026-09-18T00:01:00+00:00",
        "attestation": {
            "producer": "evaluation-harness",
            "evidence_ref": "evaluation://boot-fixture",
            "generated_at": "2026-09-18T00:01:01+00:00",
        },
    }


class SkillEvaluationTest(unittest.TestCase):
    def run_case(self, case_id: str, value: dict, *extra: str) -> tuple[subprocess.CompletedProcess, dict | None]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invocation_path = root / "invocation.json"
            output_path = root / "evaluation.json"
            invocation_path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(EVALUATOR),
                    case_id,
                    str(invocation_path),
                    "--output",
                    str(output_path),
                    *extra,
                ],
                capture_output=True,
                text=True,
            )
            receipt = json.loads(output_path.read_text(encoding="utf-8")) if output_path.is_file() else None
            return completed, receipt

    def test_plan_covers_every_skill_positive_and_block(self):
        completed = subprocess.run([sys.executable, str(PLAN_VALIDATOR)], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("23 Skills / 46", completed.stdout)

    def test_contract_pass_without_semantic_evidence_is_not_case_eligible(self):
        completed, receipt = self.run_case("SEC-BOOT-CHAIN-POS", invocation("COMPLETED"))
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt["contract_verdict"]["status"], "PASS")
        self.assertEqual(receipt["semantic_evaluation"]["status"], "NOT_EVALUATED")
        self.assertFalse(receipt["case_evidence_eligible"])

    def test_positive_case_needs_hashed_independent_semantic_evidence(self):
        completed, receipt = self.run_case(
            "SEC-BOOT-CHAIN-POS",
            invocation("COMPLETED"),
            "--semantic-status", "PASS",
            "--semantic-evaluator-kind", "independent-evaluator",
            "--semantic-evaluator-id", "reviewer-fixture",
            "--semantic-evidence-ref", "review://boot-positive",
            "--semantic-evidence-sha256", "2" * 64,
            "--require-case-eligible",
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertTrue(receipt["case_evidence_eligible"])

    def test_block_case_can_be_eligible_only_when_block_is_observed_and_semantically_reviewed(self):
        completed, receipt = self.run_case(
            "SEC-BOOT-CHAIN-BLOCK",
            invocation("BLOCKED"),
            "--semantic-status", "PASS",
            "--semantic-evaluator-kind", "human-review",
            "--semantic-evaluator-id", "human-reviewer-fixture",
            "--semantic-evidence-ref", "review://boot-block",
            "--semantic-evidence-sha256", "3" * 64,
            "--require-case-eligible",
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertEqual(receipt["contract_verdict"]["observed_invocation_status"], "BLOCKED")
        self.assertTrue(receipt["case_evidence_eligible"])

    def test_positive_invocation_does_not_satisfy_block_case(self):
        completed, receipt = self.run_case(
            "SEC-BOOT-CHAIN-BLOCK",
            invocation("COMPLETED"),
            "--semantic-status", "PASS",
            "--semantic-evaluator-kind", "human-review",
            "--semantic-evaluator-id", "human-reviewer-fixture",
            "--semantic-evidence-ref", "review://wrong-status",
            "--semantic-evidence-sha256", "4" * 64,
            "--require-case-eligible",
        )
        self.assertEqual(completed.returncode, 2, completed.stderr or completed.stdout)
        self.assertEqual(receipt["contract_verdict"]["status"], "FAIL")
        self.assertFalse(receipt["case_evidence_eligible"])

    def test_semantic_pass_without_evidence_hash_is_rejected(self):
        completed, receipt = self.run_case(
            "SEC-BOOT-CHAIN-POS",
            invocation("COMPLETED"),
            "--semantic-status", "PASS",
            "--semantic-evaluator-kind", "human-review",
            "--semantic-evaluator-id", "human-reviewer-fixture",
            "--semantic-evidence-ref", "review://missing-hash",
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIsNone(receipt)


    def test_positive_and_block_semantic_evidence_aggregate_to_evaluated_without_portability_or_product_inheritance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pos_inv_path = root / "positive-invocation.json"
            neg_inv_path = root / "block-invocation.json"
            pos_eval_path = root / "positive-evaluation.json"
            neg_eval_path = root / "block-evaluation.json"
            summary_path = root / "summary.json"
            pos_inv_path.write_text(json.dumps(invocation("COMPLETED"), indent=2) + "\n", encoding="utf-8")
            neg_inv_path.write_text(json.dumps(invocation("BLOCKED"), indent=2) + "\n", encoding="utf-8")

            for case_id, inv_path, out_path, digest in [
                ("SEC-BOOT-CHAIN-POS", pos_inv_path, pos_eval_path, "5" * 64),
                ("SEC-BOOT-CHAIN-BLOCK", neg_inv_path, neg_eval_path, "6" * 64),
            ]:
                completed = subprocess.run(
                    [
                        sys.executable, str(EVALUATOR), case_id, str(inv_path),
                        "--semantic-status", "PASS",
                        "--semantic-evaluator-kind", "independent-evaluator",
                        "--semantic-evaluator-id", "semantic-review-fixture",
                        "--semantic-evidence-ref", f"review://{case_id}",
                        "--semantic-evidence-sha256", digest,
                        "--output", str(out_path),
                        "--require-case-eligible",
                    ],
                    capture_output=True, text=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)

            aggregated = subprocess.run(
                [
                    sys.executable, str(MATURITY_EVALUATOR), "boot-chain-analysis",
                    "--positive-evaluation", str(pos_eval_path),
                    "--positive-invocation", str(pos_inv_path),
                    "--block-evaluation", str(neg_eval_path),
                    "--block-invocation", str(neg_inv_path),
                    "--output", str(summary_path),
                    "--require-evaluated",
                ],
                capture_output=True, text=True,
            )
            self.assertEqual(aggregated.returncode, 0, aggregated.stderr or aggregated.stdout)
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "EVALUATED")
            self.assertTrue(summary["evaluation_complete"])
            self.assertFalse(summary["portability_proven"])
            self.assertFalse(summary["product_readiness_inherited"])

    def test_maturity_aggregation_rejects_mixed_runtime_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pos_inv_path = root / "positive-invocation.json"
            neg_inv_path = root / "block-invocation.json"
            pos_eval_path = root / "positive-evaluation.json"
            neg_eval_path = root / "block-evaluation.json"
            summary_path = root / "summary.json"
            pos_inv_path.write_text(json.dumps(invocation("COMPLETED", "runtime-A"), indent=2) + "\n", encoding="utf-8")
            neg_inv_path.write_text(json.dumps(invocation("BLOCKED", "runtime-B"), indent=2) + "\n", encoding="utf-8")

            for case_id, inv_path, out_path, digest in [
                ("SEC-BOOT-CHAIN-POS", pos_inv_path, pos_eval_path, "7" * 64),
                ("SEC-BOOT-CHAIN-BLOCK", neg_inv_path, neg_eval_path, "8" * 64),
            ]:
                completed = subprocess.run(
                    [
                        sys.executable, str(EVALUATOR), case_id, str(inv_path),
                        "--semantic-status", "PASS",
                        "--semantic-evaluator-kind", "human-review",
                        "--semantic-evaluator-id", "reviewer-fixture",
                        "--semantic-evidence-ref", f"review://{case_id}",
                        "--semantic-evidence-sha256", digest,
                        "--output", str(out_path),
                    ],
                    capture_output=True, text=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)

            aggregated = subprocess.run(
                [
                    sys.executable, str(MATURITY_EVALUATOR), "boot-chain-analysis",
                    "--positive-evaluation", str(pos_eval_path),
                    "--positive-invocation", str(pos_inv_path),
                    "--block-evaluation", str(neg_eval_path),
                    "--block-invocation", str(neg_inv_path),
                    "--output", str(summary_path),
                    "--require-evaluated",
                ],
                capture_output=True, text=True,
            )
            self.assertEqual(aggregated.returncode, 2, aggregated.stderr or aggregated.stdout)
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "DEFINED")
            self.assertFalse(summary["checks"]["same_runtime"])
            self.assertIn("positive-and-block-do-not-use-same-runtime-implementation", summary["blockers"])



if __name__ == "__main__":
    unittest.main()
