# 研发中心 AI 数字员工研发流程规划

- 文档版本：3
- 文档状态：proposed
- 日期：2026-09-11
- 适用范围：研发中心办公协同、知识访问、AI Agent 与嵌入式研发流程
- 版本关系：本文件是当前唯一活动总体提案；历史草案位于 `docs/archive/`，后续继续更新稳定路径。
- 已确认目标：提升研发效率与质量；让知识、历史经验、工程证据和专家能力可复用；保证源码、设备、发布等高风险边界可审计、可回退、人工可控。
- 尚未冻结：总体产品组合、知识库/检索方案、唯一办公入口、唯一 Agent Runtime、统一执行网关。
- 核心决策：
  - [ADR-001：WorkBuddy 与 Codex CLI 的集成边界](docs/adr/ADR-001-workbuddy-codex-integration-boundary.md)
  - [ADR-002：嵌入式系统专家团架构与落地边界](docs/adr/ADR-002-embedded-system-expert-team-architecture.md)
  - [ADR-003：Provider-neutral AI R&D Target Architecture](docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md)

## 1. 当前判断

当前不应该先决定“WorkBuddy + 飞书 + WeKnora + Codex”这一产品组合，而应先冻结**能力架构、Contract、Evidence 和安全边界**。

以下均视为候选 Provider / Source，而不是总体架构前提：

- 飞书、飞书知识库；
- WorkBuddy 或其他办公 Agent/入口；
- NAS 上的 Datasheet/TRM/SDK/供应商资料/测试报告/历史项目资料；
- Git、Issue/PR、CI、制品库、HIL/测试系统；
- WeKnora 或其他搜索/RAG/知识平台；
- Codex、Claude Code、IDE Agent、内部 Agent 或未来其他 Engineering Agent Runtime。

稳定原则：

> **Provider 可替换，Contract 稳定；统一访问，不强制统一存储；Expert 身份与 Agent Runtime 解耦。**

## 2. 目标架构

```text
研发人员 / 主管 / 测试 / 产品
          │
          ├──────── Interaction & Collaboration ────────┐
          │  Feishu / WorkBuddy / Web / IDE / CLI      │
          │                                              │
          ▼                                              │
     Work Item / Task Contract                           │
          │                                              │
          ▼                                              │
     digital-worker Governance                           │
 Expert Team / Routing / Gate / Policy / Evaluation      │
          │                                              │
   ┌──────┼───────────┬──────────────┬──────────────────┤
   │      │           │              │                  │
   ▼      ▼           ▼              ▼                  ▼
Context  Agent      Action        Engineering        Evidence /
&Knowledge Runtime  Policy        Execution          Identity/Audit
   │      │           │              │                  │
   │   Codex/Claude    │        Git/CI/Runner/HIL        │
   │   IDE/Other       │        Device/Artifact          │
   │                   │                                 │
   └──── Knowledge Sources ──────────────────────────────┘
        Feishu / NAS / Git / Docs / CI / HIL / Other
```

总体分为七个逻辑 Plane：

1. Interaction & Collaboration；
2. Work Item / State；
3. Digital Worker Governance；
4. Context & Knowledge；
5. Agent Runtime；
6. Action & Engineering Execution；
7. Evidence / Identity / Audit。

## 3. digital-worker 的职责

`digital-worker` 是研发中心 AI R&D Operating Model 主仓，负责：

- Task Contract；
- Expert Team / Skill / Workflow；
- Routing / Gate；
- Action Policy；
- Evidence / Verification / Review；
- Cross-team Handoff；
- Evaluation / Pilot / Productionization Gate；
- Provider Adapter 需要遵守的稳定接口。

它不是某个办公 Agent、知识平台或 Coding Agent 的配置仓。

## 4. Work Item / Collaboration

总体架构不要求唯一入口。不同角色可以使用不同入口：

- 管理/协作：飞书、WorkBuddy、Web；
- 研发：IDE、CLI、Coding Agent；
- 测试/验证：测试平台、HIL、Web；
- 评审：飞书、Git PR、Review Portal 等。

稳定要求不是“入口一致”，而是所有入口最终能关联到同一个：

- `work_item_id`；
- owner / requester；
- state；
- approval / decision；
- task contract；
- evidence / artifact link；
- audit history。

飞书是重要候选 Work Item / Collaboration Provider，但当前不把“飞书必须是唯一状态 SSOT”冻结为不可替换架构决策。

## 5. 知识与上下文架构

### 5.1 Source of Truth stays at source

不同事实保留最合适的权威源：

|对象|典型 Source of Truth|
|---|---|
|当前源码 / 配置|Git|
|PR / Issue / Review|Git 平台或研发协作系统|
|构建 / 测试|CI / 测试平台|
|发布制品|Artifact Store|
|设备 / HIL 结果|HIL / 测试证据系统|
|组织流程 / 决策文档|飞书或其他协作系统|
|Datasheet / TRM / SDK / 供应商资料|NAS / DMS / 供应商源|
|AI 搜索索引|WeKnora 或其他 Knowledge Provider（不是原文 SSOT）|

