# Acceptance → Evidence Matrix

Run: `FEATURE-PCR02-OTA-001`

| Acceptance criterion | Evidence | Result |
|---|---|---|
| Manifest binds PCR02 v1.1.21 package path, size, SHA-256 and source identity | `ota-manifest.v1.json`; package SHA-256 `7687d805...a4bb`; source base `eeb926bd...` | PASS |
| Verifier fails closed on malformed/conflicting identity | `tests/test_verify_ota_manifest.py`; PR CI `34861966225` | PASS |
| Hosted CI verifies the real 76,778,472-byte package | fresh-main `34862064742`; retained receipt run `34862735035` | PASS |
| Verification receipt is retained and re-readable | artifact `10355541476`; archive SHA-256 `5da3d994...c3ab7a` | PASS |
| Scope does not overclaim device/release readiness | Verification report lists device/HIL/release as not applicable and preserves unverified device OTA work | PASS |

Current-stage review policy: Independent Review was attempted but unavailable. Static checks + Hosted CI + traceable Verification are used as the permitted iterative-Pilot substitute. This does **not** mean Independent Review PASS and does **not** authorize release.
