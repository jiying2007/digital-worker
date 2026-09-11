# 企业 AI / 研发体系循序渐进落地策略（Brainstorm）

- Status: `brainstorm / non-normative`
- Date: 2026-09-11
- Related: `docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md`
- Related: `docs/brainstorm/enterprise-ai-rd-embedded-digital-thread.md`

> 本文归档“如何避免企业 AI / 研发体系设计很大但落不了地”的讨论。它不是实施计划、不是 ADR、不是正式阶段承诺；后续应由真实 Pilot / PoC / 组织评审决定哪些内容进入正式 Roadmap。

## 1. 核心判断

最大的失败模式不是技术做不到，而是同时建设企业协同、知识平台、Agent、HIL、MES、Field、自动执行网关，导致每层都只有局部能力、没有真实业务闭环。

候选落地原则：

> 先闭环一个真实任务，再闭环一个真实团队，再闭环一个真实产品线，最后才扩展为企业级平台。

AI 不是第一步。第一步应先结构化真实研发活动中的输入、输出、证据和责任；即使暂时不用 AI，这些 Contract 也应能够被人使用。

## 2. 候选六级成熟阶梯

|阶段|核心目标|典型范围|候选权限|进入下一阶段的证据|
|---|---|---|---|---|
|L0 基线|看清现状|一个团队、若干真实任务|无自动 AI 动作|人工耗时、质量和返工基线|
|L1 辅助|AI 帮人整理/分析|Review、Debug、文档|A0-A2|节省时间且错误不增加|
|L2 工程闭环|AI 进入研发链|Task→Execution→Verification|A0-A4 受控|Debug/Feature/Review real Pilot|
|L3 知识闭环|经验可复用|RCA、Runbook、Golden Case|只读+候选写入|检索质量/权限/版本可量化|
|L4 上下游闭环|串产品/硬件/验证/Release|跨团队 Contract|局部自动|Digital Thread 可追踪|
|L5 受控自动化|重复工作自动执行|Runner/CI/设备只读|部分 A3-A5|错误率、恢复、审计稳定|
|L6 企业化|多团队复制|研发中心级|按域授权|治理、成本、收益稳定|

原则：**不跳级**。例如知识 ACL/freshness/authority 尚未验证，就不建设全公司知识 Agent；真实 Pilot 尚未完成，就不建设复杂 Runtime Gateway。

## 3. 首批适合落地的任务

### Debug

特点：证据多、人工耗时大、历史经验价值高、结果相对容易判断。

候选：Boot、Kernel Panic、HardFault、UBIFS、DMA Cache、长稳、现场问题。

### Code / Technical Review

低副作用，适合先验证：分析、风险识别、证据检查、错误 PASS 防线。

### 中等复杂度 Feature

适合驱动/组件/MCU 功能；不建议首批选择“新平台+新芯片+新硬件+新算法+新供应商”的高度耦合任务。

## 4. Copilot → Autopilot 的候选顺序

早期推荐：

```text
人给目标/边界
  → AI 分析/生成
  → 人决定
  → AI/工程师受控执行
  → 机器验证
  → 独立人/角色确认
```

而不是需求直接进入无人值守自动交付。

A0-A7 可作为成熟度边界：A0-A2 自动，A3-A4 受控，A5 授权，A6/A7 人工 Gate。

## 5. 每个 Pilot 必须和人工基线比较

建议至少记录：

- 人工耗时 / AI 辅助耗时；
- 发现问题数；
- human correction；
- unsupported claims；
- incorrect PASS；
- verification completeness；
- evidence completeness；
- rework count；
- MTTR；
- engineering time / runtime cost。

“大家觉得好用”不是生产化证据。

## 6. Task 完成后继续进入 Learning Loop

```text
Task
 → Evidence
 → RCA / Decision
 → Knowledge Candidate
 → Human Review
 → Runbook / Skill / Golden Case / Design Rule / Verification Rule
```

长期价值不只是帮工程师完成一次任务，而是减少团队重复踩坑。

## 7. Knowledge 建设候选策略

不建议一开始全量迁移 NAS / 飞书 / Git。

先选 50~100 个高价值对象验证：

- 能否搜到；
- 是否命中正确版本；
- ACL 是否正确；
- citation 是否可追踪；
- stale source 是否识别；
- source conflict 是否可处理。

验证后再扩范围。

## 8. 上下游逐条串，而不是一次串全公司

建议顺序：

1. Product → Embedded；
2. Hardware → Embedded；
3. Embedded → Verification；
4. Verification → Release；
5. Release → Manufacturing；
6. Manufacturing / Field → Incident / RCA。

Digital Thread 应通过逐段扩展形成，而不是一次性平台化。

## 9. 候选 90 天节奏

### Month 1

3~10 个 real Pilot，覆盖 Debug / Feature / Review，至少两个 Engineering Agent Runtime 做受控对比。

### Month 2

Knowledge Source Inventory + 50~100 个高价值知识对象 PoC。

### Month 3

用真实项目验证三条最小 Contract：Product→Embedded、Hardware→Embedded、Embedded→Verification。

90 天之后再决定是否投入 Context Broker、Runtime Gateway、Action Gateway、MES/Field 深度接入。

## 10. 升级门槛而不是完成清单

每一阶段必须回答：

- 什么证据允许升级？
- 出错如何退回人工路径？
- 权限扩大是否有可审计依据？
- 失败是否会被错误包装为成功？

没有证据就不扩大自动化范围。

## 11. 组织责任候选

三个角色应分开：

- Business / Process Owner：定义要解决的业务问题；
- Engineering Owner：定义 Contract / Workflow / Validation；
- AI / Platform Owner：提供 Agent / Model / Knowledge / Platform 能力。

避免由单一“AI 项目负责人”同时定义价值、工程边界和技术实现。

## 12. 快速筛选新想法的四个问题

1. 解决哪个真实任务？
2. 当前人工怎么做？
3. 成功怎么量化？
4. 失败能否安全回退？

答不清楚的内容继续放在 Brainstorm；有真实 PoC 证据后才进入 ADR / Contract / Roadmap。
