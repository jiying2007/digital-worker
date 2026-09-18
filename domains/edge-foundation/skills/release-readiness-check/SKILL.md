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

## Purpose
Independently assess whether one exact release candidate has sufficient provenance, Verification, rollback and accepted residual risk to be presented for a human release decision.

## Use When
- Release/OTA readiness review after Engineering and required Verification.
- Checking provenance/rollback/open findings before A7 decision.
- Assessing whether residual risk is owned, time-bounded and explicitly accepted.

## Do Not Use For
- Executing the release or granting A7 approval.
- Rewriting failed/unverified Verification criteria into PASS.
- Performing engineering modifications while acting as Independent Review.

## Required Inputs
- Exact release candidate source/artifact/manifest identity.
- Verification report for required layers.
- Provenance, rollback/recovery evidence and open-risk register.

## Optional Inputs
- Device/HIL/soak evidence and production telemetry relevant to scope.
- Upgrade/downgrade/power-loss evidence.
- Prior release comparison and unresolved review findings.

## Method
1. Bind source, artifact, manifest and provenance to one immutable release candidate.
2. Check each required Verification layer and preserve failed/unverified status exactly.
3. Review upgrade/downgrade/rollback/power-loss/recovery paths where in scope.
4. Review open findings and ensure each residual risk has owner, acceptor, mitigation and expiry/review condition.
5. Emit readiness findings and confirm that A7 remains an authorized human decision separate from this review.

## Outputs
- Independent review report tied to the exact candidate.
- Readiness findings, blockers and residual-risk records.
- Explicit statement that readiness is not release execution or approval.

## Evidence Rules
- Review relies on exact candidate provenance and independent Verification evidence.
- A stage exception/unavailable reviewer must not be represented as Independent Review PASS.
- Risk acceptance is a governance record, not evidence that the underlying defect is absent.

## BLOCK Conditions
- Required Verification, provenance or rollback evidence is missing.
- Critical/unaccepted findings remain open.
- A7 conditions/authority are unresolved or the candidate identity is mutable/ambiguous.

## Verification / Review Handoff
- Review remains independent from Engineering and Verification.
- It may return findings to the owning stage but must not patch the candidate while preserving review identity.
- Final A7 release decision remains with the authorized human owner.

## Evaluation
- Positive case: fully identified candidate + required Verification + rollback + owned risks yields a bounded readiness report.
- Negative case: missing Device/HIL/rollback evidence blocks readiness when required.
- Independence case: Review does not convert an unavailable review or failed Verification into PASS.

## Known Limits / Change Notes
- Release Readiness is not Product Readiness for all tracks and is not an A7 decision.
- Version 1.0.0 hardens the contract without expanding Review authority or action level.
