# 嵌入式系统专家团-核心参考

> **用途：内部讨论与评审。**
>
> 文档状态：`review-ready`
>
> 实现基线：`expert-groups/embedded-system/` v0.7.0 / `pilot-operations-ready`
>
> 总体架构：`provider-neutral / proposed-for-review`
>
> 合入 main 表示“正式评审基线”，**不等于内部评审已经通过**；评审拍板后再升级为 `reviewed-baseline`。

本目录用于把 `expert-groups/embedded-system/` 中已经落地的机器配置、Agent、Contract、Schema、Skill、Pilot 工具，转换为便于研发中心内部阅读、讨论和评审的说明文档。

它与 `产品专家团-核心参考/` 的定位一致：**不是另一个实现，不是第二套 SSOT，而是实现事实的人工可读解释层。**

## 2026-09-11 Provider-neutral 架构更新

ADR-003 已将总体架构从固定的 “WorkBuddy / 飞书 / WeKnora / Codex” 产品组合，调整为 Provider-neutral 能力架构。

因此本目录 01~15 中若仍出现 WorkBuddy、WeKnora、Codex 等名称，除非明确写成正式机器 Contract，否则应理解为**上一轮具体示例/候选 Provider**，不能覆盖以下新原则：

- WorkBuddy 不是唯一 Interaction Provider；
- 飞书是重要 Work Item/Collaboration 候选，但总体架构不绑定唯一 Provider；
- 飞书知识库、NAS、Git、CI/HIL 等按事实类型分别保留权威；
- WeKnora 是候选 Knowledge Provider，不自动成为企业知识唯一 SSOT；
- Codex、Claude Code、IDE Agent 等均可作为 Engineering Agent Runtime；
- Expert / Workflow / Gate / Evidence / Verification 与 Runtime 解耦。

总体 Provider 评审请优先阅读 **16《总体架构与 Provider 选型评审》**。

## 权威顺序

如本文档与实现资产冲突，按以下顺序裁决：

1. `研发中心AI数字员工研发流程规划.md` + ADR-003（总体架构与 Provider 边界）
2. `expert-groups/embedded-system/expert-group.yaml`
3. `config/workflow.yaml`
4. `config/task-modes.yaml`
5. `config/action-policy.yaml`
6. `config/gate-policy.yaml` / `config/material-requirements.yaml`
7. `contracts/experts/*.io.yaml` / `contracts/engineering-handoff.yaml`
8. `schemas/*.schema.json`
9. `agents/*.md`
10. `skills/*/SKILL.md`
11. 本目录说明文档
12. `docs/archive/` 与 `docs/source-materials/` 中的历史/原始输入

上位边界同时受：

- `docs/adr/ADR-001-workbuddy-codex-integration-boundary.md`
- `docs/adr/ADR-002-embedded-system-expert-team-architecture.md`
- `docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md`

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
|11|Workflow、Gate 与工程交接|评审任务模式、状态机、Gate 和 Engineering Agent Runtime 边界|
|12|Evidence、知识、自治与安全边界|评审证据模型、知识边界、A0-A7 与高风险操作|
|13|Pilot、评测与生产化评审|评审真实 Pilot、指标、安全门槛和 Productionization|
|14|跨专家团协作与职责边界|评审产品专家团、端侧底座与嵌入式系统专家团接口|
|15|内部评审问题清单|专家团组织/运行层拍板项|
|16|总体架构与 Provider 选型评审|评审 WorkBuddy/飞书/NAS/WeKnora/Codex/Claude 等候选的层级、PoC 和决策方法|

## 当前阶段必须明确的事实

- 1+7 Core Experts、23 个 P0 Skills、Engineering Handoff、Cross-Team Contract、Golden Cases、Pilot Contracts/CLI/CI 已落地。
- Engineering Handoff 已调整为 Provider-neutral `Engineer + Engineering Agent Runtime`。
- 总体 Provider 选型、Knowledge Provider 和默认 Coding Runtime 尚未冻结。
- `pilot-operations-ready` **不等于**真实 Pilot 已完成。
- #6 / #7 / #8 三条 real Pilot 仍待绑定真实工程任务。
- 端侧底座 ownership 尚未完成原文规范化和逐域裁决。
- `main` required check/branch protection 尚未由管理员启用。
- 因此当前严禁标记 `Production Ready`。