原则：**不要为了 RAG 把所有东西搬成第二份正式正文。**

### 5.2 Knowledge Registry

需要建立知识地图，而不是先建大而全知识库。

建议记录：

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

### 5.3 Knowledge Gateway

向 Agent 提供稳定访问接口：

```text
search(query, scope, identity)
get(ref, identity)
cite(ref)
resolve_authority(subject)
```

背后可以有 Feishu / NAS / Git / WeKnora / HIL 等 Adapter。

### 5.4 Context Broker

Context Broker 根据：

- task / work_item；
- user identity；
- project / product；
- repo / platform / board；
- ACL / data boundary；

组装**最小必要上下文**，并携带 source/version/ACL/evidence provenance。

目标是避免把整库权限和大量无关上下文直接交给 Agent。

### 5.5 WeKnora 的当前定位

WeKnora 是候选 Knowledge Provider，可用于索引、检索、RAG、引用与评测；是否成为默认 Provider 由 PoC 决定。

它当前不被定义为：

- 企业唯一知识 SSOT；
- 所有 NAS/Git/飞书材料必须迁入的中央仓；
- 所有 Agent 唯一知识入口。

## 6. Agent Runtime 架构

Expert Role 与 Agent Runtime 解耦。

```text
Embedded Expert / Workflow
          │
          ▼
 engineering-task-package + context
          │
   ┌──────┼─────────┐
   ▼      ▼         ▼
 Codex  Claude    Other Agent
   │      │         │
   └──────┼─────────┘
          ▼
 delivery-receipt + evidence
```

Engineering Agent Runtime 可以同时存在多个。选择依据包括：

- 任务类型；
- repo/toolchain；
- 模型能力；
- 企业权限与数据边界；
- 成本；
- 可取消/恢复/审计能力；
- Contract adherence；
- Evidence 产出能力。

任何 Runtime 都不能因为“模型更强”绕过工程 Contract 和验证门禁。

## 7. 工程执行边界

稳定主链：

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

办公入口默认不直接获得：

- 开发机任意 Shell；
- Git push/merge；
- 设备写；
- OTA；
- OTP/Fuse；
- Release。

这些动作统一由 Action Policy / Approval 管理。

## 8. Action Policy

沿用 A0-A7：

- A0 READ；
- A1 ANALYZE；
- A2 GENERATE；
- A3 MODIFY_WORKTREE；
- A4 BUILD_TEST；
- A5 DEVICE_READ；
- A6 DEVICE_WRITE；
- A7 RELEASE。

权限判断依据：

> action + identity + work item + environment + approval + evidence

而不是“这个请求来自 WorkBuddy/Codex/Claude，所以允许”。

## 9. 稳定 Contract

现阶段继续使用：

### 9.1 `task-brief v1`

核心字段：

- work_item_id；
- owner / requester；
- repo_roots；
- base branch / commit；
- goal / non_goals；
- acceptance criteria；
- required verification；
- allowed / forbidden actions；
- blocker policy；
- knowledge refs。

缺 owner、目标仓、验收或必要边界时只能保持草稿/needs-information。

### 9.2 `engineering-task-package`

由 Expert Team 把技术判断转成工程可执行输入：

- exact repo/base；
- implementation plan；
- acceptance；
- risk；
- allowed / forbidden actions；
- required verification；
- evidence / knowledge refs。

### 9.3 `delivery-receipt v1`

任何 Engineering Agent Runtime 都必须记录：

- executor identity/runtime；
- repo / base commit；
- changed files / patch / result identity；
- commands；
- artifact refs / hashes；
- evidence refs；
- host / cross-build / SIL / HIL / release 独立状态；
- blockers / risks / unverified items；
- approval required。

### 9.4 验证与审查

`delivery-receipt` 不是最终 PASS。

必须继续经过：

- Verification；
- Independent Review；
- Closure。

## 10. Knowledge Candidate 沉淀

AI 生成的排障总结、Runbook、FAQ、Decision 只能先成为 `knowledge-candidate`。

正式知识提升至少需要：

- source / evidence；
- owner；
- applicable product/platform/version；
- review；
- canonical destination；
- expiry/freshness policy（如适用）。

不得把聊天总结或 Agent 自述直接视为正式知识。

## 11. Provider Capability Matrix

每个候选产品进入默认架构前必须回答：

|维度|需要回答|
|---|---|
|Capability|支持哪些必要能力|
|Identity|如何映射员工/服务身份|
|ACL|权限如何继承/过滤/审计|
|Data boundary|哪些数据会离开源系统/内网|
|Freshness|更新/删除/撤权如何传播|
|Evidence|是否可输出可追溯证据|
|Recovery|失败、取消、重试如何处理|
|Fallback|Provider 不可用如何降级|
|Ops/Cost|运维、成本、容量|
|PoC evidence|真实验证结果|

