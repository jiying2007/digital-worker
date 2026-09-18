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

## Purpose
Analyze interrupt and DMA correctness across registration, context, mapping/addressability, ownership/lifetime, cache coherency, ordering, completion and teardown on the exact target platform.

## Use When
- IRQ loss/storm, DMA timeout, stale/corrupt buffer or cache-coherency issues.
- Driver integration with shared buffers, scatter/gather or non-coherent devices.
- Platform porting where DMA mask/addressing/cache rules differ.

## Do Not Use For
- Assuming generic Linux behavior proves a controller/platform-specific contract.
- Using delay/retry success as proof of coherency/lifetime correctness.
- Treating memory corruption symptoms as DMA root cause without discriminating evidence.

## Required Inputs
- Exact driver/source identity and relevant IRQ/DMA code path.
- Target platform/controller context.
- Logs/trace or observations tied to the target behavior.

## Optional Inputs
- TRM/controller documentation and DMA API contract.
- DMA addresses, cache-line/alignment details, IOMMU state and memory map.
- Interrupt counters, tracepoints and bus/controller diagnostics.

## Method
1. Trace IRQ registration/configuration through trigger, execution context, acknowledge/masking and teardown.
2. Trace DMA mask/addressability, mapping, ownership transfer, cache sync, start, completion/timeout and unmapping.
3. Check buffer lifetime, alignment, ordering and concurrency across CPU/device contexts.
4. Separate controller/platform facts from generic API expectations.
5. Design a discriminating capture/experiment when stale data, timeout or corruption has multiple plausible causes.

## Outputs
- Technical analysis with IRQ/DMA state/lifetime chain.
- Explicit coherency/addressability/ordering hypotheses and evidence gaps.
- Targeted next measurements and required regression scenarios.

## Evidence Rules
- Hardware-specific conclusions require target-platform/controller evidence.
- Successful retry/delay is an observation, not proof of root cause.
- DMA/IRQ logs must be correlated to exact source/build and buffer/run identity when possible.

## BLOCK Conditions
- Target platform/controller contract is unknown and required for the claim.
- Buffer ownership/lifetime or mapping identity cannot be established.
- Only a workaround observation exists but a confirmed causal claim is requested.

## Verification / Review Handoff
- Linux/BSP owns platform IRQ/DMA analysis; driver owner implements fixes.
- Hardware escalation occurs when electrical/controller behavior cannot be resolved from platform evidence.
- Verification independently exercises normal, timeout/error and affected concurrency paths.

## Evaluation
- Positive case: trace establishes mapping/ownership/completion sequence on target.
- Negative case: delay-based workaround does not qualify as confirmed root cause.
- Porting case: platform-specific DMA constraint is distinguished from generic API usage.

## Known Limits / Change Notes
- This Skill does not replace general memory-corruption analysis when the writer is still unknown.
- Version 1.0.0 is definition hardening only; no action authority changes.
