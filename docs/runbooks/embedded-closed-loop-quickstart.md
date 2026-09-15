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

Formal evidence work uses **L2 / formal-evidence** semantics. The cross-repo lock must report the selected Runtime Binding as `SOURCE_SET_BOUND`; ADK delivery remains `exact-source-set-reference`. Asset Profile and Runtime Profile are separate identities: current ADK Asset Profile is `embedded-fullstack`, while Codex Runtime Profile remains **default (runtime-owned)** unless the Runtime itself selects another profile.

The frozen identity spine is described by `contracts/cross-repo/identity-envelope.yaml`. At minimum retain:

```text
source repo + exact commit
ADK release / tree / manifest blob / exact source-set reference
Runtime Binding repository + exact commit
runtime target / Runtime Profile / runtime host
runtime distribution identity
Session Bootstrap reference
Execution Receipt reference
```

For Codex formal sessions, the Runtime Binding owns the thin bootstrap surface such as `session-bootstrap.sh`; digital-worker does not duplicate Runtime-private home/config. The Session Bootstrap is not a fifth control plane and must not contain a domain Verification PASS.

For current Formal runs, the Digital Worker Engineering Task Package is the authority for `package_id + work_item_id + run_id + base_commit`. Codex Session Bootstrap 1.2 freezes these fields into the exact Execution Source Set and projects the same Work/Run identity to Runtime Receipt v2; Runtime must not invent an independent Work/Run identifier.

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

python scripts/edge_knowledge.py evidence-pack \
  --query "<platform symptom subsystem>" \
  --scope-ref repository:<repo-id>
```

Provider HEAD/contract digest drift must fail closed. Knowledge hit is a candidate, not automatic authority. The local Registry only indexes target contracts and human entrypoints; authoritative external content remains in Knowledge Hub or the original Source of Truth.

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

### 5.1 Bind Formal Verification / Review to the frozen subject

When a Verification or Independent Review decision is used as **L2 Formal Evidence**, validate its provenance against the exact Session Bootstrap before treating that report as current:

```bash
python scripts/validate_formal_assurance.py \
  --session-bootstrap <L2_SESSION_BOOTSTRAP_JSON> \
  --verification-report <VERIFICATION_REPORT_JSON> \
  --output <FORMAL_ASSURANCE_VALIDATION_JSON>
```

When Independent Review is required by the task/release policy:

```bash
python scripts/validate_formal_assurance.py \
  --session-bootstrap <L2_SESSION_BOOTSTRAP_JSON> \
  --verification-report <VERIFICATION_REPORT_JSON> \
  --review-report <REVIEW_REPORT_JSON> \
  --require-review
```

Formal reports must bind the exact frozen `work_identity.run_id`, exact `execution_source_set.identity` and exact result identity, name the decision actor, retain independence/input evidence, and carry `report_sequence + supersedes`. A report whose Work/Run, source-set or result is stale is `BLOCKED`; do not edit or silently relabel it as current. A rerun uses a new `report_id`; sequence >1 supplies the immediately prior report with `--prior-verification-report` / `--prior-review-report` so supersession can be audited.

This stronger gate is conditional on L2 Formal use. Historical/current-stage non-Formal Pilot reports remain valid under the additive v1 report schemas and are not retroactively rewritten. `formal-assurance-provenance-validation/v1` proves provenance conformance only; it does **not** imply Product Qualification, Release Ready, or release authorization.

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

### 9.1 Validate real Knowledge reuse for E3

Only after a **real Work Item** actually consumes a real governed Knowledge item/source should the operator assemble `knowledge-reuse-evidence.v1`. The evidence file must carry the exact provider identity, authority/source/version, ACL and freshness evidence, provenance, actual-use refs and Knowledge Harvest ref. Digital Worker deliberately does not generate or auto-fill a “real evidence” template.

Use the canonical Knowledge entrypoint to evaluate the completed evidence:

```bash
python scripts/edge_knowledge.py reuse-evidence \
  --evidence <KNOWLEDGE_REUSE_EVIDENCE_JSON> \
  --output <KNOWLEDGE_REUSE_RECEIPT_JSON> \
  --require-eligible
```

The command delegates to the domain-owned `evaluate_knowledge_reuse_evidence.py` gate. Missing files, synthetic/controlled evidence, provider identity drift, non-real source, unresolved/denied ACL, stale source or authority conflict remain fail-closed. `ELIGIBLE` means only that this specific real Knowledge reuse evidence is admissible for the E3 reuse claim; it does not imply Knowledge Provider Qualification, Product Readiness, Terminal Maturity, Production Ready or Release Ready.

## 10. Safety invariants

Always preserve:

- full source/artifact/device/test identity;
- Acceptance → Evidence mapping;
- Engineering ≠ Verification ≠ Review;
- no cross-layer PASS inference;
- no unauthorized A5/A6/A7 action;
- Source of Truth stays at source;
- Asset Profile ≠ Runtime Profile;
- Runtime execution receipt ≠ domain Verification PASS;
- L2 Formal report ≠ current unless exact Work/Run / Execution Source Set / result / actor / supersession provenance validates;
- formal provenance validation ≠ Product Qualification / Release Ready / release authorization;
- Knowledge reuse eligibility ≠ provider/product/terminal/release qualification;
- product maturity and routing authority are separate concerns;
- repeated real evidence is required before adding new Schema/Skill/Capability/Expert/platform layer.

## 11. Repository governance boundary

Current `iterative-development` stage still requires repository-local CI, but server-side main protection is intentionally not a real-Pilot completion gate. Before Productionization or protected multi-contributor operation, strict governance must pass:

```bash
python scripts/verify_repository_governance.py --strict
```

A deferred server-side governance state must never be misreported as strict production governance PASS.
