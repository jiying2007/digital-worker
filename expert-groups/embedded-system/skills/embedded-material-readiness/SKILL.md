---
id: embedded-material-readiness
version: 0.3.0
owner: embedded-system-team-lead
max_action_level: A2_GENERATE
inputs: [task-brief, supplied-materials]
outputs: [engineering-material-manifest]
---
# Embedded Material Readiness

Evaluate whether repository, revision, hardware and evidence inputs are sufficient for the selected workflow.

Use `config/material-requirements.yaml`. Record every material as present, missing, stale or not-applicable with source/version. Critical gaps must BLOCK or require explicit degradation approval; never silently substitute assumptions.
