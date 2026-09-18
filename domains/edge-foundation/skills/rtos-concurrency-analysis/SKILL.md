---
id: rtos-concurrency-analysis
version: 1.0.0
owner_kind: capability
owner: embedded.mcu-rtos
max_action_level: A2_GENERATE
inputs: [rtos-config, task-map, isr-dma-context, trace]
outputs: [technical-analysis]
---
# RTOS Concurrency Analysis

## Purpose
Analyze scheduling, task/ISR synchronization, shared-resource ownership and worst-case timing under the exact RTOS and firmware configuration.

## Use When
- Deadlock, starvation, priority inversion, race or missed deadline/jitter issues.
- ISR-to-task/queue/semaphore handoff analysis.
- Design/review of shared resources and real-time scheduling.

## Do Not Use For
- Using average timing to prove a worst-case requirement.
- Assuming task priorities/config from source when runtime/build config differs.
- Replacing root-cause evidence with generic RTOS best practices.

## Required Inputs
- Exact RTOS configuration and firmware identity.
- Task/priority/resource map and relevant task/ISR source.
- Trace/timing or target evidence sufficient for the claim.

## Optional Inputs
- Cycle counter/timestamps, RTOS trace and stack watermarks.
- DMA/driver context and watchdog/reset records.
- Deadline/jitter requirements and known load profiles.

## Method
1. Map task priorities, periods/events, blocking calls and shared resources.
2. Trace ISR/DMA-to-task handoffs and each mutex/semaphore/queue ownership/lifetime path.
3. Check critical sections, lock order, races, starvation and priority inversion.
4. Evaluate timeout/watchdog behavior and worst-case latency/jitter against requirements.
5. Create discriminating load/trace experiments for ambiguous concurrency hypotheses.

## Outputs
- Technical analysis with task/resource/lock/timing relationships.
- Observed and inferred concurrency failure modes with evidence gaps.
- Targeted stress/trace and regression requirements.

## Evidence Rules
- Priority/config claims must be bound to the exact build.
- Average latency cannot prove a worst-case deadline.
- Temporal correlation alone does not prove a race without ownership/order evidence.

## BLOCK Conditions
- Task priorities/config or ISR context are unknown/mismatched.
- Timing evidence is absent for a claimed deadline/jitter result.
- A confirmed race/deadlock claim would require inferred rather than observed ordering.

## Verification / Review Handoff
- MCU/RTOS owns scheduler/concurrency analysis; driver/debug Skills may participate when evidence crosses boundaries.
- Engineering fixes remain separate from Verification.
- Verification exercises affected load, timing and failure paths independently.

## Evaluation
- Positive case: trace/resource map establishes a concrete scheduling or lock issue.
- Negative case: average latency is rejected as worst-case proof.
- Stress case: ambiguous race hypotheses get discriminating instrumentation rather than guesswork.

## Known Limits / Change Notes
- Electrical latency and hardware timing outside MCU/RTOS require cross-domain evidence.
- Version 1.0.0 adds review-grade semantics without changing owner/action.
