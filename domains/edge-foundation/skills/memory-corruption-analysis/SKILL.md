---
id: memory-corruption-analysis
version: 1.0.0
owner_kind: capability
owner: embedded.debug-reliability
max_action_level: A2_GENERATE
inputs: [memory-layout, dump-trace, source-identity, runtime-context]
outputs: [hypothesis-registry]
---
# Memory Corruption Analysis

Analyze OOB/UAF/double-free/stack/DMA ownership and concurrency paths without treating the crash site as the corruption origin.

## Method
1. Bind memory evidence to exact build/device identity.
2. Check allocation/lifetime, bounds, ownership and synchronization.
3. Include ISR/DMA/cache effects and stack/heap watermarks.
4. Correlate the earliest corrupted state with candidate writers and design discriminating experiments.

## Evidence
Use dumps, allocator diagnostics, sanitizer/guard data, trace, source, MAP/ELF and controlled reproduction.

## BLOCK
BLOCK confirmed root-cause claims when memory provenance, build identity or candidate-writer evidence is insufficient.
