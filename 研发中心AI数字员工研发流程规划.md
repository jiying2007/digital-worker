# 研发中心 AI 数字员工研发流程规划 V2

- 文档状态：proposed
- 日期：2026-09-09
- 适用范围：研发中心办公协同与嵌入式软件研发流程
- 版本关系：在 `研发中心AI数字员工研发流程规划_V1.md` 基础上结合已确认系统现状形成；评审时以本文件为当前提案，V1保留作历史草案
- 已确认条件：WorkBuddy 企业版、飞书研发流程、飞书知识库、WeKnora 内网私有部署、Codex CLI 嵌入式研发
- 待确认责任方：研发中心负责人、研发流程负责人、IT、信息安全、知识库负责人、试点产品负责人
- 核心决策：[ADR-001：WorkBuddy 与 Codex CLI 的集成边界](docs/adr/ADR-001-workbuddy-codex-integration-boundary.md)

## 1. 决策摘要

推荐采用：

> **飞书承载协作流程与人工知识主库，WeKnora作为内网AI检索层，WorkBuddy作为PC端数字员工入口，Codex CLI作为工程师控制的仓库执行端。**

一期不要求 WorkBuddy 直接启动或遥控 Codex CLI。WorkBuddy 重点管控：

- 输入侧：需求完整性、目标、非目标、平台/板卡、代码仓、验收标准、权限和知识引用；
- 输出侧：变更范围、代码/patch、验证结果、制品身份、未验证项、阻塞、风险和下一步；
- 流程侧：将输入和输出关联回同一个飞书工作项，推动人工确认和状态转换。

Codex CLI 仍由研发人员从真实仓库启动，按项目规则完成分析、修改和验证。二期才评估隔离 Runner 上的受控自动执行。

## 2. 为什么不建议 WorkBuddy 一期直接串联 CLI

“能够启动 CLI”不等于“能够可靠管控嵌入式研发”。直接串联还需要解决：

- 当前目录是否是真实目标 repo root；
- 当前分支、base commit 和 dirty worktree 是否正确；
- WorkBuddy 与 Codex 是否使用同一员工身份和权限；
- 任务中断、超时、重复启动和恢复如何处理；
- Codex能否访问正确工具链、SDK、构建容器和设备；
- SSH、ADB、串口、烧录器、OTA和板卡动作由谁批准；
- Host、交叉构建、部署、HIL和发布状态如何避免混淆；
- 源码、密钥、客户材料和日志是否越过数据边界。

一期采用“需求包 + 交付回执”可以先解决流程质量和可追溯性，同时保留工程师对真实环境的控制。它也为以后建设执行网关提供稳定接口。

## 3. 目标架构

```text
员工/主管
   │
   ├────────────── 飞书 ──────────────────────────┐
   │     工作项、负责人、状态、审批、会议、通知     │
   │                     │                         │
   │                     ▼                         │
   │                WorkBuddy企业版                │
   │       需求受理、知识查询、任务包、结果展示      │
   │             │                    │             │
   │             │检索                │输入/输出契约 │
   │             ▼                    ▼             │
   │   WeKnora内网私有部署       工程师 + Codex CLI │
   │   AI检索、引用、评测         真实代码仓中执行   │
   │             ▲                    │             │
   │             │知识候选            │交付回执      │
   │             └───────── 人工审核 ──┘             │
   │                                                │
   └─ 飞书知识库：面向人的内容主库 ◄── 受控同步 ─────┘

Git / CI / 制品库 / HIL证据：分别保存工程与产品权威事实
```

## 4. 系统职责与事实源

