---
id: log-triage
version: 1.0.0
owner_kind: capability
owner: embedded.debug-reliability
max_action_level: A2_GENERATE
inputs: [raw-logs, source-identity, device-context]
outputs: [diagnostic-evidence]
---
# Log Triage

Turn raw logs into a time-ordered diagnostic evidence set without converting inference into fact.

## Method
1. Bind log to exact source/firmware/device/environment identity.
2. Preserve raw context around the first abnormal event, not only the final error.
3. Build a timeline and classify statements as observed, inferred or confirmed.
4. Identify missing context and the next discriminating capture.

## Evidence
Keep original log references, timestamps, collection method and hashes when available.

## BLOCK
BLOCK root-cause claims when logs are truncated, identity is unknown, timestamps are inconsistent or the first abnormal event cannot be distinguished.
