# 架构、运行与数字岗位总览

这里是《嵌入式系统专家团-核心参考》的**第一阅读入口**。

目标有三个：

- 第一次接触的人在 **10 分钟**内理解整套体系；
- 日常工程人员在 **30 秒**内判断“这项任务该怎么走、谁主责、在哪个 Gate、需要什么证据”；
- 管理者和研发人员能直接理解“有哪些数字岗位、每个数字员工负责什么、要具备什么能力、如何证明胜任”。

## 先看这两页

1. **[`00 架构与运行总览.md`](00%20架构与运行总览.md)**  
   回答：体系怎么运转、任务怎么路由、Gate/Evidence/Verification 怎么闭环。
2. **[`01 数字岗位与能力模型.md`](01%20数字岗位与能力模型.md)**  
   回答：6 个职能模块、8 个数字岗位、Agent↔Skill、岗位职责、工作内容、工作要求、数字任职资格和岗位替代判定。

两页共同构成第一阅读层，但侧重点不同：

```text
架构与运行总览
  → 怎么工作

数字岗位与能力模型
  → 谁负责、会什么、凭什么胜任
```

## 架构与运行总览的 8 个视图

`00 架构与运行总览.md` 把原本分散在组织、流程、Skill、权限、Verification、RACI 和术语文档中的信息组合成 8 个连续视图：

1. 一页总览：当前基线、成熟度、主流程；
2. 专家与职责：1+7 的定位、职责、Skill、输入、输出和边界；
3. 任务路由矩阵：14 类 task type 的默认/允许 mode、主责、关键产物和验证起点；
4. 串并行与 Gate：稳定阶段骨架、Analysis 并行点、各 mode 路径和失败回流；
5. Artifact 与 Evidence：每种产物解决什么问题，以及 Work Item→Evidence→Review 身份链；
6. 权限 × Verification：A0-A7 与 7 层 Verification 的关系；
7. 跨团队 RACI：产品、项目、开发、硬件、测试/HIL、Verification、Review、Release、Knowledge、安全如何协作；
8. 术语与任务走查：通俗类比 + UBIFS 示例的完整任务路径。

## 数字岗位视图怎么理解

`01 数字岗位与能力模型.md` 使用现实研发组织语言解释现有机器架构：

- **Module**：职能模块，只用于组织理解和能力规划；
- **Position**：数字岗位的人类职责视图；
- **Agent**：承担岗位的数字员工；
- **Skill**：数字员工掌握的岗位技能；
- **Qualification**：用 Knowledge / Skill / Context / Action / Evidence / Gate / Case 证明是否真正胜任。

当前岗位模型为 **6 个职能模块 + 8 个数字岗位**，与现有 `1+7 Agent` 一一对应。Module 不参与机器路由，Position 也不是新的运行实体。

## 三层信息体系

|层级|用途|权威性|
|---|---|---|
|本目录总览|快速理解、数字岗位、评审、培训、导航|人类视图，不是 SSOT|
|Markdown 工程手册|专业方法、流程解释、案例、异常恢复|解释层|
|YAML / JSON / Schema / Contract|任务路由、Agent、Skill、Gate、权限、验证与执行规则|机器执行权威|

总览中能够由机器规则确定的内容，必须与以下资产同步：

- `expert-groups/embedded-system/expert-group.yaml`；
- `config/task-modes.yaml`；
- `config/workflow.yaml`；
- `config/gate-policy.yaml`；
- `config/action-policy.yaml`；
- `config/p0-skills.yaml`；
- `contracts/experts/*.io.yaml` 及相关 Schema。

只用于提高可读性的中文定位、模块/岗位名称、工作内容、工作要求、输入输出、边界说明、术语类比和示例走查保存在 `overview-human.yaml`。这些文字不能覆盖机器规则。

## 为什么不用独立 Position 配置做第二套 SSOT

现实岗位语言非常适合人理解，但如果再建立一套 `positions.yaml` 或 `positions/` 配置，就会和 Agent、Expert I/O Contract、Skill Registry、Action Policy 形成平行真相源。

因此当前采用：

```text
Machine Contract
      ↓
overview-human.yaml（只存人类岗位/说明注解）
      ↓
00 架构与运行总览.md
01 数字岗位与能力模型.md
      ↓
详细 Markdown 手册
```

岗位 Profile 是 **Agent Definition + I/O Contract + Skill Registry + Policy + Evaluation + Human Annotation 的组合视图**，不是新的执行配置。

## 为什么不用 Excel 做长期规则源

Excel 可以很好地展示横向矩阵，但不适合作为仓库里的长期权威资产：Git diff、Review、merge 和自动同步都弱于文本格式。

如果未来管理层需要 XLSX，可以从同一结构化源导出；**不人工维护第二套 Excel 规则。**

## 更新规则

- 修改机器 Contract 后，如果总览仍保留旧 task / mode / role / position-agent / skill-owner / gate / action / verification，CI 必须失败；
- 修改纯人类说明时，同步更新 `overview-human.yaml` 与对应总览；
- 新增数字岗位不得绕过现有 Agent/Contract 体系；
- 新增 Skill 仍由真实 Pilot 暴露的稳定工作模式驱动；
- 历史版本由 Git 保存，不在活动路径保留旧 workbook、平行 Position SSOT、兼容文档或一次性 materializer。
