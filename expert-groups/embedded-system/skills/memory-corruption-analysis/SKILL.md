---
id: memory-corruption-analysis
version: 0.3.0
owner: debug-reliability-expert
max_action_level: A2_GENERATE
inputs: [memory-evidence, source-evidence, runtime-traces]
outputs: [hypothesis-registry]
---
# Memory Corruption Analysis

Analyze bounds, lifetime, ownership, DMA interaction, stack/heap pressure, use-after-free and concurrency corruption paths.

Prefer reproducible guards, poisoning, sanitizers, watchpoints or targeted instrumentation over speculative fixes. Track each suspected writer as a hypothesis until experimentally distinguished.
