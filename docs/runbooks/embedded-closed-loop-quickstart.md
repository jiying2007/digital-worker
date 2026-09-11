# Embedded Domain Closed Loop V1 — Real Pilot Quickstart

- Status: active runbook
- Stage baseline: `docs/strategy/embedded-domain-closed-loop-v1.md`
- Four-repo baseline: `docs/strategy/four-repo-ai-operating-system.md`
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

## 4. Assemble Knowledge context

### 4.1 Preferred path: Knowledge Hub adapter

Configure a checked-out Knowledge Hub explicitly; digital-worker does not assume a user-local path:

```bash
export KNOWLEDGE_HUB_ROOT=/path/to/knowledge-hub
python scripts/embedded_knowledge.py adapter-status
```

Then use Hub-owned context/evidence surfaces through the adapter:

```bash
python scripts/embedded_knowledge.py context \
  --cwd "$PWD" \
  --query "<platform symptom subsystem>" \
  --task-type general \
  --context-budget small \
  --limit 3

python scripts/embedded_knowledge.py evidence-pack \
  --query "<platform symptom subsystem>" \
  --scope-ref repository:<repo-id>
```

The Knowledge Hub governed `digital-worker` project route is currently **pending governed registration**. If the route is unresolved, provider CI is blocked, or the checkout/surface is missing, keep Gate K `BLOCKED/NEEDS_REVIEW`; do not silently treat the adapter as successful.

### 4.2 Bootstrap fallback: local internal-seed catalog

The 50-entry local catalog remains bootstrap-only:

```bash
python scripts/embedded_knowledge.py verify
python scripts/embedded_knowledge.py query --text "spi timeout debug evidence" --limit 10
```

The JSON result identifies `mode=bootstrap-local-catalog`. It is a candidate list only and does not represent Knowledge Hub lifecycle/ACL/promotion evidence. Source authority, version/revision, ACL and provenance still require verification.

## 5. Pin cross-repo execution identity

Before a cross-repo reproducibility claim, populate the refs-first envelope defined by:

`contracts/cross-repo/identity-envelope.yaml`

At minimum capture:

```text
work_item_id / run_id
Knowledge Hub provider commit + source fingerprint / evidence pack ref
ADK provider commit + version + profiles + asset bundle hash
runtime provider / target / version / execution receipt
repo exact base/result SHA + build/artifact/device identities
verification run + review refs
```

The selected provider pins are recorded in `config/integrations/cross-repo-lock.json`. A pin identifies what the Pilot consumed; it does **not** freeze the target architecture to one provider.

## 6. Select Agent assets through ADK

`digital-worker` keeps Expert identity and domain Gate semantics. Reusable execution assets are selected from `agent-dev-kit`, with `embedded-fullstack` as the required candidate profile for this integration stage.

Consult:

`expert-groups/embedded-system/config/skill-ownership-matrix.yaml`

A `WRAP_ADK` or `ADK_REUSE_CANDIDATE` classification does not remove the existing P0 Skill. Real Pilot evidence is required before promotion/replacement.

Record the ADK commit/version/profile and produced asset bundle hash in the identity envelope. Runtime-specific exporter or user-home paths must not be implemented in digital-worker.

## 7. Execute the engineering loop

Maintain the V1 spine throughout execution:

```text
work_item_id / run_id
  -> shared Material/System Context
  -> Knowledge Hub context/evidence refs (or explicit bootstrap fallback)
  -> Expert technical analysis / decision
  -> ADK profile/skill asset identity
  -> Engineering Agent Runtime execution identity
  -> exact source/build/artifact/device/test identity
  -> Acceptance -> Evidence
  -> independent Verification / Review
  -> Knowledge Harvest
```

Debug uses one shared Hypothesis Registry. Feature work records Integration Reconciliation when multiple domains/interfaces are involved. Runtime Provider may vary, but Contract / Gate / Action / Verification semantics do not.

## 8. Runtime comparison

For #18 or any controlled cross-runtime comparison, keep the same Work Item, exact base, Material/System Context, Knowledge fingerprint, Engineering Task Package, Acceptance and Verification standard.

`llm_agent` owns target-health/comparison/Loop Readiness evidence; `agent-dev-kit` owns Profile/Skill/target-asset identity; `digital-worker` owns the engineering and Verification judgement.

A Runtime completion is never a Verification PASS.

## 9. Complete the run

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

## 10. Route Knowledge Harvest

`NO_KNOWLEDGE_DELTA` ends the knowledge branch without manufacturing a document.

For evidence-backed `KNOWLEDGE_CANDIDATE`, follow `contracts/cross-repo/knowledge-harvest-handoff.yaml`. The proposal JSON schema remains owned by Knowledge Hub; digital-worker must not fork it.

Once a valid Hub proposal has been produced according to the provider contract:

```bash
python scripts/embedded_knowledge.py proposal-route \
  --proposal <PROPOSAL_JSON>
```

This may route the candidate to reviewing/owner review. It does **not** directly write active knowledge and does not imply promotion.

## 11. Closure rules

A run is not successful merely because code builds. Before closure check:

- all required Acceptance Criteria have concrete Evidence mapping;
- no cross-layer PASS inference;
- relevant source/artifact/device/test identities are exact or explicitly unresolved;
- Knowledge/ADK/Runtime provider identities are pinned when they materially contributed;
- Verification and Review independence is preserved;
- Knowledge Harvest is finalized as either `NO_KNOWLEDGE_DELTA` or an evidence-backed proposal candidate;
- observations are fed back to #26 rather than immediately creating a new Schema/Agent/Platform.

## 12. Current implementation boundary

This runbook deliberately does **not** require a new RAG, Vector DB, Context Broker, Knowledge Graph, Integration Expert, runtime exporter, or Artifact-Lineage database inside digital-worker. Those responsibilities either belong to another control plane or remain evidence-driven future options.
