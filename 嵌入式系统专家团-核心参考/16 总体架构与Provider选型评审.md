# 16 总体架构与 Provider 选型评审

> 本文用于研发中心内部架构评审。
>
> 上位决策：`docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md`
>
> 结论状态：`proposed-for-review`

## 1. 为什么现在要重新审

前一版讨论容易把以下产品组合误认为已经确定：

```text
飞书 -> WorkBuddy -> WeKnora -> Codex
```

当前真实情况是：

- 目标明确：效率、质量、知识复用、安全审计；
- 飞书/飞书知识库是现有或重要候选协作能力；
- 部分重要资料长期存在 NAS；
- WeKnora 只是候选 Knowledge Provider；
- 研发人员可能使用 Codex、Claude Code、IDE Agent 或其他 Agent；
- 总体产品组合、知识库方案、默认 Runtime 都没有完成正式选型。

因此本次评审应先拍板**架构原则和 PoC 方法**，而不是拍板产品品牌。

## 2. 必须分开的五类东西

|类别|问题|示例|
|---|---|---|
|Interaction Provider|人从哪里进入 AI/流程|飞书、WorkBuddy、Web、IDE、CLI|
|Work Item Provider|任务 ID、状态、审批放在哪里|飞书/研发项目系统/其他|
|Knowledge Source|事实原文在哪里|飞书文档、NAS、Git、CI/HIL、Artifact Store|
|Knowledge Provider|如何索引/检索/组装知识|WeKnora、其他 RAG/Search、直接 Adapter|
|Engineering Agent Runtime|谁辅助分析/改代码/执行|Codex、Claude Code、IDE Agent、内部 Agent|

任何一个产品都不应该同时因为“功能多”就自动获得五类职责。

## 3. 建议的目标架构

```text
               User / Engineer / Reviewer
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
    Feishu           WorkBuddy          IDE / CLI
       └─────────────────┼─────────────────┘
                         ▼
                  Work Item Contract
                         │
                         ▼
                    digital-worker
          Expert / Routing / Gate / Policy
                         │
        ┌────────────────┼──────────────────┐
        ▼                ▼                  ▼
 Context & Knowledge  Agent Runtime     Action/Execution
        │                │                  │
 Registry/Gateway     Codex/Claude       Git/CI/HIL
 Context Broker       Other Agent        Device/Artifact
        │                                   │
        └──── Feishu / NAS / Git / CI/HIL ──┘
                         │
                 Evidence / Identity / Audit
```

核心不是中间画一个“大平台”，而是定义清楚每层的输入/输出、身份、权限和权威事实。

## 4. Knowledge 方案头脑风暴

### 方案 K1：单一集中知识库

所有材料同步或迁移到一个 Knowledge Platform。

优点：
- Agent 接口最简单；
- 统一检索和运营；
- Demo 快。

风险：
- NAS/Git/CI/HIL 的版本和权限容易变成副本；
- 原始资料量大时同步和更新成本高；
- “索引成功”不等于“权威、新鲜、可访问”；
- Provider 锁定明显。

当前建议：**不作为默认架构。**

### 方案 K2：纯联邦直连

Agent 分别访问飞书、NAS、Git、CI/HIL，不建立统一知识索引。

优点：
- 权威源清楚；
- 不复制数据；
- 权限更贴近源系统。

风险：
- Agent 工具数量多；
- 跨源检索和排序困难；
- 每个 Agent Runtime 都要理解很多 Provider API。

当前建议：可作为最小基线，但长期可用性一般。

### 方案 K3：混合 / Federated + Index

Source 保留权威；允许统一 Provider 为部分内容建索引，同时保留直接 Source Adapter。

示例：

```text
Feishu Docs ───────┐
NAS Docs ──────────┼──> optional index / search provider
Git Docs ──────────┤
                   │
Git Source ────────┤──> direct exact read
CI/HIL ────────────┤──> direct evidence read
Artifact Store ────┘──> identity/hash read
```

优点：
- 检索体验和权威边界平衡；
- 可逐步索引；
- 可以替换 Knowledge Provider。

风险：
- 需要 Registry/Gateway 处理 source/version/ACL；
- 设计稍复杂。

当前建议：**首选 PoC 方向。**

### 方案 K4：Context Broker 驱动

在 K3 上再增加任务级上下文组装：

```text
work_item + identity + repo/platform
             │
             ▼
       Context Broker
             │
   minimal context package
             │
       Engineering Agent
```

优点：
- 减少 Token / 噪声；
- 限制权限范围；
- 跨 Runtime 复用上下文包。

风险：
- Broker 规则本身需要维护；
- 过早建设可能复杂度高于收益。

当前建议：先定义接口思想，**PoC 后再决定是否产品化**。

## 5. NAS 应如何定位

NAS 不应简单等价于“待搬迁知识库”。建议至少拆成三类：

### A. 静态/半静态工程文档

例如 Datasheet、TRM、SDK Guide、供应商规格、认证资料。

适合：
- 注册到 Knowledge Registry；
- 可选择被 RAG/搜索系统索引；
- 保留原路径、版本和 owner。

### B. 强版本工程资产

例如 SDK/BSP 源码包、firmware、config、build output。

适合：
- exact ref/hash 读取；
- 不依赖 embedding 作为权威；
- 能迁到 Git/Artifact Store 的应优先使用更适合的工程系统。

### C. 历史项目/杂项资料

