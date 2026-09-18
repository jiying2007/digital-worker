---
id: linker-map-analysis
version: 1.0.0
owner_kind: capability
owner: embedded.mcu-rtos
max_action_level: A2_GENERATE
inputs: [linker-script, map-file, elf, memory-layout]
outputs: [technical-analysis]
---
# Linker Map Analysis

## Purpose
Quantify exact ROM/RAM/section placement and configured-vs-linked-vs-runtime memory use from linker script, MAP and ELF rather than binary-size estimates.

## Use When
- ROM/RAM overflow, unexpected section placement or memory budget review.
- MCU/RTOS porting or feature growth requiring exact memory accounting.
- Crash/startup analysis where stack, vector or section addresses matter.

## Do Not Use For
- Estimating runtime peak solely from linked size.
- Using MAP/ELF from a different build.
- Concluding heap/stack safety without runtime high-water evidence when it is required.

## Required Inputs
- Exact linker script, MAP and ELF from the target build.
- Target memory layout/regions.
- Build identity tying all artifacts together.

## Optional Inputs
- `size`/`nm`/`readelf` outputs and symbol reports.
- Stack/heap watermark and RTOS task stack data.
- Reserved bootloader/OTA/calibration region definitions.

## Method
1. Verify MAP/ELF/linker script belong to the same exact firmware build.
2. Enumerate memory regions, section load/run addresses, alignment and reserved ranges.
3. Identify large symbols, orphan/unexpected sections and region overflows/margins.
4. Account separately for linked allocation, configured heap/stack/reserved regions and measured runtime high-water.
5. Relate findings to memory budget, startup placement and regression risk.

## Outputs
- Quantified memory-layout technical analysis with region/section/symbol accounting.
- Explicit remaining ROM/RAM margins and unmeasured runtime components.
- Inputs for regression and target runtime verification.

## Evidence Rules
- MAP/ELF prove linked placement for one exact build.
- Configured stack/heap size is not evidence of runtime peak use.
- Runtime safety claims require watermark/trace or other direct runtime evidence when relevant.

## BLOCK Conditions
- Artifact build identity is unknown/mismatched.
- Target memory map does not correspond to the MCU/firmware under review.
- A runtime high-water claim is requested without runtime evidence.

## Verification / Review Handoff
- MCU/RTOS owns linked-memory analysis; architecture consumes budget impacts.
- Engineering may change linker/config/source separately.
- Verification checks build identity and runtime margins where Acceptance requires them.

## Evaluation
- Positive case: exact MAP/ELF explains a RAM/ROM budget delta.
- Negative case: binary-size guess cannot replace section/symbol accounting.
- Runtime case: linked free memory is not mislabeled as proven stack/heap headroom.

## Known Limits / Change Notes
- Dynamic fragmentation and runtime corruption require additional runtime evidence/Skills.
- Version 1.0.0 is definition hardening only.
