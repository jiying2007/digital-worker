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

Analyze performance by reproducible baseline, measured bottleneck, bounded change and remeasurement.

## Method
1. Freeze workload, target, firmware, environment and measurement method.
2. Separate latency, throughput, CPU, memory, I/O, power and scheduling dimensions.
3. Locate bottlenecks from direct measurement before proposing optimization.
4. Change one causal variable when possible and remeasure against the same baseline.
5. Record regressions and long-run side effects.

## Evidence
Use traces, profiles, counters, timestamps, measurements and exact object identity.

## BLOCK
BLOCK verified improvement claims when baseline or measurement conditions differ, numbers lack provenance or only average behavior is available for a worst-case requirement.
