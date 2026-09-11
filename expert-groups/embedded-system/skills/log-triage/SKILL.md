---
id: log-triage
version: 0.3.0
owner: debug-reliability-expert
max_action_level: A2_GENERATE
inputs: [logs, task-charter]
outputs: [diagnostic-evidence]
---
# Log Triage

Build a timestamped event timeline, identify first anomaly versus downstream noise, correlate subsystem/state/version and extract evidence references.

Do not declare root cause. Output observations, missing context, candidate subsystems and next evidence to collect. Preserve raw-log location and avoid rewriting ambiguous messages as facts.
