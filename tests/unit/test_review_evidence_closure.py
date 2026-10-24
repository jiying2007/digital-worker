"""Behavioral closure for Pilot independence, semantic evidence and safe summary."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(Path(__file__).parent)]
import embedded_pilot as pilot
import evaluate_skill_case as case
import evaluate_skill_maturity as maturity
import test_review_hardening as fixtures
import test_skill_evaluation as skill


class PilotIndependenceTests(unittest.TestCase):
    def test_conflicting_or_unknown_identities_cannot_publish_completion(self):
        for field, principal in (("verification_report_ref", "verifier"), ("review_report_ref", "reviewer")):
            for mutation in ("self", "spaced-self", "actor-self", "owner-missing", "owner-null", "owner-blank", "principal-blank"):
                with self.subTest(field=field, mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                    root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
                    run = pilot.load_run(root)
                    if field == "review_report_ref":
                        run[field] = "review.json"
                        fixtures.write(root / run[field], fixtures.load(ROOT / "tests/fixtures/review-report.valid.json"))
                        fixtures.write(root / "pilot-run.json", run)
                    doc = fixtures.load(root / run[field])
                    if mutation in {"self", "spaced-self"}:
                        doc[principal] = doc["implementation_owner"] + (" " if mutation == "spaced-self" else "")
                    elif mutation == "actor-self":
                        doc["decision_actor_identity_ref"] = " " + doc["implementation_owner"] + " "
                    elif mutation == "owner-missing":
                        doc.pop("implementation_owner")
                    elif mutation == "owner-null":
                        doc["implementation_owner"] = None
                    elif mutation == "owner-blank":
                        doc["implementation_owner"] = "  "
                    else:
                        doc[principal] = "  "
                    fixtures.write(root / run[field], doc)
                    before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
                    with self.assertRaises(ValueError):
                        pilot.cmd_complete(pilot.build_parser().parse_args(["complete", str(root)]))
                    after = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
                    self.assertEqual(before, after)
                    self.assertEqual(pilot.load_run(root)["status"], "running")

    def test_old_report_can_be_inspected_but_not_requalified_without_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            path = root / "verification_report.json"
            value = fixtures.load(path)
            value.pop("implementation_owner")
            fixtures.write(path, value)
            pilot.validate_run_dir(root)  # Nonterminal inspection remains possible.
            run = pilot.load_run(root)
            run.update(status="completed", evidence_bundle_ref="evidence-bundle.json")
            fixtures.write(root / run["evidence_bundle_ref"], pilot.collect_bundle(root, run))
            fixtures.write(root / "pilot-run.json", run)
            with self.assertRaisesRegex(ValueError, "implementation_owner"):
                fixtures.receipt_tool.build_receipt(root / "pilot-run.json", root / "pilot_result.json", None)

    def test_independent_verification_and_review_remain_eligible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            run = pilot.load_run(root)
            run["review_report_ref"] = "review.json"
            fixtures.write(root / "review.json", fixtures.load(ROOT / "tests/fixtures/review-report.valid.json"))
            fixtures.write(root / "pilot-run.json", run)
            pilot.cmd_complete(pilot.build_parser().parse_args(["complete", str(root)]))
            run = pilot.load_run(root)
            receipt = fixtures.receipt_tool.build_receipt(root / "pilot-run.json", root / run["pilot_result_ref"], None)
            self.assertTrue(receipt["product_readiness_eligible"])


def evaluated_pair(root):
    paths, evidence_paths = [], []
    for name, status, case_id in (("positive", "COMPLETED", "SEC-BOOT-CHAIN-POS"),
                                 ("block", "BLOCKED", "SEC-BOOT-CHAIN-BLOCK")):
        invocation = root / (name + "-inv.json")
        evaluation = root / (name + "-eval.json")
        fixtures.write(invocation, skill.invocation(status))
        evidence, digest = skill.semantic_evidence(root / (name + "-semantic.json"), invocation, case_id)
        value = case.evaluate(case_id, invocation, "PASS", "independent-evaluator",
                              "semantic-review-fixture", str(evidence), digest, None)
        fixtures.write(evaluation, value)
        paths.extend([evaluation, invocation])
        evidence_paths.append(evidence)
    return paths, evidence_paths


class SemanticEvidenceTests(unittest.TestCase):
    def test_original_missing_evidence_and_uri_claims_are_rejected(self):
        for ref in ("missing.json", "https://does-not-exist.invalid/review", "review://claimed-pass"):
            with self.subTest(ref=ref), tempfile.TemporaryDirectory() as tmp:
                invocation = Path(tmp) / "inv.json"
                fixtures.write(invocation, skill.invocation())
                with self.assertRaises(AssertionError):
                    case.evaluate("SEC-BOOT-CHAIN-POS", invocation, "PASS", "independent-evaluator",
                                  "reviewer", ref, "0" * 64, None)

    def test_case_checks_materialized_bytes_and_all_subject_bindings(self):
        for mutation in ("digest", "malformed", "case", "skill", "plan", "invocation", "actor", "kind", "status", "independence", "blank-summary", "no-refs"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                invocation = root / "inv.json"
                fixtures.write(invocation, skill.invocation())
                evidence, digest = skill.semantic_evidence(root / "semantic.json", invocation, "SEC-BOOT-CHAIN-POS")
                value = fixtures.load(evidence)
                fields = {"case": ("case_id", "OTHER"), "skill": ("skill_id", "other-skill"),
                          "plan": ("evaluation_plan_sha256", "0" * 64),
                          "invocation": ("invocation_receipt_sha256", "0" * 64),
                          "actor": ("evaluator_id", "other-reviewer"), "kind": ("evaluator_kind", "human-review"),
                          "status": ("status", "FAIL"), "independence": ("independence_confirmed", False),
                          "blank-summary": ("summary", "  "), "no-refs": ("evidence_refs", [])}
                if mutation in fields:
                    key, item = fields[mutation]
                    value[key] = item
                    fixtures.write(evidence, value)
                    digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
                elif mutation == "malformed":
                    evidence.write_text("not-json")
                    digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
                else:
                    digest = "0" * 64
                with self.assertRaises(Exception):
                    case.evaluate("SEC-BOOT-CHAIN-POS", invocation, "PASS", "independent-evaluator",
                                  "semantic-review-fixture", str(evidence), digest, None)

    def test_evaluator_cannot_equal_runtime_or_execution_actor_even_with_spaces(self):
        for identity_field in ("runtime_id", "execution_identity"):
            with self.subTest(identity_field=identity_field), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                invocation = root / "inv.json"
                value = skill.invocation()
                value["runtime_binding"][identity_field] = "same-actor"
                fixtures.write(invocation, value)
                evidence, digest = skill.semantic_evidence(root / "semantic.json", invocation,
                                                          "SEC-BOOT-CHAIN-POS", evaluator_id=" same-actor ")
                with self.assertRaisesRegex(AssertionError, "cannot equal"):
                    case.evaluate("SEC-BOOT-CHAIN-POS", invocation, "PASS", "independent-evaluator",
                                  " same-actor ", str(evidence), digest, None)

    def test_aggregation_rereads_evidence_and_rejects_tamper_or_forged_binding(self):
        for mutation in ("delete", "bytes", "invocation", "actor", "status", "uri"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                paths, evidence_paths = evaluated_pair(root)
                self.assertEqual(maturity.build_summary("boot-chain-analysis", *paths)["status"], "EVALUATED")
                evidence = evidence_paths[0]
                evaluation = fixtures.load(paths[0])
                if mutation == "delete":
                    evidence.unlink()
                elif mutation == "bytes":
                    evidence.write_text("tampered")
                elif mutation == "uri":
                    evaluation["semantic_evaluation"]["evidence_ref"] = "review://forged"
                else:
                    value = fixtures.load(evidence)
                    if mutation == "invocation":
                        value["invocation_receipt_sha256"] = "0" * 64
                    elif mutation == "actor":
                        value["evaluator_id"] = "skill-eval-harness-v1"
                        evaluation["semantic_evaluation"]["evaluator_id"] = value["evaluator_id"]
                    else:
                        value["status"] = "FAIL"
                    fixtures.write(evidence, value)
                    evaluation["semantic_evaluation"]["evidence_sha256"] = hashlib.sha256(evidence.read_bytes()).hexdigest()
                fixtures.write(paths[0], evaluation)
                summary = maturity.build_summary("boot-chain-analysis", *paths)
                self.assertEqual(summary["status"], "DEFINED")
                self.assertFalse(summary["checks"]["case_evidence_eligible"])

    def test_local_relative_path_works_from_external_cwd_and_fail_verdict_does_not_qualify(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invocation = root / "inv.json"
            fixtures.write(invocation, skill.invocation())
            evidence, digest = skill.semantic_evidence(root / "semantic.json", invocation,
                                                      "SEC-BOOT-CHAIN-POS", status="FAIL")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/evaluate_skill_case.py"),
                                     "SEC-BOOT-CHAIN-POS", str(invocation), "--semantic-status", "FAIL",
                                     "--semantic-evaluator-kind", "independent-evaluator",
                                     "--semantic-evaluator-id", "semantic-review-fixture",
                                     "--semantic-evidence-ref", evidence.name, "--semantic-evidence-sha256", digest,
                                     "--output", str(root / "eval.json"), "--require-case-eligible"],
                                    cwd="/tmp", capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertFalse(fixtures.load(root / "eval.json")["case_evidence_eligible"])


class SummaryDisclosureTests(unittest.TestCase):
    def test_json_text_and_output_file_never_dump_private_input(self):
        for mode in ("json", "text", "output"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
                value = pilot.load_run(root)
                private = "summary-private-marker"
                value["notes"] = private * 10000 + " https://user:secret@example.invalid/x?token=secret#private"
                fixtures.write(root / "pilot-run.json", value)
                command = [sys.executable, str(ROOT / "scripts/edge_pilot.py"), "summary", tmp]
                if mode != "text":
                    command.append("--json")
                output = Path(tmp) / "summary.json"
                if mode == "output":
                    command.extend(["--output", str(output)])
                completed = subprocess.run(command, cwd="/tmp", capture_output=True, text=True)
                self.assertEqual(completed.returncode, 2, completed.stderr)
                rendered = completed.stdout + completed.stderr
                if output.exists():
                    rendered += output.read_text(encoding="utf-8")
                self.assertNotIn(private, rendered)
                self.assertNotIn("secret", rendered)
                self.assertNotIn("Failed validating", rendered)
                self.assertLess(len(rendered), 6000)
                summary = json.loads(completed.stdout)
                self.assertEqual(len(summary["invalid_runs"]), 1)
                self.assertIn("VALIDATION_FAILED", summary["invalid_runs"][0])
                self.assertIn("notes", summary["invalid_runs"][0])

    def test_ordinary_validator_uses_same_safe_error_surface(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            value = pilot.load_run(root)
            value["notes"] = "private-validation-marker"
            fixtures.write(root / "pilot-run.json", value)
            result = subprocess.run([sys.executable, str(ROOT / "scripts/edge_pilot.py"), "validate", str(root), "--json"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("private-validation-marker", result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["field_path"], ["notes"])


if __name__ == "__main__":
    unittest.main()
