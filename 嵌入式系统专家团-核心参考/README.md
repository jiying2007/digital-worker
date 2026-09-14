# 嵌入式系统专家核心参考

> 文档状态：**运行参考（Operational Reference）** / `operational reference`  
> 目标责任架构：`domains/edge-foundation/` + `ADR-004`  
> 当前兼容执行面：`expert-groups/embedded-system/` v0.7.0  
> 当前阶段：`iterative-development`

本 README 是本目录的**唯一第一入口**。本目录沉淀 Embedded System Expert（嵌入式系统专家）的专业方法、迁移期职责、流程、工程交付、治理和案例。**它不是第二套组织 SSOT**：端侧目标组织层级由 `ADR-004` 与 `domains/edge-foundation/domain.yaml` 定义；当前旧 `1+7` 的具体执行 Contract 仍由 `expert-groups/embedded-system/` 承担，直到真实 Pilot + 独立评审完成 canonical routing 切换。

## 0. 当前责任语义

目标模型：

```text
端侧底座领域（Edge Foundation Domain）
│
├─ 端侧协调角色（Edge Coordination Role，不是第四个技术专家）
├─ 结构专家（Structure Expert）
├─ 硬件专家（Hardware Expert）
└─ 嵌入式系统专家（Embedded System Expert）
     └─ 能力域（Capability）→ 技能（Skill）
```

现有 `1+7 / 8 个数字身份 / 23 P0 Skill / 14 Task / Gate / A0-A7 / Verification` 是**兼容执行资产**，不是端侧最终组织结构。8/8 身份桥接只在 `domains/edge-foundation/compatibility/embedded-1plus7-mapping.yaml` 维护；mapping 不保存 mutable phase/readiness 状态。

三条硬边界：

1. 组织语义迁移不得破坏 Gate / Evidence / Verification / Independent Review / Action Policy；
2. Capability（能力域）默认不是 Agent，也不因 Skill 变多自动晋升 Expert；
3. `canonical_routing_switched=false` 期间旧 `1+7` 继续承担执行/rollback，不能直接删除。

Phase-3 只允许切 canonical routing authority 并引入 selector entrypoint；compatibility mapping rewrite、legacy deprecation/removal、Skill owner rewrite、A0-A7 扩权、Verification/Review 独立性变化和 Provider binding 都不属于同一动作。

## 1. 第一次阅读

推荐顺序：

1. [ADR-004：端侧底座数字责任架构](../docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md)：目标责任层级与中英术语；
2. [数字员工组织与运行总览](01-数字组织与岗位/01%20数字员工组织与运行总览.md)：理解当前兼容执行模型；
3. [数字岗位与能力模型](01-数字组织与岗位/03%20数字岗位与能力模型.md)：理解旧职责如何作为迁移资产继续使用；
4. [总体架构设计](02-架构设计/01%20总体架构设计.md)：理解控制面、Provider-neutral、Runtime 与系统边界；
5. [任务类型运行矩阵](03-流程与运行/05%20任务类型运行矩阵.md)：当前 Task/Mode 执行入口；
6. [真实 Pilot Runbook](../docs/runbooks/embedded-pilot.md)：真实任务的唯一详细操作说明。

真实 Pilot 和独立 productionization review 达标前，不声明 Production Ready，也不声明旧身份已经完成退役。

## 2. 信息架构

|目录|主要回答什么问题|
|---|---|
|`01-数字组织与岗位`|旧职责如何在迁移期协作、如何映射到新责任模型？|
|`02-架构设计`|系统边界、身份、证据、Provider/Runtime 和 NFR 是什么？|
|`03-流程与运行`|任务如何分类、经过 Gate、验证、审查和收口？|
|`04-专业能力`|Architecture / BSP / MCU / Driver / Debug / Verification / Review 怎么做？|
|`05-工程交付`|Skill、Runtime、Artifact、Receipt 和工程交付长什么样？|
|`06-治理与评审`|权限、安全、风险、评审、Pilot 和成熟度怎么管？|
|`07-案例`|具体问题如何串起 Context、Evidence、Decision 和验证？|
|`附录`|术语和缩写是什么意思？|

## 3. 内容归属

一个规则只详细解释一次：

