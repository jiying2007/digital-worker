---
id: device-tree-review
version: 1.0.0
owner_kind: capability
owner: embedded.linux-bsp
max_action_level: A2_GENERATE
inputs: [dts-dtb, board-identity, driver-evidence]
outputs: [technical-analysis]
---
# Device Tree Review

Review Device Tree resources and driver binding against the exact board/platform identity.

## Method
Check compatible, reg/irq/gpio, clocks/resets/regulators, pinctrl, aliases, reserved memory, dependency/defer behavior and revision-specific differences; correlate each resource with driver expectations.

## Block
Do not reuse another board revision's DT assumptions. Unknown electrical/resource facts must be escalated for direct evidence.
