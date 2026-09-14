# digital-worker

研发中心 AI 数字员工主仓。这里维护研发工作的稳定规则：任务、专业职责、工程交接、证据、验证、审查、权限和成熟度；不把知识全文、通用能力资产或具体 Coding Runtime 再复制一套进来。

## 当前阶段

当前仓库处于 **iterative-development**。总体 Operating Model 和 exact-source-set 身份链已经具备运行基础，当前工作重点是把规则用于真实嵌入式任务，而不是继续扩架构。

当前顺序：

```text
Debug real Pilot
  → Feature real Pilot
  → Review / Release real Pilot
  → 外部知识源与真实知识复用
  → Multi-runtime 对照
  → Productionization Review
  → strict repository governance
```

当前只目标推进到 **E2 Engineering Closed Loop，并为 E3 Knowledge Closed Loop 建基础**。真实任务证据不足时，不声明 Production Ready。

## 主要入口

- [研发中心 AI 数字员工研发流程规划](研发中心AI数字员工研发流程规划.md)：研发中心总体流程和 Provider-neutral 原则；
- [ADR-003：Provider-neutral AI R&D Target Architecture](docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md)：总体架构决策；
- [AI R&D Target Operating Model](docs/strategy/ai-rd-target-operating-model.md)：长期 Operating Model；
- [R0 Trust Closure](docs/strategy/r0-trust-closure.md)：真实 Pilot 的可信链基线；
- [Embedded Domain Closed Loop V1](docs/strategy/embedded-domain-closed-loop-v1.md)：当前嵌入式落地策略；
- [嵌入式系统专家团机器资产](expert-groups/embedded-system/README.md)：v0.7.0 的配置、Contract、Schema、Skill 和 Pilot 工具；
- [嵌入式系统专家团核心参考](嵌入式系统专家团-核心参考/)：面向人的架构、流程、职责、领域方法、治理和案例；
- [嵌入式架构评审入口](嵌入式系统专家团-核心参考/00-评审入口/01%20评审说明与决策清单.md)：正式评审时的决策和证据缺口；
- [真实 Pilot Runbook](docs/runbooks/embedded-pilot.md) 与 [Quickstart](docs/runbooks/embedded-closed-loop-quickstart.md)；
- [Contract Catalog](contracts/catalog.json)：本仓 authoritative Contract 账本。

## 长期边界

长期模型是 **4 个稳定控制面 + N 个可替换 Runtime Binding + Thin Session Bootstrap**：

- `digital-worker`：Work/Run、专家职责、Domain Gate、Action Policy、工程交接、Identity/Evidence、Verification、Review、Pilot/Maturity；
- `knowledge-hub`：Knowledge Registry、authority、ACL、freshness、context/evidence 查询和知识生命周期；
- `agent-dev-kit`：通用 Agent/Skill、Asset Profile、immutable release、资产校验与回滚；
- `llm_agent`：外部实践 intake、采用/健康度观察、Runtime 对比；不进入日常 Runtime 热链；
- Runtime Binding：Codex、Claude Code、IDE/Internal Runtime 等具体执行环境；
- Thin Session Bootstrap：单次会话装配 project/mode/contract/skill/provider identity，不成为新的控制面。

两条链保持分离：

```text
能力演进：External Practice → llm_agent → agent-dev-kit → immutable release → Runtime Binding
任务执行：Engineer → Runtime → Bootstrap → digital-worker / Knowledge Provider / ADK assets → Engineering → Verification
```

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
|Embedded Domain Closed Loop V1|`current-stage-baseline`|
|嵌入式专家团|`0.7.0 / pilot-operations-ready`|
|核心参考|`operational-reference / synchronized-v0.7.0`|
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

当前不再为历史文档保留兼容入口。失效设计由 Git history 提供，活动目录只保留当前基线。
