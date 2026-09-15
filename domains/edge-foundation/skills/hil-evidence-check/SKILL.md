---
id: hil-evidence-check
version: 1.0.0
owner_kind: assurance
owner: verification
max_action_level: A2_GENERATE
inputs: [hil-case, fixture-environment, target-identity, run-artifacts]
outputs: [verification-evidence]
---
# HIL Evidence Check

Verify that HIL evidence corresponds to the required case, fixture/environment, target identity and run rather than a reusable summary from another execution.

## Method
1. Bind case/version, fixture/environment and device/firmware identity.
2. Verify run identity and raw artifact/log provenance.
3. Compare expected and observed results including failure handling.
4. Limit the conclusion to the scenarios actually exercised.

## Evidence
Use case definition, fixture identity, run ID, target identity, logs/artifacts/hashes and verdict details.

## BLOCK
BLOCK HIL PASS when only an untraceable summary exists, fixture/target identity is unclear or the case does not exercise the required scenario.
