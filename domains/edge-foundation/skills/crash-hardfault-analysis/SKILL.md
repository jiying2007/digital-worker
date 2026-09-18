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

## Purpose
Use exact crash/HardFault context to maintain falsifiable root-cause hypotheses without treating the PC landing point or final fault as the corruption origin.

## Use When
- MCU HardFault, exception, abort, kernel/user crash or core-dump analysis.
- Crashes potentially caused by prior memory/concurrency/DMA corruption.
- When multiple plausible root causes require discriminating experiments.

## Do Not Use For
- Declaring the symbol at PC as root cause without causal evidence.
- Symbolicating with mismatched ELF/MAP/build.
- Collapsing all competing hypotheses into one narrative before evidence discriminates them.

## Required Inputs
- Raw fault registers/dump/core or equivalent context.
- Exact source/build identity and matching ELF/MAP/symbols when required.
- Runtime task/thread/ISR context sufficient to interpret the fault.

## Optional Inputs
- Prior logs/timeline, stack watermark and memory diagnostics.
- DMA/concurrency traces and watchdog/reset history.
- Controlled reproduction and instrumentation results.

## Method
1. Verify dump/register/core and ELF/MAP correspond to the exact target build.
2. Decode fault status, stacked registers, PC/LR/SP/call stack and execution context.
3. Check stack validity, memory lifetime, concurrency, DMA/cache and earlier corruption paths rather than assuming the landing point is causal.
4. Maintain competing hypotheses with evidence-for, evidence-against and explicit uncertainty.
5. Define discriminating experiments/captures and update the same hypothesis registry rather than starting over.

## Outputs
- Hypothesis registry with ranked-by-evidence hypotheses but no unsupported confirmation.
- Exact symbol/build/fault context and evidence links.
- Discriminating experiments and unresolved gaps.

## Evidence Rules
- Symbolication proves where execution faulted for that build, not necessarily why.
- A hypothesis becomes Confirmed only with discriminating evidence sufficient to rule out credible alternatives.
- Secondary corruption symptoms must not be promoted to primary cause without evidence.

## BLOCK Conditions
- Fault context or exact build/symbol identity is missing/inconsistent.
- Stack/register data is too corrupted for the requested confidence and no corroborating evidence exists.
- A confirmed root-cause statement would rely solely on PC location or temporal coincidence.

## Verification / Review Handoff
- Debug/Reliability owns hypothesis discipline; MCU/RTOS/Linux/driver Skills contribute domain evidence as triggered.
- Engineering change begins only from an explicit hypothesis/decision, not an implicit guess.
- Verification reproduces the original failure path and relevant regressions independently.

## Evaluation
- Positive case: exact fault context narrows hypotheses and defines a discriminating experiment.
- Negative case: mismatched symbols block root-cause confirmation.
- Corruption case: crash site is treated as a possible victim, not automatically the origin.

## Known Limits / Change Notes
- Severely incomplete dumps may support only low-confidence hypotheses.
- Version 1.0.0 adds contract detail without changing diagnostic routing/action.
