---
id: architecture-impact-analysis
version: 1.0.0
owner_kind: capability
owner: embedded.architecture
max_action_level: A2_GENERATE
inputs: [task-charter, evidence-ref-set]
outputs: [technical-analysis]
---
# Architecture Impact Analysis

Assess changes to software layers, interfaces, boot/runtime boundaries, tasks/threads, IPC, memory, power states, fault containment, API/ABI, compatibility and portability.

## Method
Identify affected contracts first; separate observed facts from inferred impact; compare options, resource/timing budgets, lifecycle/failure behavior and verification needs.

## Block
Do not prescribe implementation before affected responsibilities/contracts and unresolved evidence gaps are explicit.
