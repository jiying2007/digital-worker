# digital-worker

研发中心 AI 数字员工主仓。承载总体研发流程、专家团机器资产、共享 Contract/Schema、验证工具和内部评审资料。长期边界保持为 **R&D Operating Model / Domain Policy & Evidence Kernel**，不复制 Knowledge lifecycle、通用 Agent 资产或 Runtime Host。

## 当前权威入口

- [研发中心 AI 数字员工研发流程规划](研发中心AI数字员工研发流程规划.md)：文档版本 3；目标确定，Provider/知识方案/产品组合未冻结；
- [ADR-003：Provider-neutral AI R&D Target Architecture](docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md)：当前总体架构上位提案；
- [4 个稳定控制面 + N 个可替换 Runtime Binding](docs/strategy/four-control-planes-runtime-bindings.md)：当前跨仓长期边界；
- [R0 Trust Closure](docs/strategy/r0-trust-closure.md)：首个真实 Pilot 接受前的可信链 Gate；
- [Embedded Domain Closed Loop V1](docs/strategy/embedded-domain-closed-loop-v1.md)：当前阶段嵌入式落地终版策略基线；
- [Architecture Review Readiness Pack](docs/review/)：正式架构评审前的 Pre-read、Decision Matrix、Evidence Gap、RACI 和端到端 Walkthrough；
- [ADR-001](docs/adr/ADR-001-workbuddy-codex-integration-boundary.md)：`superseded-in-part`，保留 Contract 松耦合原则；
- [ADR-002](docs/adr/ADR-002-embedded-system-expert-team-architecture.md)：1+7、Evidence-first、Verification/Review、Action Gate；
- [嵌入式系统专家团机器资产](expert-groups/embedded-system/README.md)：`0.7.0 / tooling-ready / real-pilot-evidence-pending / provider-neutral`；
- [嵌入式系统专家团-核心参考](嵌入式系统专家团-核心参考/)：`review-ready / synchronized-v0.7.0`；
- [Contract Catalog](contracts/catalog.json)：本仓 authoritative Contract 的机器账本；
- [Branch Lifecycle](docs/governance/branch-lifecycle.md)：默认只长期保留 main，任务分支由受控 Branch GC 收口；
- [真实 Pilot Runbook](docs/runbooks/embedded-pilot.md) 与 [Quickstart](docs/runbooks/embedded-closed-loop-quickstart.md)。

## 当前阶段重点

> **先完成 R0 Trust Closure，再形成 Embedded Domain Closed Loop 的真实工程证据；Enterprise Digital Thread 不是当前落地前置条件。**

V1 最小执行集：

```text
One Work Item / Run
+ Shared Material/System Context
+ One Hypothesis Registry for Debug
+ Exact Source / Artifact Identity
+ Acceptance -> Evidence
+ Knowledge Harvest
+ Embedded Knowledge Registry / Knowledge Hub refs
```

R0 在首个 real completed run 被接受前额外要求：

```text
Full 40-hex source identity
+ terminal completed evidence
+ revalidated artifact SHA-256
+ exact cross-repo checkout / contract digest
+ exact Knowledge Provider runtime identity
+ GitHub server-side repository governance
```

当前只推进到 E2 Engineering Closed Loop，并为 E3 Knowledge Closed Loop 建基础；不因基础设施、synthetic CI 或 Runtime-local PASS 声明 Production Ready。

## 稳定架构原则

> **Provider 可替换，Contract 稳定；Source of Truth stays at source；统一访问，不强制统一存储；Expert 与 Runtime 解耦；Runtime output 不等于 Verification PASS。**

长期模型固定为 **4 个稳定控制面 + N 个可替换 Runtime Binding**：

- `digital-worker`：Work/Run、Expert、Domain Gate、Action Policy、Handoff、Identity/Evidence、Verification、Independent Review、Pilot/Maturity；
- `knowledge-hub`：Knowledge Registry/Context/Evidence/ACL/authority/freshness/lifecycle；
- `agent-dev-kit`：reusable Agent/Skill、Asset Profile、target export、asset release/rollback；
- `llm_agent`：外部实践 intake/adoption、Runtime health/comparison、Loop Readiness；
- Runtime Binding：Codex/Claude/Other 的 runtime distribution/host integration，不能拥有 Domain Verification PASS。

未冻结层：Work Item/Interaction Provider、Knowledge Provider、默认 Engineering Runtime、未来 Context Broker/Runtime Gateway/Action Gateway。

## R0 Trust Closure

当前 trust hardening 已形成机器控制面：

