---
id: rtos-concurrency-analysis
version: 1.0.0
owner_kind: capability
owner: embedded.mcu-rtos
max_action_level: A2_GENERATE
inputs: [rtos-config, task-map, isr-dma-context, trace]
outputs: [technical-analysis]
---
# RTOS Concurrency Analysis

Analyze task/ISR synchronization, scheduling and worst-case timing under the exact RTOS and firmware configuration.

## Method
1. Map task priorities, periods, blocking calls and shared resources.
2. Trace mutex/semaphore/queue and ISR-to-task handoff.
3. Check critical sections, lock order, races, starvation and priority inversion.
4. Evaluate timeout/watchdog and worst-case latency, not only average behavior.

## Evidence
Use RTOS config, task/ISR source, trace, timestamps/cycle counts and target-device reproduction.

## BLOCK
BLOCK verified concurrency conclusions when task priorities/configuration, ISR context or timing evidence are unavailable or mismatched.
