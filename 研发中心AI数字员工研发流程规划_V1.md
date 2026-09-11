# 总体结论

建议采用：

> **WorkBuddy 统一办公入口 + WeKnora 企业知识服务 + Codex CLI 嵌入式研发执行端 + 研发流程系统作为状态主线。**

三者不能简单串成“WorkBuddy 调用 WeKnora，再调用 Codex”这一条链。更合理的关系是：

```text
                         ┌──────── WeKnora ────────┐
                         │ 规范、设计、案例、Runbook │
                         │ 受控检索、引用、知识治理   │
                         └───────┬─────────┬───────┘
                                 │         │
                                 ▼         ▼
研发人员 ──► WorkBuddy ──► 研发工作项 ──► Codex CLI
             办公入口        流程状态SSOT      仓库执行端
                │                │               │
                │                ▼               ▼
                └──────► TAPD/项目系统     Git/构建/测试/制品
                                 │               │
                                 └──── 证据回执 ──┘
                                         │
                                         ▼
                                  审查、HIL、发布审批
```

核心原则：

- WorkBuddy 负责“人机交互、任务发起、流程协同和结果呈现”；
- WeKnora 负责“受控知识检索和知识生命周期”，不负责项目状态；
- Codex CLI 负责“进入真实代码仓、分析、修改、构建和验证”；
- TAPD或现有项目管理系统负责“工作项状态、责任人和审批”；
- Git、CI、制品库和设备日志分别保存自己的权威事实；
- 三者通过统一的“研发工作项 ID”和“执行证据回执”关联；
- 首期采用人工交接，成熟后再建设自动执行网关。

