# 嵌入式系统专家团

- Architecture status: `frozen`
- Implementation status: `p0-skills-and-engineering-handoff-defined`
- Version: `0.3.0`
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

### 组织与治理

1+7 核心专家、L1 I/O Contracts、task routing、mode-aware workflow、A0-A7 action policy、Gate policy、material readiness、Evidence、Run State、Gate Ledger、Hypothesis Registry、Verification/Review/Closure 契约均已落地。

### P0 Skills

`config/p0-skills.yaml` 注册首批高频 Skills，覆盖接诊/证据、架构、Linux/BSP、MCU/RTOS、驱动、Debug/Reliability、Verification 与 Release Readiness。P0 Skill 默认最大动作等级为 A2，不直接修改代码或设备。

### Engineering Handoff

共享契约已落地：
- `../../schemas/task-brief.v1.schema.json`
- `../../schemas/delivery-receipt.v1.schema.json`
- `../../schemas/hil-evidence.v1.schema.json`
- `contracts/engineering-handoff.yaml`

工程执行继续遵守 ADR-001：

```text
task-brief
  -> Expert Team
  -> engineering-task-package
  -> Engineer + Codex
  -> delivery-receipt
  -> Verification
  -> Independent Review
```

WorkBuddy 当前不直接遥控个人 Codex CLI。

### 自动校验

`scripts/validate_embedded_assets.py` 对专家/路由/Workflow/Skill registry/Schema/Handoff/正负 fixture 做 fail-closed 校验；`.github/workflows/embedded-expert-contracts.yml` 在相关 PR 和 main push 上自动执行。

## 3. 不可违反的工程原则

1. 先分类再路由，不默认 full chain；
2. 缺关键硬件/版本证据时 BLOCK 或显式降级；
3. Debug 区分 Observed / Inferred / Confirmed，并维护 Hypothesis Registry；
4. 实施者不能给自己的最终验证签 PASS；
5. Host / cross-build / device / HIL / release 状态分层；
6. 关键 claim 必须绑定 evidence；
7. 高风险设备写和发布动作保留人工 Gate；
8. 无 deliverable manifest 不宣称正式闭环；
9. 跨专家团通过 contract，不依赖自由聊天；
10. 新增 Agent 或 Skill 前必须通过 SSOT 注册与结构校验。

## 4. 当前状态与下一阶段

当前已经具备承接真实任务所需的**结构化输入、专家路由、技术分析、工程交接、回执和验证契约基线**，但仍不是 Production Ready。

下一阶段：
1. Product Expert / 端侧底座 Cross-Team Contract；
2. Golden Cases + regression；
3. 真实项目 Pilot；
4. 根据 Pilot 证据再决定 P1 Skills、设备实验室网关和更高自治等级。
