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

## Purpose
Verify that target-device evidence belongs to the exact board/device/firmware/environment and directly supports the claimed Acceptance Criterion.

## Use When
- Acceptance requires real target behavior beyond build/static evidence.
- Checking boot, functional, performance, power or recovery behavior on a specific device.
- Validating a product Pilot result tied to exact hardware/firmware.

## Do Not Use For
- Treating evidence from another board/firmware as equivalent.
- Promoting one-device smoke to HIL/soak/release qualification.
- Accepting a prose verdict when required raw evidence is absent.

## Required Inputs
- Exact device/board revision identity.
- Exact firmware/artifact identity.
- Test procedure and raw evidence for the claimed criterion.

## Optional Inputs
- Environment/fixture identity and calibration status.
- Timestamp/run/operator/automation identity.
- Prior-good device baseline and artifact hashes.

## Method
1. Bind device/board revision, firmware artifact and environment to the run.
2. Check preconditions, procedure and expected result against the Acceptance criterion.
3. Inspect raw logs/measurements and collection provenance rather than only the summary verdict.
4. Determine whether the observation directly proves, disproves or leaves the criterion unverified.
5. Limit the conclusion to the device(s), scenario and duration actually exercised.

## Outputs
- Device-layer verification evidence with exact identities.
- PASS/FAIL/BLOCK or equivalent criterion status supported by raw evidence.
- Explicit scope limits and remaining HIL/soak/release requirements.

## Evidence Rules
- Raw observation must be tied to exact run/object identity.
- One target device can prove only the scoped device criterion, not fleet/release reliability.
- A version string alone is insufficient if artifact identity matters to Acceptance.

## BLOCK Conditions
- Evidence comes from a different/unknown board or firmware.
- Raw evidence or procedure needed for the criterion is absent.
- Observed result cannot be tied to the exact Acceptance object.

## Verification / Review Handoff
- Verification owns the device-layer verdict independently from Engineering.
- Engineering can prepare firmware/test hooks but cannot approve its own evidence.
- HIL/Review consume this evidence within its declared scope and cannot broaden it without new evidence.

## Evaluation
- Positive case: exact device+firmware+procedure yields traceable evidence.
- Negative case: another board/version's log is rejected.
- Scope case: device smoke remains distinct from HIL/soak/release qualification.

## Known Limits / Change Notes
- Statistical fleet reliability and broad environment coverage require additional test design/evidence.
- Version 1.0.0 hardens identity/scope rules only.
