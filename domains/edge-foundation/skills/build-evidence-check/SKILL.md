---
id: build-evidence-check
version: 1.0.0
owner_kind: assurance
owner: verification
max_action_level: A2_GENERATE
inputs: [build-command, source-identity, toolchain-config, artifact]
outputs: [verification-evidence]
---
# Build Evidence Check

## Purpose
Verify that a build result corresponds to the exact source/config/toolchain/target and yields an identifiable artifact, while keeping build evidence strictly bounded from device/HIL/release claims.

## Use When
- Acceptance criteria requiring build/cross-build success.
- Checking artifact provenance before downstream testing.
- Validating that the intended configuration/toolchain actually produced the candidate.

## Do Not Use For
- Using build success to claim runtime/device behavior.
- Accepting a screenshot/summary without exact job/command/artifact identity.
- Ignoring warnings/errors that are material to the defined Acceptance.

## Required Inputs
- Exact source/base commit identity.
- Build command, target and configuration/toolchain identity.
- Produced artifact identity or an explicit expected-artifact failure.

## Optional Inputs
- CI/job/run ID and full logs.
- Artifact hash/manifest and dependency lock information.
- Known-good build baseline.

## Method
1. Bind the build to exact source/base, target, config, toolchain and command.
2. Inspect outcome, relevant warnings/errors and whether the intended path actually executed.
3. Bind produced artifact to path/name/hash or immutable manifest.
4. Separate host/static/cross-build facts from any runtime/device claim.
5. Emit Verification evidence only within the build layer and preserve unresolved warnings/identity gaps.

## Outputs
- Build-layer verification evidence with exact provenance.
- Artifact identity/hash and job/command/config metadata.
- Explicit statement of what the build result does not prove.

## Evidence Rules
- CI/job/command/config and artifact identity must be traceable.
- A green wrapper job is insufficient if the required build step was skipped.
- Build evidence cannot be promoted to Device/HIL/Release evidence.

## BLOCK Conditions
- Source/config/toolchain/artifact identity is ambiguous.
- The relevant build step did not run or evidence is untraceable.
- Build evidence is being used to satisfy a higher verification layer.

## Verification / Review Handoff
- Verification owns the build-layer verdict independently.
- Engineering supplies reproducible build inputs/artifacts but does not self-sign.
- Device/HIL/release checks consume artifact identity and establish their own evidence.

## Evaluation
- Positive case: exact source/config/toolchain produces a hashed artifact.
- Negative case: green CI with skipped target build is rejected.
- Boundary case: cross-build PASS does not become Device PASS.

## Known Limits / Change Notes
- This Skill does not test runtime functionality or production release readiness.
- Version 1.0.0 strengthens layer boundaries only.