| 对象 | 权威事实源 | WorkBuddy职责 | WeKnora职责 | Codex职责 |
|---|---|---|---|---|
| 研发工作项 | 飞书 | 创建草稿、补齐、展示、推动审批 | 提供规范和案例 | 消费已确认任务 |
| 人工协作文档 | 飞书知识库 | 搜索、总结、生成候选 | 同步索引和检索 | 读取受权引用 |
| 当前源码 | Git | 展示链接 | 不复制为源码主库 | 读取、分析和修改 |
| 构建/测试 | CI或本地受控入口 | 汇总状态 | 沉淀审核后的Runbook | 执行并生成证据 |
| 发布制品 | 制品库 | 展示版本与状态 | 只存说明和引用 | 生成或核验身份信息 |
| 板级验证 | 测试/HIL证据库 | 展示和推动人工确认 | 沉淀验证方法和案例 | 辅助执行，不自动放行 |
| 正式研发知识 | 飞书原文 + WeKnora受控索引 | 使用和提交候选 | 检索、引用、评测 | 使用和提交候选 |

## 5. 飞书知识库与 WeKnora 的关系

### 5.1 推荐方案：飞书主库，WeKnora检索层

飞书知识库继续用于：

- 人工编写和协作；
- 评论、通知和审批；
- 组织成员日常浏览；
- 文档原文、owner和人工变更。

WeKnora用于：

- 内网文档解析和分块；
- 混合检索、RAG问答和来源引用；
- 为WorkBuddy和Codex提供统一机器接口；
- 检索质量评测、失败样本和查询审计；
- 按知识域隔离不同产品、平台和团队。

不得让团队在飞书和WeKnora中各自编辑一套正式正文。WeKnora内的同步副本应标记来源、外部文档ID、更新时间和同步状态。

### 5.2 是否存在更好的方案

候选方案对比如下：

| 方案 | 优点 | 风险 | 建议 |
|---|---|---|---|
| 仅用飞书知识库 | 体系最简单、权限和协作集中 | Codex接入、复杂检索、评测和内网模型适配能力可能不足 | 可作最小基线 |
| 飞书主库 + WeKnora检索层 | 保留协作习惯，同时为AI提供统一RAG/MCP | 需要同步、ACL映射和运维 | **推荐** |
| WeKnora替代飞书知识库 | AI能力集中、内网可控 | 改变全员习惯，协作与流程迁移成本高 | 暂不推荐 |
| 飞书和WeKnora双写 | 表面灵活 | 版本、权限、删除和owner漂移 | 拒绝 |

WeKnora官方实现支持飞书数据源、增量/全量同步和删除同步，因此可用于“飞书主库 + WeKnora检索层”。但不能只根据“同步成功”推断源文档权限已经逐文档继承；必须对实际部署版本进行权限负向测试。

### 5.3 权限安全门禁

一期建议：

- 只同步权限相对同质的飞书知识空间；
- 按部门、产品线或密级拆分WeKnora知识库；
- 不把包含混合文档权限的飞书空间整体同步给广泛可见的WeKnora知识库；
- 删除、撤权和人员离职必须触发同步/缓存失效验证；
- WorkBuddy和Codex使用员工个人身份或短期令牌，不共用管理员API Key；
- 检索回执记录用户、知识库、文档、来源、时间和权限决策；
- 高敏源码、密钥、证书、客户数据和原始现场日志默认不进入知识库。

如果无法验证权限继承，应回退为：

1. WorkBuddy按飞书原生权限直接访问飞书内容；
2. WeKnora只同步全员可见或明确同权限的技术资料；
3. Codex按具体工作项获得经人工选择的知识引用或脱敏附件。

## 6. WorkBuddy 的数字员工角色

一期建议配置四个角色，不建立一个无边界的“万能研发Agent”。

### 6.1 研发需求助理

- 从飞书消息、会议和工作项中提取需求；
- 补齐产品、平台、板卡、版本、接口和验收标准；
- 从WeKnora查找现行规范和历史案例；
- 输出 `task-brief` 草稿；
- 信息不足时停在 `needs-information`。

### 6.2 研发交付助理

