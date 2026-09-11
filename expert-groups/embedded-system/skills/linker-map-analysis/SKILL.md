---
id: linker-map-analysis
version: 0.3.0
owner: mcu-rtos-expert
max_action_level: A2_GENERATE
inputs: [linker-script, map-file]
outputs: [technical-analysis]
---
# Linker Map Analysis

Analyze ROM/RAM placement, section growth, heap/stack reservations, alignment, overlays and bootloader/application boundaries.

Quantify remaining capacity from the actual map, not source estimates. Flag orphan sections, overlap risk and unexpected library growth. Keep ROM, RAM and runtime stack claims separate.
