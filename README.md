# digital-worker

研发中心 AI 数字员工主仓。这里维护研发工作的稳定规则：任务、专业职责、工程交接、证据、验证、审查、权限和成熟度；不把知识全文、通用能力资产或具体 Coding Runtime 再复制一套进来。

## 当前阶段

当前仓库处于 **iterative-development**。总体 Operating Model 和 exact-source-set 身份链已经具备运行基础；端侧方向正在从“嵌入式 1+7 目标组织”迁移到“端侧底座 Domain → Expert → Capability → Skill”的责任模型，同时保持现有嵌入式机器 Contract、Pilot 和可信治理不被破坏。

phase-1 shadow model 已在 `main=0977b8833c7fdcb0d11848bb713820678205a929` 闭环，fresh-main CI `34845537811` 全绿。当前进入 **phase-2 dual evaluation（双轨评测）**：旧 1+7 路由继续执行，新责任模型通过 `routing-shadow.yaml` 和 Golden Case 只读对照，明确不切 canonical routing、不扩大动作权限。

当前顺序：

```text
Edge Foundation phase-1 shadow model（已完成）
  → phase-2 旧 1+7 / 新责任模型双轨评测（当前）
  → Debug / Feature / Review-Release real Pilot evidence
  → canonical routing switch（证据充分后、另行评审）
  → legacy identity deprecation / proven removal
  → 外部知识源与真实知识复用
  → Multi-runtime 对照
  → Productionization Review
  → strict repository governance
```

当前只目标推进到 **E2 Engineering Closed Loop，并为 E3 Knowledge Closed Loop 建基础**。真实任务证据不足时，不声明 Production Ready，也不提前声明旧 1+7 已完成退役。

## 主要入口

- [研发中心 AI 数字员工研发流程规划](研发中心AI数字员工研发流程规划.md)：研发中心总体流程和 Provider-neutral 原则；
- [ADR-003：Provider-neutral AI R&D Target Architecture](docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md)：总体 Provider-neutral 架构决策；
- [ADR-004：端侧底座数字责任架构](docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md)：端侧 Domain / Expert / Capability / Skill 目标责任模型与中英术语；
- [端侧底座机器责任模型](domains/edge-foundation/domain.yaml)：三 Domain Expert、协调角色、编排/执行/可信保障边界及旧 1+7 兼容入口；
- [端侧双轨路由评测](domains/edge-foundation/routing-shadow.yaml)：14 类旧 Task 到新责任语义的 shadow mapping；仅用于评测，不改变执行路由；
- [AI R&D Target Operating Model](docs/strategy/ai-rd-target-operating-model.md)：长期 Operating Model；
- [R0 Trust Closure](docs/strategy/r0-trust-closure.md)：真实 Pilot 的可信链基线；
- [Embedded Domain Closed Loop V1](docs/strategy/embedded-domain-closed-loop-v1.md)：当前嵌入式落地策略与兼容执行面；
- [嵌入式系统兼容机器资产](expert-groups/embedded-system/README.md)：v0.7.0 的配置、Contract、Schema、Skill 和 Pilot 工具；
- [嵌入式系统核心参考](嵌入式系统专家团-核心参考/)：迁移期面向人的职责、流程、专业方法、治理和案例；
- [真实 Pilot Runbook](docs/runbooks/embedded-pilot.md) 与 [Quickstart](docs/runbooks/embedded-closed-loop-quickstart.md)；
- [Contract Catalog](contracts/catalog.json)：本仓 authoritative Contract 账本。

## 长期边界

长期模型是 **稳定责任/控制面 + N 个可替换 Runtime Binding + Thin Session Bootstrap**。具体 Provider、Agent 数量和 Runtime 拓扑不属于组织责任架构：

