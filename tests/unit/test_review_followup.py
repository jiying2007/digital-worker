"""Behavior regressions for the nine follow-up review findings."""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(Path(__file__).parent)]
import test_review_hardening as fixtures
import test_runtime_r2_local_flow as r2
import evaluate_embedded_pilot as metrics
import verify_cross_repo_checkouts as checkouts
import validate_material_manifest as materials


def make_run(root, run_id, track="feature", **result_changes):
    fixtures.fixture_run(root, completed=False)
    run = fixtures.load(root / "pilot-run.json")
    task_type, mode = {"feature": ("feature_development", "short_chain"),
                       "debug": ("defect_debugging", "diagnostic_chain"),
                       "review_release": ("code_review", "review_only")}[track]
    run.update(run_id=run_id, pilot_track=track, task_type=task_type, workflow_mode=mode)
    for field in ("engineering_task_package_ref", "verification_report_ref", "pilot_result_ref"):
        path = root / run[field]
        doc = fixtures.load(path)
        doc["run_id"] = run_id
        if field == "pilot_result_ref":
            doc.update(pilot_track=track, **result_changes)
            doc["route"].update(actual_mode=mode, expected_mode=mode)
        fixtures.write(path, doc)
    path = root / run["extra_artifact_refs"]["material_manifest"]
    doc = fixtures.load(path)
    doc["run_id"] = run_id
    if track == "debug":
        for kind in ("log", "reproduction"):
            doc["items"].append({"kind": kind, "required": False, "status": "available",
                                 "source": "test", "version": None, "evidence_ref": None})
        fixtures.write(root / "hypotheses.json", {"run_id": run_id, "hypotheses": []})
        run["extra_artifact_refs"]["hypothesis_registry"] = "hypotheses.json"
    fixtures.write(path, doc)
    fixtures.write(root / "pilot-run.json", run)
    fixtures.freeze(root)
    return root


def receipt(root):
    path = root / "edge-foundation-pilot-receipt.json"
    fixtures.write(path, fixtures.generate(root))
    return path


