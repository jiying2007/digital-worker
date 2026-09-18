# digital-worker

研发中心 AI 数字员工主仓。这里维护稳定的责任、任务、工程交接、证据、验证、审查、权限和成熟度规则；不复制知识全文、通用 Agent 资产或具体 Coding Runtime。

## 当前阶段

仓库处于 **iterative-development**，但 Edge Foundation 的架构与运行时迁移已经进入终态：

```text
Domain（领域）
  → Expert（专家）
    → Capability（能力域）
      → Skill（技能）
```

端侧底座领域固定为 **Structure Expert / Hardware Expert / Embedded System Expert** 三个 Domain Expert；Edge Coordination 是 Role，不是第四个 Expert。Verification / Independent Review 属于 Assurance，不属于 Embedded 专业能力。

**Canonical routing 已由 Edge Foundation target runtime 承担。旧嵌入式 1+7 compatibility tree、静态身份 mapping、shadow routing 与迁移期 switch machinery 已物理退役。** 当前活动执行面只读取 `domains/edge-foundation/**`；CI 通过 `zero-live-legacy-reference` 永久阻止旧路径回归。

这不等于产品成熟度已经完成。**Product readiness 与 routing authority 已解耦**：

| Track | 当前状态 | 主要剩余项 |
|---|---|---|
| Debug | BLOCKED | PCR02/SSC305 产品源码 exact 40-hex SHA、原始 UBI/UBIFS 日志或复现、device/flash/partition/kernel/test identity、Verification |
| Feature | DONE / eligible | `FEATURE-PCR02-OTA-001` 已完成真实 Engineering、Verification、frozen evidence 与 canonical Pilot receipt |
| Review / Release | BLOCKED | PCR02 实机 OTA install/boot/resulting-version/rollback-or-scope-exemption、Device/HIL Verification、实际发布时 A7 human decision |

因此当前 **Product readiness = 1/3 eligible，仍为 BLOCKED**。Synthetic evidence 只验证工具链，不计入产品成熟度；Product readiness 不会切换、回滚或决定 canonical routing，也不能自动声明 Production Ready / Release Ready。

Product Readiness 只描述具体产品证据轨；它与 cross-repo Terminal Maturity、Runtime Qualification、ADK Release Qualification 相互正交，任何一项 PASS/READY 都不得自动提升另一项状态。

当前目标仍是 **E2 Engineering Closed Loop，并为 E3 Knowledge Closed Loop 建基础**。

## 主要入口

- [研发中心 AI 数字员工研发流程规划](研发中心AI数字员工研发流程规划.md)：研发中心总体流程和 Provider-neutral 原则；
- [ADR-003：Provider-neutral AI R&D Target Architecture](docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md)：总体 Provider-neutral 架构决策；
- [ADR-004：端侧底座数字责任架构](docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md)：端侧责任模型与中英术语；
- [ADR-005：跨仓语义所有权、执行身份与证据联邦](docs/adr/ADR-005-cross-repo-semantic-ownership-and-evidence-federation.md)：跨仓 semantic ownership、identity、evidence 与 decision 边界；
- [Cross-Repo Terminal Maturity Landing](docs/strategy/cross-repo-terminal-maturity-landing.md)：跨仓终态成熟落地与验收基线；
- [Edge Foundation Domain](domains/edge-foundation/domain.yaml)：三 Domain Expert、Coordination、Execution、Assurance 与 Product readiness 边界；
- [Canonical Routing](domains/edge-foundation/routing.yaml)：14 个任务类型到 Expert / Capability / Assurance 的正式路由；
- [Runtime Policy](domains/edge-foundation/runtime/task-modes.yaml)：具体 workflow mode 与 execution 约束；
- [当前机器 Review Snapshot](嵌入式系统专家团-核心参考/00-评审导览/03%20当前机器状态快照.md)：从 canonical 资产派生的当前静态事实汇总，不替代 Product/Runtime/Productionization evaluator；
- [SKILLS — Skill Architecture, Plan & Review Index](SKILLS.md)：仓库级 reviewer-facing Skill 总入口，覆盖 23 个 canonical Skill、candidate、生命周期与证据成熟度；
- [Skill Registry](domains/edge-foundation/skills.yaml)：23 个 target Skill 的 canonical ownership 与物理位置；
- [Skill 规划清单与定义规范](嵌入式系统专家团-核心参考/05-工程交付/04%20Skill规划清单与定义规范.md)：reviewer-facing Skill taxonomy、定义模板、候选规划池与新增/拆分规则；
- [Skill 评审成熟度台账](嵌入式系统专家团-核心参考/05-工程交付/06%20Skill评审成熟度台账.md)：逐 Skill 区分 DEFINED / evaluation / real usage / portability，不把文档完整度冒充工程成熟度；
- [Skill Invocation Receipt Contract](schemas/skill-invocation-receipt.v1.schema.json)：Runtime/evaluation-owned Skill usage provenance，可由 Pilot 校验并冻结进 evidence bundle；
- [Skill Evaluation Plan](domains/edge-foundation/evaluation/skill-evaluation-plan.yaml)：23 个 Skill 的 46 个 positive + BLOCK 场景，只定义评测要求、不等于成熟度证据；
- [Skill Evaluation Receipt](schemas/skill-evaluation-receipt.v1.schema.json) / [Summary](schemas/skill-evaluation-summary.v1.schema.json)：绑定 invocation、独立语义评测与正负 case 聚合，只有完整 pair 才可形成 `EVALUATED` 证据；
- [Skill 评测与证据闭环](嵌入式系统专家团-核心参考/05-工程交付/07%20Skill评测与证据闭环.md)：评审人员从 case plan 一路追到 EVALUATED、真实 PILOTED 与跨 Runtime portability 的阅读入口；
- [Golden Cases](domains/edge-foundation/evaluation/golden-cases.yaml)：12 个目标评测案例；
- [Knowledge Registry](domains/edge-foundation/knowledge/registry.yaml)：本地 bootstrap 知识入口，Source of Truth 仍留在原处；
- `scripts/embedded_pilot.py` / `scripts/edge_pilot.py`：canonical Pilot CLI；
- `scripts/evaluate_edge_foundation_pilot.py`：生成 canonical Pilot receipt；
- `scripts/evaluate_edge_foundation_product_readiness.py`：聚合三轨真实 evidence，只判断 Product readiness；
- [Embedded Domain Closed Loop V1](docs/strategy/embedded-domain-closed-loop-v1.md)；
- [嵌入式核心参考](嵌入式系统专家团-核心参考/)；
- [真实 Pilot Runbook](docs/runbooks/embedded-pilot.md) 与 [Quickstart](docs/runbooks/embedded-closed-loop-quickstart.md)；
- [Contract Catalog](contracts/catalog.json)。

