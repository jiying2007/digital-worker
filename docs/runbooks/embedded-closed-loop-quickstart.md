# Embedded Domain Closed Loop V1 — Real Pilot Quickstart

- Status: active runbook
- Stage baseline: `docs/strategy/embedded-domain-closed-loop-v1.md`
- Target operating model: `docs/strategy/ai-rd-target-operating-model.md`
- Trust baseline: `docs/strategy/r0-trust-closure.md`
- Repository stage: `iterative-development`
- Scope: real Debug / Feature / Review-Release runs

## 1. Register the real task

Use the `Embedded Expert Pilot` issue template. A real task must have a stable `work_item_id`, human owner, repo root and a **full 40-hex immutable base commit SHA**. Branch names, tags and short SHAs are not accepted as real-run source identity.

## 2. Initialize and scaffold

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
  --base-commit <FULL_40_HEX_SHA>

python scripts/embedded_pilot_scaffold.py \
  expert-groups/embedded-system/pilot/runs/<RUN_ID>
```

The scaffold creates `material-manifest.json`, `acceptance-evidence-matrix.md`, `knowledge-harvest.md`, and for Debug one shared `hypothesis-registry.json`. Unknown device/test/reproduction/context identity stays `missing/BLOCKED`; never turn missing context into READY by assumption.

## 3. Resolve the L2 Formal session before Runtime execution

The Codex Runtime Binding implements the frozen thin Session Bootstrap. L2 must use the exact identities locked by digital-worker; it is not a second workflow engine and cannot produce Domain Verification PASS.

```bash
rtk bash ~/codex/scripts/session-bootstrap.sh \
  --cwd <REPO_ROOT> \
  --task "<formal task>" \
  --formal \
  --base-commit <FULL_40_HEX_SHA> \
  --engineering-task-package <ENGINEERING_TASK_PACKAGE_JSON> \
  --digital-worker-root <DIGITAL_WORKER_ROOT> \
  --knowledge-root <EXACT_PINNED_KNOWLEDGE_HUB_ROOT> \
  --summary-json
```

The bootstrap must resolve `L2 / formal-evidence`, validate the Codex Runtime Binding as `SOURCE_SET_BOUND`, retain the ADK immutable release/source-set identity, and verify the Knowledge checkout identity described below. The current Codex distribution uses its neutral default runtime profile; Runtime-profile selection remains owned by the Runtime Binding and must not be hard-coded by digital-worker. A blocked bootstrap is a formal blocker, never a PASS.

## 4. Assemble Knowledge context from the exact locked provider

The local registry is bootstrap-only. Long-term context/evidence/lifecycle belongs to Knowledge Hub.

`KNOWLEDGE_HUB_ROOT` must point to the **exact commit pinned in** `config/integrations/cross-repo-lock.json`, not simply the latest local Knowledge Hub checkout. The adapter and L2 Session Bootstrap check both Git HEAD and the canonical digest of `registry/integrations/digital-worker.json` and fail closed on drift.

```bash
export KNOWLEDGE_HUB_ROOT=/path/to/exact-pinned/knowledge-hub
python scripts/embedded_knowledge.py adapter-status

python scripts/embedded_knowledge.py context \
  --cwd "$PWD" \
  --query "<platform symptom subsystem>" \
  --task-type general --context-budget small --limit 3

python scripts/embedded_knowledge.py evidence-pack \
  --query "<platform symptom subsystem>" \
  --scope-ref repository:<repo-id>
