---
id: performance-analysis
version: 1.0.0
owner_kind: capability
owner: embedded.debug-reliability
max_action_level: A2_GENERATE
inputs: [baseline, measurement, source-identity, device-context]
outputs: [technical-analysis]
---
# Performance Analysis

## Purpose
Establish reproducible performance facts from a frozen baseline, controlled measurement and bounded change before claiming a bottleneck or improvement.

## Use When
- Latency, jitter, throughput, CPU/memory/I/O/power or scheduling regressions.
- Optimization work requiring before/after evidence.
- Long-run performance degradation where workload/environment must remain comparable.

## Do Not Use For
- Claiming improvement from incomparable baselines or changed workloads.
- Using average behavior to prove worst-case real-time requirements.
- Optimizing from intuition before a measured bottleneck is established.

## Required Inputs
- Exact source/firmware/device identity.
- Frozen baseline workload/environment and measurement method.
- Measured values or traces tied to the target run.

## Optional Inputs
- Profiles, counters, tracepoints and cycle/timestamp captures.
- Thermal/power state and long-run environment data.
- Known-good baseline from the same measurement contract.

## Method
1. Freeze target, firmware, workload, environment and measurement method.
2. Separate the dimensions being measured: latency/jitter, throughput, CPU, memory, I/O, power and scheduling.
3. Locate bottlenecks from direct traces/profiles/counters before proposing changes.
4. Change one causal variable at a time where practical and remeasure using the same baseline contract.
5. Record confidence, regressions, tail/worst-case behavior and long-run side effects.

## Outputs
- Technical analysis with reproducible baseline and measured bottleneck.
- Before/after deltas with provenance and confidence limits.
- Regression, stress and target Verification requirements.

## Evidence Rules
- Every number must retain unit, collection method, target/run identity and relevant environment.
- Comparable before/after conditions are required for causal improvement claims.
- Average/median does not prove p99/worst-case/deadline compliance.

## BLOCK Conditions
- Baseline or measurement conditions are not comparable.
- Measurements lack provenance or exact object identity.
- The claim requires worst-case or long-run evidence that has not been collected.

## Verification / Review Handoff
- Debug/Reliability owns performance analysis; Architecture consumes resource/NFR impacts.
- Engineering implements optimization separately.
- Verification independently repeats the required performance/regression measurements against Acceptance.

## Evaluation
- Positive case: a measured bottleneck and controlled change produce comparable before/after evidence.
- Negative case: changed workload invalidates an improvement claim.
- Real-time case: average latency is rejected as worst-case compliance evidence.

## Known Limits / Change Notes
- This Skill does not replace dedicated power/electrical measurement or RTOS scheduling analysis when those are the primary problem.
- Version 1.0.0 hardens contract semantics only.