## 长期边界

稳定模型是 **责任/控制面稳定 + Runtime 可替换 + Thin Session Bootstrap**：

- `digital-worker`：Domain / Role / Expert / Capability / Skill、Work/Run、Gate、Action Policy、Engineering handoff、Identity/Evidence、Verification/Review Contract、Pilot/Product readiness；
- `knowledge-hub`：Knowledge Registry、authority、ACL、freshness、context/evidence 查询与知识生命周期；
- `agent-dev-kit`：通用 Agent/Skill、Asset Profile、immutable release、资产校验与回滚；
- `llm_agent`：外部实践 intake、采用/健康度观察、Runtime 对比；
- Runtime Binding：Codex、Claude Code、IDE/Internal Engineering Runtime 或未来其他满足 Runtime Binding Contract 的实现；
- Interaction Provider：WorkBuddy、飞书、Web、CLI/IDE 入口或未来其它协作入口；Interaction Provider 不因“能发起任务”自动成为 Engineering Runtime Binding；
- Thin Session Bootstrap：单次会话装配 project/mode/contract/skill/provider identity，不成为新的控制面。

稳定原则：**Responsibility ≠ Runtime；Expert ≠ Agent；Capability 不默认等于 Agent；Knowledge index 不替代 authoritative Source；Product readiness 不决定 routing authority；Governance escalation 不提升既有 evidence 等级；Product Readiness / Terminal Maturity / Runtime Qualification / ADK Qualification 互不继承。**

## 真实 Run 最小闭环

```text
One Work Item / Run
+ Shared Material/System Context
+ Exact Source / Artifact Identity
+ Acceptance → Evidence
+ Engineering Delivery
+ Verification
+ Review when required/available by current-stage policy
+ Knowledge Harvest
```

Debug 另外要求共享 Hypothesis Registry。Material Manifest 在 `planned/running/blocked` 可诚实保持 `BLOCKED`；进入 `complete` 前必须为 `READY` 或经明确批准的 `DEGRADED`。completed run 会重新校验终态材料与 frozen evidence bundle，禁止通过“文件存在”推导材料已充分。

当任务从较低治理等级升级到更高等级（特别是 L1 → L2 Formal Evidence）时，必须重新解析 exact Digital Worker / Knowledge / ADK / Runtime / project identities 并重新冻结 Execution Source Set；升级前的 session/context 可保留为 prior observation/hypothesis，但不得自动提升为 Formal Evidence。

## 仓库治理

当前 main server-side protection 仍延后到 Productionization；repository-local CI 必须持续通过。进入 Productionization 前运行：

```bash
python scripts/verify_repository_governance.py --strict
```

活动目录只保留 canonical target、产品证据与长期治理 Contract。历史迁移方案由 Git history 与 ADR 保存，不在活动执行面维护第二套兼容架构。