截至当前，WorkBuddy 官方文档明确支持“连接器 + Skill”，其中已有 API 服务时推荐采用 MCP + Skill；WeKnora 官方提供 REST API、CLI 和 MCP 服务；Codex CLI 也支持 STDIO/Streamable HTTP MCP、工具白名单及工具审批。因此具备技术串联基础，但协议版本、认证和多用户隔离仍需做实际兼容验证。[WorkBuddy连接器文档](https://open.workbuddy.cn/docs/connector)、[WeKnora官方仓库](https://github.com/Tencent/WeKnora)、[Codex MCP官方文档](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)

---

# 一、三套系统的职责边界

| 系统 | 核心定位 | 应该承担 | 不应承担 |
|---|---|---|---|
| WorkBuddy | PC端数字员工入口 | 需求受理、会议协同、任务编排、进度查询、报告生成、审批交互 | 代码和发布事实源、无限制运行本地命令 |
| WeKnora | 企业知识服务 | 文档解析、混合检索、知识问答、引用、知识权限和版本治理 | 需求状态机、Git源码事实、发布放行 |
| Codex CLI | 研发执行端 | 读仓库、分析、修改代码、执行测试、代码审查、生成证据 | 跨团队流程总控、自动判定HIL通过、替代最终责任人 |
| TAPD/项目系统 | 流程状态SSOT | 工作项、状态、负责人、里程碑、审批和关联关系 | 存储大段研发知识和原始构建日志 |
| Git/CI/制品库 | 工程事实SSOT | 源码、commit、构建记录、测试结果、制品身份 | 办公知识问答 |
| HIL/设备证据库 | 产品验证事实 | 板卡、固件身份、测试环境、运行日志、测试结论 | 用Host测试结果代替真机验证 |

如果目前没有统一项目管理系统，可以先建立一个轻量“研发工作项服务”，但不要把状态只保存在 WorkBuddy 会话或 WeKnora 对话里。

---

# 二、建议的串联方式

## 1. WorkBuddy连接WeKnora

推荐开发一个企业内部的 `WeKnora Connector`：

```text
weknora-connector/
├── connector-meta.json
├── mcp.json
├── icon.svg
└── skills/
    ├── rd-knowledge-search/
    │   └── SKILL.md
    └── knowledge-candidate-submit/
        └── SKILL.md
```

首期只开放以下只读工具：

- 列出用户有权访问的知识库；
- 混合检索；
- 读取指定知识文档；
- 基于指定知识库问答；
- 返回知识来源、版本和引用。

首期不要开放：

- 删除知识库；
- 删除正式知识；
- 修改已发布规范；
- 自动生成并发布Wiki；
- 未经审核把会议记录、聊天内容写入正式知识库。

WorkBuddy官方建议：网络API优先采用远程 HTTPS MCP，成熟的跨平台本地工具才采用 CLI + Skill；自定义连接器还应明确认证、超时、错误恢复和高风险确认规则。[WorkBuddy连接器开发说明](https://open.workbuddy.cn/docs/connector)

### 推荐输出契约

WeKnora检索结果不要只返回一段文字，至少返回：

```json
{
  "query": "问题描述",
  "knowledge_base_id": "kb-id",
  "knowledge_id": "document-id",
  "document_title": "文档标题",
  "document_version": "版本或更新时间",
  "passages": [],
  "source_url": "受控来源",
  "retrieved_at": "时间",
  "authority_status": "current|reviewing|archived"
}
```

这样 WorkBuddy 和 Codex 都能区分“当前正式规范”“待审核材料”和“历史参考”。

## 2. Codex CLI连接WeKnora

Codex CLI建议直接连接同一个 WeKnora MCP 服务，避免让 WorkBuddy代转知识内容。

两种方式：

- 开发机单用户试点：WeKnora CLI以 STDIO MCP方式运行；
- 企业集中部署：使用 HTTPS Streamable HTTP MCP，按用户身份认证。

Codex CLI官方支持 STDIO和Streamable HTTP MCP，并能为服务器配置工具白名单、禁用名单以及 `auto/prompt/writes/approve` 等审批策略。[Codex MCP官方文档](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)

推荐给 Codex 只开放：

- `list_knowledge_bases`；
- `hybrid_search`；
- `read_document`；
- `ask_with_citations`。

知识写入应通过单独的“候选提交”流程，不建议让 Codex 直接修改正式知识。

### 项目级规则

每个嵌入式仓库继续使用 `AGENTS.md` 固化：

- 仓库边界；
- 构建入口；
- 编译工具链；
- 格式和静态检查；
- 禁止修改的文件；
- 板卡和芯片约束；
- 测试矩阵；
- 部署和HIL审批规则；
- 提交和发布规则。

Codex官方说明，Codex会在执行前读取全局和项目级 `AGENTS.md`，并按目录层级组合规则，离当前目录更近的规则具有更高优先级。[Codex AGENTS.md官方说明](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

WeKnora提供的是“可能相关的知识”，`AGENTS.md`提供的是“当前仓库必须遵守的运行规则”。两者不能互相替代。

## 3. WorkBuddy串联Codex CLI

建议分两阶段。

### 第一阶段：任务工件交接

WorkBuddy不直接启动Codex，而是生成一个经人工确认的研发任务包：

```text
任务受理
  ↓
WorkBuddy补齐需求
  ↓
WeKnora检索规范和历史案例
  ↓
生成 task-brief.md / task-brief.json
  ↓
产品或研发负责人确认
  ↓
工程师从目标仓启动Codex CLI
  ↓
Codex读取任务包、AGENTS.md和WeKnora知识
```

这是首期推荐方式，优点是：

- 权限边界清楚；
- 工程师知道 Codex 将处理什么；
- 工作目录和仓库身份容易确认；
- 不需要 WorkBuddy 掌握开发机的全局终端权限；
- 出现问题时容易中止和恢复。

### 第二阶段：受控执行网关

当人工试点稳定后，再增加内部 `Dev Workflow Gateway`：

```text
WorkBuddy
   │ 创建已审批工作项
   ▼
Dev Workflow Gateway
   │ 校验身份、仓库、权限、任务状态
   ▼
隔离Runner / Git worktree
   │ 启动 codex exec
   ▼
patch + 测试结果 + 执行回执
   │
   ▼
WorkBuddy展示结果，人工决定接受、退回或继续
```

Codex CLI本身适合终端交互，也支持非交互式、可重复的脚本流程，因此可作为受控Runner的执行能力；但企业自动化必须在外部增加身份、队列、超时、审批和证据保存。[Codex CLI官方文档](https://learn.chatgpt.com/docs/codex/cli)

不建议采用：

> WorkBuddy获得开发机Shell完全权限，然后直接执行任意自然语言生成的Codex命令。

这种方案难以解决工作目录错误、凭证暴露、dirty工作区污染、重复执行、设备误操作和执行中断恢复。

---

# 三、统一“研发工作项”领域模型

这是串联三套系统最关键的共享契约。

## 关键实体

### 研发工作项

建议字段至少包括：

```yaml
work_item_id:
title:
type: requirement | defect | refactor | investigation
priority:
project_id:
product_id:
target_platform:
target_board:
repo_urls:
repo_roots:
base_branch_or_commit:
owner:
reviewers:
goal:
non_goals:
acceptance_criteria:
constraints:
risk_level:
knowledge_refs:
required_verification:
approval_policy:
current_state:
artifact_refs:
evidence_refs:
blockers:
```

### 知识引用

```yaml
knowledge_base_id:
knowledge_id:
title:
version:
authority_status:
source:
retrieved_at:
applicable_product:
applicable_platform:
```

### 执行回执

```yaml
execution_id:
work_item_id:
executor:
repo_root:
base_commit:
result_commit_or_patch:
changed_files:
commands:
command_exit_codes:
test_results:
build_artifacts:
artifact_hashes:
unverified_items:
blocked_items:
next_actions:
```

### 板级验证回执

```yaml
hil_run_id:
work_item_id:
device_id:
board_revision:
boot_id_or_uptime:
firmware_version:
artifact_hash:
test_case:
operator:
environment:
result:
evidence_refs:
stop_reason:
```

## 状态机

建议采用：

```text
draft
  ↓
needs-information
  ↓
ready-for-analysis
  ↓
ready-for-development
  ↓
in-development
  ↓
ready-for-review
  ↓
ready-for-build
  ↓
ready-for-hil
  ↓
ready-for-release
  ↓
closed
```

异常状态：

```text
blocked
rejected
cancelled
needs-rework
```

状态转换由项目系统管理，不由 WorkBuddy对话状态或 Codex会话状态推断。

---

# 四、嵌入式研发端到端流程

## 阶段1：需求受理

WorkBuddy负责：

- 从会议、邮件或自然语言中提取需求；
- 创建研发工作项草稿；
- 补齐产品、平台、板卡、版本和影响范围；
- 调用WeKnora查询需求模板、现行规范和历史案例；
- 识别缺失信息。

必须人工确认：

- 目标；
- 非目标；
- 优先级；
- 负责人；
- 验收标准；
- 涉及的产品和硬件版本。

## 阶段2：需求分析与设计

WorkBuddy和Codex均可读取WeKnora，但分工不同：

- WorkBuddy：形成跨团队可读的需求说明和会议决策；
- Codex：从真实仓库分析入口代码、依赖关系、已有测试和影响范围；
- WeKnora：提供接口规范、芯片资料、设计决策和历史问题；
- 负责人：冻结需求与接口契约。

输出：

- `requirement.md`；
- `design.md`或ADR；
- `acceptance.yaml`；
- `task-brief.json`；
- 知识引用列表。

## 阶段3：代码实施

工程师在目标仓启动Codex CLI。

Codex必须先确认：

- 当前真实repo root；
- 分支和base commit；
- dirty状态；
-当前生效的 `AGENTS.md`；
- 目标平台和工具链；
- 本轮允许修改的文件；
- 禁止执行的设备操作。

Codex完成：

- 代码分析；
- 最小修改；
- 单元测试；
- 静态检查；
-Host/SIL验证；
- 变更说明；
- 未验证事项清单。

WorkBuddy只展示状态和结果，不直接宣布代码完成。

## 阶段4：交叉构建和制品

由受控构建环境执行：

- 交叉编译；
- 链接检查；
- 镜像或固件生成；
- 依赖和版本检查；
- 制品hash；
- 构建环境记录。

制品必须绑定：

```text
工作项ID
+ repo/commit
+ toolchain版本
+ 构建配置
+ 目标平台
+ artifact hash
```

## 阶段5：部署和板级验证

部署、串口、ADB、SSH、烧录、运动机构、电池、充电和产测设备操作必须独立授权。

板级结果必须包含：

- 设备身份；
- 板卡版本；
- 实际运行制品版本/hash；
- boot ID或等效启动身份；
- 测试步骤；
- 运行日志；
- 测试人员；
- 停止条件；
- 失败后的安全状态。

Host/SIL通过不能自动将工作项推进为“HIL通过”。

## 阶段6：评审和发布

WorkBuddy负责汇总：

- 需求完成情况；
- 代码评审结果；
- 构建状态；
- 制品身份；
- HIL状态；
- 未关闭风险；
- 外部owner事项。

发布负责人根据证据审批，而不是让数字员工自动放行。

## 阶段7：知识沉淀

关闭工作项后，数字员工生成知识候选：

- 问题现象；
- 适用产品和版本；
- 根因；
- 解决方案；
- 验证范围；
- 不适用边界；
- 代码和证据引用；
- 后续风险。

知识负责人审核后再进入WeKnora正式知识库。原始聊天、完整日志、密钥、core和二进制不直接进入知识库。

---

# 五、WeKnora知识库规划

建议按“知识权威级别 + 业务域”组织，不要按个人建立大量重复知识库。

## 推荐知识域

| 知识库 | 内容 | 主要用户 |
|---|---|---|
| 研发流程与规范 | 需求、评审、测试、发布制度 | 全研发中心 |
| 产品与系统架构 | 产品架构、模块关系、接口契约 | 产品、系统、研发、测试 |
| 平台与芯片 | SoC、MCU、BSP、SDK、工具链 | 嵌入式研发 |
| 驱动与组件 | 驱动、OSAL、中间件、协议 | 嵌入式研发 |
| 测试与质量 | 测试矩阵、缺陷模式、验收标准 | 测试、质量、研发 |
| 现场问题案例 | 脱敏问题、根因、验证和恢复 | 售后、测试、研发 |
| 构建与发布 | 构建、制品、OTA、回滚Runbook | 研发、配置、发布 |
| 历史归档 | 过期版本和历史方案 | 受限查询 |

每份知识增加：

- owner；
- 来源；
- 产品和平台；
- 适用版本；
- 生效状态；
- 审核人；
- 更新时间；
- 过期时间；
- 证据引用；
- 敏感等级。

WeKnora当前官方能力包括多知识库、混合检索、REST API、MCP、工作区RBAC、按知识库资源控制及审计能力，适合作为知识服务层；具体部署版本是否已经包含这些能力，需要以实际安装版本和Swagger为准。[WeKnora官方仓库](https://github.com/Tencent/WeKnora)、[WeKnora API说明](https://github.com/Tencent/WeKnora/blob/main/docs/api/README.md)

---

# 六、需求包拆分

## 需求包A：WeKnora知识服务接入

- Goal：WorkBuddy和Codex能按用户权限检索同一套受控研发知识。
- Non-goal：不自动发布AI生成知识，不开放删除正式知识。
- Done-when：两端均能查询指定知识库，返回同一文档身份、版本和引用。
- Required Evidence：认证测试、权限隔离测试、检索准确率测试、越权测试、审计日志。
- Artifact Paths：
  - `connectors/weknora/`
  - `schemas/knowledge-reference.v1.json`
  - `docs/knowledge-governance.md`
  - `tests/weknora-connector/`
- Blocker Policy：无法证明不同用户、不同知识库的权限隔离时，不进入团队试点。
- 优先级：P1。

## 需求包B：研发工作项契约

- Goal：以统一工作项串联WorkBuddy、项目系统和Codex。
- Non-goal：不替换现有项目管理系统。
- Done-when：一个需求可以从受理走到评审，并完整关联任务、代码、测试和阻塞。
- Required Evidence：Schema校验、状态转换测试、重复提交测试、失败恢复测试。
- Artifact Paths：
  - `schemas/rd-work-item.v1.json`
  - `schemas/execution-receipt.v1.json`
  - `schemas/hil-evidence.v1.json`
  - `docs/workflow-state-machine.md`
- Blocker Policy：owner、验收标准或目标仓缺失时，禁止进入开发态。
- 优先级：P1，建议最先冻结。

## 需求包C：Codex CLI研发规范化

- Goal：让Codex在不同嵌入式仓库遵循一致且可验证的研发规则。
- Non-goal：不让一套全局提示替代各仓真实构建和板级规则。
- Done-when：试点仓能稳定加载规则、查询WeKnora、执行既有验证入口并输出结构化回执。
- Required Evidence：规则加载检查、repo root验证、Host测试、交叉构建、失败案例。
- Artifact Paths：
  - 各仓 `AGENTS.md`
  - 各仓 `.codex/config.toml`
  - `.agents/skills/<project-skill>/`
  - `docs/codex-runbook.md`
- Blocker Policy：仓库边界、构建入口或验证方法不明确时，只允许分析，不允许自动修改。
- 优先级：P1。

## 需求包D：WorkBuddy研发数字员工

- Goal：为需求、缺陷、评审和报告提供统一PC入口。
- Non-goal：不直接控制生产设备，不绕过工程师审批。
- Done-when：能创建任务草稿、查询知识、生成任务包、接收执行回执和展示阻塞。
- Required Evidence：五类典型场景测试、权限测试、用户采纳率、错误恢复测试。
- Artifact Paths：
  - `agents/embedded-rd-employee/`
  - `skills/requirement-intake/`
  - `skills/issue-triage/`
  - `skills/development-handoff/`
  - `docs/workbuddy-user-guide.md`
- Blocker Policy：外部连接器没有最小权限或审计能力时，只保留本地草稿能力。
- 优先级：P1。

## 需求包E：自动执行网关

- Goal：让已审批任务在隔离环境中调用Codex非交互执行。
- Non-goal：首期不自动部署、不自动HIL、不自动发布。
- Done-when：任务可在独立worktree或Runner中幂等执行，失败可中止和恢复。
- Required Evidence：身份验证、任务签名、隔离测试、并发测试、超时测试、重复执行测试、凭证泄漏扫描。
- Artifact Paths：
  - `services/dev-workflow-gateway/`
  - `schemas/job-request.v1.json`
  - `schemas/job-result.v1.json`
  - `docs/runner-security.md`
  - `tests/e2e/`
- Blocker Policy：人工试点未达到验收指标前不启动建设；没有隔离Runner时不允许远程执行Codex。
- 优先级：P2。

---

# 七、分阶段实施计划

## 第0阶段：现状冻结，2周

完成：

- 明确WorkBuddy具体版本和企业能力；
- 明确WeKnora部署版本、认证方式和网络位置；
- 确定项目管理系统；
- 选定一个真实嵌入式产品线；
- 选定2–3个试点仓；
- 盘点当前需求、构建、测试、HIL和发布入口；
- 冻结研发工作项v1；
- 制定敏感数据和禁止操作清单。

## 第1阶段：知识双接入，3–4周

完成：

- WorkBuddy接入WeKnora只读MCP；
- Codex CLI接入同一WeKnora只读MCP；
- 建立最小知识分类和owner；
- 建立20–50个标准检索问题；
- 验证引用、权限、版本和拒答。

阶段门禁：

- 权限隔离通过；
- 高风险问题无可靠来源时能够拒答；
- 知识引用率达到约定阈值；
- 不发生未经审核的知识写入。

## 第2阶段：人工研发闭环，4–6周

选择一个中低风险嵌入式需求，走完整流程：

```text
WorkBuddy受理
→ WeKnora补充知识
→ 人工冻结需求
→ Codex本地实施
→ Host/交叉构建
→ 人工评审
→ HIL
→ WorkBuddy汇总
→ 知识候选审核
```

此阶段不建设远程Codex自动执行。

## 第3阶段：受控自动化，6–10周

仅在第二阶段证明有效后建设：

- Dev Workflow Gateway；
- 队列与任务状态；
- 隔离worktree/Runner；
- Codex非交互执行；
- 结构化回执；
- 超时、重试和取消；
- 人工审批；
- 成本和审计。

仍不自动执行：

- 固件烧录；
- 设备重启；
- 电机运动；
- OTA发布；
- 合并代码；
- 推送正式分支；
- 发布放行。

## 第4阶段：扩围

按产品线和角色扩展：

- 需求数字员工；
- 嵌入式开发数字员工；
- 测试数字员工；
- 发布检查数字员工；
- 现场问题分诊数字员工；
- 管理汇总数字员工。

---

# 八、试点验收标准

| ID | 验收标准 | 验证方式 |
|---|---|---|
| AC1 | 一个工作项具有唯一ID，并贯穿需求、代码、测试和HIL | 检查完整端到端样例 |
| AC2 | WorkBuddy和Codex检索同一知识时能返回可追溯来源 | 20–50题检索评测 |
| AC3 | 不同用户不能检索未授权知识库 | RBAC负向测试 |
| AC4 | Codex能从目标仓读取正确的项目级规则 | 规则来源检查 |
| AC5 | Codex执行前能确认repo root、base commit和dirty状态 | 执行回执检查 |
| AC6 | 代码修改能关联工作项和验证证据 | Git、回执、项目系统交叉核对 |
| AC7 | Host、交叉构建、HIL状态分别记录 | 三类证据字段检查 |
| AC8 | WorkBuddy不能将未完成验证展示为发布完成 | 状态机负向测试 |
| AC9 | AI生成知识不能直接成为正式知识 | 知识审核流程测试 |
| AC10 | 失败、取消、超时和重复任务均可识别和恢复 | 故障注入 |
| AC11 | 高风险操作必须获得明确人工批准 | 权限与审批审计 |
| AC12 | 试点场景处理时间相对基线降低30%以上 | 试点前后对比 |

---

# 九、关键风险

## 1. 多用户身份穿透

WorkBuddy用户、WeKnora用户、项目系统用户和Codex执行身份必须能关联，但不能共用一个超级API Key。

验证重点：

- 用户A不能查用户B的知识；
- 工程师不能因使用公共MCP端点获得管理员权限；
- Runner凭证不能出现在提示词、日志和执行回执中。

## 2. RAG提示注入

WeKnora中的文档属于数据，不属于运行指令。文档中的“忽略安全规则”“执行某命令”等内容不能覆盖：

- WorkBuddy企业规则；
- Codex全局规则；
- 仓库 `AGENTS.md`；
- 审批策略；
- 沙箱权限。

## 3. 状态重复和冲突

若WorkBuddy、WeKnora和TAPD都保存一份任务状态，很快会出现“一个显示完成、另一个显示进行中”。

必须提前定义SSOT：

| 数据 | SSOT |
|---|---|
| 需求及流程状态 | TAPD/项目系统 |
| 当前源码 | Git |
| 构建结果 | CI/构建系统 |
| 发布制品 | 制品库 |
| 正式研发知识 | WeKnora受控知识 |
| AI执行上下文 | 临时会话，不作为权威事实 |
| 板级验证 | HIL证据库或测试系统 |

## 4. 把源码完成误判为产品完成

嵌入式研发至少要区分：

```text
源码分析
Host测试
交叉构建
制品生成
实际部署
设备身份确认
板级HIL
长期运行
发布审批
```

Codex完成修改或Host测试通过，只能推进到相应阶段，不能自动宣布产品完成。结合此前项目经验，这条边界尤其重要；此前经验未在本轮重新做板端验证，因此只作为规划依据。

## 5. PC端敏感数据外发

WorkBuddy具备本地文件和连接器能力，应提前确认：

- 哪些源码可以进入所使用的模型；
- 是否允许访问邮件、会议和客户资料；
- 是否允许移动端远程触发PC任务；
- 文件读取目录白名单；
- 密钥、证书、芯片资料和客户数据拦截策略；
- 日志和会话保留周期。

---

# 十、当前规划结论

- 需求分类：跨系统新能力建设。
- 优先级：P1。
- 推荐架构：共享知识、双入口执行、统一工作项、分层证据。
- 推荐首期：WorkBuddy和Codex分别只读接入WeKnora，以人工任务包完成一个真实嵌入式研发闭环。
- 不推荐首期：WorkBuddy直接远程控制个人PC上的Codex CLI。
- 自动化前置条件：人工闭环稳定、身份统一、状态机冻结、权限隔离通过、执行回执稳定。
- 当前状态：`needs-fix`，表示仍有关键立项信息待确认，不代表方案不可行。

需要优先确认的五项信息：

1. WorkBuddy使用个人版还是企业版，当前实际版本是什么；
2. WeKnora是内网私有部署、云部署还是单机部署；
3. 研发流程的现有SSOT是TAPD、禅道、Jira还是其他系统；
4. 首个试点产品、板卡和代码仓是什么；
5. 首期仅要求“任务交接”，还是必须实现WorkBuddy自动调用Codex。

建议下一份正式产物直接形成《研发数字员工一期需求规格》，先冻结：

- 系统职责矩阵；
- `rd-work-item.v1`；
- 状态机；
- WeKnora知识权限；
- WorkBuddy连接器范围；
- Codex执行回执；
- 一个真实嵌入式试点用例；
- 12项验收标准。

本次规划事项已按当前Activity Facts v2配置成功记录，返回 `status=pass`、`applied=true`。Runtime Control工程门禁仍提示缺少repo/build工件，这是因为本轮只做需求规划，没有进入实现，不影响规划结论，但不能据此声明三套系统已经集成完成。
