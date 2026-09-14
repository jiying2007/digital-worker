# 嵌入式系统专家团真实 Pilot 执行说明

Pilot 的目标是验证 Expert Team Operating Model 与 Embedded Domain Closed Loop V1，而不是证明 AI 永远正确。当前基础设施状态为 `pilot-operations-ready`，真实三轨证据仍待执行。

当前阶段策略基线：`docs/strategy/embedded-domain-closed-loop-v1.md`。

快速执行入口：`docs/runbooks/embedded-closed-loop-quickstart.md`。

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

然后生成 V1 working artifacts：

```bash
python scripts/embedded_pilot_scaffold.py \
  expert-groups/embedded-system/pilot/runs/<run-id>
```

Scaffold 不会替工程师猜测上下文：未知设备、测试环境、复现条件等会保持 `missing`，Material Manifest 可因此保持 `BLOCKED`，直到可信 Source 补齐。

然后用 `status ... running` 开始记录。

## 3. Knowledge 候选解析

当前 Registry：`expert-groups/embedded-system/knowledge/registry.yaml`。

先校验 Registry：

```bash
python scripts/embedded_knowledge.py verify
```

再按任务查询候选：

```bash
python scripts/embedded_knowledge.py query --text "<task terms>" --limit 10
python scripts/embedded_knowledge.py query --domain <domain> --limit 10
```

查询结果只是候选 Knowledge，不自动升级为任务事实；实际使用时仍需检查 Source authority / version / ACL / provenance。

## 4. 执行

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

## 5. Embedded Domain Closed Loop V1 运行产物

每条真实 Pilot 轨道在收口时都必须附加：

1. `material_manifest`：复用现有 Material Manifest，作为共享 System Context Snapshot；
2. `acceptance_evidence_matrix`：使用 scaffold 生成的 `working/acceptance-evidence-matrix.md`；
3. `knowledge_harvest`：使用 scaffold 生成的 `working/knowledge-harvest.md`。

Debug 另外必须提供 `working/hypothesis-registry.json`。

Knowledge Harvest 允许 `NO_KNOWLEDGE_DELTA`；不得为了“完成流程”制造无价值知识。

## 6. 收口

使用 `complete` 附加 track 所需结构化产物和 V1 extra artifacts。工具会校验 required artifacts 并生成 `evidence-bundle.json`，对运行产物计算 SHA256。

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

Completed run 缺少任何当前 track 的 required artifact 时必须 fail-closed。

## 7. V1 Review 检查项

Independent Review 除现有 Evidence / Verification 规则外，额外检查：

- Work Item / Run / Context identity 是否一致；
- source / artifact / device / test identity 是否出现静默断链；
- Acceptance Criterion 是否能映射到 Evidence；
- Debug 是否只有一个共享 Hypothesis Registry；
- Knowledge Harvest 是否有证据，或明确 `NO_KNOWLEDGE_DELTA`；
- 是否出现 context rebuild、重复分析、跨域接口晚发现等信息损耗。

当前不要求新建 Artifact Lineage / Verification Matrix 正式 Schema；这些断点先作为 real Pilot evidence 记录。

## 8. Knowledge Registry

首版 Registry 是 `internal-seed`，只登记仓库内可核验对象。NAS / 飞书 / CI-HIL / 历史 RCA 等外部 Source 继续通过 #16 逐步接入；Registry 只记录 Source，不复制权威原文形成第二 SSOT。

## 9. 汇总与评分

```bash
python scripts/embedded_pilot.py summary expert-groups/embedded-system/pilot/runs --output pilot-status.json
python scripts/evaluate_embedded_pilot.py <pilot-result...> --output pilot-metrics.json --markdown-output pilot-metrics.md
```

评分门槛从 `pilot-plan.yaml` 读取。Synthetic 只验证工具链，不计入真实 Pilot / Knowledge evidence。

## 10. 生成端侧底座影子凭证并评估 phase-3 readiness

真实 Pilot 完成并验证后，额外生成一份**端侧底座影子凭证（Edge Foundation shadow receipt）**。它只把旧执行身份映射到新的 Domain / Expert / Capability / Assurance 责任语义，不改变当前 canonical routing，也不修改 frozen evidence bundle。

```bash
python scripts/evaluate_edge_foundation_pilot_shadow.py \
  <run-dir>/pilot-run.json \
  --pilot-result <run-dir>/pilot-result.json \
  --output <run-dir>/edge-foundation-shadow-receipt.json
```

只有以下六项同时为真，凭证才会标记 `phase3_evidence_eligible=true`：

- `source_real`；
- `run_completed`；
- `result_provided`；
- `outcome_pass`；
- `no_unauthorized_actions`；
- `audit_trace_complete`。

Synthetic 即使自身 PASS，也必须保持 `phase3_evidence_eligible=false`。

三轨真实任务完成后，聚合当前所有 receipt：

```bash
python scripts/evaluate_edge_foundation_phase3_readiness.py \
  --receipt-dir expert-groups/embedded-system/pilot/runs \
  --output edge-foundation-phase3-readiness.json
```

需要作为 Gate 使用时增加：

```text
--require-ready
```

未满足条件时命令以 exit `2` fail-closed，并输出 `status=BLOCKED`。门槛直接复用 `expert-groups/embedded-system/pilot/pilot-plan.yaml`，当前要求 debug / feature / review_release 各至少 1 个 eligible real receipt，合计至少 3 个。

即使输出 `ELIGIBLE_FOR_REVIEW`，也只表示**允许发起 phase-3 canonical routing switch 的独立评审**；不会自动修改 `canonical_routing_switched=false`，不会自动废弃旧 1+7，也不会扩大 A0-A7 权限。

## 11. 当前阶段退出条件

前三条 real Pilot 的目标不是自动 Production Ready，而是证明至少达到 E2 Engineering Closed Loop，并为 E3 Knowledge Closed Loop 建基础。

至少要求：

- Debug / Feature / Review-Release 三轨均有真实 completed evidence；
- `incorrect_pass_rate = 0`；
- `unauthorized_actions = 0`；
- `audit_trace_completeness = 1.0`；
- V1 三个闭环运行产物完整；
- 至少记录并复盘 context / integration / identity / acceptance-evidence / knowledge reuse 的真实断点。

满足以后也仅能提交 Productionization 人工评审；仓库不会自动扩大 A3-A7，也不会自动标记 Production Ready。
