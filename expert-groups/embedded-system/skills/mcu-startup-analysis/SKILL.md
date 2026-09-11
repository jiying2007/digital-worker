---
id: mcu-startup-analysis
version: 0.3.0
owner: mcu-rtos-expert
max_action_level: A2_GENERATE
inputs: [startup-source, linker-config, reset-evidence]
outputs: [technical-analysis]
---
# MCU Startup Analysis

Trace reset vector, stack/data/BSS init, clock setup, vector table, C runtime and application entry.

Check bootloader/application boundaries and relocation assumptions. Report the first unproven transition. Do not claim startup correctness from a successful build alone.
