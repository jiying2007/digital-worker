# ADR-003：Provider-neutral AI R&D Target Architecture

- Status: proposed-for-review
- Date: 2026-09-11
- Scope: 研发中心 AI 数字员工总体架构、知识访问、Agent Runtime、工程执行与治理边界
- Related: `研发中心AI数字员工研发流程规划.md`
- Related: `docs/adr/ADR-001-workbuddy-codex-integration-boundary.md`
- Related: `docs/adr/ADR-002-embedded-system-expert-team-architecture.md`

## Context

当前研发中心的目标是明确的：通过 AI 提升研发效率与质量，让知识、历史经验、工程证据和专家能力能够被重复使用，并在源码、设备、发布等高风险边界上保持可审计、可回退和人工可控。

但具体总体架构尚未冻结。现有或候选组件包括：

- 飞书及飞书知识库；
- WorkBuddy 或其他办公 Agent/工作入口；
- NAS 上的芯片资料、SDK 文档、测试报告、供应商资料和历史项目文件；
- Git、Issue/PR、CI、制品库、HIL/测试系统等工程事实源；
- WeKnora 或其他检索/RAG/知识平台；
- Codex、Claude Code、IDE Agent、内部 Agent 或未来其他 Engineering Agent Runtime。

此前方案把其中部分产品写成了目标架构前提，这会造成三类风险：

1. **Provider lock-in**：一旦 WorkBuddy、WeKnora、Codex 等产品能力、成本或组织策略变化，上层流程被迫重构；
2. **知识 SSOT 混淆**：飞书、NAS、Git、CI/HIL 的不同事实被强行搬进单一“知识库”，反而造成版本、权限和新鲜度漂移；
3. **Expert 与 Runtime 混淆**：将“Linux/BSP Expert”这类稳定组织角色绑定到某个模型或 CLI，导致专家体系随模型更换而变化。

因此需要先冻结**稳定能力边界与 Contract**，再通过 PoC 选择具体 Provider。

## Decision

### D1. 冻结目标与原则，不冻结产品组合

当前阶段只冻结以下目标：

- AI 能进入研发任务的接诊、分析、执行辅助、验证、审查和知识沉淀闭环；
- 任务、知识、代码、制品、设备和发布状态可追溯；
- Agent 不得绕过权限、人工审批、设备安全和发布门禁；
- 专家能力、工程 Contract、Evidence 和 Evaluation 不依赖具体模型品牌；
- Provider 可以被替换，Contract 不应随 Provider 改变。

WorkBuddy、飞书知识库、WeKnora、Codex、Claude Code 等均视为**候选 Provider / Adapter**，不是总体架构成立的前提。

### D2. 总体架构采用七个逻辑 Plane

```text
人 / 团队
   │
   ├──────── Interaction & Collaboration Plane ────────┐
   │    Feishu / WorkBuddy / Web / IDE / CLI / Other  │
   │                                                   │
   ▼                                                   │
Work Item / Task Contract                              │
   │                                                   │
   ▼                                                   │
Digital Worker Governance Plane                        │
Expert Team / Routing / Gate / Policy / Evaluation     │
   │                                                   │
   ├──────── Context & Knowledge Plane ────────────────┤
   │     Knowledge Registry / Gateway / Context Broker │
   │                                                   │
   ├──────── Agent Runtime Plane ──────────────────────┤
   │     Codex / Claude / IDE Agent / Internal Agent   │
   │                                                   │
   ├──────── Action & Execution Plane ─────────────────┤
   │     Developer Workspace / CI / Runner / HIL       │
   │                                                   │
   └──────── Evidence / Identity / Audit Plane ────────┘
         provenance / ACL / approval / verification
```

七个 Plane：

1. **Interaction & Collaboration**：员工实际工作的入口，不要求唯一入口；
2. **Work Item / State**：任务身份、owner、状态和审批；
3. **Digital Worker Governance**：专家团、路由、Contract、Gate、Policy、Evaluation；
4. **Context & Knowledge**：知识注册、检索、权限过滤、上下文组装；
5. **Agent Runtime**：不同 Agent/模型的运行适配；
6. **Action & Execution**：源码修改、构建、CI、设备和 HIL 等真实动作；
7. **Evidence / Identity / Audit**：跨所有 Plane 的身份、权限、证据和审计能力。

### D3. digital-worker 负责 Operating Model，不负责绑定具体 Provider

`digital-worker` 的长期职责是：

- Task Contract；
- Expert Team / Skill / Workflow；
- Routing / Gate / Action Policy；
- Evidence / Verification / Review；
- Cross-team Contract；
- Evaluation / Pilot / Productionization Gate；
- Provider Adapter 所需的稳定接口定义。

`digital-worker` 不应退化为：

- WorkBuddy 配置仓；
- WeKnora 配置仓；
- Codex Prompt 仓；
- Claude Prompt 仓；
- 某一种知识平台的同步脚本仓。