- 接收或读取Codex的 `delivery-receipt`；
- 校验必填字段和证据链接；
- 区分已实现、已验证、未验证和阻塞；
- 生成面向项目经理、测试和评审人的摘要；
- 不擅自把状态升级为“完成”或“可发布”。

### 6.3 知识治理助理

- 将需求决策、排障结论和Runbook整理为知识候选；
- 检查owner、适用产品、版本、来源和证据；
- 提交人工审核；
- 审核通过后进入飞书主库，再由WeKnora同步。

### 6.4 项目汇总助理

- 从飞书工作项和交付回执生成周报、风险和阻塞；
- 只按明确字段汇总，不从Git提交量推断个人绩效；
- 明确外部owner、未验证项和等待中的HIL事项。

## 7. 输入契约：task-brief v1

建议采用Markdown供人阅读、JSON供系统校验，两者使用同一字段模型。

```yaml
schema_version: 1
work_item_id:
title:
type: requirement | defect | investigation | refactor
priority:
requester:
owner:
project_id:
product_id:
target_platform:
target_board:
target_os:
repo_roots: []
base_branch_or_commit:
goal:
non_goals: []
current_behavior:
expected_behavior:
acceptance_criteria: []
constraints: []
interfaces: []
knowledge_refs: []
required_verification:
  host: required | optional | not_applicable
  cross_build: required | optional | not_applicable
  sil: required | optional | not_applicable
  hil: required | optional | not_applicable
  release: required | optional | not_applicable
allowed_actions: []
forbidden_actions: []
approval_policy:
blocker_policy:
```

进入Codex前的强制字段：

- `work_item_id`；
- `owner`；
- `repo_roots`；
- `goal`和`non_goals`；
- `acceptance_criteria`；
- `required_verification`；
- `allowed_actions`和`forbidden_actions`；
- `blocker_policy`。

缺少目标仓、owner或验收标准时，WorkBuddy只能生成草稿，不能标记为 `ready-for-development`。

## 8. 输出契约：delivery-receipt v1

```yaml
schema_version: 1
work_item_id:
execution_id:
executor_identity:
started_at:
finished_at:
repo_root:
base_commit:
result_commit_or_patch:
dirty_baseline:
changed_files: []
outcomes: []
decisions: []
validation:
  host: not_run | pass | fail | blocked
  cross_build: not_run | pass | fail | blocked
  sil: not_run | pass | fail | blocked
  hil: not_run | pass | fail | blocked
  release: not_run | pass | fail | blocked
commands: []
artifact_refs: []
artifact_hashes: []
knowledge_refs: []
evidence_refs: []
unverified_items: []
blockers: []
risks: []
next_actions: []
approval_required: []
```

WorkBuddy只能根据结构化字段更新飞书：

- `pass`只代表对应验证层通过；
- `host=pass`不能推导出`hil=pass`；
- `cross_build=pass`不能推导出设备已部署；
- 没有制品hash和设备身份，不能声称板端运行的是本次构建；
- `blocked`和`unverified_items`必须原样展示，不能在周报中省略。

## 9. 端到端流程

```text
1. 飞书产生需求/缺陷/会议行动项
2. WorkBuddy创建研发工作项草稿
3. WorkBuddy经WeKnora检索规范与历史案例
4. WorkBuddy生成task-brief，人确认目标和验收
5. 飞书状态进入ready-for-development
6. 工程师在目标仓启动Codex CLI
7. Codex读取AGENTS.md、task-brief和受权知识
8. Codex分析/修改/验证，生成delivery-receipt
9. WorkBuddy校验回执并关联回飞书工作项
10. 代码评审、交叉构建、制品身份核验
11. 经授权部署，执行Board/HIL
12. 发布负责人审批，飞书工作项关闭
13. WorkBuddy生成知识候选
14. 人工审核后写入飞书知识库
15. WeKnora同步并完成检索回归
```

## 10. 飞书状态建议

