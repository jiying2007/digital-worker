# 嵌入式系统专家团-核心参考

> **用途：内部讨论与评审。**
>
> 文档状态：`review-draft`
>
> 同步基线：`digital-worker/main@fba5e1a607619112783fdf89e8bdf0d1b481626f`
>
> 当前实现版本：`0.6.0 / pilot-operations-ready`

本目录用于把 `expert-groups/embedded-system/` 中已经落地的机器配置、Agent、Contract、Schema、Skill、Pilot 工具，转换为便于研发中心内部阅读、讨论和评审的说明文档。

它与 `产品专家团-核心参考/` 的定位一致：**不是另一个实现，不是第二套 SSOT，而是实现事实的人工可读解释层。**

如本文档与实现资产冲突，按以下顺序裁决：

1. `expert-groups/embedded-system/expert-group.yaml`
2. `config/workflow.yaml`
3. `config/task-modes.yaml`
4. `config/action-policy.yaml`
5. `config/gate-policy.yaml` / `config/material-requirements.yaml`
6. `contracts/experts/*.io.yaml`
7. `schemas/*.schema.json`
8. `agents/*.md`
9. `skills/*/SKILL.md`
10. 本目录说明文档、历史资料与示例

上位边界仍受：

- `研发中心AI数字员工研发流程规划_V2.md`
- `docs/adr/ADR-001-workbuddy-codex-integration-boundary.md`
- `docs/adr/ADR-002-embedded-system-expert-team-architecture.md`

约束。

## 文档索引

|编号|文档|主要用途|
|---|---|---|
|01|嵌入式系统专家团整体架构|理解专家团定位、1+7 组织、目录、主链和边界|
|02|主理人专家工作逻辑|评审唯一入口、路由、Gate、交接和收口纪律|
|03|嵌入式架构专家工作逻辑|评审架构/可行性/资源与接口职责|
|04|Linux BSP 专家工作逻辑|评审 Boot/BSP/Kernel/DT/IRQ/DMA/Storage 能力|
|05|MCU RTOS 专家工作逻辑|评审 MCU/RTOS/Bare-metal/Linker/ISR 等能力|
|06|驱动与组件专家工作逻辑|评审驱动、外设、组件集成和复用边界|
|07|调试与可靠性专家工作逻辑|评审 Evidence/Hypothesis/Root Cause 闭环|
|08|验证专家工作逻辑|评审 Host/Cross-build/SIL/Device/HIL/Release 分层验证|
|09|独立审查专家工作逻辑|评审独立 Review、Release Readiness 与错误放行防线|
|10|全量原子能力（Skill）清单|评审当前 23 个 P0 Skills 及后续扩展原则|
|11|Workflow、Gate 与工程交接|评审任务模式、状态机、Gate 和 Codex 工程执行边界|
|12|Evidence、知识、自治与安全边界|评审证据模型、知识边界、A0-A7 与高风险操作|
|13|Pilot、评测与生产化评审|评审真实 Pilot、指标、安全门槛和 Productionization|
|14|跨专家团协作与职责边界|评审产品专家团、端侧底座与嵌入式系统专家团接口|
|15|内部评审问题清单|会议直接使用的拍板项、争议项和建议结论|

## 当前阶段必须明确的事实

- 1+7 Core Experts、23 个 P0 Skills、Engineering Handoff、Cross-Team Contract、Golden Cases、Pilot Contracts/CLI/CI 已落地。
- `pilot-operations-ready` **不等于**真实 Pilot 已完成。
- #6 / #7 / #8 三条 real Pilot 仍待绑定真实工程任务。
- 端侧底座 ownership 尚未完成原文规范化和逐域裁决。
- `main` required check/branch protection 尚未由管理员启用。
- 因此当前严禁标记 `Production Ready`。
