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

Trace BootROM/SPL/U-Boot/kernel/rootfs or platform-equivalent startup from reset to userspace.

## Method
Bind image identity, partition/load addresses, reset/clock dependencies, command line and handoff state; identify the last confirmed stage and the next discriminating observation.

## Block
A boot log from another firmware/board identity is not proof for the target build. Missing stage identity must remain an explicit evidence gap.
