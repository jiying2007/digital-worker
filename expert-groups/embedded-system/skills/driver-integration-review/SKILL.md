---
id: driver-integration-review
version: 0.3.0
owner: driver-component-expert
max_action_level: A2_GENERATE
inputs: [driver-source, hardware-contract, integration-context]
outputs: [technical-analysis]
---
# Driver Integration Review

Review probe/init/deinit, resource ownership, error paths, IRQ/DMA interaction, power transitions, concurrency and API compatibility for a driver or reusable component.

Check platform abstraction leakage and rollback behavior. Produce concrete verification hooks; do not approve hardware behavior without board evidence where hardware facts are material.