先 Inventory，再决定：
- 保留；
- 归档；
- 规范化；
- 建索引；
- 删除重复/过期资料。

不要直接对整个 NAS 做“大规模向量化”作为第一步。

## 6. Agent Runtime 方案头脑风暴

### R1：统一一个 Coding Agent

优点：治理简单。

风险：单 Provider 锁定，且不同任务类型的模型/工具适配未必相同。

### R2：工程师自由选 Agent，无统一 Contract

优点：灵活。

风险：输出格式、证据、权限、审计和验证完全碎片化。

### R3：多 Runtime + 统一 Contract

```text
engineering-task-package
        │
 ┌──────┼──────┐
 ▼      ▼      ▼
Codex Claude  Other
 │      │       │
 └──────┼───────┘
        ▼
delivery-receipt + evidence
```

优点：
- 保留工程师选择；
- 可以通过真实指标选默认 Runtime；
- Runtime 替换不会推翻 Expert Team。

风险：
- 需要 adapter/runbook；
- 不同 Runtime 的 Contract adherence 要评测。

当前建议：**R3。**

## 7. WorkBuddy 的合理候选定位

本轮不把 WorkBuddy 定义为中央大脑。

它可以 PoC 的角色包括：

- 办公 AI 入口；
- task-brief 草稿生成；
- 结果/风险摘要；
- Work Item 状态辅助；
- Knowledge Gateway 客户端；
- 审批/通知入口。

不建议默认赋予：

- 开发机全局 Shell；
- 任意 Git write；
- A6 Device Write；
- A7 Release；
- 所有知识的管理员级访问。

## 8. 飞书的合理候选定位

可以分别讨论，不要一次绑定：

1. Collaboration Provider；
2. Work Item Provider；
3. Human Knowledge Source；
4. Approval/Notification Provider。

这四个角色可以全部由飞书承担，也可以只承担一部分。评审时应分别给证据，而不是一句“公司用飞书，所以全放飞书”。

## 9. WeKnora 的合理候选定位

PoC 时重点验证：

- 多 Source ingestion/adapter 能力；
- 权限/ACL 映射；
- source citation；
- update/delete/revoke；
- NAS 文档处理；
- Git/Markdown 接入；
- 检索质量；
- API/Agent 接入；
- 运维与数据边界。

PoC 通过后，可以成为默认 Knowledge Provider；仍不应自动替代所有 Source of Truth。

## 10. Provider Capability Matrix 模板

|Capability|Required?|Provider A|Provider B|Evidence|
|---|---|---|---|---|
|Stable work item ID|Y||||
|Identity / SSO|Y||||
|ACL negative test|Y||||
|NAS source access|Y||||
|Feishu source access|Y||||
|Git exact read|Y||||
|Citation/provenance|Y||||
|Update/delete propagation|Y||||
|Engineering task contract|Y||||
|Delivery receipt|Y||||
|Cancel/recovery|Y||||
|Audit log|Y||||
|Cost/latency|Y||||

没有 PoC evidence 的格子不能用产品宣传或主观印象填 PASS。

## 11. 建议首轮 PoC

### PoC 1：Knowledge

固定 20~50 个真实问题，覆盖：
- 芯片资料；
- 历史 Bug/RCA；
- 项目规范；
- 代码相关文档；
- 权限敏感资料。

比较不同方案的 Recall、citation、权限负向、时效和延迟。

### PoC 2：Multi-runtime Engineering

挑同一个边界清晰的真实任务：
- 同 task-brief；
- 同 repo/base；
- 同上下文；
- 同 acceptance；
- 分别使用两个 Runtime；
- 独立 Verification/Review。

不要用“谁写代码更多”评判，重点比较：
- 正确性；
- Unsupported Claim；
- Evidence；
- 人工修正；
- 运行恢复；
- 成本/耗时。

### PoC 3：Work Item / Interaction

验证从入口创建/补齐 task-brief，到 delivery/evidence 回填的最小闭环。

## 12. 当前建议决策

建议本次内部评审先接受：

1. Provider-neutral 总体架构；
2. Source-of-Truth-stays-at-source；
3. Knowledge Source / Provider 分离；
4. 多 Engineering Agent Runtime + 统一 Contract；
5. WorkBuddy/飞书/WeKnora/Codex/Claude 都先作为候选，不写死；
6. Knowledge Gateway 概念接受，具体实现待 PoC；
7. Context Broker 概念接受，但暂不建设产品；
8. A0-A7、Evidence、Verification、Independent Review 不因 Provider 变化而放宽。

## 13. 不建议现在拍板的事项

- 企业唯一 Knowledge Provider；
- 唯一 Coding Agent；
- 是否全量同步 NAS；
- 是否 WorkBuddy 直接控制开发机；
- 是否建设统一 Runtime Gateway；
- 是否建设 Context Broker 服务；
- 是否将飞书定为所有知识唯一主库。

这些应由 Inventory + PoC evidence 决定。

## 14. 会议建议输出

内部评审至少形成以下 Decision List：

|Decision|Owner|Target date|Evidence required|
|---|---|---|---|
|接受/修改 ADR-003 原则||||
|Knowledge Source Inventory owner||||
|Knowledge PoC 候选方案||||
|首批 Runtime 对比对象||||
|Work Item Provider PoC||||
|身份/ACL 负责人||||
|NAS 治理负责人||||
|真实 Pilot 任务||||

评审完成前，总体产品栈继续保持 `not-frozen`。
