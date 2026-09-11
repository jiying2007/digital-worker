# 嵌入式系统专家团

- Architecture status: `frozen`
- Implementation status: `cross-team-and-golden-baseline-defined`
- Version: `0.4.0`
- Date: 2026-09-11
- Owner domain: 研发中心 / 嵌入式系统（软件）

## 当前能力

当前已经形成可用于真实试点的结构化基线：

- 1+7 核心专家 + L1 I/O Contract；
- mode-aware Workflow、Gate、A0-A7 Action Policy、Material Readiness；
- Evidence / Run State / Gate Ledger / Hypothesis Registry / Verification / Review / Closure；
- 23 个 P0 Skills，默认最大 A2；
- `task-brief -> engineering-task-package -> delivery-receipt` Engineering Handoff；
- HIL evidence identity contract；
- Product Expert Team -> Embedded System Team 技术可行性 handoff；
- 12 个真实嵌入式类型 Golden Cases；
- fail-closed validator + GitHub Actions CI。

## Product Expert Team 协作

`contracts/cross-team/product-expert-handoff.yaml` 冻结：

```text
Product Expert Team
  -> technical-review-request
Embedded System Expert Team
  -> embedded-feasibility-review
Product Expert Team
```

产品专家团负责 What/Why/优先级/产品范围；嵌入式专家团负责 How/可行性/架构与平台影响/工程风险/验证策略。双方都不能越权替代最终产品 Go/No-Go、Production Release 或不可逆设备动作审批。

## 端侧底座边界

`contracts/cross-team/edge-foundation-ownership.yaml` 已冻结 OWN/SHARED/CONSUME/PROVIDE/OUT_OF_SCOPE 协议，但**尚未填写具体 ownership**。原因是当前权威来源仍是二进制 `端侧底座专家团创建.docx`，尚未规范化为可逐项审查的文本证据。未完成 ownership resolution 前，重叠领域禁止创建重复 Agent/Skill。

## Golden Cases

`tests/golden-cases.yaml` 首批覆盖 Boot、Kernel Panic、MCU HardFault、SPI-NAND ECC、UBIFS、DMA Cache、RTOS Deadlock、Linker/ROM-RAM、Driver、Platform Bring-up、Code Review、OTA Release。

CI 校验每个 case 的 task type、workflow mode、primary expert、schema 和唯一 ID，作为后续 Agent/Skill/Prompt/Model 变化的 regression baseline。

## 当前边界

当前仍不是 Production Ready：Golden Cases 已建立结构基线，但还没有真实项目结果标签、准确率/误报/错放行统计和试点回执。

下一阶段优先进入真实 Pilot，并用 Pilot 证据完成：
1. Golden Case expected outcome/fixture 丰富；
2. Routing / Unsupported Claim / Incorrect PASS 等指标实测；
3. 端侧底座 ownership resolution；
4. 根据真实缺口决定 P1 Skills，而不是提前堆能力。
