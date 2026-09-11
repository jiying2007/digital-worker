---
id: regression-scope-analysis
version: 0.3.0
owner: verification-expert
max_action_level: A2_GENERATE
inputs: [changed-files, architecture-impact, historical-failures]
outputs: [regression-scope]
---
# Regression Scope Analysis

Derive regression scope from changed behavior, dependencies, shared resources, failure history and platform variants.

Separate mandatory, risk-based and optional regression. A small diff does not automatically imply a small test scope; shared clocks, memory, protocol or power paths can widen impact.
