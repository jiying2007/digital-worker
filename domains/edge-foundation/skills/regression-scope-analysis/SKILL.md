---
id: regression-scope-analysis
version: 1.0.0
owner_kind: assurance
owner: verification
max_action_level: A2_GENERATE
inputs: [change-scope, architecture-impact, known-risks]
outputs: [regression-scope]
---
# Regression Scope Analysis

Derive the minimum sufficient regression set from the actual change surface and failure modes instead of using either “test everything” or “test only modified files.”

## Method
1. Trace direct modules, interfaces/protocol consumers and shared resources.
2. Include concurrency, lifecycle, Boot/OTA/Power and negative/error paths when affected.
3. Add performance, soak or device/HIL layers only when the claim requires them.
4. Record excluded areas and the evidence-based reason for exclusion.

## Evidence
Bind scope to exact change/source identity, architecture impact, interface contracts and known risks.

## BLOCK
BLOCK claims of sufficient regression when affected interfaces, lifecycle paths or required target-device layers remain unknown.
