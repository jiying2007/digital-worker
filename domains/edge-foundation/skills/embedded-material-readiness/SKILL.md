---
id: embedded-material-readiness
version: 1.0.0
owner_kind: role
owner: edge-coordination
max_action_level: A2_GENERATE
inputs: [task-brief, supplied-materials]
outputs: [engineering-material-manifest]
---
# Embedded Material Readiness

## Purpose
Determine whether the exact source, artifact, hardware, evidence and test context required by the selected workflow are sufficiently identified to start or complete engineering work.

## Use When
- After routing and before engineering execution.
- Whenever new material changes the identity or validity of the working set.
- Before completion or governance escalation when terminal material requirements must be re-checked.

## Do Not Use For
- Filling missing materials with assumptions or another product/version.
- Judging technical correctness of the supplied source or evidence.
- Treating a file's existence as proof that it is current, authoritative or bound to the target object.

## Required Inputs
- Task brief and selected workflow/task type.
- Supplied material inventory with source/location.
- Exact source/artifact/device identity required by `runtime/material-requirements.yaml` for the task.

## Optional Inputs
- Authority/freshness metadata from knowledge sources.
- Hashes, timestamps, collection/run IDs and prior manifests.
- Approved degradation or scope-exemption record.

## Method
1. Load the material requirements for the selected workflow.
2. For every required item, record status as available, missing, stale, conflicting or not-applicable.
3. Bind available materials to exact source/version/object identity and evidence reference.
4. Identify critical gaps that prevent engineering or terminal completion.
5. If policy permits degradation, record the approval, residual limitation and affected claims explicitly; otherwise remain BLOCKED.

## Outputs
- Engineering material manifest with status and identity for each required item.
- Explicit critical gaps, conflicts and stale inputs.
- Approved degradation metadata when applicable; never an implicit downgrade.

## Evidence Rules
- Availability requires traceable identity, not a filename or prose assertion.
- A log from a different firmware/device is not target evidence.
- Conflicting authoritative sources must remain visible until resolved.

## BLOCK Conditions
- A critical required material is missing, stale, conflicting or unidentifiable.
- Source/device/artifact/test identity cannot be bound to the requested object.
- A degradation path is needed but has not been explicitly approved.

## Verification / Review Handoff
- Coordination passes the manifest and gaps to Engineering; it does not decide the technical meaning of materials.
- Verification re-checks material identity relevant to Acceptance and cannot rely solely on the readiness label.
- Completion must satisfy terminal material policy independently of an earlier intake decision.

## Evaluation
- Positive case: all required identities are present and manifest is READY.
- Negative case: exact source/device identity is absent and the run remains BLOCKED.
- Degraded case: only an explicitly approved, scope-bounded degradation is accepted.

## Known Limits / Change Notes
- Readiness is about material sufficiency/identity, not engineering correctness.
- Version 1.0.0 hardens definition semantics without changing material policy or action ceiling.
