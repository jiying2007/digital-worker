---
id: interface-contract-review
version: 1.0.0
owner_kind: capability
owner: embedded.architecture
max_action_level: A2_GENERATE
inputs: [interface-spec, source-evidence]
outputs: [interface-review]
---
# Interface Contract Review

Review API, ABI, IPC, protocol, timing and ownership contracts for compatibility and failure behavior.

## Method
Check owner/direction, sync/async, data units, lifetime/context, versioning, timeout/retry, error semantics, buffer ownership, backward compatibility and rollback.

## Block
Successful compilation or one happy-path integration is insufficient evidence for compatibility; breaking or unknown semantics must be explicit.
