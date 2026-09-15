---
id: embedded-material-readiness
version: 1.0.0
owner_kind: role
owner: edge-coordination
max_action_level: A2_GENERATE
inputs: [task-brief, supplied-materials]
outputs: [engineering-material-manifest]
---
# Embedded Material Readiness

Evaluate whether repository, revision, hardware, logs and test context are sufficient for the selected workflow.

## Method
Use `domains/edge-foundation/runtime/material-requirements.yaml`; record every required material as available, missing, stale, conflicting or not-applicable with source/version/evidence reference.

## Block
Critical gaps must remain BLOCKED or use an explicit approved degradation path. Never silently substitute assumptions or another product/version.
