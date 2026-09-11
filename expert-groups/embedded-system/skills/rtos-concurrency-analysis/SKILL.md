---
id: rtos-concurrency-analysis
version: 0.3.0
owner: mcu-rtos-expert
max_action_level: A2_GENERATE
inputs: [task-model, source-evidence, trace-evidence]
outputs: [technical-analysis]
---
# RTOS Concurrency Analysis

Review task/ISR ownership, priorities, mutex/semaphore/queue usage, lock ordering, interrupt-safe APIs and timing assumptions.

Identify race, inversion, deadlock and starvation hypotheses with evidence and proposed discriminating tests. Never equate absence of a reproduced race with proof of safety.
