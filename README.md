# digital-worker

研发中心 AI 数字员工主仓。承载总体研发流程、专家团机器资产、共享 Contract/Schema、验证工具和内部评审资料。长期边界保持为 **R&D Operating Model / Domain Policy & Evidence Kernel**，不复制 Knowledge lifecycle、通用 Agent 资产或 Runtime Host。

## 当前权威入口

- [研发中心 AI 数字员工研发流程规划](研发中心AI数字员工研发流程规划.md)：文档版本 3；目标确定，Provider/知识方案/产品组合未冻结；
- [ADR-003：Provider-neutral AI R&D Target Architecture](docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md)：总体架构上位提案；
- [AI R&D Target Operating Model — Final Baseline](docs/strategy/ai-rd-target-operating-model.md)：当前长期 Operating Model；冻结 4 个稳定控制面 + N Runtime Binding + Thin Session Bootstrap、L0/L1/L2 和 exact-source-set 终态语义；
- [R0 Trust Closure](docs/strategy/r0-trust-closure.md)：首个真实 Pilot 接受前的可信链 Gate；
- [Embedded Domain Closed Loop V1](docs/strategy/embedded-domain-closed-loop-v1.md)：当前阶段嵌入式落地策略基线；
- [Architecture Review Readiness Pack](docs/review/)：正式架构评审前的 Pre-read、Decision Matrix、Evidence Gap、RACI 和端到端 Walkthrough；
- [ADR-001](docs/adr/ADR-001-workbuddy-codex-integration-boundary.md)：`superseded-in-part`，保留 Contract 松耦合原则；
- [ADR-002](docs/adr/ADR-002-embedded-system-expert-team-architecture.md)：1+7、Evidence-first、Verification/Review、Action Gate；
- [嵌入式系统专家团机器资产](expert-groups/embedded-system/README.md)：`0.7.0 / tooling-ready / real-pilot-evidence-pending / provider-neutral`；
- [嵌入式系统专家团-核心参考](嵌入式系统专家团-核心参考/)：`review-ready / synchronized-v0.7.0`；
- [Contract Catalog](contracts/catalog.json)：本仓 authoritative Contract 的机器账本；
- [Branch Lifecycle](docs/governance/branch-lifecycle.md)：默认只长期保留 main，任务分支由受控 Branch GC 收口；
- [真实 Pilot Runbook](docs/runbooks/embedded-pilot.md) 与 [Quickstart](docs/runbooks/embedded-closed-loop-quickstart.md)。

历史 4+N 阶段文档 [four-control-planes-runtime-bindings.md](docs/strategy/four-control-planes-runtime-bindings.md) 已被 Final Target Operating Model supersede；其核心 4+N 边界保留，但旧 monolithic bundle / `asset_bundle_hash` 语义不再作为终态前提。

## 当前阶段重点

> **终态 Operating Model 已冻结；下一步只做跨仓合同迁移、server governance 和真实 Pilot 证据，不再新增控制面。**

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

长期模型固定为 **4 个稳定控制面 + N 个可替换 Runtime Binding + Runtime 内的 Thin Session Bootstrap**：

- `digital-worker`：Work/Run、Expert、Domain Gate、Action Policy、Handoff、Identity/Evidence、Verification、Independent Review、Pilot/Maturity；
- `knowledge-hub`：Knowledge Registry/Context/Evidence/ACL/authority/freshness/lifecycle；
- `agent-dev-kit`：reusable Agent/Skill、Asset Profile、immutable release、exact-source-set handoff、asset validation/release/rollback；
- `llm_agent`：外部实践 intake/adoption、Runtime health/comparison、Loop Readiness；退出日常 Runtime 热链；
- Runtime Binding：Codex/Claude/Other 的 runtime distribution/host integration，不能拥有 Domain Verification PASS；
- Thin Session Bootstrap：只负责 project/mode/contract/skill/provider 装配，不形成第五控制面，不拥有 Gate/Verification/Knowledge/Skill SSOT。

终态同时区分两条链：

```text
能力演进链：External Practice -> llm_agent -> agent-dev-kit -> immutable release -> Runtime Binding
任务执行链：Engineer -> Runtime -> Bootstrap -> digital-worker / Knowledge Provider / ADK-derived skills -> Engineering -> Verification
```

