# 嵌入式系统专家团核心参考

> 文档状态：**运行参考（operational reference）**  
> 对应实现：`expert-groups/embedded-system/` v0.7.0  
> 当前阶段：`iterative-development`  
> 当前目标：真实 Debug / Feature / Review-Release 闭环，推进 E2 Engineering Closed Loop

本文件是**唯一第一入口**。核心参考按“数字组织 → 架构 → 流程 → 专业能力 → 工程交付 → 治理评审 → 案例 → 附录”组织，不再设置第二个“总览入口”或独立“评审入口”。

人类文档负责解释和导航；任务路由、Gate、Action Policy、Verification、Schema 与 Contract 的执行权威仍在 `expert-groups/embedded-system/`。

## 1. 先建立全局认知

建议第一次阅读按以下顺序：

1. [`01-数字组织与岗位/01 数字员工组织与运行总览.md`](01-数字组织与岗位/01%20数字员工组织与运行总览.md)  
   一页理解 1+7、23 P0 Skill、14 类任务、7 种 mode、8 个 Gate、A0-A7、7 层 Verification 和完整运行主链。
2. [`01-数字组织与岗位/03 数字岗位与能力模型.md`](01-数字组织与岗位/03%20数字岗位与能力模型.md)  
   理解 6 个职能模块、8 个数字岗位，以及 Agent、Skill、数字任职资格和岗位替代如何定义。
3. [`02-架构设计/01 总体架构设计.md`](02-架构设计/01%20总体架构设计.md)  
   理解控制面、Provider-neutral、Runtime Binding 和系统级架构边界。
4. [`03-流程与运行/05 任务类型运行矩阵.md`](03-流程与运行/05%20任务类型运行矩阵.md)  
   日常接单时快速判断任务该走哪条链。

## 2. 信息架构

|目录|回答的问题|主要使用者|
|---|---|---|
|`01-数字组织与岗位`|我们有哪些数字员工、模块和岗位，谁负责什么？|管理者、研发人员、数字员工设计者|
|`02-架构设计`|系统为什么这样设计，边界和控制面是什么？|架构师、主理人、评审者|
|`03-流程与运行`|一项任务如何从接单走到验证、审查和收口？|所有工程参与者|
|`04-专业能力`|Linux/BSP、MCU/RTOS、Driver、Debug、Verification 等专业工作怎么做？|各领域工程师 / Agent|
|`05-工程交付`|Skill、Runtime、Artifact、Receipt 和完整交付长什么样？|实施者、Runtime、Verification|
|`06-治理与评审`|权限、安全、评审、Pilot、成熟度和演进规则是什么？|主理人、Review、Release Owner|
|`07-案例`|这些规则在真实类型任务里如何串起来？|培训、走查、方法复用|
|`附录`|术语和缩写是什么意思？|所有读者|

## 3. 按工作场景查

|你现在要做什么|优先入口|
|---|---|
|理解数字员工组织、岗位职责与能力|[`数字员工组织与运行总览`](01-数字组织与岗位/01%20数字员工组织与运行总览.md) / [`数字岗位与能力模型`](01-数字组织与岗位/03%20数字岗位与能力模型.md)|
|看内部职责和跨团队协作|[`组织职责与 RACI`](01-数字组织与岗位/02%20组织职责与RACI.md) / [`跨团队 RACI`](01-数字组织与岗位/04%20跨团队RACI.md)|
|不知道任务该怎么走|[`任务类型运行矩阵`](03-流程与运行/05%20任务类型运行矩阵.md)|
|缺陷、长稳、现场问题|[`Debug 问题闭环`](03-流程与运行/02%20Debug问题闭环流程.md)|
|功能、驱动、Bring-up、多仓|[`功能开发与多仓协同`](03-流程与运行/03%20功能开发Bring-up与多仓协同.md)|
|验证、评审、OTA/发布|[`验证评审发布与异常恢复`](03-流程与运行/04%20验证评审发布与异常恢复.md)|
|查某一专业的工作方法|[`04-专业能力`](04-专业能力/01%20嵌入式架构领域指南.md)|
|看 Skill 和工程交付物|[`Skill 能力地图`](05-工程交付/01%20Skill能力地图.md) / [`工程交接与关键产物`](05-工程交付/02%20工程交接Runtime与关键产物.md)|
|做正式评审或看治理规则|[`评审说明与决策清单`](06-治理与评审/01%20评审说明与决策清单.md) / [`权限安全风险与例外`](06-治理与评审/02%20权限安全风险与例外.md)|
|不熟悉术语|[`术语与缩写`](附录/术语与缩写.md)|

## 4. 人类视图与机器 Contract 的关系

```text
README（唯一入口）
   ↓
01~07 + 附录（人类可读组织、方法、流程与案例）
   ↓
expert-groups/embedded-system/（机器执行权威）
```

发生冲突时，执行侧依次以这些机器资产为准：

1. `expert-groups/embedded-system/expert-group.yaml`；
2. `config/workflow.yaml`、`task-modes.yaml`、`gate-policy.yaml`、`action-policy.yaml`、`material-requirements.yaml`；
3. `contracts/**/*.yaml`、`schemas/*.schema.json`；
4. Agent Definition、Skill 与运行脚本；
5. 本目录人类可读说明。

`01-数字组织与岗位/human-view.yaml` 只保存中文定位、工作内容、岗位说明等人类注解，不是新的 Position SSOT。禁止新增 `positions.yaml` / `positions/` / `position-model.yaml` 平行机器规则源。

## 5. 当前稳定基线

- **1 名主理人 + 7 个专业角色 / 8 个数字岗位**；
- **6 个职能模块**仅作为组织与能力规划视图，不参与机器路由；
- **23 个 P0 Skill**；
- **14 类 task type → 7 种 workflow mode**；
- **Gate K/M/0/T/E/V/R/C**；
- **A0-A7**，A6 设备写入、A7 发布保留人工批准；
- **7 层 Verification**，禁止跨层推导；
- Engineering、Verification、Independent Review 分离；
- Source of Truth stays at source；
- Provider-neutral，Runtime 可替换但岗位职责和工程语义不变；
- 真实 Pilot 达标并完成人工 Productionization Review 前，**不声明 Production Ready，也不声明岗位已完全替代人工**。

## 6. 当前推进重点

当前缺口不是继续扩写目录或增加概念，而是取得真实工程证据。统一由 [#26 Embedded Domain Closed Loop V1 rollout tracker](https://github.com/jiying2007/digital-worker/issues/26) 跟踪：

`#6 Debug → #7 Feature → #8 Review/Release → #16 Knowledge reuse / 外部 Source → #18 Multi-runtime → Productionization Review → #12 strict server governance`

后续文档调整应由真实任务暴露的职责、Skill、流程或证据缺口驱动。
