---
id: release-readiness-check
version: 1.0.0
owner_kind: assurance
owner: review
max_action_level: A2_GENERATE
inputs: [release-candidate, verification-report, provenance, rollback, open-risks]
outputs: [review-report]
---
# Release Readiness Check

Assess whether an exact release candidate has sufficient evidence, provenance, rollback and accepted residual risk for a human release decision.

## Method
1. Bind source/artifact/manifest/provenance to the exact candidate.
2. Check required Verification layers and unverified items without rewriting their status.
3. Check upgrade/downgrade/rollback/power-loss paths when in scope.
4. Review open findings, risk owner/acceptor/expiry and mitigation.
5. Confirm A7 remains a human decision; readiness is not release execution.

## Evidence
Use exact candidate identity, Verification evidence, device/HIL/soak evidence as required, provenance, rollback evidence and risk records.

## BLOCK
BLOCK readiness when required evidence, rollback/provenance, critical findings or explicit A7 approval conditions are unresolved.
