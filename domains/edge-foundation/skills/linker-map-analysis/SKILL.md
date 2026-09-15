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

Quantify ROM/RAM/section placement from linker script, MAP and ELF instead of binary-size guesses.

## Method
1. Bind MAP/ELF to the exact firmware build.
2. Inspect memory regions, section placement, load/run addresses, large symbols and orphan sections.
3. Account for stack/heap/reserved memory and alignment overhead.
4. Distinguish configured budget, linked allocation and runtime high-water evidence.

## Evidence
Use linker script, MAP/ELF, size/nm/readelf output and measured stack/heap watermark when available.

## BLOCK
BLOCK verified memory conclusions when MAP/ELF identity is unknown or memory regions do not match the target MCU/firmware.
