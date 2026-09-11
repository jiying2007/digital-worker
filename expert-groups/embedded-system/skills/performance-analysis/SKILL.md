---
id: performance-analysis
version: 0.3.0
owner: debug-reliability-expert
max_action_level: A2_GENERATE
inputs: [baseline-metrics, traces, source-evidence]
outputs: [technical-analysis]
---
# Performance Analysis

Analyze CPU, latency, scheduling, IRQ load, memory, I/O, boot time, thermal or power regressions using baseline-to-measurement comparison.

Require metric definition, workload and environment identity. Report confidence and measurement noise. Optimization proposals must name expected mechanism and re-measurement criterion.
