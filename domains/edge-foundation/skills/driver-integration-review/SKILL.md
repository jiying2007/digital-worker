---
id: driver-integration-review
version: 1.0.0
owner_kind: capability
owner: embedded.driver-component
max_action_level: A2_GENERATE
inputs: [device-identity, bus-protocol, platform-resources, driver-source]
outputs: [technical-analysis]
---
# Driver Integration Review

Review device integration from hardware/bus contract through driver lifecycle, platform adapter and stable API.

## Method
1. Confirm device/board/resource identity and protocol assumptions.
2. Check init/probe/deinit, IRQ/DMA/thread context and resource lifetime.
3. Review timeout/retry/error recovery, suspend/resume and power behavior.
4. Check API/ABI/versioning, diagnostics, portability and rollback.
5. For substitutions, maintain a compatibility matrix covering normal and failure paths.

## Evidence
Use datasheet/TRM/schematic, platform resources, exact driver source, device logs and target-device verification.

## BLOCK
BLOCK compatibility or reusable-component claims when device identity, platform resource facts or failure/power evidence are missing.
