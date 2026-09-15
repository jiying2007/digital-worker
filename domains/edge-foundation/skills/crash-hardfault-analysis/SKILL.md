---
id: crash-hardfault-analysis
version: 1.0.0
owner_kind: capability
owner: embedded.debug-reliability
max_action_level: A2_GENERATE
inputs: [fault-context, elf-map, source-identity, runtime-context]
outputs: [hypothesis-registry]
---
# Crash / HardFault Analysis

Analyze crash or HardFault context as evidence for hypotheses; the PC landing point is not automatically the root cause.

## Method
1. Bind dump/registers/core/ELF/MAP to the exact build and target.
2. Decode fault status, stacked registers, PC/LR/SP and task/ISR context.
3. Check stack, memory lifetime, concurrency, DMA/cache and prior corruption paths.
4. Maintain competing hypotheses with evidence_for/evidence_against and discriminating experiments.

## Evidence
Use raw fault registers/dump/core, ELF/MAP, source, task/ISR context and reproducible observations.

## BLOCK
BLOCK confirmed root-cause claims when build identity or critical fault context is missing, inconsistent or unrecoverable.
