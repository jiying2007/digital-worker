---
id: interface-contract-review
version: 1.0.0
owner_kind: capability
owner: embedded.architecture
max_action_level: A2_GENERATE
inputs: [interface-spec, source-evidence]
outputs: [interface-review]
---
# Interface Contract Review

## Purpose
Review API, ABI, IPC, protocol, timing and ownership contracts for unambiguous lifecycle, failure semantics, compatibility and rollback behavior.

## Use When
- Creating or changing an API/ABI/protocol/IPC boundary.
- Integrating components whose ownership, versioning or error behavior may differ.
- Reviewing backward compatibility or migration risk.

## Do Not Use For
- Proving whole-system behavior from an interface review alone.
- Treating compile success or one happy path as compatibility evidence.
- Resolving electrical details that belong to Hardware/board evidence.

## Required Inputs
- Interface specification or exact source defining the interface.
- Producer/consumer identity and version where relevant.
- Known lifecycle, concurrency and error-path expectations.

## Optional Inputs
- Protocol traces, integration logs and compatibility history.
- Performance/timing requirements.
- Migration and rollback plan.

## Method
1. Identify owner, direction, caller/callee or producer/consumer roles.
2. Check sync/async behavior, units/ranges, lifetime/context, buffer ownership and concurrency.
3. Check versioning, negotiation, timeout/retry/cancel and error semantics.
4. Compare old/new contracts for compatibility, migration and rollback.
5. Record ambiguous or underspecified semantics as findings rather than choosing a hidden convention.

## Outputs
- Interface review with contract findings and compatibility risks.
- Explicit breaking/unknown semantics and required changes or evidence.
- Verification scenarios for normal, error, version and lifecycle paths.

## Evidence Rules
- Contract claims come from authoritative spec/source or direct protocol evidence.
- One successful integration does not prove backward/error-path compatibility.
- Assumed ownership/lifetime rules must remain labeled as assumptions until confirmed.

## BLOCK Conditions
- Authoritative interface definition cannot be identified.
- Producer/consumer versions or ownership semantics are unknown and materially affect compatibility.
- Required breaking-change/rollback decision lacks an accountable owner.

## Verification / Review Handoff
- Architecture owns contract analysis; component owners implement changes.
- Verification tests the specified scenarios independently.
- Review can assess residual compatibility risk but cannot rewrite a failed Verification result.

## Evaluation
- Positive case: a versioned interface change yields explicit compatibility/rollback findings.
- Negative case: happy-path-only evidence does not pass compatibility review.
- Failure case: ambiguous ownership/timeout semantics are surfaced as blocking findings.

## Known Limits / Change Notes
- This Skill reviews the contract, not every implementation defect behind it.
- Version 1.0.0 adds review-grade definition without changing canonical ownership.
