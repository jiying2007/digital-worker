from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "verify_cross_repo_checkouts.py"

spec = importlib.util.spec_from_file_location("verify_cross_repo_checkouts", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def future_binding() -> dict:
    return {
        "claude-code": {
            "runtime": "claude-code",
            "repository": None,
            "target": "claude-code",
            "source_identity_mode": None,
            "status": "future-binding",
        }
    }


def blocked_candidate() -> dict:
    return {
        "claude-code": {
            "runtime": "claude-code",
            "repository": "jiying2007/claude",
            "target": "claude-code",
            "source_identity_mode": "exact-release-source-blobs",
            "status": "binding-candidate-blocked",
            "candidate_pr": "jiying2007/claude#1",
            "blocker_ref": "jiying2007/claude#2",
            "blocker": "github-hosted-runner-admission-before-step-execution",
        }
    }


def ready_candidate() -> dict:
    return {
        "claude-code": {
            "runtime": "claude-code",
            "repository": "https://github.com/jiying2007/claude.git",
            "target": "claude-code",
            "source_identity_mode": "exact-release-source-blobs",
            "status": "source-set-bound",
            "merged_pr": "jiying2007/claude#1",
            "binding_commit": "9768012c46f348421050192919a91b8070b5d672",
            "exact_head_workflow_run": "jiying2007/claude/actions/runs/35111664791",
            "fresh_main_workflow_run": "jiying2007/claude/actions/runs/35111772454",
            "r1_binding_conformance": "passed",
            "verified_runtime_execution_receipt": "pending",
            "r2_real_provider_substitution": "pending",
        }
    }


def approved_binding() -> dict:
    return {
        "repository": "jiying2007/claude",
        "runtime_target": "claude-code",
        "source_identity_mode": "exact-release-source-blobs",
        "runtime_readiness": "SOURCE_SET_READY_R1",
        "commit": "9768012c46f348421050192919a91b8070b5d672",
        "r1_exact_head_workflow_run": "jiying2007/claude/actions/runs/35111664791",
        "r1_fresh_main_workflow_run": "jiying2007/claude/actions/runs/35111772454",
        "verified_runtime_execution_receipt": "PENDING",
        "r2_real_provider_substitution": "PENDING",
    }


class RuntimeCandidateStateTests(unittest.TestCase):
    def test_future_binding_remains_valid_before_real_candidate_exists(self) -> None:
        self.assertEqual(module.verify_second_runtime_candidate(future_binding()), "future-binding")

    def test_real_but_blocked_candidate_is_valid_without_becoming_ready(self) -> None:
        self.assertEqual(
            module.verify_second_runtime_candidate(blocked_candidate()),
            "binding-candidate-blocked",
        )

    def test_blocked_candidate_requires_exact_machine_blocker_identity(self) -> None:
        candidates = blocked_candidate()
        del candidates["claude-code"]["blocker_ref"]
        with self.assertRaisesRegex(RuntimeError, "blocker_ref drift"):
            module.verify_second_runtime_candidate(candidates)

    def test_future_binding_cannot_claim_source_identity(self) -> None:
        candidates = future_binding()
        candidates["claude-code"]["repository"] = "jiying2007/claude"
        with self.assertRaisesRegex(RuntimeError, "future-binding must not claim"):
            module.verify_second_runtime_candidate(candidates)

    def test_ready_upstream_still_requires_explicit_digital_worker_binding(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "not yet an approved Digital Worker runtime binding"):
            module.verify_second_runtime_candidate(ready_candidate())

    def test_ready_candidate_passes_only_with_exact_approved_r1_binding(self) -> None:
        self.assertEqual(
            module.verify_second_runtime_candidate(ready_candidate(), approved_binding()),
            "source-set-bound",
        )

    def test_ready_candidate_commit_must_match_approved_binding(self) -> None:
        candidates = ready_candidate()
        candidates["claude-code"]["binding_commit"] = "0" * 40
        with self.assertRaisesRegex(RuntimeError, "binding_commit drift"):
            module.verify_second_runtime_candidate(candidates, approved_binding())

    def test_ready_binding_cannot_claim_real_receipt_or_r2_without_evidence(self) -> None:
        binding = approved_binding()
        binding["r2_real_provider_substitution"] = "PASS"
        with self.assertRaisesRegex(RuntimeError, "approved claude-code binding r2_real_provider_substitution drift"):
            module.verify_second_runtime_candidate(ready_candidate(), binding)

    def test_unknown_candidate_status_fails_closed(self) -> None:
        candidates = blocked_candidate()
        candidates["claude-code"]["status"] = "almost-ready"
        with self.assertRaisesRegex(RuntimeError, "unsupported claude-code candidate status"):
            module.verify_second_runtime_candidate(candidates)


if __name__ == "__main__":
    unittest.main()
