# Embedded Domain Closed Loop V1 — Real Pilot Quickstart

- Status: active runbook
- Stage baseline: `docs/strategy/embedded-domain-closed-loop-v1.md`
- Trust gate: `docs/strategy/r0-trust-closure.md`
- Cross-repo baseline: `docs/strategy/four-control-planes-runtime-bindings.md`
- Scope: first real Debug / Feature / Review-Release runs

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

## 3. Assemble Knowledge context from the exact locked provider

The local 50-entry registry is bootstrap-only. Long-term context/evidence/lifecycle belongs to Knowledge Hub.

`KNOWLEDGE_HUB_ROOT` must point to the **exact commit pinned in** `config/integrations/cross-repo-lock.json`, not simply the latest local Knowledge Hub checkout. The adapter checks both Git HEAD and the canonical digest of `registry/integrations/digital-worker.json` and fails closed with `BLOCKED_PROVIDER_IDENTITY_MISMATCH` on drift.

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

## 4. Pin the cross-plane identity spine

Use `contracts/cross-repo/identity-envelope.yaml`. At minimum bind:

```text
work_item_id / run_id
Knowledge Hub exact commit + source fingerprint / evidence pack ref
ADK exact commit + version + Asset Profile + provider-produced bundle hash
Runtime Binding repository + exact commit + target + Runtime Profile + host
runtime/model/MCP/sandbox/approval identity + Execution Receipt ref
repo exact base/result SHA + build/artifact/device identities
verification run + review refs
```

`Asset Profile` and `Runtime Profile` are distinct identities:

```text
ADK Asset Profile     = embedded-fullstack
Codex Runtime Profile = token-lean or team-collab
Runtime Target        = codex-cli
```

The lock intentionally may lag provider main. Freshness is not compatibility. Pin promotion requires a real checkout at the exact SHA plus contract version/digest verification by `scripts/verify_cross_repo_checkouts.py`.

## 5. ADK and Runtime Binding

`digital-worker` owns Expert identity, Domain Gate, Verification and Review. Reusable Agent/Skill assets belong to `agent-dev-kit`; runtime distribution/host integration belongs to a replaceable Runtime Binding.

For Codex, the binding is `jiying2007/codex`. The current binding remains `BLOCKED_ASSET_BUNDLE_IDENTITY` until ADK emits a provider-produced `embedded-fullstack -> codex-cli` bundle identity and Codex proves consumption of the same bundle. Git blob SHA, consumer lock hash, short commit or tag is not a substitute.

A Runtime Execution Receipt records execution facts only and must never contain or imply:

```text
verification_pass
release_ready
domain_gate_pass
```

Runtime-local success is not digital-worker Verification PASS.

## 6. Execute the task

Maintain one V1 spine:

```text
work_item_id / run_id
  -> shared Material/System Context
  -> Knowledge context/evidence refs
  -> Expert analysis / decision
  -> ADK Asset Profile / bundle identity
  -> Runtime Binding exact identity
  -> Runtime Execution Receipt
  -> exact source/build/artifact/device/test identity
  -> Acceptance -> Evidence
  -> independent Verification / Review
  -> Knowledge Harvest
```

Debug uses one shared Hypothesis Registry. Feature work records Integration Reconciliation where multiple domains/interfaces are involved. Device write/OTA/release remains behind the existing A0-A7 human gates.

## 7. Complete exactly once

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

Validation recomputes every referenced artifact SHA-256 and requires the live artifact set to match the frozen bundle. Any post-completion artifact modification therefore invalidates the run until a new superseding run is created.

## 8. Runtime comparison

For #18, freeze Work Item, exact base, Material/System Context, Knowledge fingerprint, Engineering Task Package, Acceptance, ADK Asset Profile/bundle and Verification standard. Each candidate gets an independent Runtime Binding/Profile/Execution Receipt. The next Runtime must not receive the previous Runtime's final answer or patch.

`llm_agent` owns runtime health/comparison/Loop Readiness evidence; digital-worker retains the final engineering Verification/Review judgment.

## 9. Knowledge Harvest

`NO_KNOWLEDGE_DELTA` is valid. For evidence-backed `KNOWLEDGE_CANDIDATE`, use `contracts/cross-repo/knowledge-harvest-handoff.yaml`; digital-worker does not fork the Knowledge Hub proposal schema.

```bash
python scripts/embedded_knowledge.py proposal-route --proposal <PROPOSAL_JSON>
```

This only routes a candidate for Hub lifecycle/owner review; it never directly creates active knowledge.

## 10. Closure gate

Before accepting a real completed run:

- `scripts/verify_repository_governance.py` must report server-side governance PASS;
- `scripts/verify_cross_repo_checkouts.py` must verify every materially used locked provider/binding;
- all Acceptance Criteria map to concrete Evidence;
- source/artifact/device/test identity is exact or explicitly unresolved;
- Runtime Execution Receipt is retained when a binding executed work;
- Verification and Review independence is preserved;
- `incorrect_pass=0` and no unauthorized action;
- Knowledge Harvest is finalized;
- observations feed #26 before new Schema/Agent/Platform is proposed.

## 11. Current implementation boundary

Do not add a unified Knowledge Platform, Vector DB, Context Broker, Knowledge Graph, Integration Expert, central Runtime Gateway or Runtime-specific exporter to digital-worker without repeated real evidence. The stable model remains **4 control planes + N replaceable Runtime Bindings**.
