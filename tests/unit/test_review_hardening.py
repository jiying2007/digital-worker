"""Regression tests for the eight whole-repository review findings."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
import embedded_pilot as pilot
import evaluate_edge_foundation_pilot as receipt_tool
import evaluate_edge_foundation_product_readiness as readiness
import evaluate_skill_case as case_tool
import evaluate_skill_maturity as maturity
import verify_repository_governance as governance


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def fixture_run(root, *, completed=True):
    """Build a fully bound test Run; no retained real evidence is edited."""
    fixtures = ROOT / "tests/fixtures"
    root.mkdir()
    run = load(fixtures / "pilot-run.valid.json")
    run.update(run_id="CI-PILOT-001", work_item_id="EMB-001", source_type="real",
               pilot_track="feature", task_type="feature_development", workflow_mode="short_chain",
               repo_root="firmware/main", status="running")
    refs = {
        "task_brief_ref": "task-brief.valid.json",
        "engineering_task_package_ref": "engineering-task-package.valid.json",
        "delivery_receipt_ref": "delivery-receipt.valid.json",
        "verification_report_ref": "verification-report.valid.json",
        "pilot_result_ref": "pilot-result.feature.valid.json",
    }
    for field, name in refs.items():
        value = load(fixtures / name)
        if field == "pilot_result_ref":
            value["source_type"] = "real"
        if field == "task_brief_ref":
            value["required_verification"]["hil"] = "not_applicable"
        target = field.removesuffix("_ref") + ".json"
        write(root / target, value)
        run[field] = target
    run["extra_artifact_refs"] = {}
    for kind, name in [("material_manifest", "material-manifest.valid.json"),
                       ("acceptance_evidence_matrix", "acceptance-evidence-matrix.valid.md"),
                       ("knowledge_harvest", "knowledge-harvest.valid.md")]:
        dest = "extras/" + name
        (root / dest).parent.mkdir(exist_ok=True)
        shutil.copy2(fixtures / name, root / dest)
        run["extra_artifact_refs"][kind] = dest
    run["evidence_bundle_ref"] = None
    write(root / "pilot-run.json", run)
    if completed:
        freeze(root)
    return root


def freeze(root):
    run = load(root / "pilot-run.json")
    run["status"] = "completed"
    run["evidence_bundle_ref"] = "evidence-bundle.json"
    write(root / "evidence-bundle.json", pilot.collect_bundle(root, run))
    write(root / "pilot-run.json", run)
    pilot.validate_run_dir(root)


def generate(root):
    return receipt_tool.build_receipt(root / "pilot-run.json", root / "pilot_result.json", None)


class PilotQualificationTests(unittest.TestCase):
    def test_valid_bound_run_remains_eligible_but_missing_bundle_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixture_run(Path(tmp) / "run")
            self.assertTrue(generate(root)["product_readiness_eligible"])
            (root / "evidence-bundle.json").unlink()
            with self.assertRaisesRegex(ValueError, "artifact ref missing"):
                generate(root)

    def test_incorrect_pass_and_incomplete_verification_never_qualify(self):
        for mutation, check in [("incorrect_pass", "no_incorrect_pass"), ("verification", "verification_complete")]:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                root = fixture_run(Path(tmp) / "run")
                result = load(root / "pilot_result.json")
                if mutation == "incorrect_pass":
                    result["expected_block"] = True
                else:
                    result["verification"]["completed_layers"] = []
                write(root / "pilot_result.json", result)
                freeze(root)
                receipt = generate(root)
                self.assertFalse(receipt["eligibility_checks"][check])
                self.assertFalse(receipt["product_readiness_eligible"])

    def test_aggregate_recomputes_claims_and_detects_artifact_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixture_run(Path(tmp) / "run")
            path = root / "edge-foundation-pilot-receipt.json"
            receipt = generate(root)
            write(path, receipt)
            self.assertEqual(readiness.evaluate([path])["eligible_real_receipts"], 1)
            receipt["target_experts"] = ["hardware-expert"]
            write(path, receipt)
            with self.assertRaisesRegex(AssertionError, "recomputed frozen evidence"):
                readiness.evaluate([path])
            write(path, generate(root))
            (root / "extras/knowledge-harvest.valid.md").write_text("changed")
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                readiness.evaluate([path])

    def test_completion_failure_preserves_original_run_and_can_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixture_run(Path(tmp) / "run", completed=False)
            verification = load(root / "verification_report.json")
            verification["independence_confirmed"] = False
            bad = Path(tmp) / "bad-verification.json"
            write(bad, verification)
            before = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            args = pilot.build_parser().parse_args(["complete", str(root), "--verification-report", str(bad)])
            with self.assertRaisesRegex(ValueError, "confirm independence"):
                pilot.cmd_complete(args)
            after = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            self.assertFalse(list(root.parent.glob(".pilot-complete-*")))
            pilot.cmd_complete(pilot.build_parser().parse_args(["complete", str(root)]))
            self.assertEqual(pilot.validate_run_dir(root)["status"], "completed")


class SkillSummaryTests(unittest.TestCase):
    def test_forged_block_verdict_does_not_promote_completed_invocation(self):
        spec = importlib.util.spec_from_file_location("skill_test_fixture", ROOT / "tests/unit/test_skill_evaluation.py")
        fixture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = []
            for kind, case_id in [("positive", "SEC-BOOT-CHAIN-POS"), ("block", "SEC-BOOT-CHAIN-BLOCK")]:
                inv = root / (kind + "-inv.json")
                ev = root / (kind + "-eval.json")
                write(inv, fixture.invocation("COMPLETED"))
                semantic_path, digest = fixture.semantic_evidence(root / (kind + "-semantic.json"), inv,
                                                                 case_id, "human-review", "reviewer")
                result = case_tool.evaluate(case_id, inv, "PASS", "human-review", "reviewer", str(semantic_path), digest, None)
                result["contract_verdict"]["status"] = "PASS"
                result["case_evidence_eligible"] = True
                write(ev, result)
                paths.extend([ev, inv])
            summary = maturity.build_summary("boot-chain-analysis", *paths)
            self.assertEqual(summary["status"], "DEFINED")
            self.assertFalse(summary["checks"]["case_evidence_eligible"])


class GovernanceTests(unittest.TestCase):
    def run_audit(self, rules, *, protected=True):
        def fake_api(url, token):
            if "/rules/branches/" in url:
                return rules
            if "/branches/" in url:
                return {"name": "main", "protected": protected}
            if "/rulesets?" in url:
                return [{"id": 1, "enforcement": "active"}]
            return {"id": 1, "name": "develop-only", "rules": self.required_rules()}
        output = io.StringIO()
        with patch.object(governance, "api", fake_api), patch.object(sys, "argv", ["audit", "--strict"]), contextlib.redirect_stdout(output):
            try:
                governance.main()
            except SystemExit as exc:
                self.assertEqual(exc.code, 2)
        return json.loads(output.getvalue())

    def required_rules(self):
        contexts = load(governance.CONTRACT)["required"]["required_status_checks"]
        return [{"type": "pull_request"}, {"type": "non_fast_forward"}, {"type": "deletion"},
                {"type": "required_status_checks", "parameters": {"required_status_checks": [{"context": c} for c in contexts]}}]

    def test_unrelated_or_excluded_rulesets_do_not_protect_main(self):
        self.assertEqual(self.run_audit([], protected=False)["status"], "BLOCKED_SERVER_GOVERNANCE")
        self.assertEqual(self.run_audit([])["status"], "BLOCKED_SERVER_GOVERNANCE")

    def test_effective_main_rules_pass_and_missing_checks_fail(self):
        self.assertEqual(self.run_audit(self.required_rules())["status"], "PASS")
        self.assertEqual(self.run_audit(self.required_rules()[:-1])["status"], "BLOCKED_SERVER_GOVERNANCE")

    def test_effective_rule_pagination_is_consumed(self):
        with patch.object(governance, "api", side_effect=[[{}] * 100, [{"type": "deletion"}]]) as api:
            self.assertEqual(len(governance.api_list("https://example.invalid/rules", None)), 101)
            self.assertEqual(api.call_count, 2)


if __name__ == "__main__":
    unittest.main()
