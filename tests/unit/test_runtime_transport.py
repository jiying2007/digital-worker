from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.runtime_transport import TransportBlocked, resolve


ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT / "config/integrations/runtime-transport-profiles.json").read_text(encoding="utf-8"))


class RuntimeTransportTests(unittest.TestCase):
    def test_daily_development_defaults_to_codex_runtime_owned_session(self) -> None:
        architecture = CONFIG["architecture"]
        self.assertEqual(architecture["daily_development_default_runtime"], "codex")
        self.assertEqual(architecture["daily_development_default_transport"], "runtime-owned-session")
        self.assertTrue(architecture["runtime_identity_is_independent_of_transport"])
        self.assertTrue(architecture["credential_material_must_not_be_persisted"])

    def test_codex_runtime_owned_session_needs_no_digital_worker_credential(self) -> None:
        result = resolve(
            CONFIG,
            runtime="codex",
            profile="runtime-owned-session",
            environment="developer-workstation",
            endpoint="",
            credential_present=False,
        )
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["transport_kind"], "runtime-owned")
        self.assertEqual(result["credential_mode"], "runtime-session")
        self.assertFalse(result["r2_github_hosted_eligible"])

    def test_runtime_owned_session_is_blocked_on_ephemeral_github_hosted_runner(self) -> None:
        with self.assertRaisesRegex(TransportBlocked, "not allowed in github-hosted"):
            resolve(
                CONFIG,
                runtime="codex",
                profile="runtime-owned-session",
                environment="github-hosted",
                endpoint="",
                credential_present=False,
            )

    def test_codex_relay_requires_endpoint_and_external_credential(self) -> None:
        with self.assertRaisesRegex(TransportBlocked, "requires a configured endpoint"):
            resolve(CONFIG, runtime="codex", profile="relay", environment="github-hosted", endpoint="", credential_present=True)
        with self.assertRaisesRegex(TransportBlocked, "requires external credential material"):
            resolve(CONFIG, runtime="codex", profile="relay", environment="github-hosted", endpoint="https://relay.example/v1/responses", credential_present=False)
        result = resolve(CONFIG, runtime="codex", profile="relay", environment="github-hosted", endpoint="https://relay.example/v1/responses", credential_present=True)
        self.assertEqual(result["protocol"], "openai-responses-api-compatible")
        self.assertEqual(result["endpoint_class"], "configured-relay")
        self.assertEqual(len(result["endpoint_sha256"]), 64)

    def test_claude_relay_is_transport_only_and_does_not_change_runtime_identity(self) -> None:
        result = resolve(CONFIG, runtime="claude-code", profile="relay", environment="github-hosted", endpoint="https://relay.example/anthropic", credential_present=True)
        self.assertEqual(result["runtime"], "claude-code")
        self.assertEqual(result["runtime_target"], "claude-code")
        self.assertEqual(result["transport_kind"], "relay")
        self.assertEqual(result["protocol"], "anthropic-claude-code-compatible")

    def test_direct_profiles_use_official_default_endpoint(self) -> None:
        result = resolve(CONFIG, runtime="codex", profile="direct", environment="github-hosted", endpoint="", credential_present=True)
        self.assertEqual(result["endpoint_class"], "official-default")
        self.assertIsNone(result["endpoint_sha256"])
        with self.assertRaisesRegex(TransportBlocked, "must not override the official endpoint"):
            resolve(CONFIG, runtime="codex", profile="direct", environment="github-hosted", endpoint="https://relay.example", credential_present=True)

    def test_resolution_never_contains_secret_material(self) -> None:
        result = resolve(CONFIG, runtime="codex", profile="relay", environment="github-hosted", endpoint="https://relay.example/v1/responses", credential_present=True)
        serialized = json.dumps(result, sort_keys=True).lower()
        for forbidden in ("api_key", "secret", "bearer", "credential_value", "token_value"):
            self.assertNotIn(forbidden, serialized)
        self.assertIn("credential_present", result)
        self.assertEqual(len(result["gateway_identity_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
