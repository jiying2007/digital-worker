# 嵌入式系统专家团核心参考

> 文档状态：**运行参考（operational reference）**  
> 对应兼容实现：`expert-groups/embedded-system/` v0.7.0  
> 目标责任架构：`domains/edge-foundation/` + `ADR-004`  
> 当前阶段：`iterative-development` / `phase-1-shadow`  
> 当前目标：在不破坏现有机器 Contract 和 Pilot 的前提下，将嵌入式 `1+7` 从“目标组织结构”迁移为“嵌入式专家内部能力 + 可信保障职责”的兼容执行面。

本文件仍是**唯一第一入口**。核心参考按“数字组织 → 架构 → 流程 → 专业能力 → 工程交付 → 治理评审 → 案例 → 附录”组织；现有详细机器规则仍由 `expert-groups/embedded-system/` 执行，新目标责任模型以 `docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md` 和 `domains/edge-foundation/domain.yaml` 为准。

## 0. 当前迁移语义

端侧底座目标责任模型不再把嵌入式 `1+7` 视为最终组织层级。当前目标是：

```text
端侧底座领域（Edge Foundation Domain）
│
├─ 端侧协调角色（Edge Coordination Role）
├─ 结构专家（Structure Expert）
├─ 硬件专家（Hardware Expert）
└─ 嵌入式系统专家（Embedded System Expert）
     └─ 能力域（Capability）→ 技能（Skill）
```

现有 `1+7 / 8 个数字岗位 / 23 P0 Skill / 14 Task / 7 Mode / 8 Gate / A0-A7 / 7 层 Verification` 是**迁移期机器兼容基线**，不是新的端侧目标组织语义。旧身份与新模型的 8/8 显式映射见 `domains/edge-foundation/compatibility/embedded-1plus7-mapping.yaml`。

三条迁移红线：

1. 不因组织语义重构破坏现有 Gate / Evidence / Verification / Review / Action Policy；
2. 不把 Capability（能力域）默认固化成独立 Agent；
3. 在 canonical routing 切换和真实 Pilot 证明前，不直接删除旧 1+7 身份。

## 1. 第一次阅读

按以下顺序即可建立全局认知：

1. [ADR-004：端侧底座数字责任架构](../docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md)：理解新的稳定责任层级与中英术语；
2. [数字员工组织与运行总览](01-数字组织与岗位/01%20数字员工组织与运行总览.md)：理解当前兼容执行模型和主链；
3. [数字岗位与能力模型](01-数字组织与岗位/03%20数字岗位与能力模型.md)：理解旧 6 Module / 8 Position 如何作为迁移资产继续使用；
4. [总体架构设计](02-架构设计/01%20总体架构设计.md)：理解控制面、Provider-neutral、Runtime 和系统边界；
5. [任务类型运行矩阵](03-流程与运行/05%20任务类型运行矩阵.md)：迁移期日常接单仍按现有 Task/Mode 执行。

真实 Pilot 和人工 Productionization Review 达标前，不声明 Production Ready，也不声明旧数字岗位已经完全替代人工或已经完成 canonical 迁移。

## 2. 信息架构

|目录|只回答什么问题|
|---|---|
|`01-数字组织与岗位`|迁移期数字岗位、职责、协作和胜任证据是什么？|
|`02-架构设计`|系统为什么这样设计，边界、身份、证据和 NFR 是什么？|
|`03-流程与运行`|一项任务如何分类、经过 Gate、验证、审查和收口？|
|`04-专业能力`|Architecture / BSP / MCU / Driver / Debug / Verification / Review 具体怎么做专业工作？|
|`05-工程交付`|Skill、Runtime、Artifact、Receipt 和完整交付长什么样？|
|`06-治理与评审`|权限、安全、风险、评审、Pilot、成熟度和演进怎么管？|
|`07-案例`|一类具体任务如何把 Context、Evidence、Decision 和各阶段串起来？|
|`附录`|术语和缩写是什么意思？|

## 3. 内容归属：一个规则只详细解释一次

