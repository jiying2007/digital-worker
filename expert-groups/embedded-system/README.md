# 嵌入式系统专家团

- Architecture status: `frozen`
- Implementation status: `governance-and-core-experts-defined`
- Version: `0.2.0`
- Date: 2026-09-11
- Owner domain: 研发中心 / 嵌入式系统（软件）

## 1. 定位

本目录是 `digital-worker` 内嵌入式系统专家团的正式 SSOT。外部 `agent-dev-kit`、`knowledge-hub`、`codex` 等仓库只作参考或未来可选连接，不是当前运行前置依赖。

权威设计：

- `../../docs/architecture/embedded-system-expert-team-v1.md`
- `../../docs/adr/ADR-002-embedded-system-expert-team-architecture.md`

上游总体流程：

- `../../研发中心AI数字员工研发流程规划_V2.md`
- `../../docs/adr/ADR-001-workbuddy-codex-integration-boundary.md`

## 2. 当前已落地

### 组织

1+7 核心专家定义已经落入 `agents/`，并为每个专家建立 L1 I/O Contract：

- `embedded-system-team-lead`
- `embedded-architecture-expert`
- `linux-bsp-expert`
- `mcu-rtos-expert`
- `driver-component-expert`
- `debug-reliability-expert`
- `verification-expert`
- `embedded-review-governor`

### Governance Skeleton

已建立：

- `config/task-modes.yaml`：task type 与路由；
- `config/workflow.yaml`：阶段/Gate/恢复；
- `config/action-policy.yaml`：A0-A7 动作边界；
- `config/gate-policy.yaml`：Gate 判定契约；
- `config/material-requirements.yaml`：材料就绪矩阵；
- `contracts/io-layering.md`：三层 I/O 规则；
- `contracts/experts/`：专家 L1 契约；
- `schemas/`：证据、运行态、门禁、诊断、交接、验证、审查、收口机器契约；
- `governance/authority-index.md`：权威来源顺序；
- `governance/done-definition.md`：完成声明边界。

## 3. 当前核心运行链

```text
task-brief
  -> Gate K / Gate M / Gate 0
  -> Technical Triage
  -> Domain Analysis
  -> Gate T
  -> Gate E / engineering-task-package
  -> Engineer + Codex
  -> delivery-receipt
  -> Gate V / Verification Expert
  -> Gate R / Review Governor
  -> Gate C / deliverable-manifest
```

当前仍遵守 ADR-001：WorkBuddy 不直接遥控个人 Codex CLI。

## 4. 不可违反的工程原则

1. 先分类再路由，不默认 full chain；
2. 缺关键硬件/版本证据时 BLOCK 或显式降级；
3. Debug 区分 Observed / Inferred / Confirmed，并维护 Hypothesis Registry；
4. 实施者不能给自己的最终验证签 PASS；
5. Host / cross-build / device / HIL / release 状态分层；
6. 关键 claim 必须绑定 evidence；
7. 高风险设备写和发布动作保留人工 Gate；
8. 无 deliverable manifest 不宣称正式闭环；
9. 跨专家团通过 contract，不依赖自由聊天；
10. 新增 Agent 前先证明不能由现有 Agent + Skill 承担。

## 5. 尚未完成

当前不是 Production Ready。下一阶段依次为：

1. P0 Skills；
2. Engineering Handoff 与共享 `task-brief/delivery-receipt` schema；
3. Product Expert / 端侧底座 Cross-Team Contract；
4. Golden Cases、结构校验脚本与回归；
5. 真实项目 Pilot。
