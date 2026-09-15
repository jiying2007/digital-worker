# Embedded Domain Closed Loop — Real Pilot Quickstart

- Status: active runbook
- Repository stage: `iterative-development`
- Canonical domain: `domains/edge-foundation/domain.yaml`
- Canonical routing: `domains/edge-foundation/routing.yaml`
- Scope: real Debug / Feature / Review-Release runs
- Product readiness: independent from routing authority

## 1. Register the real task

Use the Embedded Expert Pilot issue template. A real task must have stable `work_item_id`, human owner, repo root and a **full 40-hex immutable base commit SHA**. Branch names, tags and short SHAs are not accepted as real-run source identity.

## 2. Initialize and scaffold

```bash
python scripts/edge_pilot.py init \
  --run-id <RUN_ID> \
  --track <debug|feature|review_release> \
  --source-type real \
  --task-type <TASK_TYPE> \
  --workflow-mode <MODE> \
  --human-owner <OWNER> \
  --task-brief <TASK_BRIEF_JSON> \
  --repo-root <REPO_ROOT> \
  --base-commit <FULL_40_HEX_SHA>

python scripts/edge_pilot_scaffold.py \
  domains/edge-foundation/pilot/runs/<RUN_ID>
```

Scaffold creates Material Manifest, Acceptance→Evidence Matrix, Knowledge Harvest, and for Debug one shared Hypothesis Registry. Unknown context stays `missing/BLOCKED`.

## 3. Resolve Formal Runtime identity

Before Engineering execution, bind exact source, Engineering Task Package, provider locks, ADK immutable release/source-set, Runtime distribution/profile/host, Session Bootstrap, sandbox/approval and Execution Receipt. A Runtime-local PASS never means Verification PASS or Release Ready.

## 4. Resolve Knowledge context

```bash
python scripts/edge_knowledge.py verify
python scripts/edge_knowledge.py query --text "<task terms>" --limit 10
```

For Knowledge Hub:

```bash
export KNOWLEDGE_HUB_ROOT=/path/to/exact-pinned/knowledge-hub
python scripts/edge_knowledge.py adapter-status
python scripts/edge_knowledge.py context \
  --cwd "$PWD" --query "<platform symptom subsystem>" \
  --task-type general --context-budget small --limit 3
```

Provider HEAD/contract digest drift must fail closed. Knowledge hit is a candidate, not automatic authority.

## 5. Execute against canonical responsibility

```text
Task Brief
→ Material/System Context
→ Edge Coordination
→ canonical routing
→ Embedded System Expert / required Capability(s)
→ Technical Decision
→ Engineering Package(s)
→ Engineer + Runtime
→ Delivery Receipt
→ Verification
→ Review according to current-stage policy
→ Closure / Knowledge Harvest
```

Debug uses one shared Hypothesis Registry. Multi-repo Feature uses one Run with multiple exact Engineering Packages where appropriate.

## 6. Complete once

```bash
python scripts/edge_pilot.py complete <RUN_DIR> \
  ...track-specific structured artifacts... \
  --verification-report <VERIFICATION_JSON> \
  --pilot-result <PILOT_RESULT_JSON> \
  --extra material_manifest=<RUN_DIR>/working/material-manifest.json \
  --extra acceptance_evidence_matrix=<RUN_DIR>/working/acceptance-evidence-matrix.md \
  --extra knowledge_harvest=<RUN_DIR>/working/knowledge-harvest.md
```

Debug adds `hypothesis_registry`. Feature adds Engineering Task Package and Delivery Receipt. When Independent Review is available, attach `--review-report`; when unavailable in the current iterative Pilot stage, the explicit substitute remains Verification + static checks + Hosted CI and must not be labeled Review PASS.

`complete` freezes `evidence-bundle.json`; completed/cancelled Run cannot be reopened or rebundled. Corrections require a superseding Run.

```bash
python scripts/edge_pilot.py validate <RUN_DIR>
```

## 7. Generate canonical receipt

```bash
python scripts/edge_pilot.py receipt <RUN_DIR>
```

Receipt must state `routing_authority=edge-foundation` and `canonical_routing=true`. A real completed PASS with zero unauthorized action and complete audit trace may set `product_readiness_eligible=true`.

## 8. Aggregate Product readiness

```bash
python scripts/edge_pilot.py product-readiness \
  domains/edge-foundation/pilot/runs \
  --output edge-foundation-product-readiness.json \
  --require-ready
```

Current state remains Feature=1, Debug=0, Review/Release=0 → **BLOCKED**. Product readiness does not control or revert canonical routing. 3/3 only permits Productionization Review; it does not auto-release or auto-promote.

## 9. Knowledge Harvest

`NO_KNOWLEDGE_DELTA` is valid. Evidence-backed candidates route to Knowledge Hub lifecycle:

```bash
python scripts/edge_knowledge.py proposal-route --proposal <PROPOSAL_JSON>
```

Do not copy authoritative source content into digital-worker just to satisfy the process.

## 10. Safety invariants

Always preserve:

- full source/artifact/device/test identity;
- Acceptance → Evidence mapping;
- Engineering ≠ Verification ≠ Review;
- no cross-layer PASS inference;
- no unauthorized A5/A6/A7 action;
- Source of Truth stays at source;
- product maturity and routing authority are separate concerns;
- repeated real evidence is required before adding new Schema/Skill/Capability/Expert/platform layer.
