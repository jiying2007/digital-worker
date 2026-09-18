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

## Purpose
Analyze OOB, UAF, double-free, stack/heap overwrite, DMA ownership and concurrency corruption by tracing the earliest corrupted state and candidate writers.

## Use When
- Crash/data corruption with evidence of invalid memory state.
- Heap/stack corruption, allocator failure or intermittent overwrite.
- DMA/cache/lifetime/concurrency cases where the visible crash likely follows earlier corruption.

## Do Not Use For
- Treating the crash/read site as the write origin.
- Confirming a writer without provenance/order evidence.
- Using static layout alone to prove runtime memory safety.

## Required Inputs
- Exact source/build identity and memory layout relevant to the failure.
- Dump/trace or other runtime evidence showing corrupted state.
- Runtime ownership/lifetime context for candidate objects.

## Optional Inputs
- Allocator diagnostics, guards/sanitizers, stack/heap watermarks.
- MAP/ELF, DMA/cache traces and watchpoints.
- Controlled stress/reproduction and candidate-writer instrumentation.

## Method
1. Bind all memory evidence to the exact target build/device.
2. Identify the earliest observed corrupted object/state and its intended lifetime/owner.
3. Enumerate candidate writers and check bounds, allocation/free lifecycle, synchronization, ISR/DMA/cache effects and stack/heap margins.
4. Use ordering/watchpoint/guard/instrumentation evidence to eliminate or strengthen hypotheses.
5. Maintain evidence-for/evidence-against and design the next discriminating experiment.

## Outputs
- Hypothesis registry centered on candidate corruption origins.
- Object/lifetime/ownership analysis and direct evidence references.
- Instrumentation/reproduction and regression requirements.

## Evidence Rules
- Corrupted memory proves a symptom; writer/origin requires separate evidence.
- Static source review supports hypotheses but does not by itself prove runtime occurrence.
- Watchpoint/guard/sanitizer/trace evidence must match exact target/build and execution context.

## BLOCK Conditions
- Memory provenance/build identity is unknown.
- No evidence distinguishes candidate writers but a confirmed root cause is requested.
- Runtime lifetime/ownership facts needed for the claim are unavailable.

## Verification / Review Handoff
- Debug/Reliability owns corruption hypotheses; MCU/RTOS/driver/Linux Skills supply scheduling/DMA/platform evidence when triggered.
- Engineering fixes follow an explicit technical decision.
- Verification must test original corruption path plus recurrence/stress scenarios.

## Evaluation
- Positive case: earliest corruption plus writer evidence converges on a cause.
- Negative case: crash location is not accepted as corruption origin.
- Concurrency/DMA case: competing writer paths remain explicit until discriminated.

## Known Limits / Change Notes
- Some corruptions may remain non-deterministic and only support bounded hypotheses until instrumentation succeeds.
- Version 1.0.0 is definition hardening only.
