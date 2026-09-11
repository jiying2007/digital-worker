---
id: device-tree-review
version: 0.3.0
owner: linux-bsp-expert
max_action_level: A2_GENERATE
inputs: [device-tree, schematic, driver-source]
outputs: [technical-analysis]
---
# Device Tree Review

Review compatible strings, resources, interrupts, clocks, resets, pinctrl, regulators, DMA and dependency ordering against schematic/TRM/driver expectations.

Flag unverifiable hardware facts. A syntactically valid DTS is not proof that addresses, polarity or wiring are correct.