```

If the route, ACL/authority, provider identity or public surface is unresolved, Gate K remains `BLOCKED/NEEDS_REVIEW`.

Bootstrap fallback remains explicit:

```bash
python scripts/embedded_knowledge.py verify
python scripts/embedded_knowledge.py query --text "spi timeout debug evidence" --limit 10
```

A bootstrap hit is only a candidate; authority/version/ACL/provenance still require verification.

## 5. Pin the cross-plane identity spine

Use `contracts/cross-repo/identity-envelope.yaml`. At minimum bind:

```text
work_item_id / run_id
Knowledge Hub exact commit + contract digest + source fingerprint / evidence pack ref
ADK provider contract commit + immutable v5.1.0 release identity + Asset Profile
Runtime exact source-set identity ref + runtime distribution identity ref
Runtime Binding repository + exact commit + target + Runtime Profile + host
Session Bootstrap ref + runtime/model/MCP/sandbox/approval identity + Execution Receipt ref
repo exact base/result SHA + build/artifact/device identities
verification run + review refs
```

`Asset Profile` and `Runtime Profile` remain distinct identities:

```text
ADK Asset Profile     = embedded-fullstack
Codex Runtime Profile = default (runtime-owned)
Runtime Target        = codex-cli
```

A monolithic Runtime bundle digest is **not** a required identity. ADK owns the immutable release and source-set handoff contract; the Runtime Binding owns exact source selection, Runtime-profile semantics and Runtime distribution assembly.

The lock intentionally may lag provider main. Freshness is not compatibility. Pin promotion requires a real checkout at the exact SHA plus contract version/digest verification by `scripts/verify_cross_repo_checkouts.py`.

## 6. ADK and Runtime Binding

`digital-worker` owns Expert identity, Domain Gate, Verification and Review. Reusable Agent/Skill assets belong to `agent-dev-kit`; runtime distribution/host integration belongs to a replaceable Runtime Binding.

For Codex, the locked target state is:

```text
ADK release baseline  = v5.1.0 @ 59cbd5cb40ca7077ee5407636bfc617e295ec7e5
ADK Asset Profile     = embedded-fullstack
ADK handoff           = exact-source-set-reference
Codex source identity = exact-release-source-blobs
Codex readiness       = SOURCE_SET_BOUND
Session Bootstrap     = active L0/L1/L2 thin bootstrap
Runtime profile       = neutral default, owned by Codex Runtime Binding
```

`SOURCE_SET_BOUND` means the Runtime source/distribution binding is identity-ready. It does **not** mean the engineering task passed Verification or the product is Release Ready.

A Runtime Execution Receipt records execution facts only and must never contain or imply:

```text
verification_pass
release_ready
domain_gate_pass
```

Runtime-local success is not digital-worker Verification PASS.

## 7. Execute the task

Maintain one V1 spine:

```text
work_item_id / run_id
  -> shared Material/System Context
  -> Knowledge context/evidence refs
  -> Expert analysis / decision
  -> ADK immutable release / Asset Profile
  -> Runtime exact source-set / distribution identity
  -> Session Bootstrap / Runtime Binding exact identity
  -> Runtime Execution Receipt
  -> exact source/build/artifact/device/test identity
  -> Acceptance -> Evidence
  -> independent Verification / Review
  -> Knowledge Harvest
```

Debug uses one shared Hypothesis Registry. Feature work records Integration Reconciliation where multiple domains/interfaces are involved. Device write/OTA/release remains behind the existing A0-A7 human gates.

## 8. Complete exactly once

Copy reviewed working artifacts into the run with `complete`:

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

`complete` creates the final `evidence-bundle.json` and then makes the run terminal. **Do not run `bundle` after completion.** A completed/cancelled run cannot be reopened or rebundled through the CLI; corrections require a superseding run so history remains auditable.

Validate the terminal evidence:

```bash
python scripts/embedded_pilot.py validate <RUN_DIR>
```

Validation recomputes every referenced artifact SHA-256 and requires the live artifact set to match the frozen evidence bundle. Any post-completion artifact modification therefore invalidates the run until a new superseding run is created.

## 9. Runtime comparison

For runtime comparison, freeze Work Item, exact base, Material/System Context, Knowledge fingerprint, Engineering Task Package, Acceptance, ADK immutable release/Asset Profile/source-set standard and Verification standard. Each candidate gets an independent Runtime Binding/Profile/source-set/distribution identity/Execution Receipt. The next Runtime must not receive the previous Runtime's final answer or patch.

`llm_agent` owns runtime health/comparison/Loop Readiness evidence; digital-worker retains the final engineering Verification/Review judgment.

## 10. Knowledge Harvest

`NO_KNOWLEDGE_DELTA` is valid. For evidence-backed `KNOWLEDGE_CANDIDATE`, use `contracts/cross-repo/knowledge-harvest-handoff.yaml`; digital-worker does not fork the Knowledge Hub proposal schema.

```bash
python scripts/embedded_knowledge.py proposal-route --proposal <PROPOSAL_JSON>
```

This only routes a candidate for Hub lifecycle/owner review; it never directly creates active knowledge.

## 11. Current-stage closure gate

Before accepting a real completed run in the current `iterative-development` stage:

- `scripts/verify_cross_repo_checkouts.py` must verify every materially used locked provider/binding plus the Codex Session Bootstrap contract;
- all Acceptance Criteria map to concrete Evidence;
- source/artifact/device/test identity is exact or explicitly unresolved;
- immutable ADK release, Runtime source-set and Runtime distribution identity are retained when a binding executed work;
- Runtime Execution Receipt is retained when a binding executed work;
- Verification and Review independence is preserved;
- `incorrect_pass=0` and no unauthorized action；
- Knowledge Harvest is finalized；
- repeated observations must exist before new Schema/Agent/Platform is proposed。

**Main branch protection is intentionally not a current-stage acceptance gate.** `python scripts/verify_repository_governance.py` remains advisory and may report `DEFERRED_CURRENT_STAGE` while main is unprotected.

Before Productionization / protected multi-contributor operation, run:

```bash
python scripts/verify_repository_governance.py --strict
```

Strict mode must PASS before the repository is treated as production-governed.

## 12. Current implementation boundary

Do not add a unified Knowledge Platform, Vector DB, Context Broker, Knowledge Graph, Integration Expert, central Runtime Gateway or Runtime-specific exporter to digital-worker without repeated real evidence. The stable model remains **4 control planes + N replaceable Runtime Bindings + thin Session Bootstrap inside each Runtime Binding**.
