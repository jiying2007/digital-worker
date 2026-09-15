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

Normalize logs, commits, source locations, datasheets, schematics, binaries, measurements and HIL artifacts into traceable Evidence references.

## Method
Preserve source type, object identity/location, collection context, timestamp/run identity and verification state. Link duplicates without destroying original provenance.

## Block
Inference is not Evidence. Missing source identity, version, origin or collection context must remain explicit instead of being filled by guesswork.