```text
draft
  → needs-information
  → ready-for-analysis
  → ready-for-development
  → in-development
  → ready-for-review
  → ready-for-build
  → ready-for-hil
  → ready-for-release
  → closed
```

异常状态：

- `blocked`；
- `needs-rework`；
- `rejected`；
- `cancelled`。

飞书是状态SSOT。WorkBuddy会话、Codex会话、WeKnora会话都不得单独改变最终状态。

## 11. Codex CLI 项目治理

每个试点代码仓至少具备：

- 根目录和必要子目录的 `AGENTS.md`；
- 明确的repo root和独立子仓边界；
- 可复跑的Host/单元测试入口；
- 交叉构建入口和工具链说明；
- 格式、静态检查和代码评审规则；
- 设备连接、部署和HIL Runbook；
- 禁止自动执行的命令和目录；
- 交付回执生成方式。

Codex可直接通过只读MCP访问WeKnora。首期工具白名单建议限定为：

- 列出授权知识库；
- 混合检索；
- 读取指定文档；
- 返回带引用的问答。

知识创建、修改和删除工具不进入Codex默认工具集。

## 12. 分阶段计划

### 阶段0：边界与基线，2周

- 确认飞书工作项形态和API能力；
- 确认WorkBuddy企业版连接器、Skill和管理员策略；
- 确认WeKnora实际版本、部署拓扑、备份和监控；
- 选定一个产品线、2–3个代码仓和10–20名试点用户；
- 冻结 `task-brief v1`、`delivery-receipt v1`和飞书状态映射；
- 建立试点前耗时和质量基线。

### 阶段1：知识接入，3–4周

- 飞书指定空间单向同步到WeKnora；
- 验证增量、删除、撤权和失败重试；
- WorkBuddy只读接入WeKnora；
- Codex CLI只读接入WeKnora；
- 建立20–50条检索评测题和越权测试。

门禁：权限、版本和删除同步未通过，不扩展到敏感知识空间。

### 阶段2：人工闭环，4–6周

- WorkBuddy生成任务包；
- 工程师人工启动Codex；
- Codex生成交付回执；
- WorkBuddy回填飞书；
- 完成至少3个真实嵌入式工作项；
- 至少一个工作项覆盖真实Board/HIL。

门禁：输入完整率、回执合格率或安全指标未达标，不建设自动执行网关。

### 阶段3：受控自动化评估，2周

- 统计人工启动耗时和任务重复度；
- 识别可自动化的只读分析、批量审查和Host测试；
- 评估隔离Runner、worktree、服务身份、任务取消和成本；
- 形成是否建设执行网关的二次ADR。

## 13. 一期验收标准

| ID | 验收标准 | Required Evidence |
|---|---|---|
| AC1 | 飞书工作项能生成完整task-brief | Schema校验和真实样例 |
| AC2 | WorkBuddy和Codex均能检索WeKnora并返回来源 | 检索回执、文档ID和版本 |
| AC3 | 未授权用户无法检索受限知识 | 负向权限测试和审计日志 |
| AC4 | 飞书更新和删除能反映到WeKnora | 增量、删除同步测试 |
| AC5 | Codex执行绑定真实repo root和base commit | delivery-receipt |
| AC6 | dirty基线和用户既有改动不被覆盖 | 执行前后Git状态证据 |
| AC7 | Host、交叉构建、HIL和发布状态分开记录 | 分层验证回执 |
| AC8 | 一个工作项能关联需求、变更、构建和HIL | 端到端追溯演示 |
| AC9 | AI知识候选未经审核不能进入正式飞书知识库 | 审核流测试 |
| AC10 | 未发生自动提交、推送、烧录、部署或发布 | 权限与操作审计 |
| AC11 | task-brief和delivery-receipt合格率≥90% | 试点统计 |
| AC12 | 需求澄清和交付汇总耗时下降≥30% | 试点前后基线对比 |

