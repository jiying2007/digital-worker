---
id: hil-evidence-check
version: 1.0.0
owner_kind: assurance
owner: verification
max_action_level: A2_GENERATE
inputs: [hil-case, fixture-environment, target-identity, run-artifacts]
outputs: [verification-evidence]
---
# HIL Evidence Check

## Purpose
Verify that HIL evidence is bound to the exact case, fixture/environment, target identity and run, and limit the verdict to scenarios actually exercised.

## Use When
- Acceptance explicitly requires hardware-in-the-loop behavior.
- Automated fixture scenarios cover power/reset/peripheral/fault interactions.
- Release/Pilot evidence requires repeatable hardware scenarios rather than one manual smoke test.

## Do Not Use For
- Accepting a reusable report summary without raw run provenance.
- Calling a scenario HIL when fixture/target identity is not controlled.
- Generalizing one HIL case to unexecuted conditions.

## Required Inputs
- Versioned HIL case definition.
- Fixture/environment identity.
- Exact target/firmware identity and run artifacts.

## Optional Inputs
- Calibration/status of fixture instrumentation.
- Run ID, timestamps, automation revision and hashes.
- Repeated-run statistics and failure captures.

## Method
1. Bind case/version, fixture/environment, target and firmware artifact.
2. Verify that the intended case steps and fault/interaction scenario actually executed.
3. Inspect raw run artifacts/logs and provenance.
4. Compare expected vs observed outcome including failure handling and recovery.
5. Issue a verdict only for the exact scenario/range/duration exercised and record uncovered conditions.

## Outputs
- HIL-layer verification evidence with case/fixture/target/run identity.
- Scenario-specific status and raw artifact references.
- Explicit uncovered conditions and follow-up requirements.

## Evidence Rules
- A HIL summary must trace to raw run artifacts and exact case version.
- Fixture identity/calibration matters when measurements or injected conditions depend on it.
- Repeated success supports only the tested distribution/scenario, not arbitrary release conditions.

## BLOCK Conditions
- Only an untraceable summary exists.
- Fixture/target/case/run identity is unclear or mismatched.
- The executed case does not exercise the Acceptance scenario being claimed.

## Verification / Review Handoff
- Verification owns HIL verdicts independently.
- Engineering may maintain test hooks but cannot self-sign the result.
- Review consumes HIL scope and residual risks without broadening the evidence.

## Evaluation
- Positive case: exact case/fixture/target/run provides traceable scenario evidence.
- Negative case: summary-only report is blocked.
- Coverage case: unexecuted power-loss/recovery scenario remains explicitly unverified.

## Known Limits / Change Notes
- HIL quality depends on fixture fidelity and case design; it is not automatically equivalent to field behavior.
- Version 1.0.0 adds explicit review boundaries only.