|主题|唯一详细人类来源|其他文档怎么处理|
|---|---|---|
|目标责任架构 / Domain-Expert-Capability-Skill 层级|[ADR-004](../docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md)|本核心参考只解释兼容执行语义|
|迁移期数字岗位职责 / 输入输出 / 任职资格|[数字岗位与能力模型](01-数字组织与岗位/03%20数字岗位与能力模型.md)|总览和 RACI 只摘要/引用|
|岗位内部协作|[数字岗位协作与 RACI](01-数字组织与岗位/02%20组织职责与RACI.md)|岗位说明不重复 RACI 表|
|跨团队协作|[跨团队 RACI](01-数字组织与岗位/04%20跨团队RACI.md)|案例只引用相关责任|
|Task Type / Workflow Mode 路由|[任务类型运行矩阵](03-流程与运行/05%20任务类型运行矩阵.md)|迁移期不复制第二套路由表|
|Gate / 状态 / 失败回流|[任务生命周期与 Gate](03-流程与运行/01%20任务生命周期与Gate.md)|专业 SOP 不重定义 Gate|
|P0 Skill ID / Owner / 用途|[Skill 能力地图](05-工程交付/01%20Skill能力地图.md)|岗位只显示 Skill 数和 Profile 链接|
|A0-A7 / 人工高风险边界|[权限、安全、风险与例外](06-治理与评审/02%20权限安全风险与例外.md)|总览只说明能力≠权限|
|Verification Layer / Review Decision / Release Readiness|[验证、评审、发布与异常恢复](03-流程与运行/04%20验证评审发布与异常恢复.md)|Verification/Review SOP 只写“怎么做”|
|专业分析方法|`04-专业能力/*`|岗位文档只说明“负责什么”|
|术语|[术语与缩写](附录/术语与缩写.md) + ADR-004 规范术语表|其他文档不维护第三套词典|

维护原则：**详细定义只在唯一来源修改；其他位置只保留必要摘要和链接。** 这避免人类文档之间形成第二套 SSOT。

## 4. 按工作场景查

|现在要做什么|优先入口|
|---|---|
|理解最终责任架构|[ADR-004](../docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md)|
|理解迁移期数字岗位|[数字岗位与能力模型](01-数字组织与岗位/03%20数字岗位与能力模型.md)|
|看岗位内部/跨团队协作|[数字岗位协作与 RACI](01-数字组织与岗位/02%20组织职责与RACI.md) / [跨团队 RACI](01-数字组织与岗位/04%20跨团队RACI.md)|
|不知道任务走哪条链|[任务类型运行矩阵](03-流程与运行/05%20任务类型运行矩阵.md)|
|缺陷、长稳、现场问题|[Debug 问题闭环](03-流程与运行/02%20Debug问题闭环流程.md)|
|功能、驱动、Bring-up、多仓|[功能开发与多仓协同](03-流程与运行/03%20功能开发Bring-up与多仓协同.md)|
|验证、Review、OTA/Release|[验证评审发布与异常恢复](03-流程与运行/04%20验证评审发布与异常恢复.md)|
|查某一专业 SOP|[专业能力](04-专业能力/01%20嵌入式架构领域指南.md)|
|看 Skill / 工程交付物|[Skill 能力地图](05-工程交付/01%20Skill能力地图.md) / [工程交接与关键产物](05-工程交付/02%20工程交接Runtime与关键产物.md)|
|做正式评审或治理|[评审说明与决策清单](06-治理与评审/01%20评审说明与决策清单.md) / [权限安全风险与例外](06-治理与评审/02%20权限安全风险与例外.md)|
|看完整任务如何走|[案例](07-案例/01%20UBIFS只读问题走查.md)|

## 5. 人类视图与机器 Contract

```text
ADR-004 + domains/edge-foundation/（目标责任模型）
   ↓
README（唯一人类入口）
   ↓
01~07 + 附录（迁移期职责、方法、流程、治理和案例）
   ↓
expert-groups/embedded-system/（旧机器 Contract 兼容执行面）
```

迁移期执行冲突时：目标责任语义优先回 `ADR-004` / `domains/edge-foundation/domain.yaml`；旧任务的具体 Task / Skill / Gate / Action / Verification 执行仍回 `expert-groups/embedded-system/expert-group.yaml` → `config/*` → `contracts/* / schemas/*` → Agent Definition / Skill / Runtime scripts。

`01-数字组织与岗位/human-view.yaml` 继续只保存旧岗位的人类注解，不新增第二套 Domain/Capability 机器规则。新的责任层级只在 `domains/edge-foundation/` 维护。

## 6. 当前推进重点

当前迁移顺序：

`phase-1 shadow model → dual evaluation → canonical routing switch → legacy identity deprecation → real Pilot proven removal`

同时真实工程证据链继续推进：

`Debug → Feature → Review/Release → Knowledge reuse / 外部 Source → Multi-runtime → Productionization Review`

只有真实任务暴露稳定、重复的职责/Skill/流程/Evidence 缺口时，才调整核心 Contract；不能仅为了让组织图更整齐而增加 Expert 或 Agent。
