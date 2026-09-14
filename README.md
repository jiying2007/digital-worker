# digital-worker

研发中心 AI 数字员工主仓。承载总体研发流程、专家团机器资产、共享 Contract/Schema、验证工具和内部评审资料。长期边界保持为 **R&D Operating Model / Domain Policy & Evidence Kernel**，不复制 Knowledge lifecycle、通用 Agent 资产或 Runtime Host。

## 当前权威入口

- [研发中心 AI 数字员工研发流程规划](研发中心AI数字员工研发流程规划.md)：文档版本 3；目标确定，Provider/知识方案/产品组合未冻结；
- [ADR-003：Provider-neutral AI R&D Target Architecture](docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md)：总体架构上位提案；
- [AI R&D Target Operating Model — Final Baseline](docs/strategy/ai-rd-target-operating-model.md)：长期 Operating Model；冻结 4 个稳定控制面 + N Runtime Binding + Thin Session Bootstrap、L0/L1/L2 和 exact-source-set 终态语义；
- [R0 Trust Closure](docs/strategy/r0-trust-closure.md)：当前 real Pilot 的 trust baseline；
- [Embedded Domain Closed Loop V1](docs/strategy/embedded-domain-closed-loop-v1.md)：当前阶段嵌入式落地策略基线；
- [嵌入式系统专家团机器资产](expert-groups/embedded-system/README.md)：`0.7.0 / tooling-ready / real-pilot-evidence-pending / provider-neutral`；
- [Contract Catalog](contracts/catalog.json)：本仓 authoritative Contract 的机器账本；
- [Branch Lifecycle](docs/governance/branch-lifecycle.md)：任务分支与长期分支治理；
- [真实 Pilot Runbook](docs/runbooks/embedded-pilot.md) 与 [Quickstart](docs/runbooks/embedded-closed-loop-quickstart.md)。

历史 4+N 阶段文档 [four-control-planes-runtime-bindings.md](docs/strategy/four-control-planes-runtime-bindings.md) 已被 Final Target Operating Model supersede；其核心 4+N 边界保留，但旧 monolithic bundle / `asset_bundle_hash` 语义不再作为 active identity。

## 当前阶段重点

> **当前是 iterative-development：终态 Operating Model 与 exact-source-set 机器合同已经收敛，立即转入真实 Debug / Feature / Review-Release Pilot。main 暂不要求 server-side protection，治理 strict gate 延后到 Productionization。**

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

当前 real completed run 的 trust baseline：

```text
Full 40-hex source identity
+ terminal completed evidence
+ revalidated artifact SHA-256
+ exact cross-repo checkout / contract digest
+ exact Knowledge Provider runtime identity
+ immutable ADK release / Runtime source-set / distribution identity
+ Session Bootstrap / Runtime Execution Receipt identity
+ independent Verification / Review
```

当前只推进到 E2 Engineering Closed Loop，并为 E3 Knowledge Closed Loop 建基础；不因基础设施、synthetic CI、source-set identity 或 Runtime-local PASS 声明 Production Ready。

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

## R0 Trust Closure

当前 trust/source-set hardening 已形成机器控制面：

- real `base_commit` 强制 full 40-hex SHA；
- completed/cancelled run 为 terminal；
- completed validate 每次重新计算全部 artifact SHA-256，artifact set 必须与 evidence bundle 精确一致；
- `cross-repo-lock.json` v4 绑定 exact provider/runtime commit + canonical contract digest + immutable ADK release + Codex Session Bootstrap identity；
- permanent CI 实际 fetch locked Knowledge Hub / ADK / llm_agent / Codex SHA 并核验 contract；
- ADK provider contract 与 llm_agent Runtime Pilot contract 已迁移到 exact-source-set 语义；
- Codex Runtime Binding v2 已 `SOURCE_SET_BOUND`，并实现 L0/L1/L2 Thin Session Bootstrap；
- `embedded_knowledge.py` 校验实际 Knowledge Hub checkout HEAD + contract digest；
- `contracts/catalog.json` 统一本仓 Contract authority；
- GitHub Actions 使用 full-SHA pin、最小权限、超时与 trust regression。

`main` 当前保持 unprotected 是**阶段性明确决策**，不是缺陷：`.github/repository-governance-contract.json` 将 server-side protection 标记为 `deferred-until-productionization`。默认治理审计是 advisory；Productionization 前必须运行 `python scripts/verify_repository_governance.py --strict` 并 PASS。

## 当前状态

|对象|状态|
|---|---|
|研发目标|`confirmed`|
|AI R&D Target Operating Model|`target-baseline / frozen-for-implementation`|
|R0 Trust Closure|`closed-for-iterative-pilots / strict-governance-deferred`|
|Embedded Domain Closed Loop V1|`current-stage-baseline`|
|Provider / Knowledge 选型|`not-frozen`|
|嵌入式专家团|`0.7.0 / tooling-ready / real-pilot-evidence-pending`|
|Embedded Knowledge Registry|`internal-seed / 50 entries`|
|ADK/Codex identity model|`immutable-release + exact-source-set / source-set-bound`|
|Codex Session Bootstrap|`L0/L1/L2 active / provider-identity-aware`|
|llm_agent Runtime Pilot contract|`v1.2 / exact-release-source-set-distribution identity`|
|真实 Pilot|`ready-for-real-evidence` (#6/#7/#8)|
|Knowledge PoC|open (#16)|
|Provider Capability Matrix|open (#17)|
|Multi-runtime Pilot|open (#18)|
|main server governance|`deferred-until-productionization` (#12)|
|Production Ready|**禁止声明**|

## 权威与治理规则

1. 总体架构以研发流程总纲 + ADR-003 + Final Target Operating Model 为上位边界；
2. `docs/strategy/` 规定当前阶段实施范围和退出条件，不覆盖 ADR / machine Contract；
3. `contracts/catalog.json` 只登记 digital-worker 自有 authoritative Contract，不复制外部 Provider Contract；
4. 外部 Provider/Binding 由 `config/integrations/cross-repo-lock.json` exact pin + canonical digest 管理；
5. Provider-specific 配置不得反向变成总体架构前提；
6. `main` 是否保护由 stage policy 决定：iterative-development 可暂不保护，Productionization 必须 strict governance PASS；
7. Runtime/Knowledge/AI 输出均不得自行产生 Domain Verification PASS；
8. 新跨仓合同不得重新引入 monolithic Runtime bundle 作为 universal required identity；
9. Target Baseline 描述终态方向；当前机器状态必须以 exact pin / Contract / CI / Evidence 为准。

## 下一步

1. **立即执行 #6 Debug real Pilot**：使用 Embedded Domain Closed Loop V1 + Codex L2 Session Bootstrap，形成第一条真实 terminal evidence；
2. 执行 #7 Feature real Pilot；
3. 执行 #8 Review/Release real Pilot；
4. #16 引入真实 NAS / 飞书 / CI-HIL Source，并完成至少一次真实 Knowledge reuse；
5. #18 用同一 Work/Context/Acceptance/Verification Contract 完成第二 Runtime Binding 对照；
6. 满足 #26 的 E2/Knowledge foundation 门槛后进入独立 Productionization Review；
7. **Productionization 前**配置 main server-side ruleset，并让 `Repository Governance Audit --strict` PASS。

当前阶段不再等待 main protection，不回到大架构设计阶段，也不扩大 A3-A7 自动化权限。