## 14. Blocker Policy

出现以下情况时停止推进对应环节：

- 飞书工作项缺少owner、目标、验收或目标仓：不得进入开发；
- WeKnora无法证明用户或知识库隔离：不得接入受限知识；
- 飞书撤权/删除不能可靠同步：不得把WeKnora结果当现行权威；
- Codex无法确认repo root、base commit或dirty基线：不得修改；
- 构建结果未绑定源码版本和配置：不得进入部署；
- 制品未绑定hash和设备运行身份：不得声明Board/HIL有效；
- 设备操作缺少人工批准、安全条件或回退：不得执行；
- 缺少发布责任人或外部依赖证据：不得宣称可发布。

## 15. Artifact Paths

建议后续在数字员工方案仓中形成：

```text
数字员工/
├── 研发中心AI数字员工研发流程规划_V2.md
├── docs/
│   ├── adr/
│   │   └── ADR-001-workbuddy-codex-integration-boundary.md
│   ├── architecture/
│   │   └── system-context.md
│   ├── governance/
│   │   ├── knowledge-governance.md
│   │   └── permission-model.md
│   └── runbooks/
│       ├── workbuddy-user-guide.md
│       ├── codex-handoff.md
│       └── weknora-feishu-sync.md
├── schemas/
│   ├── task-brief.v1.schema.json
│   ├── delivery-receipt.v1.schema.json
│   └── hil-evidence.v1.schema.json
├── connectors/
│   └── weknora/
└── tests/
    ├── retrieval-eval/
    ├── permission-negative/
    └── end-to-end/
```

本文件和ADR是本次已归档产物；其余路径为后续实施建议，当前尚未创建。

## 16. 非目标

- 一期不建设无人值守的自动编码平台；
- 不让WorkBuddy拥有开发机全局Shell权限；
- 不用WeKnora替代飞书工作项或Git；
- 不人工双写飞书知识库和WeKnora；
- 不根据Git提交量、WorkBuddy使用量或Codex会话量直接评价个人绩效；
- 不用Host或交叉构建结果替代部署和HIL证据；
- 不自动提交、推送、合并、烧录、OTA或发布；
- 不将聊天全文、原始日志、core、binary、密钥和客户敏感数据直接归档为知识。

## 17. 待确认事项

| 问题 | 建议Owner | 是否阻塞一期 |
|---|---|---|
| 飞书研发流程使用多维表格、项目还是审批 | 研发流程负责人 | 是 |
| 飞书工作项是否有稳定API和唯一ID | IT/飞书管理员 | 是 |
| WorkBuddy企业版连接器是否支持内网MCP访问 | WorkBuddy管理员/IT | 是 |
| WorkBuddy、飞书、WeKnora如何映射同一员工身份 | IT/信息安全 | 是 |
| WeKnora实际版本是否支持飞书增量与删除同步 | WeKnora平台Owner | 是 |
| 源文档权限是否可安全映射到WeKnora检索 | 信息安全/平台Owner | 是 |
| 首个试点产品、板卡和代码仓 | 研发负责人 | 是 |
| HIL证据保存在哪个系统 | 测试负责人 | 是 |
| 是否允许WorkBuddy移动端远程触发PC任务 | 信息安全 | 否，一期建议关闭 |
| 何时评估执行网关 | 研发中心负责人 | 否，阶段2后评估 |

## 18. 当前状态

- 需求分类：跨系统新能力建设。
- 优先级：P1。
- 方案状态：proposed。
- 架构充分性：可进入PoC设计，不可直接宣布集成完成。
- Done-when：完成阶段0决策、3个真实工作项闭环和12项一期验收。
- Required Evidence：身份映射、权限负向测试、同步测试、结构化任务包、交付回执、Git/构建/HIL关联证据和试点指标。
- 核心阻塞：身份映射、飞书工作项API、WeKnora文档权限继承、首个试点范围尚未确认。
