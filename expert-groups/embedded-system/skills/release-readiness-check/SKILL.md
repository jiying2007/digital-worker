---
id: release-readiness-check
version: 0.3.0
owner: embedded-review-governor
max_action_level: A2_GENERATE
inputs: [verification-report, delivery-receipt, release-evidence]
outputs: [review-report]
---
# Release Readiness Check

Independently check source/artifact provenance, required verification layers, open risks, rollback evidence and required approvals.

Do not perform release promotion. Any missing mandatory evidence or unresolved BLOCKER prevents READY. Warnings and accepted residual risks must remain visible in the final review.
