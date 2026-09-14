# 嵌入式系统专家团核心参考

> 文档状态：**运行参考（operational reference）**  
> 对应实现：`expert-groups/embedded-system/` v0.7.0  
> 当前阶段：`iterative-development`  
> 当前目标：真实 Debug / Feature / Review-Release 闭环，推进 E2 Engineering Closed Loop

本文件是**唯一第一入口**。核心参考按“数字组织 → 架构 → 流程 → 专业能力 → 工程交付 → 治理评审 → 案例 → 附录”组织；详细机器规则仍以 `expert-groups/embedded-system/` 为执行权威。

## 1. 第一次阅读

按以下顺序即可建立全局认知：

1. [数字员工组织与运行总览](01-数字组织与岗位/01%20数字员工组织与运行总览.md)：10 分钟理解整体模型和主链；
2. [数字岗位与能力模型](01-数字组织与岗位/03%20数字岗位与能力模型.md)：理解 6 Module / 8 Position / Agent / Qualification；
3. [总体架构设计](02-架构设计/01%20总体架构设计.md)：理解控制面、Provider-neutral、Runtime 和系统边界；
4. [任务类型运行矩阵](03-流程与运行/05%20任务类型运行矩阵.md)：日常接单判断 Task/Mode。

稳定基线：**1+7 / 8 个数字岗位 / 23 P0 Skill / 14 Task / 7 Mode / 8 Gate / A0-A7 / 7 层 Verification**。真实 Pilot 和人工 Productionization Review 达标前，不声明 Production Ready，也不声明岗位已完全替代人工。

## 2. 信息架构

|目录|只回答什么问题|
|---|---|
|`01-数字组织与岗位`|有哪些数字岗位、职责是什么、岗位之间怎么协作、怎样证明胜任？|
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
|数字岗位职责 / 输入输出 / 任职资格|[数字岗位与能力模型](01-数字组织与岗位/03%20数字岗位与能力模型.md)|总览和 RACI 只摘要/引用|
|岗位内部协作|[数字岗位协作与 RACI](01-数字组织与岗位/02%20组织职责与RACI.md)|岗位说明不重复 RACI 表|
|跨团队协作|[跨团队 RACI](01-数字组织与岗位/04%20跨团队RACI.md)|案例只引用相关责任|
|Task Type / Workflow Mode 路由|[任务类型运行矩阵](03-流程与运行/05%20任务类型运行矩阵.md)|总览、岗位、案例不复制 14 行矩阵|
|Gate / 状态 / 失败回流|[任务生命周期与 Gate](03-流程与运行/01%20任务生命周期与Gate.md)|专业 SOP 不重定义 Gate|
|P0 Skill ID / Owner / 用途|[Skill 能力地图](05-工程交付/01%20Skill能力地图.md)|岗位只显示 Skill 数和 Profile 链接|
|A0-A7 / 人工高风险边界|[权限、安全、风险与例外](06-治理与评审/02%20权限安全风险与例外.md)|总览只说明能力≠权限|
|Verification Layer / Review Decision / Release Readiness|[验证、评审、发布与异常恢复](03-流程与运行/04%20验证评审发布与异常恢复.md)|Verification/Review SOP 只写“怎么做”|
|专业分析方法|`04-专业能力/*`|岗位文档只说明“负责什么”|
|术语|[术语与缩写](附录/术语与缩写.md)|其他文档不维护第二套词典|

维护原则：**详细定义只在唯一来源修改；其他位置只保留必要摘要和链接。** 这避免人类文档之间形成第二套 SSOT。

## 4. 按工作场景查

|现在要做什么|优先入口|
|---|---|
|理解数字员工岗位|[数字岗位与能力模型](01-数字组织与岗位/03%20数字岗位与能力模型.md)|
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
README（唯一入口）
   ↓
01~07 + 附录（职责、方法、流程、治理和案例）
   ↓
expert-groups/embedded-system/（机器执行权威）
```

执行冲突时依次回机器资产：`expert-group.yaml` → `config/*` → `contracts/* / schemas/*` → Agent Definition / Skill / Runtime scripts。

`01-数字组织与岗位/human-view.yaml` 只保存模块和岗位的人类注解，不复制 Task、Skill、Gate、Action、Verification、Artifact、RACI、术语或案例。禁止建立 `positions.yaml` / `positions/` / `position-model.yaml` 平行机器规则源。

## 6. 当前推进重点

当前缺口是**真实工程证据**，不是继续扩写文档：

`#6 Debug → #7 Feature → #8 Review/Release → #16 Knowledge reuse / 外部 Source → #18 Multi-runtime → Productionization Review → #12 strict server governance`

后续只有真实任务暴露稳定、重复的职责/Skill/流程/Evidence 缺口时，才调整核心参考或机器 Contract。
