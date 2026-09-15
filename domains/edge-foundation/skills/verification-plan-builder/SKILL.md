---
id: verification-plan-builder
version: 1.0.0
owner_kind: assurance
owner: verification
max_action_level: A2_GENERATE
inputs: [acceptance-criteria, engineering-scope, risk-context]
outputs: [verification-plan]
---
# Verification Plan Builder

Map each Acceptance Criterion to the minimum sufficient verification layer and direct evidence before implementation results are interpreted.

## Method
1. Define criterion, object identity and required verification layer.
2. Specify preconditions, steps/observation method, expected result and failure handling.
3. Record evidence identity and regression scope.
4. Do not downgrade a required layer after failure merely to improve completion rate.

## Evidence
The plan must preserve source/artifact/device/test identities and the evidence location expected for each criterion.

## BLOCK
BLOCK a PASS-capable plan when Acceptance is ambiguous, required layer is undefined or the target identity cannot be fixed.