- real `base_commit` 强制 full 40-hex SHA；
- completed/cancelled run 为 terminal；
- completed validate 每次重新计算全部 artifact SHA-256，artifact set 必须与 evidence bundle 精确一致；
- `cross-repo-lock.json` v3 绑定 exact commit + contract canonical SHA-256；
- permanent CI 实际 fetch locked Knowledge Hub / ADK / llm_agent / Codex SHA 并核验 contract；
- `embedded_knowledge.py` 校验实际 Knowledge Hub checkout HEAD + contract digest；
- `contracts/catalog.json` 统一本仓 Contract authority；
- GitHub Actions 使用 full-SHA pin、最小权限、超时与 trust regression。

GitHub live `main` server governance 仍必须由具有 repository administration 权限的主体配置并通过 `Repository Governance Audit`；仓库内 CI 不能替代 server-side enforcement。该项在 live audit PASS 前是 external blocker，不得伪造完成。

## 仓库结构

```text
digital-worker/
├── README.md
├── 研发中心AI数字员工研发流程规划.md
├── docs/
│   ├── adr/
│   ├── strategy/
│   ├── review/
│   ├── governance/
│   ├── brainstorm/
│   ├── archive/
│   ├── runbooks/
│   └── source-materials/
├── expert-groups/embedded-system/
│   └── knowledge/
├── config/integrations/
├── contracts/
│   ├── catalog.json
│   └── cross-repo/
├── schemas/
├── scripts/
├── tests/
├── 产品专家团-核心参考/
└── 嵌入式系统专家团-核心参考/
```

## 当前状态

|对象|状态|
|---|---|
|研发目标|`confirmed`|
|总体能力架构|`proposed-for-review`|
|4+N 控制面边界|`current-stage-baseline`|
|Architecture Review Pack|`review-candidate`|
|R0 Trust Closure|`implemented / live-governance-pending`|
|Embedded Domain Closed Loop V1|`current-stage-baseline`|
|Provider / Knowledge 选型|`not-frozen`|
|嵌入式专家团|`0.7.0 / tooling-ready / real-pilot-evidence-pending`|
|Embedded Knowledge Registry|`internal-seed / 50 entries`|
|核心参考|`review-ready / synchronized-v0.7.0`|
|真实 Pilot|`pending-real-binding` (#6/#7/#8)|
|Knowledge PoC|open (#16)|
|Provider Capability Matrix|open (#17)|
|Multi-runtime Pilot|open (#18)|
|merged branch GC|`completed` (#19)|
|main server governance|`external-blocker` (#12 until live audit PASS)|
|Production Ready|**禁止声明**|

## 权威与治理规则

1. 总体架构以研发流程总纲 + ADR-003 + 4+N strategy 为上位边界；
2. `docs/strategy/` 规定当前阶段实施范围和退出条件，不覆盖 ADR / machine Contract；
3. `contracts/catalog.json` 只登记 digital-worker 自有 authoritative Contract，不复制外部 Provider Contract；
4. 外部 Provider/Binding 由 `config/integrations/cross-repo-lock.json` exact pin + canonical digest 管理；
5. 机器资产冲突按 `expert-groups/embedded-system/governance/authority-index.md` 裁决；
6. 核心参考只做解释/评审，不覆盖机器 Contract；
7. Provider-specific 配置不得反向变成总体架构前提；
8. 历史草案进 `docs/archive/`，原始输入进 `docs/source-materials/`，Brainstorm 不产生架构权威；
9. `main` 默认唯一长期分支，任务分支按 Branch Lifecycle + Branch GC 收口；
10. Runtime/Knowledge/AI 输出均不得自行产生 Domain Verification PASS。

## 下一步

1. R0 仓内/跨仓可信链已闭合；下一唯一 R0 blocker 是让 live Repository Governance Audit PASS；
2. Codex 参与正式执行前闭合 ADK provider-produced bundle identity + Codex consumer identity；
3. 使用 Embedded Domain Closed Loop V1 执行 #6 Debug real Pilot；
4. 执行 #7 Feature、#8 Review/Release；
5. #16 引入真实 NAS / 飞书 / CI-HIL Source 并完成至少一次真实 Knowledge reuse；
6. #18 用同一 Contract 完成第二 Runtime Binding 对照；
7. 满足 #26 的 E2/Knowledge foundation 门槛后才进入独立 Productionization Review。

在真实 PoC/Pilot evidence 出现前，不冻结唯一 WorkBuddy/WeKnora/Codex/Claude 方案，也不扩大 A3-A7 自动化权限。
