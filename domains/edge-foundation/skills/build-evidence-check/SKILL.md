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

Verify that a build result proves the intended source/config/toolchain target and produces an identifiable artifact.

## Method
1. Bind source/base commit, toolchain, config and command.
2. Record target, warnings/errors and artifact identity/hash.
3. Distinguish host/static/cross-build evidence from device behavior.
4. Reject summaries that cannot be traced to the exact build object.

## Evidence
Use CI/job identity, command/config, compiler/toolchain version, artifact path/hash and logs.

## BLOCK
BLOCK build PASS when source/config/artifact identity is ambiguous, or when build evidence is being used to claim Device/HIL/Release behavior.
