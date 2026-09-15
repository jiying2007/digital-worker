---
id: device-evidence-check
version: 1.0.0
owner_kind: assurance
owner: verification
max_action_level: A2_GENERATE
inputs: [device-identity, firmware-identity, test-procedure, raw-evidence]
outputs: [verification-evidence]
---
# Device Evidence Check

Verify target-device evidence against the exact board/device/firmware/environment and claimed Acceptance Criterion.

## Method
1. Confirm device/board revision and firmware/artifact identity.
2. Check environment, precondition, steps and expected result.
3. Preserve raw logs/measurements and collection context.
4. Separate one-device smoke from broader HIL/soak/release claims.

## Evidence
Use device identity, firmware hash/version, procedure, logs/measurements, timestamps and test-run identity.

## BLOCK
BLOCK Device PASS when evidence comes from another board/version, raw evidence is absent, or the observed result cannot be tied to the claimed object.
