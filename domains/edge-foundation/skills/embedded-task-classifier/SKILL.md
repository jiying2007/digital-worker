---
id: embedded-task-classifier
version: 1.0.0
owner_kind: role
owner: edge-coordination
max_action_level: A2_GENERATE
inputs: [task-brief]
outputs: [routing-decision]
---
# Embedded Task Classifier

## Purpose
Classify an embedded request into the canonical task taxonomy and select the smallest allowed responsibility path without manufacturing technical facts or expanding scope.

## Use When
- At task intake, when one primary task type must be selected.
- When a material scope change invalidates the existing route.
- When governance escalation requires the route and source set to be re-evaluated.

## Do Not Use For
- Root-cause diagnosis, architecture judgment, implementation design or Verification.
- Using a broad multi-domain route merely because context is incomplete.
- Inventing product, platform, risk or acceptance details that are absent from the task brief.

## Required Inputs
- Goal and expected outcome.
- Scope and known non-goals.
- Acceptance criteria or an explicit statement that they are unresolved.
- Enough product/platform context to distinguish routes when the taxonomy depends on it.

## Optional Inputs
- Existing evidence references and known incidents.
- Product stage, release/risk context and prior routing decisions.
- Known cross-domain triggers.

## Method
1. Normalize the request into goal, scope, non-goals, object identity and acceptance.
2. Choose exactly one primary canonical task type; record secondary concerns separately.
3. Check `domains/edge-foundation/routing.yaml` and `runtime/task-modes.yaml` for allowed mode and responsibilities.
4. Select the minimum required Expert/Capability/Assurance set and record evidence-driven expansion triggers rather than pre-loading every capability.
5. Emit unresolved ambiguities, stop conditions and required Assurance without converting them into technical conclusions.

## Outputs
- A routing decision containing primary task type, target mode, responsibilities and Assurance.
- Explicit unresolved context and any evidence-driven expansion trigger.
- A `needs_information`/blocked disposition when classification would otherwise require invented scope.

## Evidence Rules
- Classification claims must point to explicit task-brief facts or supplied evidence.
- A secondary concern does not become a primary route without a scope/evidence trigger.
- Unknown or contradictory context stays unknown; it is not normalized into a convenient default.

## BLOCK Conditions
- No canonical task type can be selected without changing the requested scope.
- Missing context would materially change the primary route or allowed mode.
- The request maps to an unsupported/unknown task type.

## Verification / Review Handoff
- Edge Coordination owns classification and routing metadata, not Embedded professional conclusions.
- Selected Capability owners determine engineering facts after handoff.
- Verification/Review remain independent and are not implied by a routing decision.

## Evaluation
- Positive case: a clear single-domain request maps to the minimal canonical route.
- Diagnostic case: expansion remains evidence-driven rather than eager.
- Negative case: an ambiguous/unknown task is blocked instead of defaulting to the largest workflow.

## Known Limits / Change Notes
- This Skill does not decide whether the engineering result is correct or complete.
- Version 1.0.0 hardens the human contract only; taxonomy, ownership, routing authority and action ceiling are unchanged.
