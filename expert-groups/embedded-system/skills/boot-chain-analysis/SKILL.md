---
id: boot-chain-analysis
version: 0.3.0
owner: linux-bsp-expert
max_action_level: A2_GENERATE
inputs: [boot-materials, logs, source-evidence]
outputs: [technical-analysis]
---
# Boot Chain Analysis

Trace BootROM/SPL/U-Boot/kernel/rootfs or platform-equivalent startup from reset to userspace.

Map image identity, partition/load addresses, reset/clock dependencies, command line and handoff state. For a failure, identify the last confirmed stage and the next discriminating observation. Never treat a boot log from another firmware identity as proof for the target build.
