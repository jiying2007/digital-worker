---
id: mcu-startup-analysis
version: 1.0.0
owner_kind: capability
owner: embedded.mcu-rtos
max_action_level: A2_GENERATE
inputs: [firmware-source, startup-vector, linker-map, device-evidence]
outputs: [technical-analysis]
---
# MCU Startup Analysis

## Purpose
Trace reset, vector, stack, clock, C runtime and platform initialization through scheduler or main-loop entry for the exact MCU firmware and board.

## Use When
- MCU fails before normal application behavior, resets during initialization or starts inconsistently.
- Bootloader-to-application handoff/startup changes.
- MCU/SDK/toolchain porting that changes vector, linker or init order.

## Do Not Use For
- General runtime crash diagnosis after startup has completed.
- Assuming reset reason, clock state or vector placement from another build.
- Treating debugger attachment behavior as equivalent to cold-boot device behavior.

## Required Inputs
- Exact MCU/board and firmware build identity.
- Startup/vector and linker inputs for the build.
- Target-device reset/startup evidence sufficient to locate progress.

## Optional Inputs
- Reset-reason registers, clock/power trace and bootloader handoff data.
- ELF/MAP, debugger trace and GPIO/timestamp instrumentation.
- Known-good firmware baseline.

## Method
1. Bind all conclusions to exact MCU, board, firmware and build artifacts.
2. Trace reset source, vector table and initial stack before clock/runtime initialization.
3. Trace `.data` copy, `.bss` zeroing, C/C++ runtime, HAL/BSP init and scheduler/main entry.
4. Check bootloader handoff, VTOR/vector relocation and reset/clock assumptions where applicable.
5. Identify the last confirmed startup stage and the smallest next observation that distinguishes hypotheses.

## Outputs
- Stage-by-stage startup technical analysis.
- Exact startup/linker/build identity and unresolved gaps.
- Next discriminating capture and affected Verification scenarios.

## Evidence Rules
- Startup source/linker files show intended behavior; target observation proves actual progress.
- A debugger-assisted start is not automatically evidence for standalone reset behavior.
- Reset-reason claims require target register/log evidence tied to the event.

## BLOCK Conditions
- Firmware/MCU/board identity is unknown or inconsistent.
- Startup/vector/linker inputs do not correspond to the observed build.
- Critical reset/startup context is missing for the requested confirmed conclusion.

## Verification / Review Handoff
- MCU/RTOS owns startup analysis; Hardware is engaged for unresolved power/reset/clock facts.
- Engineering changes are implemented separately.
- Verification repeats required reset/boot paths on the exact target.

## Evaluation
- Positive case: exact evidence locates failure before scheduler/main entry.
- Negative case: mismatched ELF/startup source blocks confirmed diagnosis.
- Bootloader case: handoff assumptions are explicitly checked rather than inferred.

## Known Limits / Change Notes
- This Skill stops at normal runtime entry; later crashes/concurrency use dedicated Skills.
- Version 1.0.0 expands contract detail only.
