---
id: hil-evidence-check
version: 0.3.0
owner: verification-expert
max_action_level: A2_GENERATE
inputs: [hil-evidence]
outputs: [verification-evidence]
---
# HIL Evidence Check

Validate HIL device/board/firmware/environment identity, test case, raw artifacts and result against `schemas/hil-evidence.v1.schema.json`.

Do not infer HIL PASS from cross-build or manual observation. Missing firmware identity, test artifact or explicit result blocks HIL acceptance.
