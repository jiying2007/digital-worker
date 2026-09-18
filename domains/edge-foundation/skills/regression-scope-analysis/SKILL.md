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

## Purpose
Derive the minimum sufficient regression surface from actual change dependencies, interfaces, lifecycle and failure modes rather than testing either everything or only modified files.

## Use When
- Any Engineering change requiring Verification beyond the directly modified code.
- Architecture/interface/driver/RTOS changes with shared-resource or lifecycle impact.
- Selecting device/HIL/soak coverage based on evidence and risk.

## Do Not Use For
- Treating file-diff size as the complete regression scope.
- Adding expensive layers without a claim/risk that requires them.
- Excluding a path merely because it was not modified directly.

## Required Inputs
- Exact change/source identity and change scope.
- Architecture/interface impact where relevant.
- Known risks/failure modes.

## Optional Inputs
- Dependency graph, previous defects and coverage history.
- Device/HIL/soak availability.
- Production/release risk classification.

## Method
1. Trace directly modified modules and their interface/protocol consumers.
2. Identify shared resources, concurrency, lifecycle, boot/OTA/power and error/recovery paths affected by the change.
3. Map each affected behavior to an appropriate regression layer.
4. Add performance, stress, soak, device or HIL only where the claim/risk requires it.
5. Record excluded areas with an evidence-based reason and residual risk.

## Outputs
- Regression scope with included behaviors/layers and rationale.
- Explicit exclusions, assumptions and residual risks.
- Inputs for Verification execution and review.

## Evidence Rules
- Scope must bind to the exact change, not a generic component checklist.
- Indirect interface/resource consumers count when evidence shows dependency.
- Absence of previous failures is not sufficient reason to exclude a newly affected path.

## BLOCK Conditions
- Affected interfaces/lifecycle/shared resources remain unknown.
- Required target-device/HIL layer cannot be determined for a material risk.
- A claimed sufficient regression set relies on unexplained exclusions.

## Verification / Review Handoff
- Verification owns regression sufficiency independently from Engineering.
- Engineering can provide impact data but cannot self-approve the final scope.
- Review may challenge residual risk/exclusions without substituting for Verification.

## Evaluation
- Positive case: small code change expands to the correct interface/error-path regression.
- Negative case: 'only changed files' is rejected when shared behavior is affected.
- Efficiency case: unrelated layers are excluded with explicit evidence/rationale.

## Known Limits / Change Notes
- This Skill selects scope, not the PASS verdict of individual tests.
- Version 1.0.0 adds lifecycle governance semantics only.
