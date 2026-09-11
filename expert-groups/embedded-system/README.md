# 嵌入式系统专家团

- Status: `architecture-frozen`
- Version: `0.1.0`
- Date: 2026-09-11
- Owner domain: 研发中心 / 嵌入式系统（软件）

## 1. 定位

本目录是 `digital-worker` 内嵌入式系统专家团的正式落地点。

权威设计：

- `../../docs/architecture/embedded-system-expert-team-v1.md`
- `../../docs/adr/ADR-002-embedded-system-expert-team-architecture.md`

上游总体流程：

- `../../研发中心AI数字员工研发流程规划_V2.md`
- `../../docs/adr/ADR-001-workbuddy-codex-integration-boundary.md`

主要工程化参考：

- `../../产品专家团-核心参考/`

`agent-dev-kit`、`knowledge-hub`、`codex` 等外部仓库可作为设计与实现参考，但不是本专家团定义的 SSOT，也不是当前阶段运行前置条件。

## 2. 当前冻结范围

当前只冻结架构契约，不宣称专家团生产实现完成：

- 1+7 组织模型；
- task taxonomy；
- workflow modes；
- Gate；
- evidence-first；
- 独立 verification/review；
- autonomy/action boundary；
- product expert handoff；
- 端侧底座 capability ownership 原则；
- evaluation contract。

## 3. 核心专家

- `embedded-system-team-lead`
- `embedded-architecture-expert`
- `linux-bsp-expert`
- `mcu-rtos-expert`
- `driver-component-expert`
- `debug-reliability-expert`
- `verification-expert`
- `embedded-review-governor`

## 4. 当前机器可读资产

- `expert-group.yaml`：顶层身份、成员、能力与治理边界；
- `config/task-modes.yaml`：task type 与默认路由；
- `config/workflow.yaml`：阶段、Gate 与主 transition skeleton。

后续将继续建设：

```text
agents/
contracts/
schemas/
skills/
references/
knowledge/
scripts/
tests/
```

## 5. 不可违反的工程原则

1. 先分类再路由，不默认 full chain；
2. 缺关键硬件/版本证据时 BLOCK 或显式降级；
3. Debug 区分 Observed / Inferred / Confirmed；
4. 实施者不能给自己的最终验证签 PASS；
5. Host / cross-build / device / HIL / release 状态分层；
6. 关键 claim 必须绑定 evidence；
7. 高风险设备写和发布动作保留人工 Gate；
8. 无 deliverable manifest 不宣称正式闭环；
9. 跨专家团通过 contract，不依赖自由聊天；
10. 新增 Agent 前先证明不能由现有 Agent + Skill 承担。

## 6. 下一阶段

按以下顺序推进：

1. Governance Skeleton；
2. Core Experts + L1 Contracts；
3. P0 Skills；
4. Engineering Handoff；
5. Product/端侧底座 Cross-Team Contract；
6. Golden Cases + Pilot。
