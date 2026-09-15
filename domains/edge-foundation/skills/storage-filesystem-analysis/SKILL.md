---
id: storage-filesystem-analysis
version: 1.0.0
owner_kind: capability
owner: embedded.linux-bsp
max_action_level: A2_GENERATE
inputs: [storage-identity, logs, source-evidence]
outputs: [technical-analysis]
---
# Storage Filesystem Analysis

Analyze storage faults across media/ECC, controller/driver, MTD, UBI, filesystem, application write pattern and reset/power-loss boundaries.

## Method
Build a time-ordered evidence chain; preserve ECC/bad-block/read-write-erase status, UBI/UBIFS context, workload and concurrency. Collect non-destructive evidence before recovery actions.

## Block
A filesystem read-only symptom or final UBIFS error is not itself a root cause. Missing lower-layer evidence or unauthorized destructive recovery must remain BLOCKED.
