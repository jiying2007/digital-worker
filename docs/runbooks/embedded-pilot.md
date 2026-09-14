# 嵌入式真实 Pilot 执行说明

Pilot 用于验证 Embedded Domain Closed Loop V1 和端侧底座目标责任模型是否能在真实工程中闭环，不用于证明 AI 永远正确，也不直接授予 Production Ready。

当前机器基础设施为 `pilot-operations-ready`。三轨真实证据进度不同：Debug 已选题但等待产品源码/日志 identity；Feature 已完成真实 Engineering 与可复跑 Verification，等待 Independent Review 与终态 bundle；Review/Release 已完成 PCR02 OTA artifact / distribution evidence，等待设备侧 OTA 与独立 release review。

策略基线：`docs/strategy/embedded-domain-closed-loop-v1.md`。快速入口：`docs/runbooks/embedded-closed-loop-quickstart.md`。

## 1. 绑定真实任务

先形成 `task-brief v1`。真实 Pilot 必须有 human owner、repo root、**full 40-hex exact Git base SHA**、验收条件和 required verification。只提供 `main/dev` 等漂移分支名不得开始 real run。

同一 Run 的参与角色共享同一个 Work Item / Run Identity 和 Material/System Context，不各自重建版本事实。

## 2. 初始化与材料清单

```bash
python scripts/embedded_pilot.py init \
  --run-id <run-id> \
  --track <debug|feature|review_release> \
  --source-type real \
  --task-type <task-type> \
  --workflow-mode <mode> \
  --human-owner <owner> \
  --task-brief <task-brief.json> \
  --repo-root <repo-root> \
  --base-commit <full-40-hex-sha>

python scripts/embedded_pilot_scaffold.py \
  expert-groups/embedded-system/pilot/runs/<run-id>
```

Scaffold 不猜测未知事实。源码、日志、设备、测试环境等尚未确认时，Material Manifest（材料清单）应保持 `missing / BLOCKED`。

Material Manifest 的终态规则只有一套，由 `scripts/validate_material_manifest.py` 与 `scripts/embedded_pilot.py` 共同执行：

- `planned / running / blocked` 阶段允许 `readiness=BLOCKED`，用于诚实表达材料仍不完整；
- `complete` 前必须重新计算材料门槛；`BLOCKED` 不得进入 completed evidence bundle；
- `DEGRADED` 只有存在明确 `degradation_approved_by` 才可进入终态；
- completed run 后续 `validate` 会再次重算同一门槛并核对 frozen bundle；
- Debug 采用 **reproduction OR authoritative log**：稳定复现和可追溯原始日志至少一个可用；
- Material readiness 只回答“材料是否足以收口”，不替代 Verification（验证）或 Independent Review（独立审查）。

然后使用 `status ... running` 开始记录。

## 3. Knowledge 候选解析

当前 Registry：`expert-groups/embedded-system/knowledge/registry.yaml`。

```bash
python scripts/embedded_knowledge.py verify
python scripts/embedded_knowledge.py query --text "<task terms>" --limit 10
python scripts/embedded_knowledge.py query --domain <domain> --limit 10
```

查询结果只是候选 Knowledge。实际使用前仍需核对 Source authority / version / ACL / provenance；Knowledge Index 不替代权威 Source。

## 4. Engineering 执行

默认链路：

```text
Technical Decision
  → engineering-task-package
  → Engineer + Engineering Agent Runtime
  → delivery-receipt
  → Verification
  → Independent Review
```

Expert Team 默认 A0-A2；受控 Engineering 可使用 A3-A4；设备写和 Release 保留人工 Gate。Runtime Provider 可替换，但 Contract / Action Policy 不变。

Debug 强制使用 Observed / Inferred / Confirmed，并且同一 Run 只维护一份共享 `hypothesis_registry`。Feature 涉及多个仓库时优先 `One Run → Multiple Engineering Packages`，每个 Package 保持独立 exact base / scope / delivery identity。

## 5. Embedded Domain Closed Loop V1 运行产物

每条真实 Pilot 收口必须包含：

1. `material_manifest`：共享 Material/System Context Snapshot；
2. `acceptance_evidence_matrix`：Acceptance Criterion → Verification/Evidence；
3. `knowledge_harvest`：复用/新增知识结果，可合法为 `NO_KNOWLEDGE_DELTA`。

Debug 另外必须有 `hypothesis_registry`。

Feature 必须有 `engineering-task-package` 和 `delivery-receipt`。所有轨道都必须保留 Verification / Independent Review 和 exact source/artifact/test identity。

## 6. 收口与冻结证据

Feature 示例：

```bash
python scripts/embedded_pilot.py complete <run-dir> \
  --engineering-task-package <engineering-task-package.json> \
  --delivery-receipt <delivery-receipt.json> \
  --verification-report <verification.json> \
  --review-report <review.json> \
  --pilot-result <pilot-result.json> \
  --extra material_manifest=<run-dir>/working/material-manifest.json \
  --extra acceptance_evidence_matrix=<run-dir>/working/acceptance-evidence-matrix.md \
  --extra knowledge_harvest=<run-dir>/working/knowledge-harvest.md
```

