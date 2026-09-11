# Embedded Domain Closed Loop V1

- Status: `current-stage-baseline`
- Date: 2026-09-11
- Scope: 嵌入式研发域内闭环
- Architecture: `provider-neutral`
- Related: ADR-002 / ADR-003 / `expert-groups/embedded-system/`
- Supersedes for current-stage execution: `docs/brainstorm/embedded-internal-engineering-thread.md` 中尚未收敛的落地建议

> 当前阶段主策略：**先让嵌入式研发自身形成可运行、可验证、可学习的 Domain Closed Loop；Enterprise Digital Thread 不是前置条件。**

## 1. 为什么现在收敛到域内闭环

企业级串联涉及产品、硬件、测试、知识平台、MES、售后和多个 Provider，组织依赖大、周期长。嵌入式内部已经具备 Work Item、1+7 Expert Team、Evidence、Hypothesis、Engineering Handoff、Verification、Review、Pilot 与 Git/CI/HIL 接口，因此应先证明一个领域自身能够持续产生真实收益。

外部模块暂时无法接入时，统一降级为 `Intake Adapter / Delivery Adapter`：人工录入、飞书、Issue、NAS、文件等均可作为输入来源，但进入嵌入式域后使用稳定 Work Item / Run / Evidence / Artifact Identity。

## 2. V1 成功定义

V1 不是“平台建设完成”，而是 3~10 个真实嵌入式任务能够稳定完成：

```text
External Input
  -> Embedded Work Item
  -> Shared System Context
  -> Expert DAG / Decision
  -> Engineering Package(s)
  -> Engineer + Engineering Agent Runtime
  -> Source / Artifact Identity
  -> Verification / Independent Review
  -> Delivery
  -> Knowledge Harvest
  -> 下一任务可复用
```

并且不出现：
- incorrect PASS；
- unauthorized action；
- source/artifact/device identity 静默断链；
- Verification 跨层推导；
- Knowledge Source 被复制成第二份未受控 SSOT。

## 3. V1 七个必做项

### V1-1 One Work Item / One Run Identity

所有真实任务必须有稳定 `work_item_id` 和 `run_id`。外部来源可以变化，但域内身份不可漂移。

继续复用现有 `task-brief`、`pilot-run`、`team-run-state`，不建设新的需求管理系统。

### V1-2 Shared System Context

每个真实 run 共享一份 Context Snapshot，第一阶段复用现有 `material-manifest`，至少明确：
- repo / exact base commit；
- board revision；
- SoC / MCU；
- SDK / kernel / RTOS / toolchain；
- firmware / device / test environment；
- missing / stale / conflicting material。

所有 Expert 默认消费同一份 Context，不重复构建自己的版本事实。

### V1-3 One Hypothesis Registry for Debug

Debug / stability / field incident 强制共享一份 Hypothesis Registry。Architecture/BSP/MCU/Driver/Debug Expert 只能向同一棵假设树补充 evidence、experiment、supported/rejected/confirmed 状态，不允许分别维护互相冲突的 RCA。

### V1-4 Exact Source + Artifact Identity

Engineering Execution 必须继续使用 exact source base；完成真实任务时必须能够回答：

```text
work_item -> repo SHA -> build/config -> binary/firmware -> device/test -> evidence
```

V1 不新增完整 Artifact Lineage Schema；先使用 engineering-task-package、delivery-receipt、evidence bundle、HIL evidence 与受控引用证明身份连续性。

### V1-5 Acceptance -> Evidence

每个真实 Pilot 增加轻量 `acceptance-evidence-matrix` 运行产物，把 acceptance criterion 显式映射到：
- verification layer；
- artifact/device/test identity；
- evidence ref；
- PASS/FAIL/BLOCKED/NOT_RUN。

当前先使用 Markdown 模板，不新增正式 Schema。只有真实任务反复证明字段稳定且存在自动化需求后再 Schema 化。

### V1-6 Knowledge Harvest

每个真实 completed run 增加轻量 Knowledge Harvest：

```text
NO_KNOWLEDGE_DELTA
或
KNOWLEDGE_CANDIDATE
```

