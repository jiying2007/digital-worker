# Embedded Domain Closed Loop V1 — Real Pilot Quickstart

- Repository stage: `iterative-development`
- Scope: real Debug / Feature / Review-Release
- Detailed runbook: `docs/runbooks/embedded-pilot.md`
- Machine policy: `expert-groups/embedded-system/pilot/pilot-plan.yaml`

## 1. Real task identity

A real task must have:

- stable `work_item_id`；
- human owner；
- repo root；
- **full 40-hex immutable base SHA**；
- Acceptance Criteria；
- required Verification；
- explicit A0-A7 boundary。

Never start a real run from a short SHA, mutable branch-only identity, placeholder source, or synthetic production evidence.

## 2. Init + scaffold

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

Unknown context stays `missing / BLOCKED`.

Debug supports `reproduction OR authoritative log`，但 source/device/build identity 仍必须可追溯。

## 3. Engineering / Runtime boundary

Stable chain:

```text
Task / Material Context
→ Edge Coordination
→ Domain Expert / Capability
→ Engineer + replaceable Engineering Agent Runtime
→ Delivery Receipt
→ Verification
→ optional Independent Review when available
→ Closure
```

Runtime-local PASS is not Domain Verification PASS.

Runtime Provider / profile remains owned by Runtime Binding and must not redefine Domain responsibility or release authority.

## 4. Current-stage Review policy

Current stage = `iterative-pilot`.

Independent Review is **preferred but not a hard completion gate when unavailable**.

Allowed substitute:

```text
static checks
+ Hosted CI
+ traceable Verification Report
```

Substitution does not mean:

```text
Independent Review PASS
Device PASS
HIL PASS
Release PASS
Production Ready
```

`verification_report_ref` remains required for all three tracks.

For Review/Release, real device/release evidence and applicable A7 human decision remain mandatory; CI cannot waive them.

## 5. Complete

Feature example:

```bash
python scripts/embedded_pilot.py complete <RUN_DIR> \
  --engineering-task-package <ENGINEERING_TASK_PACKAGE_JSON> \
  --delivery-receipt <DELIVERY_RECEIPT_JSON> \
  --verification-report <VERIFICATION_REPORT_JSON> \
  --pilot-result <PILOT_RESULT_JSON> \
  --extra material_manifest=<MATERIAL_MANIFEST_JSON> \
  --extra acceptance_evidence_matrix=<ACCEPTANCE_EVIDENCE_MATRIX_MD> \
  --extra knowledge_harvest=<KNOWLEDGE_HARVEST_MD>
```

If Independent Review exists, add:

```text
--review-report <REVIEW_REPORT_JSON>
```

Debug also adds:

```text
--extra hypothesis_registry=<HYPOTHESIS_REGISTRY_JSON>
```

A completed run is terminal. Corrections require a superseding run.

## 6. Validate + Edge receipt

```bash
python scripts/embedded_pilot.py validate <RUN_DIR>
python scripts/embedded_pilot.py edge-shadow <RUN_DIR>
```

A real receipt is phase-3 eligible only when:

- source is real；
- run is completed；
- result exists；
- outcome is PASS；
- unauthorized actions = 0；
- audit trace complete。

Independent Review is not an eligibility field in the current iterative stage.

## 7. Aggregate readiness

```bash
python scripts/embedded_pilot.py phase3-readiness \
  <RUNS_ROOT> \
  --output edge-foundation-phase3-readiness.json \
  --require-ready
```

Required:

```text
Debug         >= 1 eligible real receipt
Feature       >= 1 eligible real receipt
ReviewRelease >= 1 eligible real receipt
Total         >= 3
incorrect_pass_rate = 0
unauthorized_actions = 0
audit_trace_completeness = 1.0
```

Current status:

```text
Feature       = DONE (`FEATURE-PCR02-OTA-001`)
Debug         = OPEN
ReviewRelease = OPEN
Phase-3       = BLOCKED
```

Therefore `canonical_routing_switched=false` remains mandatory.

## 8. Current next work

- #6: SSC305/UBIFS exact source + raw log/reproduction + device identity；
- #8: PCR02 device OTA install/boot/rollback evidence + required Verification + A7 decision；
- 3/3 eligible 后才进入 canonical-switch review；
- switch 稳定后再 deprecate / physically remove legacy 1+7。
