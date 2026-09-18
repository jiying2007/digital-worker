---
id: device-tree-review
version: 1.0.0
owner_kind: capability
owner: embedded.linux-bsp
max_action_level: A2_GENERATE
inputs: [dts-dtb, board-identity, driver-evidence]
outputs: [technical-analysis]
---
# Device Tree Review

## Purpose
Review Device Tree resources and driver binding against the exact board/platform revision and the consuming driver's contract.

## Use When
- Board bring-up, BSP porting and peripheral enablement.
- Driver probe/resource failures involving DT bindings.
- Revision changes to clocks, resets, pinctrl, regulators, interrupts or reserved memory.

## Do Not Use For
- Inferring electrical truth from DT alone when schematic/board evidence is needed.
- Reusing another board revision's resource assumptions as target evidence.
- Proving runtime behavior without device evidence.

## Required Inputs
- Exact board/platform revision identity.
- DTS/DTB or generated tree being reviewed.
- Driver/binding source or authoritative expectations for consumed resources.

## Optional Inputs
- Schematic, TRM/binding docs and boot/runtime logs.
- Known-good board revision diff.
- Clock/reset/power measurements.

## Method
1. Bind the DTS/DTB to the exact target image and board revision.
2. Check `compatible`, address/reg, IRQ/GPIO, clocks/resets/regulators, pinctrl, aliases and reserved memory as applicable.
3. Trace dependencies, probe/defer behavior and resource ownership into the exact driver source.
4. Compare revision-specific differences against authoritative board facts.
5. Record unknown electrical/resource facts as escalation/evidence gaps instead of silently inheriting another board's values.

## Outputs
- Technical analysis of DT/resource/binding consistency.
- Revision-specific findings and unresolved hardware facts.
- Required runtime/device verification scenarios.

## Evidence Rules
- DT text proves configured intent, not electrical reality.
- Binding/driver source proves software expectations, not successful target behavior.
- Board-specific claims require exact revision evidence.

## BLOCK Conditions
- Board revision or DTS/DTB identity is unknown/mismatched.
- Required electrical/resource facts are unavailable and materially affect the conclusion.
- The review would need to assume a binding/resource not present in authoritative source.

## Verification / Review Handoff
- Linux/BSP owns DT analysis; unresolved electrical facts escalate to Hardware.
- Driver/component owners consume findings for implementation.
- Verification checks probe/resource/runtime behavior on the exact target.

## Evaluation
- Positive case: DT and driver expectations align with exact board resources.
- Negative case: revision mismatch is detected and blocks reuse.
- Cross-domain case: an electrical uncertainty becomes a Hardware evidence request rather than a software guess.

## Known Limits / Change Notes
- This Skill is not a schematic or signal-integrity review.
- Version 1.0.0 adds contract detail without changing owner or action level.
