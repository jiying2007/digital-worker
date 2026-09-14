# 架构与运行总览

这里是《嵌入式系统专家团-核心参考》的**第一阅读入口**，目标是让第一次接触的人在 10 分钟内理解全貌，让日常工程人员在 30 秒内找到任务应该怎么走。

## 三层信息体系

|层级|用途|权威性|
|---|---|---|
|架构与运行总览.xlsx|快速理解、评审、培训、导航|人类视图，不是 SSOT|
|Markdown 工程手册|专业方法、流程解释、案例、异常恢复|解释层|
|YAML / JSON / Schema / Contract|任务路由、Gate、权限、验证与执行规则|机器执行权威|

因此不要手工把 Excel 当成独立规则源。机器字段发生变化时，必须同步刷新总览，并通过 CI 的 workbook drift check。

## 8 张表怎么读

1. **00 总览**：当前基线、主流程、三层体系和阅读路径；
2. **01 专家与职责**：1+7 的定位、职责、Skill、输入、输出和边界；
3. **02 任务路由矩阵**：14 类任务的默认/允许 mode、主责、关键产物和验证起点；
4. **03 串并行与Gate**：稳定阶段骨架、Analysis 并行点、各 mode 路径和失败回流；
5. **04 Artifact与Evidence**：每种产物解决什么问题，以及 Work Item→Evidence→Review 身份链；
6. **05 权限与Verification**：A0-A7 与 7 层 Verification 的关系；
7. **06 跨团队RACI**：产品、项目、软件、硬件、测试、验证、审查、发布、知识、安全的协作责任；
8. **07 术语与任务走查**：术语类比和 UBIFS 示例的完整任务走查。

## 数据从哪里来

总览中能够由机器规则确定的内容，直接取自或被校验于：

- `expert-groups/embedded-system/expert-group.yaml`；
- `config/task-modes.yaml`；
- `config/workflow.yaml`；
- `config/gate-policy.yaml`；
- `config/action-policy.yaml`；
- `config/p0-skills.yaml`。

只用于提高可读性的定位、输入输出、通俗说明、术语类比等文字保存在 `overview-human.yaml`。这些文字不能覆盖机器规则。

## 更新规则

修改机器 Contract 后，如果总览仍保持旧内容，CI 必须失败；修改纯人类说明后，需要同步更新 `overview-human.yaml` 与 workbook。历史版本由 Git 保存，不在活动总览中保留兼容副本。
