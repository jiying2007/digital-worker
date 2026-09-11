---
id: embedded-task-classifier
version: 0.3.0
owner: embedded-system-team-lead
max_action_level: A2_GENERATE
inputs: [task-brief]
outputs: [routing-decision]
---
# Embedded Task Classifier

Classify one task into the frozen task taxonomy, choose an allowed workflow mode, and name primary experts. Do not default to `full_chain`.

## Method
1. Read goal, non-goals, evidence, platform and acceptance criteria.
2. Select exactly one primary task type; record secondary concerns separately.
3. Check `config/task-modes.yaml` for allowed modes.
4. Emit route, experts, stop condition, required verification and ambiguity list.

## Block
If task type cannot be determined without changing scope, return `needs_information` rather than guessing.
