# Architecture Review End-to-End Walkthroughs

> 以下为 **illustrative walkthroughs**，用于检验架构是否连贯，不构成 real Pilot evidence，也不替代 #6/#7/#8。

## Walkthrough A — Debug：设备现场出现文件系统只读

```text
Field symptom
  → task-brief
  → Gate K/M/0
  → diagnostic_chain
  → shared System Context / material-manifest
  → Debug + BSP analysis
  → one Hypothesis Registry
  → experiment / evidence
  → root cause candidate
  → engineering-task-package
  → Engineering Agent Runtime
  → delivery-receipt
  → host/cross-build/device/HIL verification
  → independent review
  → RCA / knowledge candidate / closure
```

### 评审观察

- 所有专家是否共享同一 board/repo/base/firmware identity？
- 假设是否集中在同一 Registry，而不是多个专家各自产生“根因”？
- 修改后现象消失是否仍要求独立 Verification？
- RCA 是否可以反向形成 Golden Case / Skill candidate？

---

## Walkthrough B — Feature：Linux + MCU 多仓功能

```text
Product / technical request
  → embedded feasibility review
  → one expert-team run
  → Architecture defines interface / timing / resource constraints
  → BSP and MCU analysis can run in parallel
  → Driver/Component reconciles protocol and integration details
  → Integration Reconciliation before Gate T
  → one Technical Decision
  → Package A: Linux repo + exact SHA
  → Package B: MCU repo + exact SHA
  → Runtime executes independently per package
  → delivery receipts
  → system artifact set / firmware identities
  → device/HIL verification against acceptance criteria
  → independent review
```

### 评审观察

- 是否需要 One Run → Multiple Engineering Packages？
- 接口冲突在哪一阶段最早暴露？
- 是否需要把 Integration Reconciliation 正式化成 Skill？
- Acceptance 是否可以清楚映射到具体 Artifact / Device / Evidence？

---

## Walkthrough C — Review / OTA Readiness

```text
Release candidate identity
  → exact source / artifact / manifest
  → release_chain or review_only
  → existing CI / build / HIL / provenance evidence
  → Verification reads existing thread, does not invent missing PASS
  → Independent Review checks risk / waiver / rollback / unverified items
  → human Release Owner decision
```

### 评审观察

- Release 阶段是否还需要重新追问 binary/version/device identity？如果需要，说明上游 Artifact Lineage 断裂。
- HIL PASS 是否被错误推导成 Release PASS？
- Release Owner 是否独立于实施者与 AI Runtime？
- 缺 evidence 时系统能否明确 BLOCK，而不是补语言解释？

---

## 三条 Walkthrough 共通检查表

1. One Work Item 是否贯穿？
2. One System Context 是否共享？
3. Claim / Decision / Evidence 是否可追溯？
4. 多 repo 时 exact identity 是否保持？
5. Engineering Runtime 是否可替换而不改变 Contract？
6. Artifact identity 是否从 source 一路连到 device/HIL？
7. Acceptance 是否明确落到验证证据？
8. Verification / Review 是否保持独立？
9. Blocker / unverified item 是否在 Closure 前被保留？
10. 任务结束后是否产生可复用 Knowledge / Golden Case / Skill candidate？
