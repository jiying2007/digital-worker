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

已建立 task routing、workflow、A0-A7 action policy、Gate policy、material readiness、三层 I/O、Evidence、Run State、Gate Ledger、Hypothesis Registry、Engineering Task Package、Verification、Independent Review 和 Closure Manifest 契约。

## 3. 运行路径

`config/workflow.yaml` 按 `workflow_mode` 明确不同路径；**并非所有任务都进入工程执行**。

- `full_chain / short_chain / diagnostic_chain / bringup_chain`：可进入 Engineering Execution；
- `review_only`：只分析/审查，不允许隐式进入代码修改；
- `release_chain`：默认做发布准备度验证，若需代码修改必须显式扩展模式；
- `single_expert`：完成单领域分析后收口，不自动扩链。

工程执行路径仍遵守 ADR-001：

```text
engineering-task-package -> Engineer + Codex -> delivery-receipt
```

WorkBuddy 当前不直接遥控个人 Codex CLI。

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
