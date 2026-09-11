---
id: build-evidence-check
version: 0.3.0
owner: verification-expert
max_action_level: A2_GENERATE
inputs: [delivery-receipt, build-artifacts]
outputs: [verification-evidence]
---
# Build Evidence Check

Verify repository/base identity, toolchain/configuration, command outcome and artifact hash for Host or cross-build evidence.

A build marked successful without source/config identity is insufficient for downstream deployment claims. Record exactly which verification layer the evidence supports.
