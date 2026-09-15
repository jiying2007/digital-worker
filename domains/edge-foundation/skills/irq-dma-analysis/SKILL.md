---
id: irq-dma-analysis
version: 1.0.0
owner_kind: capability
owner: embedded.linux-bsp
max_action_level: A2_GENERATE
inputs: [source-evidence, logs, dma-context]
outputs: [technical-analysis]
---
# IRQ DMA Analysis

Analyze interrupt delivery, DMA mapping/addressability, buffer ownership/lifetime, cache maintenance, alignment, completion/timeout and ordering.

## Method
Follow registration → trigger → context → mapping → cache/ownership → start → completion/timeout → teardown. Separate controller facts from generic Linux assumptions.

## Block
Delay-based workarounds or a successful retry do not prove cache/coherency/lifetime correctness. Require target-platform evidence for hardware-specific behavior.