只检查是否产生：新 root cause、design rule、known issue、compatibility conclusion、checklist、test case、Skill candidate 或 stale knowledge。Knowledge Harvest 不是“每个任务必须写文档”的 KPI。

### V1-7 Embedded Knowledge Registry

先建立 50~100 条高价值 Knowledge Registry，而不是建设 RAG 平台。

Registry 记录：
- knowledge_id / title / domain / type；
- authority / source provider / source ref；
- owner；
- product/platform scope；
- version；
- ACL；
- freshness；
- tags。

首版只登记仓库内可核验对象，状态明确为 `internal-seed`。NAS / 飞书 / CI-HIL / 历史 RCA 等真实外部 Source 由 #16 分阶段补充，不得伪造已接入状态。

## 4. V1 不做的三件事

### N1 不建设统一 Knowledge Platform

当前不冻结 WeKnora、Vector DB、RAG、统一知识主库。继续遵循 `Source of Truth stays at source`。

### N2 不建设 Context Broker / Knowledge Graph

Context Package 先人工或脚本组装；关系先通过 source_ref / evidence_ref / work_item_id 表达。没有真实规模问题前不增加平台层。

### N3 不新增一批 Schema / Agent

当前不正式新增：
- system-context-manifest；
- artifact-lineage；
- verification-matrix；
- integration-readiness；
- context-package；
- agent-runtime-receipt；
- Integration Expert。

先在 real Pilot 中记录重复缺口；至少出现可复用的真实需求后再升级。

## 5. 内部运行模型

### 5.1 Feature

```text
Task Brief
 -> Material/System Context
 -> Architecture Impact
 -> BSP / MCU / Driver 并行分析
 -> Integration Reconciliation
 -> Technical Decision
 -> one or more Engineering Packages
 -> Runtime / Engineer
 -> Delivery + identity
 -> Acceptance -> Evidence
 -> Independent Review
 -> Knowledge Harvest
```

### 5.2 Debug

```text
Incident/Reproduction
 -> Context
 -> Evidence Normalize
 -> One Hypothesis Registry
 -> Expert experiments
 -> Root Cause
 -> Fix Package
 -> Regression / Stress / HIL
 -> Review
 -> Knowledge Harvest
```

### 5.3 Review / Release

```text
Source/Artifact identity
 -> Existing Verification evidence
 -> Acceptance coverage
 -> Risk / waiver / rollback
 -> Independent readiness review
 -> Knowledge Harvest
```

Release 不重新制造工程事实；如果 Review 阶段仍无法回答“哪个 SHA / binary / device / HIL”，记录为 identity gap。

## 6. Integration Reconciliation

V1 将 Integration 视为动作，不新增 Expert。由 Team Lead + Architecture Expert 在进入 Execution 前检查：
- interface；
- timing；
- resource；
- dependency/version；
- identity；
- ownership。

若 3~10 个真实任务证明该动作持续成为独立工作量，再考虑 `system-integration` Skill；只有进一步证据充分时才讨论第 8 个 Expert。

## 7. Multi-Repo

V1 推荐 `One Run -> Multiple Engineering Packages`，而不是改造成一个巨型多仓 Package。

每个 package 独立保持 exact base、scope、acceptance、required verification、delivery receipt。Run 层负责把多个 package 的结果重新汇合到同一 Verification / Review。

## 8. Knowledge 分层

四层逻辑模型：
1. Authority Knowledge：Datasheet/TRM/SDK/Schematic/Git/CI-HIL evidence；
2. Engineering Knowledge：Architecture/Design Rule/Compatibility/Porting；
3. Operational Knowledge：RCA/Runbook/Known Issue/Checklist；
4. AI Execution Knowledge：Skill/Golden Case/Evaluation Fixture/Tool Rule。

Knowledge Registry 只索引和描述 Source，不改变 Source Authority。

## 9. 五个闭环

V1 最终要证明五个环能够连接：
- Task Loop：需求/问题 -> Delivery；
- Engineering Loop：Analysis -> Execution -> Verification；
- Quality Loop：Failure -> RCA -> Regression；
- Knowledge Loop：Experience -> Reviewed Knowledge -> Reuse；
- Capability Loop：Repeated Gap -> Skill/Tool Candidate -> Evaluation。

