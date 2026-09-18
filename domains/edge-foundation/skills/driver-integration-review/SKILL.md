---
id: driver-integration-review
version: 1.0.0
owner_kind: capability
owner: embedded.driver-component
max_action_level: A2_GENERATE
inputs: [device-identity, bus-protocol, platform-resources, driver-source]
outputs: [technical-analysis]
---
# Driver Integration Review

## Purpose
Review a device integration from hardware/bus contract through driver lifecycle, concurrency, power/error recovery and stable API/compatibility behavior.

## Use When
- New peripheral/driver integration or BSP migration.
- Component reuse and device substitution/second-source qualification.
- Failures involving probe/init, IRQ/DMA, suspend/resume, retry/recovery or API compatibility.

## Do Not Use For
- Declaring drop-in compatibility from pinout/register similarity alone.
- Replacing Hardware evidence when electrical/power/timing facts are uncertain.
- Self-signing target-device Verification.

## Required Inputs
- Exact device/board identity and revision.
- Authoritative bus/protocol/device contract.
- Platform resources and exact driver source under review.

## Optional Inputs
- Datasheet/TRM/schematic and known-good implementation.
- Target logs, bus traces and failure captures.
- Production calibration/test requirements and compatibility matrix.

## Method
1. Confirm device/board/resource identity and protocol/electrical assumptions.
2. Trace probe/init/open/use/close/deinit plus IRQ/DMA/thread context and resource lifetime.
3. Review timeout/retry/error recovery and degraded/fault states.
4. Review suspend/resume/power sequencing and reset/recovery interactions.
5. Check API/ABI/versioning, diagnostics, portability and rollback; for substitutions maintain a normal/error/power compatibility matrix.

## Outputs
- Technical integration analysis with lifecycle/resource/error findings.
- Compatibility matrix and explicit unknowns for substitutions.
- Required device/regression tests and cross-domain escalations.

## Evidence Rules
- Datasheet/TRM/schematic establish intended contracts; target traces establish actual behavior.
- Happy-path initialization does not prove error, power or recovery correctness.
- Compatibility claims require evidence for the dimensions claimed, not component-name similarity.

## BLOCK Conditions
- Device/board/platform-resource identity is missing.
- Electrical/power facts required for the claim are unresolved.
- Failure/power/recovery evidence is absent for a reusable/substitution claim that depends on it.

## Verification / Review Handoff
- Driver/Component owns integration contract; Linux/BSP or MCU/RTOS assists for platform-specific execution, Hardware for electrical uncertainty.
- Engineering changes are separate from Assurance.
- Verification independently checks normal, failure, power and regression paths required by Acceptance.

## Evaluation
- Positive case: exact device integration covers lifecycle and recovery, not only probe success.
- Negative case: pin-compatible substitute is not declared compatible without matrix evidence.
- Cross-domain case: uncertain electrical behavior escalates instead of being guessed in software.

## Known Limits / Change Notes
- Highly specialized calibration/production qualification may become a future Skill only after repeated real evidence.
- Version 1.0.0 hardens the contract without expanding runtime authority.
