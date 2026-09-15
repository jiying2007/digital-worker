# 嵌入式系统专家团核心参考

> **状态：运行参考（Operational Reference） / canonical target human view**  
> **当前仓库阶段：`iterative-development`**  
> **目标架构：ADR-004 / Edge Foundation Digital Responsibility Architecture**

本目录是嵌入式系统专家团的**唯一第一入口**。它解释当前 canonical 责任模型、工程运行方式和可信保障边界；机器权威位于 `domains/edge-foundation/**`，历史迁移过程由 Git/ADR 保存，不在活动文档维护第二套兼容架构。

## 1. Canonical 责任模型

```text
Edge Foundation Domain
├─ Edge Coordination Role        # 协调职责，不是 Expert
├─ Structure Expert
├─ Hardware Expert
└─ Embedded System Expert
   ├─ embedded.architecture
   ├─ embedded.linux-bsp
   ├─ embedded.mcu-rtos
   ├─ embedded.driver-component
   └─ embedded.debug-reliability

Assurance Plane
├─ Verification
└─ Independent Review
```

稳定语义只有四层：`Domain → Expert → Capability → Skill`。

同时保持：

- Expert ≠ Agent / Session / Worker；
- Capability ≠ Agent；
- Edge Coordination 是 Role，不是第四个 Expert；
- Verification / Independent Review 属于 Assurance；
- Engineering ≠ Verification ≠ Review；
- Source of Truth stays at source；
- Runtime Provider 可替换，责任、Gate 与 Evidence Contract 不随 Provider 改变。

机器权威：[`../domains/edge-foundation/domain.yaml`](../domains/edge-foundation/domain.yaml)。正式任务路由：[`../domains/edge-foundation/routing.yaml`](../domains/edge-foundation/routing.yaml)。

## 2. Runtime 与 Product readiness 已解耦

Edge Foundation target runtime 已是 **canonical execution authority**。Skill、Gate、Routing、Pilot、Schema、Knowledge bootstrap、Golden Cases 和 Assurance 都从 `domains/edge-foundation/**` 读取；活动执行面不再维护旧组织兼容树。

**Product readiness** 是独立的真实产品证据 Gate，不控制 routing authority。目前三轨状态：

| Track | 状态 | 真实剩余项 |
|---|---|---|
| Feature | **DONE / eligible** | `FEATURE-PCR02-OTA-001` 已 completed，canonical Pilot receipt 为 eligible |
| Debug | **BLOCKED** | SSC305/UBIFS exact repo/SHA、原始日志或复现、device/flash/kernel/test identity、Verification |
| Review / Release | **BLOCKED** | PCR02 实机 install/boot/resulting-version/rollback-or-scope-exemption、Device/HIL Verification、实际发布时 A7 human decision |

所以当前 Product readiness 仍是 **1/3 eligible / BLOCKED**。这不会回滚 canonical routing，也不代表 Production Ready 或 Release Ready。

当前 iterative Pilot 阶段，Independent Review 优先；不可用时可按当前 stage policy 使用 traceable Verification + static checks + Hosted CI 完成 Pilot。该豁免不等价于 Independent Review PASS，更不能替代 Device/HIL 或 A7。

## 3. 信息架构

### 01 责任模型与协作
- [责任模型总览](01-责任模型与协作/01%20责任模型总览.md)
- [责任协作与 RACI](01-责任模型与协作/02%20责任协作与RACI.md)
- [跨域协作与边界](01-责任模型与协作/03%20跨域协作与边界.md)

### 02 架构设计
- [总体架构设计](02-架构设计/01%20总体架构设计.md)
- [系统边界与控制面](02-架构设计/02%20系统边界与控制面.md)
- [身份证据与知识架构](02-架构设计/03%20身份证据与知识架构.md)
- [质量属性与非功能约束](02-架构设计/04%20质量属性与非功能约束.md)

### 03 流程与运行
- [任务生命周期与 Gate](03-流程与运行/01%20任务生命周期与Gate.md)
- [Debug 问题闭环流程](03-流程与运行/02%20Debug问题闭环流程.md)
- [功能开发、Bring-up 与多仓协同](03-流程与运行/03%20功能开发Bring-up与多仓协同.md)
- [验证、评审、发布与异常恢复](03-流程与运行/04%20验证评审发布与异常恢复.md)
- [任务类型运行矩阵](03-流程与运行/05%20任务类型运行矩阵.md)

### 04 Embedded System Expert 的 5 个 Capability
- [嵌入式架构](04-专业能力/01%20嵌入式架构能力域指南.md)
- [Linux / BSP](04-专业能力/02%20Linux%20BSP能力域指南.md)
- [MCU / RTOS](04-专业能力/03%20MCU%20RTOS能力域指南.md)
- [驱动与组件](04-专业能力/04%20驱动与组件能力域指南.md)
- [调试与可靠性](04-专业能力/05%20调试与可靠性能力域指南.md)

### 05 工程交付
- [Skill 能力地图](05-工程交付/01%20Skill能力地图.md)
- [工程交接、Runtime 与关键产物](05-工程交付/02%20工程交接Runtime与关键产物.md)
- [完整任务产物样例](05-工程交付/03%20完整任务产物样例.md)

### 06 治理与可信保障
- [评审说明与决策清单](06-治理与评审/01%20评审说明与决策清单.md)
- [权限、安全、风险与例外](06-治理与评审/02%20权限安全风险与例外.md)
- [Pilot 指标、成熟度与生产化](06-治理与评审/03%20Pilot指标成熟度与生产化.md)
- [架构取舍与演进原则](06-治理与评审/04%20架构取舍与演进原则.md)
- [Verification 责任与证据](06-治理与评审/05%20Verification责任与证据.md)
- [Independent Review 与发布边界](06-治理与评审/06%20Independent%20Review与发布边界.md)

### 07 案例
案例演示如何套用 canonical 责任模型。Golden Case 的机器权威是 [`../domains/edge-foundation/evaluation/golden-cases.yaml`](../domains/edge-foundation/evaluation/golden-cases.yaml)。

## 4. 阅读原则

1. 查“谁负责什么” → `01-责任模型与协作` 与 `domains/edge-foundation/domain.yaml`；
2. 查“Embedded 专业能力” → `04-专业能力` 的 5 个 Capability；
3. 查“原子技能归谁” → Skill 能力地图与 `domains/edge-foundation/skills.yaml`；
4. 查“任务怎么路由” → 任务类型运行矩阵与 `domains/edge-foundation/routing.yaml`；
5. 查“Evidence 是否足够” → Gate、Verification、Pilot receipt；
6. 查“产品是否可进入生产化评审” → `scripts/evaluate_edge_foundation_product_readiness.py`；
7. 查历史迁移原因 → ADR / Git history，不从活动 runtime 反推。

终态目标是：**canonical 责任与执行只有一套；Product readiness 对真实产品证据保持 fail-closed；历史迁移只保留在可审计历史中。**
