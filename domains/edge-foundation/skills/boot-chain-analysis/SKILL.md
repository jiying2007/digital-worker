---
id: boot-chain-analysis
version: 1.0.0
owner_kind: capability
owner: embedded.linux-bsp
max_action_level: A2_GENERATE
inputs: [boot-materials, logs, source-evidence]
outputs: [technical-analysis]
---
# Boot Chain Analysis

## Purpose
Trace the exact target boot chain from reset through bootloaders, kernel and rootfs/userspace to identify the last confirmed stage, violated handoff or next discriminating observation.

## Use When
- Boot failure, boot loop, early reset, kernel handoff or rootfs mount issues.
- BSP porting or image/partition changes that alter startup.
- Boot-time regressions requiring stage-by-stage evidence.

## Do Not Use For
- Using logs from another firmware/board as proof for the target.
- Treating the final visible error as the root cause without earlier-stage evidence.
- Executing destructive recovery/flash changes without the separate required authorization.

## Required Inputs
- Exact firmware/image and board/device identity.
- Relevant boot log or direct observation.
- Boot configuration/source evidence sufficient to map expected stages.

## Optional Inputs
- Partition table, load addresses, command line, DTB, kernel config and image hashes.
- Reset reason, power/clock traces and prior-good baseline.
- Boot timing measurements.

## Method
1. Freeze target image, board revision and boot configuration identity.
2. Map expected stages such as BootROM/SPL/U-Boot/kernel/rootfs (or platform equivalent) and their handoff contracts.
3. Correlate partition/load addresses, reset/clock state, command line/DT and logs to each stage.
4. Identify the last directly confirmed stage and first missing/abnormal transition.
5. Generate the smallest next observation/experiment that distinguishes leading hypotheses.

## Outputs
- Stage-by-stage technical analysis with confirmed/unknown transitions.
- Relevant image/partition/config identity and evidence links.
- Next discriminating observation plus unresolved evidence gaps.

## Evidence Rules
- A stage is confirmed only by evidence bound to the exact target build/device.
- Absence of a log line is not automatically proof that the previous stage failed.
- Generic boot knowledge may guide hypotheses but cannot replace target evidence.

## BLOCK Conditions
- Firmware/board identity is mismatched or unknown.
- Critical stage/config/partition evidence is missing and a root-cause claim would require guessing.
- Requested recovery would exceed the Skill's A2_GENERATE action ceiling.

## Verification / Review Handoff
- Linux/BSP owns boot analysis; Hardware is engaged when electrical/reset/power evidence triggers cross-domain escalation.
- Engineering implementation is handed off separately from this analysis.
- Verification must reproduce startup/boot Acceptance on the required target layer.

## Evaluation
- Positive case: exact logs locate a last-confirmed stage and discriminating next step.
- Negative case: another board/build's boot log is rejected as target proof.
- Recovery case: destructive action remains blocked while non-destructive evidence collection proceeds.

## Known Limits / Change Notes
- This Skill does not authorize flashing, release or destructive recovery.
- Version 1.0.0 hardens reviewability; boot routing/action policy is unchanged.