- `digital-worker`：Work/Run、Domain / Role / Expert / Capability / Skill 责任模型、Gate、Action Policy、工程交接、Identity/Evidence、Verification、Review、Pilot/Maturity；
- `knowledge-hub`：Knowledge Registry、authority、ACL、freshness、context/evidence 查询和知识生命周期；
- `agent-dev-kit`：通用 Agent/Skill、Asset Profile、immutable release、资产校验与回滚；
- `llm_agent`：外部实践 intake、采用/健康度观察、Runtime 对比；不进入日常 Runtime 热链；
- Runtime Binding：Codex、Claude Code、IDE/Internal Runtime、WorkBuddy 或未来其他具体执行/编排实现；
- Thin Session Bootstrap：单次会话装配 project/mode/contract/skill/provider identity，不成为新的控制面。

稳定原则：**责任（Responsibility）不等于运行时（Runtime），专家（Expert）不等于 Agent，能力域（Capability）不默认等于 Agent。**

两条链保持分离：

```text
能力演进：External Practice → llm_agent → agent-dev-kit → immutable release → Runtime Binding
任务执行：Engineer / Orchestrator → Contract → digital-worker / Knowledge Provider / ADK assets → Engineering → Verification → Review
```

## 端侧底座当前目标模型

```text
端侧底座领域（Edge Foundation Domain）
│
├─ 端侧协调角色（Edge Coordination Role，不是第四个技术专家）
├─ 结构专家（Structure Expert）
├─ 硬件专家（Hardware Expert）
└─ 嵌入式系统专家（Embedded System Expert）
     └─ 能力域（Capability）→ 原子技能（Skill）
```

现有嵌入式 `1+7` 暂时保留为 **legacy compatibility surface（旧版兼容表面）**：继续承载已运行的 Task / Gate / Skill owner / Golden Case / Pilot Contract，但不再作为端侧目标组织结构继续扩张。兼容映射在 `domains/edge-foundation/compatibility/embedded-1plus7-mapping.yaml`。

当前 `routing-shadow.yaml` 只负责双轨评测：它必须保持 `canonical_routing: false`、不得修改旧执行 route、不得扩大 A0-A7 动作权限；所有未映射 Task、未知 Capability 或无证据跨域扩展均 fail-closed（保守阻断）。

## 嵌入式当前最小闭环

每个真实 Run 至少要维持：

```text
One Work Item / Run
+ Shared Material/System Context
+ One Hypothesis Registry for Debug
+ Exact Source / Artifact Identity
+ Acceptance → Evidence
+ Knowledge Harvest
+ Knowledge Registry / Knowledge Hub refs
```

同时要求：full 40-hex source identity、terminal evidence integrity、artifact SHA-256、exact cross-repo identity、Runtime/Session identity、独立 Verification / Review。

## 当前状态

|对象|状态|
|---|---|
|AI R&D Target Operating Model|`target-baseline / frozen-for-implementation`|
|Edge Foundation Target Architecture|`ADR-004 / phase-2-dual-evaluation`|
|Edge Foundation Domain Contract|`target-v1 / canonical-responsibility-model`|
|Edge Foundation Shadow Routing|`dual-evaluation / non-canonical`|
|Embedded Domain Closed Loop V1|`compatibility-execution-baseline`|
|嵌入式 1+7 机器资产|`0.7.0 / legacy-compatibility-surface / pilot-operations-ready`|
|核心参考|`operational-reference / migration-aware`|
|Provider / Knowledge 选型|`not-frozen`|
|Embedded Knowledge Registry|`internal-seed`|
|真实 Pilot|`ready-for-real-evidence`|
|main server governance|`deferred-until-productionization`|
|Production Ready|**禁止声明**|

## 仓库治理

当前阶段 main server-side protection 明确延后到 Productionization；repository-local CI 仍必须通过。进入 Productionization 前必须配置严格 server governance，并运行：

```bash
python scripts/verify_repository_governance.py --strict
```

当前不再为失效设计保留平行“最新版/最终版”入口。历史设计由 Git history 与 ADR 提供；活动目录只保留当前 target、兼容执行面和明确的迁移状态。
