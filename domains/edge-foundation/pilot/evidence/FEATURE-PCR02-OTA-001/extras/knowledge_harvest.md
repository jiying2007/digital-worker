# Knowledge Harvest

Run: `FEATURE-PCR02-OTA-001`

## Result

Evidence-backed reusable pattern:

- Treat OTA package identity as a contract over product/version/path/byte-size/SHA-256/source identity.
- Reject path traversal, malformed manifest structure, duplicate checksum entries, byte-size mismatch and SHA mismatch fail-closed.
- Retain a machine-readable verification receipt with an archive digest.
- Never extrapolate Hosted CI artifact-identity PASS to device install/boot/rollback or release readiness.

Authority remains with the source repository and its immutable commits/artifacts; this document is only a harvest summary.

## Review availability note

Independent Review was requested through available tooling but produced no review submission. Under the iterative-Pilot policy, static checks + Hosted CI + Verification evidence are accepted as the substitute; no Independent Review PASS or release approval is claimed.