class PilotFollowupTests(unittest.TestCase):
    def test_completion_rejects_file_directory_and_dangling_links_without_changes(self):
        for kind in ("file", "directory", "dangling"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                root = fixtures.fixture_run(Path(tmp) / "run", completed=False)
                original = root / "delivery_receipt.json"
                target = original if kind == "file" else root / ("extras" if kind == "directory" else "absent")
                link = root / ("delivery-receipt.json" if kind == "file" else "linked")
                link.symlink_to(target, target_is_directory=kind == "directory")
                before = original.read_bytes(), (root / "pilot-run.json").read_bytes()
                source = Path(tmp) / "replacement.json"
                doc = fixtures.load(original)
                doc["outcomes"] = ["replacement"]
                fixtures.write(source, doc)
                args = fixtures.pilot.build_parser().parse_args(["complete", str(root), "--delivery-receipt", str(source)])
                with self.assertRaisesRegex(ValueError, "symlink"):
                    fixtures.pilot.cmd_complete(args)
                self.assertEqual(before, (original.read_bytes(), (root / "pilot-run.json").read_bytes()))
                self.assertFalse(list(root.parent.glob(".pilot-complete-*")))
                link.unlink()
                fixtures.pilot.cmd_complete(args)
                self.assertEqual(fixtures.pilot.validate_run_dir(root)["status"], "completed")

    def test_available_review_decision_controls_eligibility(self):
        for decision in ("APPROVE", "APPROVE_WITH_RISK", "BLOCKED", "REQUEST_CHANGES"):
            with self.subTest(decision=decision), tempfile.TemporaryDirectory() as tmp:
                root = fixtures.fixture_run(Path(tmp) / "run")
                run = fixtures.load(root / "pilot-run.json")
                doc = fixtures.load(ROOT / "tests/fixtures/review-report.valid.json")
                doc["decision"] = decision
                run["review_report_ref"] = "review.json"
                fixtures.write(root / "review.json", doc)
                fixtures.write(root / "pilot-run.json", run)
                fixtures.freeze(root)
                result = fixtures.generate(root)
                expected = decision in {"APPROVE", "APPROVE_WITH_RISK"}
                self.assertEqual(result["product_readiness_eligible"], expected)
                self.assertEqual(result["eligibility_checks"]["review_acceptable"], expected)

    def test_all_completed_real_runs_contribute_to_safety_gate(self):
        for changes, check in [({"unauthorized_actions": 1}, "no_unauthorized_actions"),
                               ({"expected_block": True}, "no_incorrect_pass"),
                               ({"audit_trace_complete": False}, "audit_trace_complete")]:
            with self.subTest(check=check), tempfile.TemporaryDirectory() as tmp:
                base = Path(tmp)
                paths = [receipt(make_run(base / track, track, track))
                         for track in ("debug", "feature", "review_release")]
                self.assertTrue(fixtures.readiness.evaluate(paths)["eligible_for_product_review"])
                paths.append(receipt(make_run(base / "unsafe", "unsafe", **changes)))
                result = fixtures.readiness.evaluate(paths)
                self.assertEqual(result["eligible_real_receipts"], 3)
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIn(f"safety-violation:unsafe:{check}", result["blockers"])

    def test_synthetic_unsafe_run_does_not_count_or_block_real_cohort(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            paths = [receipt(make_run(base / track, track, track))
                     for track in ("debug", "feature", "review_release")]
            synthetic = fixtures.receipt_tool.build_receipt(ROOT / "tests/fixtures/pilot-run.valid.json",
                                                            ROOT / "tests/fixtures/pilot-result.valid.json", None)
            path = base / "synthetic.json"
            fixtures.write(path, synthetic)
            result = fixtures.readiness.evaluate(paths + [path])
            self.assertEqual(result["eligible_real_receipts"], 3)
            self.assertTrue(result["eligible_for_product_review"])


class MaterialIdentityTests(unittest.TestCase):
    def test_conflicting_identity_cannot_qualify_even_with_degradation_approval(self):
        for kind, field, value in [("repo", "source", "different/repository"),
                                    ("base_commit", "version", "f" * 40)]:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                root = fixtures.fixture_run(Path(tmp) / "run")
                run = fixtures.load(root / "pilot-run.json")
                path = root / run["extra_artifact_refs"]["material_manifest"]
                doc = fixtures.load(path)
                next(item for item in doc["items"] if item["kind"] == kind)[field] = value
                doc.update(readiness="DEGRADED", degradation_approved_by="owner")
                fixtures.write(path, doc)
                with self.assertRaisesRegex(ValueError, "identity mismatch"):
                    fixtures.freeze(root)

    def test_equivalent_github_url_preserves_result_commit_context(self):
        doc = fixtures.load(ROOT / "domains/edge-foundation/pilot/evidence/FEATURE-PCR02-OTA-001/extras/material_manifest.json")
        run = {"run_id": doc["run_id"], "pilot_track": "feature", "task_type": "component_development",
               "repo_root": "jiying2007/ota_download_test", "base_commit": "eeb926bd1fff75d2a5d5abb9f0ede9c8f582cc6d"}
        for suffix in ("", ".git", "/"):
            next(item for item in doc["items"] if item["kind"] == "repo")["source"] = "https://github.com/jiying2007/ota_download_test" + suffix
            self.assertTrue(materials.validate_manifest(doc, "feature", True, pilot_run=run)["terminal_acceptable"])

    def test_standalone_structure_is_not_terminal_identity_validation(self):
        doc = fixtures.load(ROOT / "tests/fixtures/material-manifest.valid.json")
        self.assertFalse(materials.validate_manifest(doc, "feature")["terminal_acceptable"])
        with self.assertRaisesRegex(AssertionError, "Pilot Run context"):
            materials.validate_manifest(doc, "feature", True)

    def test_unknown_planned_identity_can_remain_honestly_blocked(self):
        doc = fixtures.load(ROOT / "tests/fixtures/material-manifest.valid.json")
        for item in doc["items"]:
            if item["kind"] in {"repo", "base_commit"}:
                item.update(status="missing", source=None, version=None)
        doc.update(readiness="BLOCKED", missing_critical=["repo", "base_commit"])
        result = materials.validate_manifest(doc, "feature", pilot_run={"run_id": doc["run_id"]})
        self.assertFalse(result["terminal_acceptable"])


class MetricsFollowupTests(unittest.TestCase):
    def test_duplicate_run_ids_are_rejected(self):
        path = ROOT / "tests/fixtures/pilot-result.valid.json"
        with self.assertRaisesRegex(ValueError, "duplicate"):
            metrics.evaluate([path, path])

    def test_raw_results_never_grant_product_qualification(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for index, track in enumerate(("debug", "feature", "review_release")):
                doc = fixtures.load(ROOT / "tests/fixtures/pilot-result.valid.json")
                doc.update(run_id=str(index), pilot_track=track, source_type="real", outcome="BLOCKED")
                path = Path(tmp) / f"{index}.json"
                fixtures.write(path, doc)
                paths.append(path)
            result = metrics.evaluate(paths)
            self.assertEqual(result["real_completed_runs"], 0)
            for path in paths:
                doc = fixtures.load(path)
                doc["outcome"] = "PASS"
                fixtures.write(path, doc)
            result = metrics.evaluate(paths)
            self.assertEqual(result["real_completed_runs"], 3)
            self.assertFalse(result["promotion_eligible"])
            self.assertIn("canonical-receipt-evaluation-required", result["promotion_blockers"])
            self.assertNotIn("Product-readiness eligible", metrics.render_markdown(result))


class CheckoutSafetyTests(unittest.TestCase):
    def test_existing_directories_and_links_are_never_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "existing"
            existing.mkdir()
            marker = existing / "dirty.txt"
            marker.write_text("retain")
            link = root / "link"
            link.symlink_to(existing)
            dangling = root / "dangling"
            dangling.symlink_to(root / "absent")
            with patch.object(checkouts, "run") as command:
                for dest in (existing, link, dangling):
                    with self.assertRaisesRegex(RuntimeError, "already exists"):
                        checkouts.checkout("jiying2007/codex", "a" * 40, dest)
                command.assert_not_called()
            self.assertEqual(marker.read_text(), "retain")

    def test_failed_fetch_does_not_publish_and_success_requires_exact_head(self):
        for actual in (None, "b" * 40, "a" * 40):
            with self.subTest(actual=actual), tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / "checkout"
                def command(*args, **kwargs):
                    if actual is None:
                        raise RuntimeError("fetch failed")
                    return actual if "rev-parse" in args else ""
                with patch.object(checkouts, "run", side_effect=command):
                    if actual == "a" * 40:
                        checkouts.checkout("jiying2007/codex", "a" * 40, dest)
                        self.assertTrue(dest.is_dir())
                    else:
                        with self.assertRaises(RuntimeError):
                            checkouts.checkout("jiying2007/codex", "a" * 40, dest)
                        self.assertFalse(dest.exists())
                self.assertFalse(list(Path(tmp).glob(".provider-checkout-*")))

    def test_destination_appearing_during_fetch_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "checkout"
            def command(*args, **kwargs):
                if "fetch" in args:
                    dest.mkdir()
                    (dest / "user.txt").write_text("retain")
                return "a" * 40 if "rev-parse" in args else ""
            with patch.object(checkouts, "run", side_effect=command), self.assertRaisesRegex(RuntimeError, "already exists"):
                checkouts.checkout("jiying2007/codex", "a" * 40, dest)
            self.assertEqual((dest / "user.txt").read_text(), "retain")


class R2FollowupTests(unittest.TestCase):
    def test_archive_binding_and_git_metadata_rejected_before_host_execution(self):
        for rebind in (False, True):
            with self.subTest(rebind=rebind), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                plan = r2.build_plan()
                frozen = r2.freeze(root, plan)
                codex = r2.runtime_dir(root, "codex", plan)
                claude = r2.runtime_dir(root, "claude-code", plan)
                archive = codex / "result-tree.tar.gz"
                rows = []
                with tarfile.open(archive, "r:gz") as src:
                    for member in src.getmembers():
                        rows.append((member, src.extractfile(member).read() if member.isfile() else None))
                with tarfile.open(archive, "w:gz") as dst:
                    for member, data in rows:
                        dst.addfile(member, io.BytesIO(data) if data is not None else None)
                    data = b"ref: refs/heads/injected\n"
                    member = tarfile.TarInfo(".git/HEAD")
                    member.size = len(data)
                    dst.addfile(member, io.BytesIO(data))
                if rebind:
                    postflight = fixtures.load(codex / "result-postflight.json")
                    postflight["result_archive_sha256"] = r2.sha(archive)
                    r2.write_json(codex / "result-postflight.json", postflight)
                    native = fixtures.load(codex / "codex-native.json")
                    native["evidence_refs"] = [ref for ref in native["evidence_refs"] if not ref.startswith("replay-postflight:")]
                    native["evidence_refs"].append("replay-postflight:sha256:" + r2.sha(codex / "result-postflight.json"))
                    r2.write_json(codex / "codex-native.json", native)
                with patch.object(r2.verify, "_run_native_host_verification") as host:
                    with self.assertRaisesRegex(r2.verify.VerificationError, "archive|Git metadata"):
                        r2.verify.verify_local_r2(ROOT, frozen, codex, claude, root / "out", "independent")
                    host.assert_not_called()
                self.assertFalse((root / "out/runtime-r2-domain-verification.json").exists())

    def test_actor_whitespace_never_creates_independence(self):
        for actor in (" local-test-codex ", "\tlocal-test-claude-code\n", "   "):
            with self.subTest(actor=actor), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                plan = r2.build_plan()
                frozen = r2.freeze(root, plan)
                codex = r2.runtime_dir(root, "codex", plan)
                claude = r2.runtime_dir(root, "claude-code", plan)
                with self.assertRaises(r2.verify.VerificationError):
                    r2.verify.verify_local_r2(ROOT, frozen, codex, claude, root / "out", actor)

    def test_provider_and_independent_actor_are_normalized_in_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = r2.build_plan()
            frozen = r2.freeze(root, plan)
            codex = r2.runtime_dir(root, "codex", plan)
            claude = r2.runtime_dir(root, "claude-code", plan)
            path = codex / "provider-authorization.json"
            auth = fixtures.load(path)
            auth["actor"] = " local-test-codex "
            r2.write_json(path, auth)
            with self.assertRaisesRegex(r2.verify.VerificationError, "must be distinct"):
                r2.verify.verify_local_r2(ROOT, frozen, codex, claude, root / "self", "local-test-codex")
            result = r2.verify.verify_local_r2(ROOT, frozen, codex, claude, root / "independent", " independent ")
            self.assertEqual(result["verification_actor"], "independent")
            self.assertEqual(result["provider_execution_actors"]["codex"], "local-test-codex")

    def test_standalone_verifier_rejects_git_metadata_before_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            (root / ".git/HEAD").write_text("injected")
            log = root / "host.log"
            with self.assertRaisesRegex(r2.verify.VerificationError, "Git metadata"):
                r2.verify._run_native_host_verification(root, log, r2.build_plan())
            self.assertFalse(log.exists())


class BranchGcTests(unittest.TestCase):
    def run_gc(self, **changes):
        workflow = yaml.safe_load((ROOT / ".github/workflows/branch-gc.yml").read_text())
        body = workflow["jobs"]["gc"]["steps"][1]["run"]
        mocks = r'''
sed() { printf '%s\n' fix/probe; }
git() {
  case "$*" in
    'rev-parse HEAD') printf '%s\n' "$GITHUB_SHA" ;;
    'check-ref-format --branch fix/probe') return 0 ;;
    push*)
      printf 'MOCK_PUSH %s\n' "$*"
      [[ "$*" == *"--force-with-lease=refs/heads/fix/probe:ffffffffffffffffffffffffffffffffffffffff"* ]] || return 90
      return "$LEASE_EXIT" ;;
    *) printf '%s\n' 'unexpected git call' >&2; return 91 ;;
  esac
}
gh() {
  case "$*" in
    *'--method DELETE'*) printf '%s\n' MOCK_UNSAFE_DELETE; return 92 ;;
    *'--paginate'*) printf '%s\n' main fix/probe ;;
    *'git/ref/heads/'*)
      [[ "$REF_ERROR" == 0 ]] || return 1
      printf '%s\n' '{"object":{"sha":"ffffffffffffffffffffffffffffffffffffffff"}}' ;;
    *'branches/fix'*) printf '%s\n' "$PROTECTED" ;;
    *'--state open'*) printf '%s\n' "$OPEN_COUNT" ;;
    *'--state closed'*) printf '%s\n' 0 ;;
    *'/compare/'*)
      printf 'MOCK_COMPARE %s\n' "$*" >&2
      printf '%s\n' "$COMPARE_STATUS" ;;
    *) printf '%s\n' 'unexpected gh call' >&2; return 93 ;;
  esac
}
'''
        env = dict(os.environ, GITHUB_REF="refs/heads/main", GITHUB_SHA="a" * 40,
                   GITHUB_EVENT_NAME="workflow_dispatch", GITHUB_REPOSITORY="test/repo", DRY_RUN="false",
                   LEASE_EXIT="0", REF_ERROR="0", PROTECTED="false", OPEN_COUNT="0", COMPARE_STATUS="ahead")
        env.update(changes)
        return subprocess.run(["bash", "-c", mocks + body], env=env, capture_output=True, text=True, cwd=ROOT)

    def test_nonmain_dispatch_is_rejected_without_remote_write(self):
        result = self.run_gc(GITHUB_REF="refs/heads/fix/probe", COMPARE_STATUS="identical")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("MOCK_PUSH", result.stdout)
        self.assertNotIn("MOCK_UNSAFE_DELETE", result.stdout)

    def test_main_comparison_and_exact_tip_lease(self):
        result = self.run_gc()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("..." + "a" * 40, result.stderr)
        self.assertIn("MOCK_PUSH", result.stdout)
        self.assertNotIn("MOCK_UNSAFE_DELETE", result.stdout)

    def test_dry_run_performs_no_write_and_racing_tip_is_rejected(self):
        result = self.run_gc(DRY_RUN="true")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("MOCK_PUSH", result.stdout)
        self.assertNotEqual(self.run_gc(LEASE_EXIT="1").returncode, 0)

    def test_api_failure_protection_open_pr_and_unmerged_tip_are_blocked(self):
        for changes in ({"REF_ERROR": "1"}, {"PROTECTED": "true"}, {"OPEN_COUNT": "1"},
                        {"COMPARE_STATUS": "diverged"}):
            with self.subTest(changes=changes):
                result = self.run_gc(**changes)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("MOCK_PUSH", result.stdout)

    def test_git_lease_rejects_advanced_tip_in_local_temporary_remote(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            remote, work = root / "remote.git", root / "work"
            work.mkdir()
            env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                       GIT_AUTHOR_NAME="Fixture", GIT_COMMITTER_NAME="Fixture",
                       GIT_AUTHOR_EMAIL="fixture@example.invalid", GIT_COMMITTER_EMAIL="fixture@example.invalid")
            def git(*args, check=True):
                return subprocess.run(["git", *args], cwd=work, env=env, check=check, capture_output=True, text=True)
            git("init", "--bare", str(remote))
            git("-c", "init.defaultBranch=main", "init")
            git("remote", "add", "origin", str(remote))
            git("commit", "--allow-empty", "-m", "fixture baseline")
            expected = git("rev-parse", "HEAD").stdout.strip()
            git("push", "origin", "HEAD:refs/heads/fix/probe")
            git("commit", "--allow-empty", "-m", "fixture advanced tip")
            advanced = git("rev-parse", "HEAD").stdout.strip()
            git("push", "origin", "HEAD:refs/heads/fix/probe")
            stale = git("push", f"--force-with-lease=refs/heads/fix/probe:{expected}", "origin", ":refs/heads/fix/probe", check=False)
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn(advanced, git("ls-remote", "origin", "refs/heads/fix/probe").stdout)
            git("push", f"--force-with-lease=refs/heads/fix/probe:{advanced}", "origin", ":refs/heads/fix/probe")
            self.assertEqual(git("ls-remote", "origin", "refs/heads/fix/probe").stdout, "")


if __name__ == "__main__":
    unittest.main()
