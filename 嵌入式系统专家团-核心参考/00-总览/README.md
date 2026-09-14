# 架构与运行总览

这里是《嵌入式系统专家团-核心参考》的**第一阅读入口**。

目标只有两个：

- 第一次接触的人在 **10 分钟**内理解整套体系；
- 日常工程人员在 **30 秒**内判断“这项任务该怎么走、谁主责、在哪个 Gate、需要什么证据”。

## 先看这一页

**[`00 架构与运行总览.md`](00%20架构与运行总览.md)**

它把原本分散在组织、流程、Skill、权限、Verification、RACI 和术语文档中的信息组合成 8 个连续视图：

1. 一页总览：当前基线、成熟度、主流程；
2. 专家与职责：1+7 的定位、职责、Skill、输入、输出和边界；
3. 任务路由矩阵：14 类 task type 的默认/允许 mode、主责、关键产物和验证起点；
4. 串并行与 Gate：稳定阶段骨架、Analysis 并行点、各 mode 路径和失败回流；
5. Artifact 与 Evidence：每种产物解决什么问题，以及 Work Item→Evidence→Review 身份链；
6. 权限 × Verification：A0-A7 与 7 层 Verification 的关系；
7. 跨团队 RACI：产品、项目、开发、硬件、测试/HIL、Verification、Review、Release、Knowledge、安全如何协作；
8. 术语与任务走查：通俗类比 + UBIFS 示例的完整任务路径。

## 三层信息体系

|层级|用途|权威性|
|---|---|---|
|本目录总览|快速理解、评审、培训、导航|人类视图，不是 SSOT|
|Markdown 工程手册|专业方法、流程解释、案例、异常恢复|解释层|
|YAML / JSON / Schema / Contract|任务路由、Gate、权限、验证与执行规则|机器执行权威|

总览中能够由机器规则确定的内容，必须与以下资产同步：

- `expert-groups/embedded-system/expert-group.yaml`；
- `config/task-modes.yaml`；
- `config/workflow.yaml`；
- `config/gate-policy.yaml`；
- `config/action-policy.yaml`；
- `config/p0-skills.yaml`。

只用于提高可读性的中文定位、输入输出、边界说明、术语类比和示例走查保存在 `overview-human.yaml`。这些文字不能覆盖机器规则。

## 为什么不用 Excel 做长期规则源

Excel 可以很好地展示横向矩阵，但不适合作为仓库里的长期权威资产：Git diff、Review、merge 和自动同步都弱于文本格式。

因此当前采用：

```text
Machine Contract
      ↓
overview-human.yaml（只存人类说明）
      ↓
00 架构与运行总览.md（可读视图）
      ↓
详细 Markdown 手册
```

如果未来管理层需要 XLSX，可以从同一结构化源导出；**不人工维护第二套 Excel 规则。**

## 更新规则

- 修改机器 Contract 后，如果总览仍保留旧 task / mode / role / gate / action / verification，CI 必须失败；
- 修改纯人类说明时，同步更新 `overview-human.yaml` 与总览；
- 历史版本由 Git 保存，不在活动路径保留旧 workbook、兼容文档或一次性 materializer。
