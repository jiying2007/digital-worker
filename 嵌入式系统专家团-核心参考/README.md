# 嵌入式系统专家团-核心参考

> **用途：内部讨论与评审。**
>
> 文档状态：`review-ready`
>
> 实现基线：`expert-groups/embedded-system/` v0.7.0 / `pilot-operations-ready`
>
> 总体架构：`provider-neutral / proposed-for-review`

本目录是嵌入式系统专家团机器资产的人类可读解释层，与 `产品专家团-核心参考/` 同类型；不是第二套实现，也不是第二套 SSOT。

正式 Architecture Review 请从 [`docs/review/`](../docs/review/) 开始。`docs/review/` 提供 Pre-read、Decision Matrix、Evidence Gap、RACI 与端到端 Walkthrough；本目录用于需要深入追溯专家团细节时查阅。

## 当前同步状态

01~16 已统一按 ADR-003 的 Provider-neutral 架构解释：

- WorkBuddy 只是候选 Interaction / Office Agent Provider；
- 飞书是重要 Collaboration / Work Item 候选，但不是架构硬依赖；
- 飞书知识库、NAS、Git、CI/HIL、Artifact Store 等按事实类型分别保持权威；
- WeKnora 是候选 Knowledge Provider，不自动成为企业知识唯一 SSOT；
- Codex、Claude Code、IDE Agent、内部 Agent 等均可作为 Engineering Agent Runtime；
- Expert / Workflow / Gate / Evidence / Verification 与 Runtime 解耦；
- Provider 选型必须基于 Source Inventory、Capability Matrix 与 PoC evidence。

## 权威顺序

1. `研发中心AI数字员工研发流程规划.md` + ADR-003；
2. `expert-groups/embedded-system/expert-group.yaml`；
3. `config/workflow.yaml`；
4. `config/task-modes.yaml`；
5. `config/action-policy.yaml`；
6. `config/gate-policy.yaml` / `config/material-requirements.yaml`；
7. `contracts/**/*.yaml`；
8. `schemas/*.schema.json`；
9. `agents/*.md`；
10. `skills/*/SKILL.md`；
11. 本目录说明文档；
12. `docs/review/`（评审准备材料，不覆盖上位权威）；
13. `docs/archive/` 与 `docs/source-materials/`。

## 文档索引

|编号|文档|主要用途|
|---|---|---|
|01|嵌入式系统专家团整体架构|1+7、Provider-neutral 主链、Gate、边界|
|02|主理人专家工作逻辑|接诊、路由、Gate、Runtime-neutral Handoff、收口|
|03|嵌入式架构专家工作逻辑|架构/可行性/资源与接口职责|
|04|Linux BSP 专家工作逻辑|Boot/BSP/Kernel/DT/IRQ/DMA/Storage|
|05|MCU RTOS 专家工作逻辑|MCU/RTOS/Bare-metal/Linker/ISR|
|06|驱动与组件专家工作逻辑|驱动、外设、组件集成与复用|
|07|调试与可靠性专家工作逻辑|Evidence/Hypothesis/Root Cause|
|08|验证专家工作逻辑|Host/Cross-build/SIL/Device/HIL/Release|
|09|独立审查专家工作逻辑|Independent Review / Release Readiness|
|10|全量原子能力（Skill）清单|23 个 P0 Skills 与扩展原则|
|11|Workflow、Gate 与工程交接|Mode、Gate、Engineering Agent Runtime 边界|
|12|Evidence、知识、自治与安全边界|Evidence、Source-of-Truth、Knowledge Provider、A0-A7|
|13|Pilot、评测与生产化评审|三轨 Pilot、Multi-runtime、生产化门槛|
|14|跨专家团协作与职责边界|跨团 Contract、Runtime、Knowledge/Work Item Provider 边界|
|15|内部评审问题清单|组织、治理、Provider-neutral 决策清单|
|16|总体架构与 Provider 选型评审|Knowledge/Provider/Runtime PoC 与 Capability Matrix|

## 当前事实

- 1+7、23 P0 Skills、Engineering Handoff、Cross-Team Contract、Golden Cases、Pilot CLI/CI 已落地；
- Engineering Handoff 已是 `Engineer + Engineering Agent Runtime`；
- Provider / Knowledge 方案 / 默认 Coding Runtime 仍 `not-frozen`；
- #16 Knowledge Source Inventory、#17 Provider Capability Matrix、#18 Multi-runtime Pilot 已登记；
- #6/#7/#8 real Pilot 仍待真实任务绑定；
- #11 端侧底座 ownership、#12 main protection、#19 merged branch GC 尚未完成；
- 当前禁止声明 `Production Ready`。
