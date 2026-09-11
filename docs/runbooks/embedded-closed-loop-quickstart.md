# Embedded Domain Closed Loop V1 — Real Pilot Quickstart

- Status: active runbook
- Stage baseline: `docs/strategy/embedded-domain-closed-loop-v1.md`
- Scope: first real Debug / Feature / Review-Release runs

## 1. Register the real task

Use the `Embedded Expert Pilot` issue template. A real task must have a stable `work_item_id`, human owner, repo root and **exact immutable base commit SHA**. Do not bind a real run only to `main` / `dev`.

## 2. Create task-brief and initialize the run

```bash
python scripts/embedded_pilot.py init \
  --run-id <RUN_ID> \
  --track <debug|feature|review_release> \
  --source-type real \
  --task-type <TASK_TYPE> \
  --workflow-mode <MODE> \
  --human-owner <OWNER> \
  --task-brief <TASK_BRIEF_JSON> \
  --repo-root <REPO_ROOT> \
  --base-commit <EXACT_SHA>
```

## 3. Scaffold the V1 working artifacts

```bash
python scripts/embedded_pilot_scaffold.py \
  expert-groups/embedded-system/pilot/runs/<RUN_ID>
```

This creates under `working/`:

- `material-manifest.json`
- `acceptance-evidence-matrix.md`
- `knowledge-harvest.md`
- Debug only: `hypothesis-registry.json`

The scaffold is intentionally fail-safe: unresolved device/test/reproduction/context identity remains `missing` and the Material Manifest may start as `BLOCKED`. Fill it from trusted sources; never change missing context to READY by assumption.

## 4. Find candidate Knowledge

Verify the Registry first:

```bash
python scripts/embedded_knowledge.py verify
```

Search by task terms, domain or tag:

```bash
python scripts/embedded_knowledge.py query --text "spi timeout debug evidence" --limit 10
python scripts/embedded_knowledge.py query --domain linux-bsp --limit 10
python scripts/embedded_knowledge.py query --tag verification --limit 10
```

Registry results are **candidates**, not automatic truth. At task-use time confirm source authority, version/revision, ACL and provenance. Record reused Registry IDs or real external source refs in the task context / Knowledge Harvest.

## 5. Execute the engineering loop

Maintain the V1 spine throughout execution:

```text
work_item_id / run_id
  -> shared Material/System Context
  -> technical analysis / decision
  -> exact source identity
  -> engineering package / receipt
  -> exact artifact/device/test identity
  -> Acceptance -> Evidence
  -> independent verification/review
  -> Knowledge Harvest
```

Debug uses one shared Hypothesis Registry. Feature work records Integration Reconciliation when multiple domains/interfaces are involved. Runtime Provider may vary, but Contract / Gate / Action / Verification semantics do not.

## 6. Complete the run

Copy the reviewed working artifacts into the evidence bundle through `--extra`:

```bash
python scripts/embedded_pilot.py complete <RUN_DIR> \
  ...track-specific structured artifacts... \
  --extra material_manifest=<RUN_DIR>/working/material-manifest.json \
  --extra acceptance_evidence_matrix=<RUN_DIR>/working/acceptance-evidence-matrix.md \
  --extra knowledge_harvest=<RUN_DIR>/working/knowledge-harvest.md
```

Debug additionally supplies:

```bash
--extra hypothesis_registry=<RUN_DIR>/working/hypothesis-registry.json
```

Then:

```bash
python scripts/embedded_pilot.py validate <RUN_DIR>
python scripts/embedded_pilot.py bundle <RUN_DIR> --fail-incomplete
```

## 7. Closure rules

A run is not successful merely because code builds. Before closure check:

- all required Acceptance Criteria have concrete Evidence mapping;
- no cross-layer PASS inference;
- relevant source/artifact/device/test identities are exact or explicitly unresolved;
- Verification and Review independence is preserved;
- Knowledge Harvest is finalized as either `NO_KNOWLEDGE_DELTA` or an evidence-backed candidate;
- observations are fed back to #26 rather than immediately creating a new Schema/Agent/Platform.

## 8. Current implementation boundary

This runbook deliberately does **not** require a unified Knowledge Platform, Context Broker, Knowledge Graph, Integration Expert, or new Artifact-Lineage Schema. Those remain evidence-driven future options.