## 10. 90 天落地顺序

### 0~30 天：真实任务闭环

优先 #6/#7/#8 三轨 real Pilot。每个真实 run 强制 material manifest、acceptance-evidence matrix、knowledge harvest；Debug 继续强制 hypothesis registry。

退出条件：至少一个真实任务完成全链，且没有 incorrect PASS / unauthorized action / identity 静默断链。

### 31~60 天：Knowledge 最小闭环

扩充 Knowledge Registry 到 50~100 个高价值对象，并通过 #16 加入至少三类真实 Source；验证 citation / authority / freshness / ACL negative case。

退出条件：Knowledge 能够在下一真实任务被实际引用，而不是只完成登记。

### 61~90 天：内部 Thread 验证

重点观察：
- context rebuild；
- duplicate analysis；
- cross-domain interface mismatch；
- multi-repo package；
- artifact identity gap；
- acceptance-evidence coverage；
- review 时重新追问上下文；
- knowledge reuse。

重复出现的信息断点才允许升级正式 Schema / Skill。

## 11. 180 天候选

仅在 V1 evidence 成立后考虑：
- Compatibility Intelligence；
- 自动 Context Package；
- Knowledge Retrieval Automation；
- HIL 深度集成；
- P1 Skills；
- Platform / Project Memory；
- Context Broker / Runtime Gateway 的必要性评估。

## 12. 指标

### Safety / Quality
- incorrect_pass_rate = 0；
- unauthorized_actions = 0；
- unsupported_claim_rate；
- late interface mismatch；
- regression escape。

### Efficiency
- task lead time；
- debug MTTR；
- context rebuild count；
- duplicate analysis；
- human correction time。

### Traceability
- exact source coverage；
- artifact identity coverage；
- device identity coverage；
- acceptance -> evidence coverage；
- audit trace completeness。

### Knowledge
- registry coverage；
- citation correctness；
- knowledge reuse count；
- stale knowledge detection；
- RCA -> reusable knowledge conversion。

## 13. 成熟度

- E0 Defined：Contract / Gate / Policy 已定义；
- E1 Assisted：AI 辅助分析；
- E2 Engineering Closed Loop：真实 Task -> Execution -> Verification -> Review 完整；
- E3 Knowledge Closed Loop：Knowledge 真正重新进入后续任务；
- E4 Self-improving：真实任务驱动 Skill/Tool/Knowledge 改进；
- E5 Controlled Automation：低风险流程在 evidence 支撑下受控自动化。

当前目标只推进到 **E2，并为 E3 建基础**。不得因为 V1 infrastructure 落地声明 E3/E4/E5 或 Production Ready。

## 14. 反向审查结论

本方案已经主动删掉四类过度设计：统一知识平台、Context Broker、Knowledge Graph、大批新 Schema/Agent。

仍需持续警惕：
1. 流程负担超过收益：复杂任务用完整链，简单任务按现有 workflow mode 裁剪；
2. Knowledge Harvest 变成写文档 KPI：允许 `NO_KNOWLEDGE_DELTA`；
3. Registry 变成复制资料：只登记 Source，原权威不搬迁；
4. Pilot 只在 `digital-worker` 仓库里成功：最终必须绑定真实研发任务；
5. Schema 爆炸：真实重复需求是唯一升级理由。

## 15. 当前阶段最终结论

> **先建设 Embedded Domain Closed Loop，再向外连接 Enterprise Digital Thread。**

当前最小执行集固定为：

```text
One Work Item / Run
+ Shared Material/System Context
+ One Hypothesis Registry for Debug
+ Exact Source / Artifact Identity
+ Acceptance -> Evidence
+ Knowledge Harvest
+ Embedded Knowledge Registry
```

这七项是当前阶段的实施基线。未来 Provider、Knowledge Platform、Context Broker、额外 Schema 和更高自动化权限继续保持 not-frozen，必须由真实 evidence 决定。
