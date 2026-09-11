# 嵌入式系统专家团

- Architecture status: `frozen`
- Implementation status: `pilot-infrastructure-ready`
- Version: `0.5.0`
- Date: 2026-09-11
- Owner domain: 研发中心 / 嵌入式系统（软件）

## 当前已落地

专家团已经从“架构/契约基线”推进到“真实 Pilot 可接入”的阶段：

- 1+7 核心专家 + L1 I/O Contract；
- mode-aware Workflow、Gate、A0-A7、Material Readiness；
- Evidence / Run State / Gate Ledger / Hypothesis / Verification / Independent Review；
- 23 个 P0 Skills（默认最大 A2）；
- Engineering Handoff：`task-brief -> engineering-task-package -> Engineer + Codex -> delivery-receipt`；
- Product Expert Team 技术可行性跨团队契约；
- 端侧底座 ownership fail-closed 协议；
- 12 个 Golden Cases；
- fail-closed validator + PR/main CI；
- Pilot Run / Result / Metrics 三套共享 Schema；
- 三轨 Pilot Plan、真实 Pilot Runbook、指标聚合器与安全自测 fixture。

## Pilot 状态

`pilot-infrastructure-ready` 只表示基础设施具备，**真实 Pilot 目前还没有在本仓形成 completed evidence**。

真实 Pilot 至少覆盖：

1. `debug`：真实 Bug / Crash / HardFault / UBIFS / DMA / 长稳任务；
2. `feature`：真实 Feature / Driver / Component / MCU / Bring-up；
3. `review_release`：真实 Code Review / Feasibility / OTA Release Readiness。

详见 `pilot/README.md` 与 `../../docs/runbooks/embedded-pilot.md`。

## Pilot 安全门槛

三个轨道各至少 1 个真实 completed run，且：

- `incorrect_pass_rate = 0`；
- `unauthorized_actions = 0`；
- `audit_trace_completeness = 1.0`。

通过这些门槛也**不会自动改为 Production Ready**，只允许进入单独的人工生产化评审。Synthetic fixtures 永远不计入真实 Pilot 数量。

## 跨团队边界

产品专家团已经有正式 technical review handoff。端侧底座目前只冻结 ownership 协议，具体 ownership 仍为 unresolved；在权威原文未规范化并裁决前，不创建重复 Agent/Skill。

## 下一阶段

不再继续无证据扩张专家数量。下一步是绑定 3 个真实研发工作项，跑完整 Pilot，采集 Routing / Evidence / Unsupported Claim / Incorrect PASS / Verification / Human Correction 等指标，再决定 P1 Skills 和 productionization 是否值得推进。
