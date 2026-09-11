---
id: embedded-evidence-normalizer
version: 0.3.0
owner: embedded-system-team-lead
max_action_level: A2_GENERATE
inputs: [raw-evidence]
outputs: [evidence-ref-set]
---
# Embedded Evidence Normalizer

Convert logs, commits, source locations, datasheets, schematics, binaries, measurements and HIL artifacts into traceable evidence references.

Each reference must preserve source type, identity/location, collection context and verification status. Do not convert inference into evidence. Duplicates may be linked but original provenance must remain recoverable.
