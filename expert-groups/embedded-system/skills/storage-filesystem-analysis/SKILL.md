---
id: storage-filesystem-analysis
version: 0.3.0
owner: linux-bsp-expert
max_action_level: A2_GENERATE
inputs: [storage-layout, logs, source-evidence]
outputs: [technical-analysis]
---
# Storage Filesystem Analysis

Analyze NAND/eMMC/NOR, ECC, bad blocks, partitions, UBI/UBIFS, squashfs and writable data paths.

Preserve distinction between media errors, controller/ECC results, MTD/UBI behavior and filesystem policy. For recovery advice, state data-loss risk and required backup/readonly evidence before proposing destructive actions.
