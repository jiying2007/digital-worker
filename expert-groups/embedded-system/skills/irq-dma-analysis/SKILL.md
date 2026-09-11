---
id: irq-dma-analysis
version: 0.3.0
owner: linux-bsp-expert
max_action_level: A2_GENERATE
inputs: [source-evidence, logs, platform-materials]
outputs: [technical-analysis]
---
# IRQ DMA Analysis

Analyze interrupt routing, masking, affinity, completion ordering, DMA direction, mapping, cache coherency and buffer lifetime.

Require platform-specific evidence for coherency assumptions. Distinguish RIU/PIO-style access from DMA paths and identify where barriers/cache maintenance are required by the actual platform contract.
