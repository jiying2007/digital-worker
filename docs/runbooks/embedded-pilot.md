# 嵌入式系统专家团真实 Pilot 执行说明

Pilot 的目标是验证 Expert Team Operating Model 与 Embedded Domain Closed Loop V1，而不是证明 AI 永远正确。当前基础设施状态为 `pilot-operations-ready`，真实三轨证据仍待执行。

当前阶段策略基线：`docs/strategy/embedded-domain-closed-loop-v1.md`。

## 1. 绑定真实任务

先形成 `task-brief v1`。真实 Pilot 必须有 human owner、repo root、**exact Git base SHA**、验收和所需验证层级。只提供 `main/dev` 等漂移分支名时不得开始 real run。

同一 run 的 Expert 默认共享同一个 Work Item / Run Identity 和 Material/System Context，不各自重新假设版本事实。

## 2. 初始化

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
  --base-commit <exact-sha>
```

然后用 `status ... running` 开始记录。

## 3. 执行

Expert Team 默认 A0-A2。代码修改/构建经：

```text
Expert Team
 -> engineering-task-package
 -> Engineer + Engineering Agent Runtime
 -> delivery-receipt
 -> Verification
 -> Independent Review
```

Runtime Provider 可替换，但 Contract / Action Policy 不变。设备写和 Release 保留人工 Gate。Debug 强制 Observed / Inferred / Confirmed + **同一份 Hypothesis Registry**。

Feature 若涉及多个仓库，优先采用 `One Run -> Multiple Engineering Packages`，每个 Package 保持自己的 exact base / scope / delivery identity；不要把多个仓库硬塞进一个巨型 Package。

## 4. Embedded Domain Closed Loop V1 运行产物

每条真实 Pilot 轨道在收口时都必须附加：

1. `material_manifest`：复用现有 Material Manifest，作为共享 System Context Snapshot；
2. `acceptance_evidence_matrix`：使用 `expert-groups/embedded-system/templates/acceptance-evidence-matrix.md`；
3. `knowledge_harvest`：使用 `expert-groups/embedded-system/templates/knowledge-harvest.md`。

Debug 另外必须提供 `hypothesis_registry`。

Knowledge Harvest 允许 `NO_KNOWLEDGE_DELTA`；不得为了“完成流程”制造无价值知识。

## 5. 收口

使用 `complete` 附加 track 所需结构化产物和 V1 extra artifacts。工具会校验 required artifacts 并生成 `evidence-bundle.json`，对运行产物计算 SHA256。

Feature 示例：

```bash
python scripts/embedded_pilot.py complete <run-dir> \
  --engineering-task-package <engineering-task-package.json> \
  --delivery-receipt <delivery-receipt.json> \
  --verification-report <verification.json> \
  --review-report <review.json> \
  --pilot-result <pilot-result.json> \
  --extra material_manifest=<material-manifest.json> \
  --extra acceptance_evidence_matrix=<acceptance-evidence-matrix.md> \
  --extra knowledge_harvest=<knowledge-harvest.md>
```

Debug 再增加：

```text
--extra hypothesis_registry=<hypothesis-registry.json>
```

Completed run 缺少任何当前 track 的 required artifact 时必须 fail-closed。

## 6. V1 Review 检查项

Independent Review 除现有 Evidence / Verification 规则外，额外检查：

- Work Item / Run / Context identity 是否一致；
- source / artifact / device / test identity 是否出现静默断链；
- Acceptance Criterion 是否能映射到 Evidence；
- Debug 是否只有一个共享 Hypothesis Registry；
- Knowledge Harvest 是否有证据，或明确 `NO_KNOWLEDGE_DELTA`；
- 是否出现 context rebuild、重复分析、跨域接口晚发现等信息损耗。

当前不要求新建 Artifact Lineage / Verification Matrix 正式 Schema；这些断点先作为 real Pilot evidence 记录。

## 7. Knowledge Registry

当前 Registry：`expert-groups/embedded-system/knowledge/registry.yaml`。

首版是 `internal-seed`，只登记仓库内可核验对象。NAS / 飞书 / CI-HIL / 历史 RCA 等外部 Source 继续通过 #16 逐步接入；Registry 只记录 Source，不复制权威原文形成第二 SSOT。

## 8. 汇总与评分

```bash
python scripts/embedded_pilot.py summary expert-groups/embedded-system/pilot/runs --output pilot-status.json
python scripts/evaluate_embedded_pilot.py <pilot-result...> --output pilot-metrics.json --markdown-output pilot-metrics.md
```

评分门槛从 `pilot-plan.yaml` 读取。Synthetic 只验证工具链，不计入真实 Pilot / Knowledge evidence。

## 9. 当前阶段退出条件

前三条 real Pilot 的目标不是自动 Production Ready，而是证明至少达到 E2 Engineering Closed Loop，并为 E3 Knowledge Closed Loop 建基础。

至少要求：

- Debug / Feature / Review-Release 三轨均有真实 completed evidence；
- `incorrect_pass_rate = 0`；
- `unauthorized_actions = 0`；
- `audit_trace_completeness = 1.0`；
- V1 三个闭环运行产物完整；
- 至少记录并复盘 context / integration / identity / acceptance-evidence / knowledge reuse 的真实断点。

满足以后也仅能提交 Productionization 人工评审；仓库不会自动扩大 A3-A7，也不会自动标记 Production Ready。
