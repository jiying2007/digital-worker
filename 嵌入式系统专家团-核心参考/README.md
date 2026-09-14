# 嵌入式系统专家团核心参考

> 文档状态：**运行参考（operational reference）**  
> 对应实现：`expert-groups/embedded-system/` v0.7.0  
> 当前阶段：`iterative-development`  
> 当前目标：真实 Debug / Feature / Review-Release 闭环，推进 E2 Engineering Closed Loop

本目录采用三层信息体系：**总览负责快速理解，Markdown 手册负责工程方法，机器 Contract 负责精确执行**。三层不能互相替代。

## 1. 第一次看：先打开总览

优先阅读 [`00-总览/README.md`](00-总览/README.md)，并打开：

**[`嵌入式系统专家团-架构与运行总览.xlsx`](00-总览/嵌入式系统专家团-架构与运行总览.xlsx)**

总览用 8 张表回答最常见的问题：

1. 整套体系是什么、当前成熟度在哪里；
2. 1+7 各角色负责什么、输入输出是什么；
3. 14 类任务分别走什么 mode、谁主责；
4. Gate 如何串并行、失败后回哪里；
5. Artifact / Evidence 为什么存在、如何串成身份链；
6. A0-A7 权限与 7 层 Verification 如何区分；
7. 产品、项目、开发、硬件、测试/HIL、Verification、Review、Release 如何分工；
8. 常用术语以及一次完整任务如何走通。

**Excel 只是视图，不是第二个 SSOT。** 其中机器字段来自或校验于 `expert-group.yaml`、`task-modes.yaml`、`workflow.yaml`、`gate-policy.yaml`、`action-policy.yaml` 和 `p0-skills.yaml`；CI 会检查它们是否漂移。

## 2. 做具体任务：再下钻工程手册

|你现在要做什么|优先入口|
|---|---|
|不知道任务该怎么走|[`任务类型运行矩阵`](02-流程与运行/05%20任务类型运行矩阵.md)|
|缺陷、长稳、现场问题|[`Debug 问题闭环`](02-流程与运行/02%20Debug问题闭环流程.md)|
|功能、驱动、Bring-up、多仓|[`功能开发与多仓协同`](02-流程与运行/03%20功能开发Bring-up与多仓协同.md)|
|验证、评审、OTA/发布|[`验证评审发布与异常恢复`](02-流程与运行/04%20验证评审发布与异常恢复.md)|
|要看专家职责与跨团队分工|[`组织职责`](03-角色与领域/01%20组织模型职责与RACI.md) / [`跨团队 RACI`](03-角色与领域/02%20跨团队RACI.md)|
|要看专业方法|[`嵌入式架构`](03-角色与领域/03%20嵌入式架构领域指南.md) / [`Linux BSP`](03-角色与领域/04%20Linux%20BSP领域指南.md) / [`MCU RTOS`](03-角色与领域/05%20MCU%20RTOS领域指南.md) / [`驱动组件`](03-角色与领域/06%20驱动与组件领域指南.md) / [`调试可靠性`](03-角色与领域/07%20调试与可靠性领域指南.md) / [`验证`](03-角色与领域/08%20验证领域指南.md) / [`独立审查`](03-角色与领域/09%20独立审查领域指南.md)|
|要看工程交付物|[`工程交接与关键产物`](04-工程交付/02%20工程交接Runtime与关键产物.md) / [`完整产物样例`](04-工程交付/03%20完整任务产物样例.md)|
|不熟悉术语|[`术语与缩写`](00-评审入口/02%20术语与缩写.md)|

案例目录覆盖 UBIFS、Linux+MCU 多仓 OTA、MCU HardFault/RTOS 并发、新板 Bring-up、器件替代。案例用于解释工作方法，不计入 real Pilot evidence。

## 3. 需要精确规则：回机器 Contract

发生冲突时，执行侧以机器资产为准：

1. `expert-groups/embedded-system/expert-group.yaml`；
2. `config/workflow.yaml`、`task-modes.yaml`、`gate-policy.yaml`、`action-policy.yaml`、`material-requirements.yaml`；
3. `contracts/**/*.yaml`、`schemas/*.schema.json`；
4. 专家定义、Skill 与运行脚本；
5. 本目录人类可读说明。

总览和 Markdown 都不能用文字覆盖机器 Contract。

## 4. 当前稳定基线

- **1 名主理人 + 7 个专业角色**；
- **23 个 P0 Skill**；
- **14 类 task type → 7 种 workflow mode**；
- **Gate K/M/0/T/E/V/R/C**；
- **A0-A7**，A6 设备写入、A7 发布保留人工批准；
- **7 层 Verification**，禁止跨层推导；
- 工程实施、Verification、Independent Review 分开；
- Source of Truth stays at source；
- Provider-neutral，Runtime 可替换但工程语义不变；
- 真实 Pilot 达到门槛并通过人工 Productionization Review 前，**不声明 Production Ready**。

## 5. 当前真正需要推进的事项

当前缺口不是继续扩写架构，而是取得真实工程证据。统一由 [#26 Embedded Domain Closed Loop V1 rollout tracker](https://github.com/jiying2007/digital-worker/issues/26) 跟踪：

`#6 Debug → #7 Feature → #8 Review/Release → #16 Knowledge reuse / 外部 Source → #18 Multi-runtime → Productionization Review → #12 strict server governance`

后续文档调整应由真实任务暴露的缺口驱动，而不是先增加新的概念、角色或模板。
