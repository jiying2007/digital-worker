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

    def test_ready_status_requires_explicit_digital_worker_runtime_binding_promotion(self) -> None:
        for status in sorted(module.READY_RUNTIME_BINDING_STATUSES):
            candidates = blocked_candidate()
            candidates["claude-code"]["status"] = status
            with self.assertRaisesRegex(RuntimeError, "R1-ready upstream"):
                module.verify_second_runtime_candidate(candidates)

    def test_unknown_candidate_status_fails_closed(self) -> None:
        candidates = blocked_candidate()
        candidates["claude-code"]["status"] = "almost-ready"
        with self.assertRaisesRegex(RuntimeError, "unsupported claude-code candidate status"):
            module.verify_second_runtime_candidate(candidates)


if __name__ == "__main__":
    unittest.main()
