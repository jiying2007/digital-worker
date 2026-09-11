---
id: crash-hardfault-analysis
version: 0.3.0
owner: debug-reliability-expert
max_action_level: A2_GENERATE
inputs: [crash-evidence, symbols, source-evidence]
outputs: [hypothesis-registry]
---
# Crash / HardFault Analysis

Decode panic/oops/backtrace/fault registers against the exact symbols and binary identity. Separate crash site from corruption origin.

Create ranked hypotheses with evidence-for, evidence-against and discriminating experiments. A symbolic backtrace without matching build identity is insufficient for a confirmed root cause.