### D4. 知识采用 Source-of-Truth-stays-at-source

不同对象保留各自最合适的权威事实源：

|对象|典型权威源|
|---|---|
|源码 / 当前配置|Git|
|PR / Issue / Review|Git 平台或研发协作系统|
|构建 / 测试|CI、测试系统|
|发布制品|Artifact Store|
|板端/HIL验证|HIL/测试证据系统|
|组织流程 / 决策文档|飞书或其他协作平台|
|Datasheet/TRM/SDK/供应商资料|NAS、文档管理系统或供应商源|
|AI检索索引|WeKnora 或其他 Knowledge Provider（非原文 SSOT）|

原则：**统一访问，不强制统一存储。**

### D5. 引入 Knowledge Registry、Knowledge Gateway、Context Broker 三层概念

#### Knowledge Registry

描述“知识在哪里、谁负责、版本/权限/新鲜度如何”，而不是复制正文。

建议最小字段：

```yaml
knowledge_id:
type:
authority:
source_provider:
source_ref:
owner:
version_or_revision:
acl_policy:
freshness:
indexed_by: []
```

#### Knowledge Gateway

向上提供稳定能力：

```text
search(query, scope, identity)
get(ref, identity)
cite(ref)
resolve_authority(subject)
```

背后可以接：飞书、NAS、Git、WeKnora、Issue/PR、HIL Evidence 等 Adapter。

#### Context Broker

输入任务身份、用户身份、project/repo/platform 等约束，输出**最小必要上下文包**，而不是给 Agent 整库访问权限。

目标：

- 减少 Token 和噪声；
- 降低越权范围；
- 保留 source / version / ACL / evidence provenance；
- 支持同一个任务在 Codex、Claude 或其他 Runtime 间切换。

### D6. Knowledge Provider 与 Knowledge Source 分离

WeKnora、未来其他 RAG/搜索系统属于 **Knowledge Provider**，可以负责索引、检索、RAG、引用与评测，但不能天然成为所有知识的 canonical store。

NAS、飞书、Git、CI/HIL 等属于 **Knowledge / Evidence Source**。某些 Source 可以被 Provider 索引，也可以由 Gateway 直接读取。

知识方案在 PoC 前保持 `not-frozen`。

### D7. Expert Identity 与 Agent Runtime 解耦

例如 `linux-bsp-expert` 是组织能力身份，不等于 Codex Agent 或 Claude Agent。

```text
Embedded Expert Role
       │
       ▼
standard task/context contract
       │
 ┌─────┼─────────┐
 ▼     ▼         ▼
Codex  Claude   Other Runtime
```

Runtime 选择由任务、权限、代码仓、模型能力、成本、合规和工程环境共同决定。

任何 Runtime 均必须消费相同的工程 Contract，并输出可验证的 Receipt / Evidence。

### D8. Engineering Execution 使用 provider-neutral Handoff

稳定主链定义为：

```text
Work Item / Interaction Provider
      -> task-brief
      -> Expert Team
      -> engineering-task-package
      -> Engineer + Engineering Agent Runtime
      -> delivery-receipt
      -> Verification
      -> Independent Review
      -> Work Item / Collaboration Provider
```

`Engineer + Engineering Agent Runtime` 可以是：

- Engineer + Codex；
- Engineer + Claude Code；
- Engineer + IDE Agent；
- 受控 Runner + approved Agent；
- 未来其他实现。

办公入口或 Work Item Provider 默认不得直接获得个人开发机、设备写、发布等无限执行权。

### D9. Action Gateway 是未来自动化的安全边界

当从“建议/生成”进入真实动作时，统一受 Action Policy 控制：

- A0 READ；
- A1 ANALYZE；
- A2 GENERATE；
- A3 MODIFY_WORKTREE；
- A4 BUILD_TEST；
- A5 DEVICE_READ；
- A6 DEVICE_WRITE；
- A7 RELEASE。

无论调用来自 WorkBuddy、Codex、Claude 还是其他 Agent，权限判断应基于**动作、身份、任务、环境、审批和证据**，而不是 Provider 名称。

### D10. 保留现有稳定 Contract，新增 Provider-neutral 接口

现有稳定资产继续保留：

- `task-brief`；
- `engineering-task-package`；
- `delivery-receipt`；
- `evidence-ref`；
- `verification-report`；
- `review-report`；
- Pilot Run / Result / Metrics。

后续按 PoC 证据决定是否正式新增：

- `knowledge-source-ref`；
- `context-package`；
- `agent-runtime-receipt`；
- `action-request / action-approval`；
- `provider-capability-profile`。

在字段需求没有被真实 PoC 证明前，不提前堆 Schema。

### D11. Work Item Provider 也保持可替换

飞书是当前重要候选协作平台，但总体架构只依赖：

- stable work_item_id；
- owner / requester；
- state；
- approval / decision；
- task contract 与 evidence link；
- audit history。

