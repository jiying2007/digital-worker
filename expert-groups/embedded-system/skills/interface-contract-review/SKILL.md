---
id: interface-contract-review
version: 0.3.0
owner: embedded-architecture-expert
max_action_level: A2_GENERATE
inputs: [interface-spec, source-evidence]
outputs: [interface-review]
---
# Interface Contract Review

Review API, ABI, IPC, protocol, timing and ownership contracts for compatibility and failure behavior.

Check versioning, lifecycle, concurrency, error semantics, timeout/retry rules, buffer ownership and backward compatibility. Report breaking changes explicitly; never infer compatibility solely from successful compilation.