## 12. 推荐 PoC，不先做平台迁移

### PoC-A：Knowledge

至少覆盖：

1. 飞书/协作文档；
2. NAS PDF/SDK/供应商资料；
3. Git Markdown/ADR/Runbook；
4. 历史 RCA / Issue（条件允许时）。

比较：集中式、联邦式、混合式三种方案。

关键指标：

- retrieval quality；
- citation correctness；
- ACL negative tests；
- update/delete propagation；
- latency；
- ops cost；
- source freshness；
- cross-source authority resolution。

### PoC-B：Engineering Agent Runtime

至少选择两个 Runtime，用同一个真实任务和同一 Contract 比较：

- route/context consumption；
- code change quality；
- cross-build/host evidence；
- recovery/cancel；
- human correction；
- unsupported claims；
- security/audit；
- cost/latency。

不要求两个 Runtime 都成为默认方案；目的是证明架构可替换。

### PoC-C：Interaction / Work Item

验证候选入口是否能稳定提供：

- work_item_id；
- owner/state；
- task-brief；
- approval；
- delivery/evidence link；
- audit history。

## 13. 分阶段推进

### Phase 0：Architecture & Inventory

- 冻结 ADR-003 原则；
- 建 Knowledge Source Inventory；
- 建 Provider Capability Matrix；
- 确定首批真实 Pilot；
- 建身份/ACL/数据边界清单。

### Phase 1：Read-only Knowledge PoC

- 接入飞书/协作文档、NAS、Git；
- Knowledge Gateway 只读；
- 做权限负向测试；
- 不迁移 canonical source。

### Phase 2：Multi-runtime Engineering Pilot

- 用统一 Contract 跑至少两个 Engineering Agent Runtime；
- 完成真实 Debug / Feature / Review-Release Pilot；
- 对比 evidence、纠正率、错误 PASS、成本和恢复能力。

### Phase 3：Provider Selection

- 根据 PoC 选择默认/备用 Provider；
- 用 ADR 固化具体选型；
- 仍保留 Provider adapter boundary。

### Phase 4：Controlled Automation Evaluation

只有前序 evidence 充分后才评估：

- Agent Runtime Gateway；
- Context Broker 自动组包；
- isolated Runner；
- Action Gateway；
- 更高 A3-A7 自动化等级。

## 14. 验收标准

当前架构阶段的验收不是“某产品接通”，而是：

|ID|验收标准|
|---|---|
|A1|任务 Contract 不依赖具体 WorkBuddy/Codex/Claude 名称|
|A2|至少三类 Knowledge Source 可被受控访问|
|A3|权限负向测试能阻止不应访问的知识|
|A4|同一工程 Contract 能被至少两种 Runtime 消费|
|A5|Runtime 切换不改变 Verification / Review 语义|
|A6|Host/Cross-build/HIL/Release 仍分层记录|
|A7|设备写和 Release 仍有人工 Gate|
|A8|Knowledge Provider 不被当作原始事实唯一 SSOT|
|A9|所有关键结论可追溯到 source/evidence|
|A10|Provider capability matrix 有真实 PoC evidence|

## 15. Blocker Policy

出现以下情况停止扩大范围：

- 无法确认用户/服务身份；
- Knowledge Provider 无法证明 ACL 隔离；
- Source 更新/删除/撤权无法可靠反映；
- Runtime 无法确认 repo root / exact base / dirty baseline；
- 构建或 HIL 未绑定源码/制品 identity；
- Agent 把未验证输出上推为 PASS；
- Provider 切换导致 Contract 字段或验证语义丢失；
- 高风险动作缺审批和 rollback；
- 数据边界无法被审计。

## 16. 当前待决问题

|问题|当前状态|
|---|---|
|默认 Work Item / Collaboration Provider|未冻结；飞书是重要候选|
|WorkBuddy 定位|未冻结；候选 Interaction/Office Agent Provider|
|知识 SSOT|不统一；按 Source 类型分别确定|
|默认 Knowledge Provider|未冻结；WeKnora 是候选|
|NAS 接入方式|待 Inventory + PoC|
|默认 Engineering Agent Runtime|未冻结；Codex/Claude/其他均候选|
|Agent Runtime Gateway|暂不建设，先验证 Contract 可替换|
|Context Broker|概念接受，是否产品化待 PoC|
|Action Gateway|暂不建设，沿用现有 Action Policy + 人工 Gate|
|Production Ready|禁止声明，需真实 Pilot + productionization review|

## 17. 当前状态

- 目标：已确定；
- 总体能力架构：`proposed-for-review`；
- Provider 选型：`not-frozen`；
- 知识方案：`not-frozen`；
- 嵌入式专家团：`pilot-operations-ready`；
- 真实 Pilot：待绑定/执行；
- 下一步：Architecture Review + Knowledge Inventory/PoC + Multi-runtime Pilot。
