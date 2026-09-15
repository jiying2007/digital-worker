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

Analyze reset/vector/clock/C-runtime/startup ordering through scheduler or main-loop entry.

## Method
1. Bind conclusions to exact firmware, MCU and board identity.
2. Trace reset source, vector table, stack, clock, .data/.bss, runtime init, HAL/BSP and scheduler/main entry.
3. Separate observed startup facts from inferred failure causes.
4. Identify the last confirmed stage and the next discriminating observation.

## Evidence
Prefer startup/vector source, linker script, map/ELF, reset reason, trace/log and target-device observation.

## BLOCK
BLOCK high-confidence conclusions when firmware identity, reset context or startup/linker inputs are inconsistent or missing.
