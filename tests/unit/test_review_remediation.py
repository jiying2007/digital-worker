"""Evidence qualification, derived output and CI regressions for review F1/F2/F3/F6."""
from __future__ import annotations

import contextlib
import fnmatch
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import embedded_pilot as pilot
import evaluate_edge_foundation_pilot as receipts
import evaluate_edge_foundation_product_readiness as readiness
import test_review_hardening as fixtures


class ReviewRemediationTests(unittest.TestCase):
    def complete(self, root):
        with contextlib.redirect_stdout(io.StringIO()):
            pilot.cmd_complete(pilot.build_parser().parse_args(["complete", str(root)]))
        run = pilot.validate_run_dir(root)
        return receipts.build_receipt(root / "pilot-run.json", root / run["pilot_result_ref"], None)

    def test_missing_review_requires_each_structured_substitute_field(self):
        for missing in ("review_substitute", "unavailable_reason", "static_checks", "hosted_ci", "traceable_ref", "listed_ref"):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as tmp:
                root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
                value = fixtures.load(root / "verification_report.json")
                if missing == "review_substitute":
                    value.pop(missing)
                elif missing == "traceable_ref":
                    value["review_substitute"]["static_checks"]["evidence_ref"] = "CI passed"
                elif missing == "listed_ref":
                    value["evidence_refs"] = []
                else:
                    value["review_substitute"].pop(missing)
                fixtures.write(root / "verification_report.json", value)
                before = (root / "pilot-run.json").read_bytes()
                with self.assertRaises(Exception):
                    self.complete(root)
                self.assertEqual(before, (root / "pilot-run.json").read_bytes())
                self.assertEqual(fixtures.load(root / "pilot-run.json")["status"], "running")

    def test_valid_substitute_survives_completion_receipt_and_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            receipt = self.complete(root)
            self.assertTrue(receipt["eligibility_checks"]["review_acceptable"])
            path = root / "edge-foundation-pilot-receipt.json"
            pilot.write_derived_json(path, receipt)
            self.assertEqual(readiness.evaluate([path])["eligible_real_receipts"], 1)
            # Re-freeze a changed Verification to prove semantic checking is not just bundle hashes.
            run = pilot.load_run(root)
            verification = root / run["verification_report_ref"]
            value = fixtures.load(verification)
            value.pop("review_substitute")
            fixtures.write(verification, value)
            fixtures.write(root / run["evidence_bundle_ref"], pilot.collect_bundle(root, run))
            with self.assertRaisesRegex(ValueError, "review_substitute"):
                receipts.build_receipt(root / "pilot-run.json", root / run["pilot_result_ref"], None)
            with self.assertRaises(Exception):
                readiness.evaluate([path])

    def test_required_hil_materials_cannot_be_available_without_identity(self):
        for kind in ("device_identity", "test_environment"):
            for key in ("source", "evidence_ref"):
                with self.subTest(kind=kind, key=key), tempfile.TemporaryDirectory() as tmp:
                    root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
                    task = fixtures.load(root / "task_brief.json")
                    task["required_verification"]["hil"] = "required"
                    fixtures.write(root / "task_brief.json", task)
                    value = fixtures.load(root / "verification_report.json")
                    value["layers"]["hil"] = "pass"
                    fixtures.write(root / "verification_report.json", value)
                    path = root / "extras/material-manifest.valid.json"
                    manifest = fixtures.load(path)
                    next(i for i in manifest["items"] if i["kind"] == kind)[key] = "  "
                    fixtures.write(path, manifest)
                    pilot.validate_run_dir(root)  # Unknown identity can remain nonterminal.
                    with self.assertRaisesRegex(ValueError, "requires nonempty source and evidence_ref"):
                        self.complete(root)

    def test_derived_outputs_reject_marker_frozen_refs_and_symlinks(self):
        for target in ("pilot-run.json", "task_brief.json", "evidence-bundle.json"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                root = fixtures.fixture_run(Path(tmp) / "run")
                before = (root / target).read_bytes()
                with self.assertRaisesRegex(ValueError, "collides"):
                    with contextlib.redirect_stdout(io.StringIO()):
                        pilot.cmd_pilot_receipt(pilot.build_parser().parse_args(
                            ["pilot-receipt", str(root), "--output", str(root / target)]))
                self.assertEqual(before, (root / target).read_bytes())
                pilot.validate_run_dir(root)
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run")
            before = (root / "pilot-run.json").read_bytes()
            (root / "edge-foundation-pilot-receipt.json").symlink_to(root / "pilot-run.json")
            with self.assertRaisesRegex(ValueError, "symlink"):
                pilot.cmd_pilot_receipt(pilot.build_parser().parse_args(["pilot-receipt", str(root)]))
            self.assertEqual(before, (root / "pilot-run.json").read_bytes())

    def test_summary_and_readiness_outputs_follow_same_write_protocol(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run")
            marker = root / "pilot-run.json"
            before = marker.read_bytes()
            for command in ("summary", "product-readiness"):
                with self.subTest(command=command), self.assertRaisesRegex(ValueError, "collides"):
                    with contextlib.redirect_stdout(io.StringIO()):
                        pilot.build_parser().parse_args([command, tmp, "--output", str(marker)]).func(
                            pilot.build_parser().parse_args([command, tmp, "--output", str(marker)]))
                self.assertEqual(before, marker.read_bytes())
            with pilot.writer_lock(root):
                with self.assertRaisesRegex(pilot.PilotError, "Another writer"):
                    pilot.cmd_pilot_receipt(pilot.build_parser().parse_args(["pilot-receipt", str(root)]))
            output = root / "report.json"
            output.write_text("original")
            with patch.object(pilot.json, "dumps", side_effect=ValueError("serialization failed")):
                with self.assertRaisesRegex(ValueError, "serialization failed"):
                    pilot.write_derived_json(output, {})
            self.assertEqual(output.read_text(), "original")
            self.assertFalse(list(root.glob(".pilot-derived-*")))

    def test_nested_marker_cannot_hide_outer_frozen_refs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
            self.complete(root)
            run = pilot.load_run(root)
            frozen = root / run["task_brief_ref"]
            nested_marker = frozen.parent / "pilot-run.json"
            with self.assertRaisesRegex(ValueError, "nested Run marker"):
                pilot.write_derived_json(nested_marker, {})
            # Simulate a marker written by an unrelated tool: every ancestor still protects its refs.
            fake = dict(run, status="planned", task_brief_ref="pilot-run.json", evidence_bundle_ref=None,
                        skill_invocation_refs=[], extra_artifact_refs={})
            for key in pilot.REF_SCHEMAS:
                fake[key] = None
            fixtures.write(nested_marker, fake)
            before = frozen.read_bytes()
            with self.assertRaisesRegex(ValueError, "collides"):
                pilot.write_derived_json(frozen, {"corrupt": True})
            self.assertEqual(before, frozen.read_bytes())

    def test_real_feature_ci_covers_schemas_and_direct_validators(self):
        import yaml
        workflow = yaml.load((ROOT / ".github/workflows/real-feature-pilot-evidence.yml").read_text(), Loader=yaml.BaseLoader)
        for event in ("pull_request", "push"):
            patterns = workflow["on"][event]["paths"]
            for path in ("schemas/pilot-run.v1.schema.json", "schemas/pilot-result.v1.schema.json",
                         "scripts/validate_material_manifest.py", "scripts/validate_skill_invocation_receipt.py",
                         "scripts/pilot_support.py", "tests/unit/test_review_remediation.py"):
                self.assertTrue(any(fnmatch.fnmatchcase(path, p) for p in patterns), (event, path))


if __name__ == "__main__":
    unittest.main()