如果未来使用其他研发项目/协作系统，只要满足上述 Contract，不应推翻 Expert Team 或 Engineering Handoff。

### D12. Provider 选型必须通过 PoC + Evaluation，而不是先写死架构

建议至少评测四个维度：

#### Interaction / Collaboration
- 用户 adoption；
- work item/API 能力；
- 身份与权限；
- 审批与通知；
- 移动/桌面体验。

#### Knowledge
- NAS / 飞书 / Git 等 Source 接入；
- ACL 映射；
- 更新/删除传播；
- citation / provenance；
- retrieval quality；
- latency / availability / ops cost。

#### Agent Runtime
- 代码理解/修改质量；
- repo/toolchain 适配；
- Contract adherence；
- evidence generation；
- cancel/retry/recovery；
- 权限、安全、成本和可观测性。

#### Action / Execution
- workspace isolation；
- exact base / dirty baseline；
- CI / HIL 对接；
- approval；
- idempotency / rollback；
- auditability。

### D13. Provider 决策采用 Capability Matrix

每个候选 Provider 进入正式架构前，需要记录：

```text
capability
required / optional
provider
native / adapter / unsupported
identity model
permission model
data boundary
failure mode
fallback
owner
PoC evidence
```

禁止仅凭“能连上”“有 MCP”“能 RAG”“模型更强”等单点能力直接成为企业默认 Provider。

### D14. 一期先做互操作性 PoC，不做大迁移

优先验证：

1. 1 个 Work Item Provider；
2. 飞书文档/知识库、NAS、Git 三类不同 Knowledge Source；
3. 至少 2 种 Engineering Agent Runtime；
4. 同一 `task-brief / engineering-task-package / delivery-receipt` 是否可跨 Runtime 工作；
5. Evidence / ACL / exact base / Verification 是否保持一致；
6. Provider 替换是否只影响 Adapter，不影响 Expert / Workflow / Contract。

### D15. 生产化前保持人工 Gate

在 Provider、知识权限、Runtime 和 Action Gateway 没有真实 Pilot evidence 前：

- 不自动扩大 A3-A7；
- 不把 RAG 检索成功视为知识权限正确；
- 不把 Agent 输出视为工程事实；
- 不把模型/Provider 切换隐藏在不可审计的自动路由后；
- 不自动将聊天或 Agent 总结提升为正式知识；
- 不自动 Production Release。

## What this ADR supersedes

本 ADR **不废弃** ADR-001 的“办公/协作入口与工程执行端应通过 Contract 松耦合”原则，也不废弃 ADR-002 的 Expert/Gate/Evidence/Verification 架构。

本 ADR supersede 的是以下过早绑定：

- WorkBuddy 是唯一数字员工入口；
- 飞书知识库必然是所有知识的唯一人工主库；
- WeKnora 必然是统一 AI 检索层；
- Codex CLI 必然是唯一工程 Agent Runtime；
- “WorkBuddy → WeKnora → Codex”是总体架构本身。

这些均降级为 Provider 候选与 PoC 假设。

## Consequences

### 正向

- 模型和产品替换不会破坏专家团与研发 Contract；
- NAS、Git、HIL 等工程事实可以保留原生权威；
- 同时支持 Codex、Claude 或其他 Agent；
- 能先验证知识权限/检索/上下文质量，再决定知识平台；
- 降低大规模知识迁移和平台锁定风险。

### 成本

- 需要维护 Adapter / Provider capability matrix；
- Knowledge Gateway / Context Broker 增加一层架构抽象；
- 初期不会获得“单平台全包”的表面简洁；
- 身份、ACL 和 Evidence 跨系统映射需要独立设计。

## Review / Revisit Triggers

以下事件应触发重新评审：

- 知识平台 PoC 证明集中式单平台显著优于混合/联邦式；
- 组织确定唯一 Work Item / Collaboration Provider；
- 某 Agent Runtime 获得企业级统一托管和审计能力；
- 建设受控 Agent Runtime Gateway / Action Gateway；
- NAS 或飞书知识权限模型发生重大变化；
- 真实 Pilot 证明 Context Broker 复杂度大于实际收益。

## Acceptance Criteria

ADR-003 从 `proposed-for-review` 转为 `accepted` 前至少需要：

1. 研发中心确认“Provider 可替换、Contract 稳定”的总体原则；
2. 完成 Knowledge Source Inventory；
3. 定义至少一版 Provider Capability Matrix；
4. 用同一真实任务至少验证两种 Engineering Agent Runtime；
5. 至少验证飞书/协作文档、NAS、Git 三类 Knowledge Source 的受控访问；
6. 完成 ACL / identity / citation 的负向测试；
7. 明确 Work Item Provider 的 stable ID / state / approval 机制；
8. 保持现有 Pilot Safety Gate 与高风险 Action Gate 不被弱化。