Debug 再增加：

```text
--extra hypothesis_registry=<run-dir>/working/hypothesis-registry.json
```

`complete` 会校验结构化 Contract、Material Manifest terminal readiness、required artifacts，并生成 `evidence-bundle.json` 与 SHA-256。Completed run 是 terminal；修订历史证据必须创建 superseding run，不得改写旧 run。

后续校验：

```bash
python scripts/embedded_pilot.py validate <run-dir>
```

任何 material readiness、artifact set 或 SHA 漂移都必须 fail-closed。

## 7. Verification 与 Independent Review

Verification 与 Independent Review 不得由实施者自签，也不得用 Runtime-local PASS 推导 Domain Verification PASS。

Independent Review 至少检查：

- Work Item / Run / Context identity 是否一致；
- source / artifact / device / test identity 是否断链；
- Acceptance Criterion 是否逐项映射到 Evidence；
- Debug 是否只有一个共享 Hypothesis Registry；
- Material Manifest 是否真实 READY / approved DEGRADED；
- Knowledge Harvest 是否有证据或明确 `NO_KNOWLEDGE_DELTA`；
- 是否出现 context rebuild、重复分析、跨域接口晚发现；
- 是否有 unsupported claim、unauthorized action 或错误 PASS。

## 8. Knowledge Registry

首版 Registry 是 `internal-seed`，只登记仓库内可核验对象。NAS / 飞书 / CI-HIL / 历史 RCA 等外部 Source 后续按真实 Provider 接入；Registry 记录 Source identity，不复制权威原文形成第二 SSOT。

## 9. 汇总与 Pilot 评分

```bash
python scripts/embedded_pilot.py summary \
  expert-groups/embedded-system/pilot/runs \
  --output pilot-status.json

python scripts/evaluate_embedded_pilot.py \
  <pilot-result...> \
  --output pilot-metrics.json \
  --markdown-output pilot-metrics.md
```

门槛从 `expert-groups/embedded-system/pilot/pilot-plan.yaml` 读取。Synthetic 只验证工具链，不计入真实 Pilot promotion。

## 10. Edge Foundation shadow receipt 与 phase-3 readiness

真实 completed Pilot 通过 terminal integrity 后：

```bash
python scripts/embedded_pilot.py edge-shadow <run-dir>
```

默认生成：

```text
<run-dir>/edge-foundation-shadow-receipt.json
```

只有以下检查同时为真，才可得到 `phase3_evidence_eligible=true`：

- `source_real`；
- `run_completed`；
- `result_provided`；
- `outcome_pass`；
- `no_unauthorized_actions`；
- `audit_trace_complete`。

三轨聚合：

```bash
python scripts/embedded_pilot.py phase3-readiness \
  expert-groups/embedded-system/pilot/runs \
  --output edge-foundation-phase3-readiness.json \
  --require-ready
```

当前 promotion gate 要求 debug / feature / review_release 各至少 1 个 eligible real receipt、合计至少 3 个，同时 `incorrect_pass_rate=0`、`unauthorized_actions=0`、`audit_trace_completeness=1.0`。

`ELIGIBLE_FOR_REVIEW` 只表示允许发起独立 canonical-routing 评审；不会自动切换、不会自动废弃旧 `1+7`、不会扩大 A0-A7。

## 11. Phase-3 独立评审与 canonical-switch 边界

Readiness 合格后生成评审包：

```bash
python scripts/generate_edge_foundation_phase3_review_package.py \
  edge-foundation-phase3-readiness.json \
  --output edge-foundation-phase3-review-package.json
```

Phase-3 的改动面已经收窄为两类：

1. `canonical-routing-authority`：`domains/edge-foundation/domain.yaml`；
2. `routing-selector-entrypoint`：未来 `domains/edge-foundation/canonical-routing.yaml`。

Phase-3 **禁止**修改 `domains/edge-foundation/compatibility/**`、旧 Expert/Skill owner、Pilot threshold、A0-A7、Verification / Review 独立性、Provider binding 或 Source-of-Truth authority。

旧 `1+7` compatibility mapping 在 Phase-3 必须保持静态 8/8；legacy deprecation 属于独立 Phase-4，legacy removal 属于独立 Phase-5。真正 switch 必须使用独立 PR/ADR、review package、dry-run plan、change manifest 和 exact diff guard。

## 12. 当前阶段退出条件

当前目标是至少证明 **E2 Engineering Closed Loop**，并为 **E3 Knowledge Closed Loop** 建基础：

- Debug / Feature / Review-Release 三轨均有真实 completed evidence；
- `incorrect_pass_rate = 0`；
- `unauthorized_actions = 0`；
- `audit_trace_completeness = 1.0`；
- Material / Acceptance-Evidence / Knowledge Harvest 完整；
- Verification 与 Independent Review 独立；
- context / integration / identity / knowledge reuse 的真实断点得到复盘。

达到以上门槛仍只允许进入后续 productionization / canonical-routing 人工评审；仓库不会自动扩大权限，也不会自动标记 Production Ready。
