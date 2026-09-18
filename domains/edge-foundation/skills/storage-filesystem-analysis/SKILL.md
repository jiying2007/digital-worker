---
id: storage-filesystem-analysis
version: 1.0.0
owner_kind: capability
owner: embedded.linux-bsp
max_action_level: A2_GENERATE
inputs: [storage-identity, logs, source-evidence]
outputs: [technical-analysis]
---
# Storage Filesystem Analysis

## Purpose
Analyze storage failures across media/ECC, controller/driver, MTD, UBI, filesystem and application workload while preserving power-loss/reset/concurrency context and evidence provenance.

## Use When
- Read-only remount, I/O/ECC/erase/write failures, UBI/UBIFS corruption or mount issues.
- NAND/NOR/eMMC storage reliability incidents and long-run degradation.
- Storage changes where lower-layer media/controller behavior must be separated from filesystem symptoms.

## Do Not Use For
- Treating the final filesystem error as root cause.
- Performing destructive repair/erase/reformat under an A2 analysis Skill.
- Using a successful remount/reboot as proof that integrity or media health is restored.

## Required Inputs
- Exact storage/media/controller/device identity.
- Raw logs or direct observations tied to the target run.
- Relevant source/config evidence for storage stack and partition/layout.

## Optional Inputs
- ECC/bad-block counters, raw MTD/UBI diagnostics and wear information.
- Workload/concurrency/reset/power-loss timeline.
- Known-good baseline and flash vendor/TRM data.

## Method
1. Freeze device, firmware/kernel/config, media and partition identity.
2. Build a time-ordered chain from application write/load through filesystem, UBI, MTD, controller and media/ECC evidence.
3. Preserve read/write/erase/ECC/bad-block status and identify the earliest abnormal layer rather than the loudest final error.
4. Correlate workload, concurrency, reset/power-loss and recovery attempts with the event.
5. Collect non-destructive evidence first and propose the next discriminating observation before any destructive recovery.

## Outputs
- Layered technical analysis separating symptom, earliest abnormal evidence and hypotheses.
- Storage identity, partition/config context and evidence gaps.
- Non-destructive next-step plan and Verification implications.

## Evidence Rules
- Filesystem read-only state is an observed symptom, not by itself a root cause.
- Corrected/uncorrectable ECC and bad-block claims require exact controller/media evidence.
- Recovery success does not prove absence of latent corruption or media failure.

## BLOCK Conditions
- Lower-layer evidence needed for a causal claim is missing.
- Storage/media/partition identity is ambiguous or mismatched.
- Requested recovery is destructive or exceeds the A2_GENERATE ceiling without separate authorization.

## Verification / Review Handoff
- Linux/BSP owns storage-stack analysis; driver/hardware owners are engaged when controller/media evidence requires it.
- Engineering fixes are separate from diagnostic evidence collection.
- Verification must test the same affected storage paths and required power-loss/long-run scenarios.

## Evaluation
- Positive case: UBIFS symptom is traced through exact UBI/MTD/media evidence.
- Negative case: read-only remount alone is not accepted as confirmed root cause.
- Safety case: destructive repair remains blocked while diagnostic evidence is preserved.

## Known Limits / Change Notes
- Deep vendor-specific ECC/controller behavior may require dedicated evidence or a future evidence-backed Skill split.
- Version 1.0.0 hardens definition without changing canonical scope/action.
