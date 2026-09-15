# 嵌入式系统专家团核心参考

> **状态：运行参考（Operational Reference） / target-first human view**  
> **当前仓库阶段：`iterative-development`**  
> **目标架构：ADR-004 / Edge Foundation Digital Responsibility Architecture**

本目录是嵌入式系统专家团的**唯一第一入口**。它只解释目标责任模型、工程运行方式和可信保障边界，不复制机器 Contract，也不把当前兼容执行身份重新包装成人类组织模型。

## 1. 先记住目标模型

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

稳定语义只有四层：

`Domain → Expert → Capability → Skill`

同时保持：

- Expert ≠ Agent / Session / Worker；
- Capability ≠ Agent；
- Edge Coordination 是 Role，不是第四个 Expert；
- Verification / Independent Review 属于 Assurance，不是 Embedded Capability；
- Engineering ≠ Verification ≠ Review；
- Source of Truth stays at source；
- Runtime Provider 可替换，责任与 Gate 不随 Provider 改变。

机器权威：[`../domains/edge-foundation/domain.yaml`](../domains/edge-foundation/domain.yaml)。

## 2. 当前为什么还能看到 legacy compatibility

当前 `canonical_routing_switched=false`。因此 `expert-groups/embedded-system/` 仍承担**兼容执行与 rollback surface**，但它不再定义目标组织、能力所有权或 Golden Case 权威。

旧身份到目标责任模型的唯一映射位于：

[`../domains/edge-foundation/compatibility/embedded-1plus7-mapping.yaml`](../domains/edge-foundation/compatibility/embedded-1plus7-mapping.yaml)

本核心参考**不复制映射内容、不列旧身份、不建立第二套“数字岗位”模型**。需要审计迁移关系时直接查看该机器映射；日常研发只按目标责任模型阅读本目录。

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

案例只演示如何套用目标模型，不重新定义组织或路由。Golden Case 的唯一机器权威是 [`../domains/edge-foundation/evaluation/golden-cases.yaml`](../domains/edge-foundation/evaluation/golden-cases.yaml)。

## 4. 当前真实 Pilot 状态

| Track | 状态 | 真实剩余项 |
|---|---|---|
| Feature | **DONE / eligible** | `FEATURE-PCR02-OTA-001` 已 completed，`phase3_evidence_eligible=true` |
| Debug | OPEN | SSC305/UBIFS exact repo/SHA、原始日志或复现、device/flash/kernel/test identity |
| Review / Release | OPEN | PCR02 实机 download/install/boot/rollback、required Verification、适用时 A7 human decision |

当前 iterative Pilot 阶段，Independent Review **优先但不可用时不是硬 completion gate**；可由 static checks + Hosted CI + traceable Verification evidence 替代。替代不等价于 Independent Review PASS，更不等价于 Device/HIL/Release/Production Ready PASS。

三轨未完成前，Phase-3 readiness 保持 BLOCKED，且：

```text
canonical_routing_switched=false
```

## 5. 阅读原则

1. 查“谁负责什么” → `01-责任模型与协作` 与 `domains/edge-foundation/domain.yaml`；
2. 查“Embedded 专业能力” → `04-专业能力` 的 5 个 Capability；
3. 查“原子技能归谁” → Skill 能力地图与 `domains/edge-foundation/skills.yaml`；
4. 查“任务怎么路由” → 任务类型运行矩阵与 `domains/edge-foundation/routing-shadow.yaml`；
5. 查“证据够不够” → Verification / Gate / Pilot；
6. 查“旧执行身份为什么还存在” → compatibility mapping，核心参考不再复制。

目标不是继续维护两套语义，而是在 canonical switch 前做到：**目标责任模型唯一、兼容执行面最小、历史通过 Git/PR/Issue 保存。**