运行等级冻结为：

- `L0 Quick Assist`：低摩擦日常辅助；
- `L1 Governed Engineering`：主要正式工程模式；
- `L2 Formal Evidence`：Real Pilot / Release / 高风险 / Multi-runtime 的完整可审计模式。

未冻结层：具体 Work Item/Interaction Provider、具体 Knowledge Provider、默认 Engineering Runtime。中央 Runtime Gateway、Context Broker Service 或大一统 Knowledge 平台不是当前前置条件，只有重复真实证据证明必要后才评审引入。

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
|ADR-003 总体能力架构|`proposed-for-review`|
|AI R&D Target Operating Model|`target-baseline / frozen-for-implementation`|
|旧 4+N strategy|`superseded-by-target-operating-model`|
|Architecture Review Pack|`review-candidate`|
|R0 Trust Closure|`implemented / live-governance-pending`|
|Embedded Domain Closed Loop V1|`current-stage-baseline`|
|Provider / Knowledge 选型|`not-frozen`|
|嵌入式专家团|`0.7.0 / tooling-ready / real-pilot-evidence-pending`|
|Embedded Knowledge Registry|`internal-seed / 50 entries`|
|核心参考|`review-ready / synchronized-v0.7.0`|
|ADK/Codex target identity model|`exact-source-set target / upstream-consumer-migration-pending`|
|真实 Pilot|`pending-contract-migration-and-real-evidence` (#6/#7/#8)|
|Knowledge PoC|open (#16)|
|Provider Capability Matrix|open (#17)|
|Multi-runtime Pilot|open (#18)|
|merged branch GC|`completed` (#19)|
|main server governance|`external-blocker` (#12 until live audit PASS)|
|Production Ready|**禁止声明**|

## 权威与治理规则

1. 总体架构以研发流程总纲 + ADR-003 + Final Target Operating Model 为上位边界；
2. `docs/strategy/` 规定当前阶段实施范围和退出条件，不覆盖 ADR / machine Contract；
3. `contracts/catalog.json` 只登记 digital-worker 自有 authoritative Contract，不复制外部 Provider Contract；
4. 外部 Provider/Binding 由 `config/integrations/cross-repo-lock.json` exact pin + canonical digest 管理；
5. 机器资产冲突按 `expert-groups/embedded-system/governance/authority-index.md` 裁决；
6. 核心参考只做解释/评审，不覆盖机器 Contract；
7. Provider-specific 配置不得反向变成总体架构前提；
8. 历史草案进 `docs/archive/`，原始输入进 `docs/source-materials/`，Brainstorm 不产生架构权威；
9. `main` 默认唯一长期分支，任务分支按 Branch Lifecycle + Branch GC 收口；
10. Runtime/Knowledge/AI 输出均不得自行产生 Domain Verification PASS；
11. 新跨仓合同不得重新引入 monolithic Runtime bundle 作为 universal required identity；
12. Target Baseline 描述终态方向；当前机器状态必须以 exact pin / Contract / CI / Evidence 为准，不能用目标文档覆盖未完成迁移。

## 下一步

1. 把 `digital-worker` 的 `asset_bundle_hash / BLOCKED_ASSET_BUNDLE_IDENTITY` 过渡语义迁移为 ADK immutable release + exact-source-set refs；
2. 同步迁移 `llm_agent` Runtime Pilot contract 的 bundle identity frozen input / hard rule；
3. promotion 兼容 ADK/Codex integration contract exact SHA + canonical digest，并跑 fresh cross-repo verification；
4. 让 live Repository Governance Audit PASS；
5. 使用 Embedded Domain Closed Loop V1 执行 #6 Debug real Pilot；
6. 执行 #7 Feature、#8 Review/Release；
7. #16 引入真实 NAS / 飞书 / CI-HIL Source 并完成至少一次真实 Knowledge reuse；
8. #18 用同一 Contract 完成第二 Runtime Binding 对照；
9. 满足 #26 的 E2/Knowledge foundation 门槛后才进入独立 Productionization Review。

在真实 PoC/Pilot evidence 出现前，不冻结唯一 WorkBuddy/WeKnora/Codex/Claude 方案，也不扩大 A3-A7 自动化权限。
