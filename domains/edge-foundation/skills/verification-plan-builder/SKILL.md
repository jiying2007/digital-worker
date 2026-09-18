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

## Purpose
Translate each Acceptance Criterion into the minimum sufficient independent verification layer, object identity, procedure and direct evidence requirement before implementation results are interpreted.

## Use When
- Before or during Engineering when Acceptance must be made testable.
- When a change spans build/static/device/HIL/release layers.
- When risk or scope changes require re-planning Verification.

## Do Not Use For
- Downgrading the required layer after a failure to obtain a PASS.
- Using Engineering self-report as independent Verification.
- Inventing Acceptance or target identity that the work item did not define.

## Required Inputs
- Acceptance criteria with unambiguous expected outcomes.
- Engineering scope/change object.
- Risk context sufficient to determine required Verification layer.

## Optional Inputs
- Architecture impact and regression-scope analysis.
- Known failure modes and prior Verification evidence.
- Device/HIL fixture availability and release constraints.

## Method
1. Decompose Acceptance into individually verifiable criteria and bind each to the exact object identity.
2. Select the minimum sufficient layer: build/static/SIL/device/HIL/release or a justified combination.
3. Define preconditions, procedure/observation method, expected result and failure disposition.
4. Specify the raw evidence identity/location required for each criterion and relevant regression coverage.
5. Record unavailable required layers as blockers/risks; never silently substitute a weaker layer.

## Outputs
- Verification plan mapping every Acceptance criterion to layer, procedure and evidence.
- Explicit target/source/artifact/device identities.
- Unverified items, blockers and required regression scope.

## Evidence Rules
- A plan defines required evidence; it is not itself evidence of PASS.
- Engineering logs may be inputs but do not become independent Verification by relabeling.
- Layer adequacy must match the claim: build evidence cannot prove target-device behavior.

## BLOCK Conditions
- Acceptance is ambiguous or not testable.
- The required verification layer cannot be identified.
- Target/source/artifact identity needed for PASS cannot be fixed.

## Verification / Review Handoff
- Verification owns the plan independently of Engineering implementation.
- Engineering may provide test hooks/materials but cannot approve its own result.
- Review consumes Verification status without rewriting failed or unverified criteria.

## Evaluation
- Positive case: every Acceptance row maps to an adequate evidence layer.
- Negative case: device behavior cannot be downgraded to build-only evidence.
- Ambiguity case: unclear Acceptance blocks PASS-capable planning.

## Known Limits / Change Notes
- This Skill plans Verification; execution/evidence checks are handled by the corresponding Assurance Skills.
- Version 1.0.0 strengthens the contract without changing Assurance authority.
