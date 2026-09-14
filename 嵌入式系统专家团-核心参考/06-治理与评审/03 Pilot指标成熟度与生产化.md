# Pilot、指标、成熟度与生产化

## 1. 为什么要真实 Pilot

Golden Case、fixture 和 CI 主要证明“规则和工具没有明显坏掉”，不能证明真实项目中资料是否找得到、跨团队是否顺畅、证据链是否完整、流程成本是否值得。

因此 Productionization 必须依赖真实任务，而不是 synthetic run 数量。

## 2. 三条必跑轨道

### Debug

覆盖缺陷、现场、长稳、Crash、存储、DMA、并发等。必须有共享 Hypothesis Registry。

### Feature

覆盖功能、驱动、组件、MCU firmware、Bring-up。必须有 Engineering Package 和 Delivery Receipt。

### Review / Release

覆盖 Code Review、技术可行性、OTA/Release Readiness。重点检查 source/artifact/verification/risk/rollback。

进入第一次 Productionization Review 前，三条轨道至少各有 1 个 real completed run。

## 3. 每个真实 Run 的最低要求

所有轨道：

- full 40-hex source identity；
- material/system context；
- acceptance-evidence matrix；
- verification / review；
- knowledge harvest；
- evidence bundle；
- terminal evidence integrity。

Debug 额外要求 Hypothesis Registry；Feature 额外要求 Engineering Package + Delivery Receipt。

## 4. 重点指标

### Safety / Quality

- `incorrect_pass_rate`：应 BLOCKED/FAIL 却被写 PASS 的比例；
- `unauthorized_actions`：越权动作次数；
- unsupported claim rate；
- regression escape；
- late interface mismatch。

### Efficiency

- task lead time；
- debug MTTR；
- context rebuild count；
- duplicate analysis；
- human correction time；
- review re-ask count。

### Traceability

- exact source coverage；
- artifact identity coverage；
- device identity coverage；
- acceptance → evidence coverage；
- audit trace completeness。

### Knowledge

- citation correctness；
- knowledge reuse count；
- stale/conflict detection；
- RCA → reusable knowledge conversion。

代码行数、Prompt 数、调用次数、Token 数不能作为主要成效指标。

## 5. 安全硬门槛

进入 Productionization Review 前至少：

- real completed runs ≥ 3；
- Debug / Feature / Review-Release 各 ≥ 1；
- `incorrect_pass_rate = 0`；
- `unauthorized_actions = 0`；
- `audit_trace_completeness = 1.0`；
- required V1 artifact 无缺失；
- 至少一个真实 Knowledge reuse evidence；
- 重大 identity/integration/verification gap 有 Owner；
- Multi-runtime 至少完成两种 Runtime 的同条件对照。

满足这些条件只是“有资格进入人工 Productionization Review”，不是自动 Production Ready。

## 6. 成熟度

|等级|含义|当前判断|
|---|---|---|
|E0 Defined|Contract/Gate/Policy 已定义|已具备|
|E1 Assisted|研发任务可获得结构化辅助|已具备基础|
|E2 Engineering Closed Loop|真实 Task→Execution→Verification→Review 闭环|当前目标|
|E3 Knowledge Closed Loop|知识进入后续真实任务并被复用|建立基础中|
|E4 Self-improving|重复缺口驱动 Skill/Tool/Knowledge 改进|未宣称|
|E5 Controlled Automation|低风险流程在证据支持下受控自动化|未宣称|

## 7. 当前推进顺序

```text
Debug real Pilot
  → Feature real Pilot
  → Review/Release real Pilot
  → 外部 Knowledge Source + real reuse
  → Multi-runtime 对照
  → Productionization Review
  → strict repository governance
```

当前不回到“大架构重新设计”阶段，除非真实任务暴露了架构级问题。

## 8. Pilot 复盘要回答什么

每个阶段至少复盘：

- 哪些 Context 被重复重建？
- 哪些信息在交接时丢失？
- 哪些接口冲突发现太晚？
- 哪些验证被重复询问？
- 哪些步骤流程负担大于收益？
- 哪些知识真正被后续任务复用？
- 哪些问题只是 Provider 限制，哪些是领域 Contract 缺陷？
- 是否有重复缺口足以升级新 Schema/Skill/平台能力？

## 9. 何时扩大自动化

只有满足以下条件时才考虑扩大 A3-A7 自动化：

- 同类任务已有足够真实样本；
- fail-closed 机制经负向案例验证；
- rollback 可测试；
- identity/evidence 自动采集稳定；
- 权限可按任务和目标最小化；
- 人工介入点清楚；
- 出错后能恢复并审计。

自动化应该是成熟工程流程的结果，不是成熟度的替代品。
