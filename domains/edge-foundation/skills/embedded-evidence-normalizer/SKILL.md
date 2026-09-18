---
id: embedded-evidence-normalizer
version: 1.0.0
owner_kind: role
owner: edge-coordination
max_action_level: A2_GENERATE
inputs: [raw-evidence]
outputs: [evidence-ref-set]
---
# Embedded Evidence Normalizer

## Purpose
Convert heterogeneous raw evidence into traceable references while preserving original provenance, object identity and claim strength.

## Use When
- When logs, commits, source locations, datasheets, schematics, binaries, measurements or HIL artifacts enter a run.
- When multiple Skills need to reference the same evidence without duplicating authority.
- When evidence must be frozen or handed to Verification/Review.

## Do Not Use For
- Turning inference, summary or model output into direct evidence.
- Rewriting raw evidence to make it fit a hypothesis.
- Replacing an authoritative source with a normalized copy.

## Required Inputs
- Raw evidence or a durable reference to it.
- Source type and origin.
- Target object identity or an explicit statement that it is unknown.

## Optional Inputs
- Hash, timestamp, collection method, run ID and collector identity.
- Authority/freshness metadata.
- Relations to duplicate or derived artifacts.

## Method
1. Preserve the original evidence location/content reference without destructive transformation.
2. Record source type, origin, exact object identity, collection context, timestamp/run identity and current verification state.
3. Distinguish direct evidence from derived summaries and inferences.
4. Link duplicates/derivatives to the same underlying provenance rather than creating new authority.
5. Emit explicit gaps for missing identity, origin or collection context.

## Outputs
- Evidence reference set with provenance and target-object identity.
- Relations between original, duplicate and derived evidence.
- Explicit evidence gaps and verification state.

## Evidence Rules
- Inference is never promoted to Evidence by normalization.
- Derived summaries must retain a pointer to their original source.
- Unknown identity/version remains unknown; normalization cannot repair it by guesswork.

## BLOCK Conditions
- Evidence origin cannot be established for a claim that requires direct evidence.
- Target object/version is ambiguous and that ambiguity affects the claim.
- Only an untraceable summary exists where raw evidence is required.

## Verification / Review Handoff
- Engineering consumes normalized references but owns technical interpretation.
- Verification independently checks whether a reference is sufficient for an Acceptance claim.
- Review may inspect provenance/risk but does not gain stronger evidence merely because the record is normalized.

## Evaluation
- Positive case: raw log + exact firmware/device metadata becomes a traceable evidence reference.
- Negative case: copied screenshot/summary without origin remains insufficient.
- Deduplication case: multiple references point to one authoritative source without creating a second SSOT.

## Known Limits / Change Notes
- This Skill normalizes evidence metadata; it does not decide root cause or PASS.
- Version 1.0.0 adds review-grade boundaries without changing evidence authority.
