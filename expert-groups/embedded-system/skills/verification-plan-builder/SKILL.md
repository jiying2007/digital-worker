---
id: verification-plan-builder
version: 0.3.0
owner: verification-expert
max_action_level: A2_GENERATE
inputs: [task-charter, technical-decision]
outputs: [verification-plan]
---
# Verification Plan Builder

Map acceptance criteria and identified risks to Host, cross-build, SIL, device, HIL and release verification layers.

For every required layer define test, environment, expected evidence and pass/fail rule. Mark not-applicable explicitly. Never allow a lower verification layer to substitute for a required higher layer.
