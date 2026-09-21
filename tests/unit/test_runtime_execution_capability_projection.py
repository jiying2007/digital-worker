from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = ROOT / "config/integrations/runtime-execution-profiles.json"
CAPABILITY_PATH = ROOT / "config/integrations/provider-capability-matrix.yaml"


class RuntimeExecutionCapabilityProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        self.capability = yaml.safe_load(CAPABILITY_PATH.read_text(encoding="utf-8"))

    def test_default_development_profile_projects_native_codex_cli(self) -> None:
        profiles = self.registry["profiles"]
        runtime = self.capability["roles"]["runtime_binding"]
        projection = runtime["execution_profiles"]
        codex = runtime["candidates"]["codex"]

        self.assertEqual(self.registry["default_development_profile"], "codex-cli-native")
        self.assertEqual(projection["identity_ref"], "config/integrations/runtime-execution-profiles.json")
        self.assertEqual(projection["default_development_profile"], self.registry["default_development_profile"])
        self.assertEqual(projection["default_development_runtime"], profiles["codex-cli-native"]["runtime"])
        self.assertEqual(projection["credential_ownership"], "runtime-or-executor")
        self.assertTrue(projection["runtime_identity_independent_from_transport"])
        self.assertEqual(codex["capabilities"]["native_cli_execution"], "native-default-development-path")
        self.assertEqual(codex["capabilities"]["runtime_managed_auth_session"], "native")
        self.assertEqual(codex["capabilities"]["transport_auth_decoupling"], "provider-neutral-profile")

    def test_controlled_r2_profiles_use_runtime_owned_local_cli(self) -> None:
        profiles = self.registry["profiles"]
        controlled = self.capability["roles"]["runtime_binding"]["execution_profiles"]["controlled_r2_profiles"]
        expected = {
            "codex": "codex-cli-native",
            "claude_code": "claude-cli-native",
        }
        self.assertEqual(controlled, expected)
        self.assertEqual(set(profiles), {"codex-cli-native", "claude-cli-native"})
        self.assertEqual(profiles[controlled["codex"]]["runtime"], "codex")
        self.assertEqual(profiles[controlled["claude_code"]]["runtime"], "claude-code")
        for profile_name in controlled.values():
            profile = profiles[profile_name]
            self.assertEqual(profile["executor"], "native-cli")
            self.assertEqual(profile["credential_mode"], "runtime-managed-session")
            self.assertIn("controlled-r2", profile["intended_scope"])
            self.assertEqual(profile["source_set_binding"], "required")
            self.assertFalse(profile["verification_authority"])
        self.assertTrue(self.registry["rules"]["r2_provider_execution_must_use_runtime_owned_local_terminal"])

    def test_transport_contract_remains_provider_neutral(self) -> None:
        registry_text = PROFILE_PATH.read_text(encoding="utf-8")
        capability_text = CAPABILITY_PATH.read_text(encoding="utf-8")
        for forbidden in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
            self.assertNotIn(forbidden, registry_text)
            self.assertNotIn(forbidden, capability_text)
        rules = self.registry["rules"]
        self.assertTrue(rules["runtime_identity_is_independent_from_transport"])
        self.assertTrue(rules["credential_material_must_not_enter_execution_receipts"])
        self.assertTrue(rules["native_cli_may_reuse_existing_authenticated_runtime_session"])
        self.assertTrue(rules["relay_or_gateway_must_not_change_declared_runtime_identity"])


if __name__ == "__main__":
    unittest.main()
