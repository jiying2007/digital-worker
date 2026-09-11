---
id: device-evidence-check
version: 0.3.0
owner: verification-expert
max_action_level: A2_GENERATE
inputs: [device-run-evidence, delivery-receipt]
outputs: [verification-evidence]
---
# Device Evidence Check

Validate device identity, board revision, firmware hash/version, deployment method and observed result before accepting board-level evidence.

If running firmware identity cannot be tied to the build under review, device status is BLOCKED rather than PASS.
