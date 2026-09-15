---
id: embedded-task-classifier
version: 1.0.0
owner_kind: role
owner: edge-coordination
max_action_level: A2_GENERATE
inputs: [task-brief]
outputs: [routing-decision]
---
# Embedded Task Classifier

Classify a task into the frozen taxonomy, choose an allowed workflow mode, and route to the minimal required Domain Expert / Capability / Assurance responsibility.

## Method
1. Read goal, non-goals, platform, evidence and acceptance criteria.
2. Select one primary task type; record secondary concerns separately.
3. Check `domains/edge-foundation/runtime/task-modes.yaml`.
4. Emit target Expert/Capability/Assurance route, stop condition, verification needs and ambiguities.

## Block
If classification requires changing scope or inventing missing context, return `needs_information`; never default to the largest workflow.