|主题|唯一详细人类来源|
|---|---|
|目标 Domain / Expert / Capability / Skill 层级|[ADR-004](../docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md)|
|迁移期旧职责 / 输入输出 / 胜任证据|[数字岗位与能力模型](01-数字组织与岗位/03%20数字岗位与能力模型.md)|
|岗位内部协作|[组织职责与 RACI](01-数字组织与岗位/02%20组织职责与RACI.md)|
|跨团队协作|[跨团队 RACI](01-数字组织与岗位/04%20跨团队RACI.md)|
|Task Type / Workflow Mode|[任务类型运行矩阵](03-流程与运行/05%20任务类型运行矩阵.md)|
|Gate / 状态 / 失败回流|[任务生命周期与 Gate](03-流程与运行/01%20任务生命周期与Gate.md)|
|P0 Skill|[Skill 能力地图](05-工程交付/01%20Skill能力地图.md)|
|A0-A7 / 人工高风险边界|[权限、安全、风险与例外](06-治理与评审/02%20权限安全风险与例外.md)|
|Verification / Review / Release Readiness|[验证、评审、发布与异常恢复](03-流程与运行/04%20验证评审发布与异常恢复.md)|
|真实 Pilot 操作|[Embedded Pilot Runbook](../docs/runbooks/embedded-pilot.md)|
|专业分析方法|`04-专业能力/*`|
|术语|[术语与缩写](附录/术语与缩写.md) + ADR-004|

其他文档只保留必要摘要和链接，禁止维护平行 SSOT。

## 4. 按工作场景查

|场景|优先入口|
|---|---|
|理解最终责任架构|[ADR-004](../docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md)|
|理解旧职责/迁移映射|[数字岗位与能力模型](01-数字组织与岗位/03%20数字岗位与能力模型.md)|
|不知道任务走哪条链|[任务类型运行矩阵](03-流程与运行/05%20任务类型运行矩阵.md)|
|缺陷、长稳、现场问题|[Debug 问题闭环](03-流程与运行/02%20Debug问题闭环流程.md)|
|功能、驱动、Bring-up、多仓|[功能开发与多仓协同](03-流程与运行/03%20功能开发Bring-up与多仓协同.md)|
|验证、Review、OTA/Release|[验证评审发布与异常恢复](03-流程与运行/04%20验证评审发布与异常恢复.md)|
|查专业 SOP|[专业能力](04-专业能力/01%20嵌入式架构领域指南.md)|
|看 Skill / 工程交付物|[Skill 能力地图](05-工程交付/01%20Skill能力地图.md) / [工程交接与关键产物](05-工程交付/02%20工程交接Runtime与关键产物.md)|
|执行真实 Pilot|[Embedded Pilot Runbook](../docs/runbooks/embedded-pilot.md)|
|正式治理/评审|[评审说明与决策清单](06-治理与评审/01%20评审说明与决策清单.md)|
|看完整案例|[UBIFS 只读问题走查](07-案例/01%20UBIFS只读问题走查.md)|

## 5. 人类视图与机器 Contract

```text
ADR-004 + domains/edge-foundation/     目标责任模型
        ↓
routing-shadow + evaluators            非 canonical 对照 / readiness
        ↓
真实 Pilot receipts                     晋级证据
        ↓
本 README + 01~07 + 附录                专业参考与迁移期人类视图
        ↓
expert-groups/embedded-system/          当前 legacy execution / rollback surface
```

目标责任语义冲突时回 `ADR-004` / `domains/edge-foundation/domain.yaml`；旧 Task / Skill / Gate / Action / Verification 的当前执行细节回 `expert-groups/embedded-system/`。

## 6. 当前真实推进

当前不是“等待所有真实任务开始”：

- **Debug**：已选 SSC305 / SPI-NAND / UBI-UBIFS 并发写后只读问题；等待产品 repo exact SHA、原始日志和设备/Flash/Kernel/Test identity；
- **Feature**：PCR02 OTA artifact identity 已完成真实 Engineering、PR/fresh-main Verification 和 retained machine receipt；等待 Independent Review 与 Pilot terminal bundle；
- **Review / Release**：PCR02 v1.1.21 artifact identity 与真实 HTTP/HTTPS distribution evidence 已完成；等待设备下载/安装/启动/回滚、Independent Review 与 human release gate。

三轨只有形成 eligible real receipt 后才能进入 `phase3-readiness = ELIGIBLE_FOR_REVIEW`。这仍只允许发起独立 canonical-switch review，不自动切路由。

当前原则：**优先完成真实 evidence，只有真实任务反复暴露稳定缺口时才新增 Schema / Skill / Platform；不再通过增加 Expert、Agent 或重复状态字段制造“进展”。**
