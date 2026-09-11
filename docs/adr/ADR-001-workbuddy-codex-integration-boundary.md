# ADR-001：WorkBuddy 与 Codex CLI 的集成边界

- Status: superseded-in-part
- Date: 2026-09-09
- Scope: 当 WorkBuddy 作为办公入口、Codex CLI 作为工程 Runtime 时的集成边界
- Superseded by: `ADR-003-provider-neutral-ai-rd-target-architecture.md`（总体 Provider 绑定部分）
- Retained principle: 办公/协作入口与工程执行 Runtime 通过结构化 Contract 松耦合，不直接把办公入口变成个人开发机控制面
- Related: `../../研发中心AI数字员工研发流程规划.md`

## Context

本 ADR 最初用于比较三种 WorkBuddy ↔ Codex 集成方式：

1. WorkBuddy 直接启动/遥控个人开发机 Codex CLI；
2. WorkBuddy 生成结构化任务输入，工程师在目标仓启动 Codex，Codex 输出结构化回执；
3. 建设隔离 Runner/执行网关，由 WorkBuddy 调用受控工程执行环境。

后续架构审查确认：WorkBuddy 不是唯一办公入口，Codex 也不是唯一 Engineering Agent Runtime。Claude Code、IDE Agent、内部 Agent 或其他 Runtime 都可能存在。因此，本 ADR 不再承担“总体平台选型”职责，只保留其**执行边界原则**。

## Decision retained

当任何 Office / Interaction Provider 与个人开发环境或 Engineering Agent Runtime 协作时，默认采用：

> **输入/输出 Contract 松耦合，而不是办公入口直接获得个人开发机、设备和发布控制权。**

稳定主链：

```text
Interaction / Work Item Provider
        -> task-brief
        -> Expert / Governance
        -> engineering-task-package
        -> Engineer + Engineering Agent Runtime
        -> delivery-receipt
        -> Verification / Review
        -> Work Item / Collaboration Provider
```

具体 Runtime 可以是 Codex、Claude Code、IDE Agent、受控 Runner 或其他实现。

## Why direct desktop control is not the default

直接把办公 Agent 变成个人开发机控制面会放大以下问题：

- repo root / branch / exact base / dirty baseline 不确定；
- 个人凭证、SSH、设备权限和生产密钥边界模糊；
- 会话超时、取消、重复执行和恢复难以审计；
- Host / build / device / HIL / release 状态容易混淆；
- 办公身份与工程身份可能不是同一安全主体；
- Agent Provider 更换时控制链会整体重构。

## Decision Matrix retained as historical rationale

原比较结论仍有效地支持“Contract 松耦合优先”：

|维度|直接控制个人 CLI|Contract 松耦合|受控执行网关|
|---|---:|---:|---:|
|一期复杂度|中|低|高|
|权限边界|弱|强|强|
|审计/恢复|弱|中-强|强|
|嵌入式现场适配|中|强|中|
|长期自动化|高但风险大|中|高|

当前阶段默认选择 Contract 松耦合；受控执行网关是否建设，由真实 Pilot 和 Runtime PoC 决定。

## Provider-neutral interpretation

ADR-003 生效后，本 ADR 中的专有名词应按下列方式理解：

- WorkBuddy → `Interaction / Office Agent Provider` 的一个候选；
- Codex CLI → `Engineering Agent Runtime` 的一个候选；
- 飞书 → `Work Item / Collaboration Provider` 的一个候选；
- WeKnora → `Knowledge Provider` 的一个候选。

因此，任何新 Provider 不需要复制一套新 ADR，只要遵守同样的 Contract / Action / Evidence 边界即可。

## Invariants

- 办公入口默认不持有开发机全局 Shell；
- Runtime 修改代码前必须确认 repo root / exact base / dirty baseline；
- A6 Device Write 与 A7 Release 保持人工审批；
- Host/Cross-build/HIL/Release 状态不得互相推导；
- `blocked`、`unverified_items`、risk 不得被入口层隐藏；
- Provider 更换不得改变 `task-brief` / `delivery-receipt` 的工程语义。

## Revisit triggers

- 组织建设统一受控 Agent Runtime Gateway；
- 某办公平台获得经企业安全评审的工程执行能力；
- 真实 Pilot 证明人工 handoff 成为主要瓶颈；
- 需要夜间无人值守批量任务；
- 现有 Contract 无法覆盖新的工程 Runtime。
