---
id: architecture-impact-analysis
version: 1.0.0
owner_kind: capability
owner: embedded.architecture
max_action_level: A2_GENERATE
inputs: [task-charter, evidence-ref-set]
outputs: [technical-analysis]
---
# Architecture Impact Analysis

## Purpose
Assess how a proposed or observed change affects system boundaries, interfaces, resources, lifecycle, failure containment, compatibility and required verification.

## Use When
- Feature/architecture changes crossing modules, boot/runtime boundaries or resource budgets.
- Performance, power, OTA/recovery or portability changes with system-level consequences.
- When implementation options must be compared before engineering handoff.

## Do Not Use For
- Detailed root-cause debugging when no architectural consequence has been established.
- Declaring implementation correctness or release readiness.
- Designing from assumptions before affected contracts and object identities are known.

## Required Inputs
- Task charter with scope/non-goals and Acceptance.
- Evidence references for the current system/change where available.
- Known architecture/interface/resource constraints relevant to the change.

## Optional Inputs
- Baseline resource/timing/power measurements.
- Existing ADRs, interface contracts and failure/recovery requirements.
- Migration/rollback constraints.

## Method
1. Identify affected responsibilities, layers, interfaces and lifecycle states before selecting an implementation.
2. Separate observed current-state facts from inferred impact and open assumptions.
3. Trace impacts to memory/CPU/timing/power/storage/concurrency, fault containment, API/ABI and compatibility as applicable.
4. Compare feasible options, trade-offs, rollback/migration implications and failure behavior.
5. Map each material impact to a Verification need or explicit unresolved evidence gap.

## Outputs
- Technical analysis with affected contracts/layers and change surface.
- Option/trade-off and risk analysis with unresolved assumptions.
- Verification implications and cross-capability handoff triggers.

## Evidence Rules
- Observed facts require direct source/config/measurement evidence.
- Impact may be inferred only when assumptions and dependency chain are explicit.
- A successful local build is not evidence that system-level timing, power, compatibility or recovery is safe.

## BLOCK Conditions
- Affected system boundary or responsibility cannot be identified.
- Critical source/interface/resource facts are missing or contradictory.
- The requested recommendation would depend on an unstated product or safety assumption.

## Verification / Review Handoff
- Architecture provides impact/contract analysis; implementation remains with the responsible engineering Capability/Runtime.
- Verification independently proves Acceptance at the required layers.
- Independent Review may challenge risk/trade-offs but does not replace architecture evidence.

## Evaluation
- Positive case: a bounded feature change produces explicit impact, risks and Verification plan inputs.
- Negative case: missing interface/resource facts force a block rather than a confident design.
- Cross-boundary case: evidence triggers the correct Hardware/other Capability escalation.

## Known Limits / Change Notes
- This Skill does not establish target-device behavior without target evidence.
- Version 1.0.0 hardens the definition only; architecture ownership and action ceiling are unchanged.
