# Cross-Repo Terminal Maturity Landing — 终态成熟落地方案

- Status: `active / implementation-baseline`
- Date: 2026-09-15
- Last reviewed: 2026-09-15
- Architecture authority: `../adr/ADR-003-provider-neutral-ai-rd-target-architecture.md`
- Semantic ownership authority: `../adr/ADR-005-cross-repo-semantic-ownership-and-evidence-federation.md`
- Domain architecture: `../adr/ADR-004-edge-foundation-digital-responsibility-architecture.md`
- Operating model: `ai-rd-target-operating-model.md`
- Trust baseline: `r0-trust-closure.md`
- Machine baseline: `../../contracts/cross-repo/embedded-ai-operating-system.yaml`
- Identity spine: `../../contracts/cross-repo/identity-envelope.yaml`

## 1. 目标

本方案把 `digital-worker`、`knowledge-hub`、`agent-dev-kit`、`llm_agent`、`codex` 与 Codex Safe Family 从“架构边界已清晰”推进到“真实任务可重复运行、证据可追溯、Provider 可替换、长期运维可持续”的成熟状态。

终态不是把所有仓合并成一个平台，也不是要求所有任务走固定流水线，而是做到：

1. 每类语义只有一个 canonical owner；
2. 每次 Formal Run 有可重放的 exact identity spine，并能精确回答“按哪一版 Digital Worker Domain/Governance 语义执行”；
3. source facts、provider receipts、verification/review reports、qualification 与 run-specific decision 不混层；
4. Runtime / Assurance / Knowledge Provider 可以在不改变 Domain semantics 的前提下替换；Interaction Provider 的“可替换”若要宣称为已实证，也必须有真实第二入口证据；
5. `llm_agent` 只影响下一代能力演进，不阻塞日常生产链；
6. 真实 Debug / Feature / Release / Evolution evidence 能长期被机器和人复核；
7. 缺关键 identity/evidence 时 fail-closed，不以 synthetic evidence 或“文件存在”冒充成熟；
8. 同一系统可以产生不同 authority/evidence kind 的 artifact，分类以 artifact 为粒度，而不是由 producer 名称推断；
9. L0/L1 → L2 等治理升级会重新冻结 exact identities / Source Set，旧 session/context 不会自动升级为 Formal Evidence；
10. Verification / Review decision 能精确绑定被审查候选、Execution Source Set、actor identity 与 supersession provenance；
11. Product Readiness、Terminal Maturity、Runtime/ADK/Knowledge Provider Qualification 分别评估、互不继承。

## 2. 成熟度定义

本方案区分六个独立成熟轴，不再使用一个模糊的“已完成”覆盖全部状态。

| 轴 | 终态要求 |
| --- | --- |
| Architecture | ADR / semantic ownership / dependency direction 稳定，无第二控制面和 legacy live path |
| Identity | Work、Digital Worker Domain/Governance、Knowledge、ADK、Runtime、Engineering、Artifact、Device、Verification/Review subject 均可 exact trace |
| Delivery | 代表性工程任务可从 intake 到 closure 重放；L1→L2 等升级不会依赖旧 session 隐式补链 |
| Assurance | Fact / Receipt / Report / Qualification 分层稳定，Decision Authority 正交，Verifier/Reviewer 独立性与 decision provenance 有证据 |
| Replaceability | R1 Binding conformance 是稳定日常基线；R2 作为周期性真实 Runtime qualification 独立维护，fresh evidence 只约束 replaceability claim，不阻塞其它成熟轴 |
| Operations | repository governance、release、rollback、drift、freshness、knowledge lifecycle、owner 机制长期可运营 |

任何单轴未闭环时，只能声明对应轴已成熟，不得声明整体 terminal maturity。

此外，以下状态不属于六轴的自动派生物：

```text
Product Readiness
Runtime Qualification
ADK Release Qualification
Knowledge Provider Qualification
```

它们可以作为某些 maturity 判断的 evidence/constraint，但不得自动提升整体 terminal maturity；反向也同样禁止。

## 3. 不做的事情

本阶段明确不做：

- 不合并六个仓；
- 不新增中央 Agent Gateway / Context Broker Service / Runtime Server；
- 不建立全局 Domain Skill ↔ ADK Skill 一一映射；
- 不把 Knowledge Hub 变成 Git/CI/HIL/Device 的事实副本；
- 不把 Codex Safe 变成强制 Assurance authority；
- 不让 `llm_agent` 进入 Formal Run 热路径；
- 不为尚无真实 consumer 的接口预建兼容层；
- 不为了“统一”复制 Skill、Workflow、Profile、Gate 或 Evidence 到多个仓；
- 不通过破坏性重命名 `four-control-planes-plus-replaceable-runtime-bindings` 来解决文档术语问题；现有 machine baseline 兼容保留，后续只增加向后兼容的 responsibility/semantic ownership 标记；
- 不把 fake/controlled adapter 的通过结果包装成真实 Provider substitution evidence；
- 不把 L1/current-provider session/context 原样包装成 L2 Formal Evidence；
- 不把 Product Readiness、Runtime/ADK/Knowledge Qualification 或局部 PASS 解释为 Terminal Maturity；
- 不让 Verification/Review report 静默跟随“最新 commit/patch”而失去 exact reviewed subject。

## 4. 终态生产链

Formal Engineering Delivery Loop：

```text
Intent / Work Item
    ↓
Digital Worker task / domain / policy / acceptance
    ↓
Context resolution
  ├─ Digital Worker exact governance refs
  ├─ Knowledge Hub refs / authority / freshness
  ├─ Project source identity
  └─ Material / system context
    ↓
Capability selection
  ├─ Digital Worker Domain Skill
  └─ optional ADK reusable assets / Asset Profile
    ↓
Exact Execution Source Set
    ↓
Runtime Binding
    ↓
Engineering Action
    ↓
Git / CI / HIL / Device / Artifact facts
    ↓
Assurance Provider receipts when required
    ↓
Independent Verification bound to exact subject/source set
    ↓
Independent Review when required, also bound to exact subject/source set
    ↓
Decision / Qualification / Closure
    ↓
Knowledge Candidate
    ↓
Knowledge Hub lifecycle / promotion
```

`llm_agent` 不出现在这条必经链路中。

注意：CI/HIL 等系统可以同时承担“产生原始 fact”和“执行 assurance step”的角色，但每个具体 artifact 必须显式区分 `authority_kind` / `evidence_layer`，不能因为 producer 相同就混层。

## 5. 能力演进链

Capability Evolution Loop：

```text
External Practice / New Runtime / Failures / Real Usage Evidence
    ↓
llm_agent evaluate / compare / recommend
    ↓
semantic ownership routing
    ├─ digital-worker: domain semantics / workflow / policy
    ├─ knowledge-hub: knowledge governance / retrieval contract
    ├─ agent-dev-kit: reusable agent assets
    ├─ runtime binding: runtime-specific capability
    └─ assurance provider: provider-specific capability
    ↓
owner-side validation / acceptance / reject / observe
    ↓
release / promotion
    ↓
real adoption evidence
```

`llm_agent Recommendation ≠ Adoption Decision` 是永久不变量。

## 6. Governance Escalation / Evidence Boundary

Risk-based Progressive Orchestration 允许任务在运行中升级治理等级，但治理升级本身不改变已有 evidence 的等级。

特别是 L1 → L2：

```text
L1 current-provider session
    ↓ escalation decision
re-resolve exact Digital Worker governance
    ↓
re-resolve exact-pinned Knowledge / rebuild context
    ↓
freeze ADK release/assets
    ↓
freeze Runtime Binding/profile/host
    ↓
freeze project source / dirty baseline
    ↓
new exact Execution Source Set
    ↓
Formal Evidence begins here
```

升级前的内容只允许作为 prior observation / hypothesis / provisional context。若某条旧信息 materially used 于 L2 decision，必须重新从对应 authority 解析/引用并进入新的 frozen Source Set。

退出条件：至少一个真实 L1→L2 任务证明旧 session/context 不会自动 promotion，并能生成新的 source-set/bootstrap provenance。

## 7. Decision Provenance / Exact Reviewed Subject

Formal Verification / Review 的判定对象必须不可歧义。

终态需要至少表达：

```text
report_id
run_id
execution_source_set_ref
exact reviewed result/source identity
decision_actor_identity_ref
independence evidence
input evidence refs
report sequence
supersedes / previous-report-ref when rerun
```

若同一 Run 在 Verification 后产生新的 result commit/patch/source set，则旧 report 保留历史 provenance，不得被解释为对新结果仍然有效；必须产生新的报告或显式 supersession。

Delivery Receipt 的 `validation` 只属于 Engineering self-validation / execution observation；`decisions` 只属于 implementation/engineering decisions，不得被视为 Independent Verification / Review / Qualification / A7 approval。

退出条件：至少一个 Feature 或 Release Pilot 中发生“修复后复核”，并能够机器区分 old report 与 new reviewed subject。

## 8. 落地阶段

### 阶段 0：语义与活动面冻结

目标：停止继续产生第二架构、第二 SSOT、第二命名体系。

必须完成：

- ADR-003 / ADR-004 / ADR-005 形成稳定优先级；
- Repository Responsibility Map 在文档入口可发现；
- legacy 1+7、shadow routing、migration switch 等已退役 surface 不回到活动执行面；
- 同名对象在文档和机器 contract 中明确 Domain / Reusable / Runtime 语义；
- 新增 cross-repo 资产必须声明 canonical owner；
- 不再创建 `_final/_v2` 平行活动文档；
- 现有 machine baseline 的 `architecture_model` / `planes` 明确被解释为 repository responsibility projection，而不是新一套 architecture-plane authority；机器契约后续自然演进时只补兼容元数据，不做无收益破坏性改名；
- frozen docs 中的 Runtime/Profile/Provider 示例必须服从 canonical owner，不保留已退役 selector/profile 名称作为活动示例；
- Interaction Provider 与 Engineering Runtime Binding 的概念边界明确，WorkBuddy/飞书等不因能发起任务就自动成为 Runtime Binding。

退出条件：

- 新任务不需要通过口头解释判断“哪个仓说了算”；
- 任意一个 Skill / Workflow / Profile / Gate / Evidence 对象能明确回答 semantic kind 与 owner；
- 任意一个关键 artifact 能明确回答 producer/source、semantic owner、authority kind，以及适用时的 evidence layer；
- canonical-reference 检查不会让已退役 Runtime/Profile/Provider 例子在 frozen docs 中长期漂移。

### 阶段 1：Identity Spine / Source Set 闭环

目标：任何 Formal Run 都能回答“这次到底用了什么、按哪一版规则执行、验证的是哪个精确对象”。

必须具备：

- `work_item_id` / `run_id`；
- **exact Digital Worker Domain/Governance identity**：provider commit、contract/catalog identity/digest、selected Domain/routing refs、materially-used Domain Skill refs/digests；
- exact project source/base/result identity；
- Knowledge provider identity + context/evidence fingerprint；
- immutable ADK release identity；
- selected ADK asset/profile refs；
- exact Runtime Binding repository/commit/target/profile/host；
- runtime source-set / distribution / session-bootstrap / execution receipt refs；
- build/artifact/device/test identity；
- verification/review report refs、exact reviewed subject、actor identity 与 supersession provenance。

实施原则：

- 优先扩展现有 `identity-envelope` / source-set refs；
- Digital Worker identity 只保存 exact ref/digest，不复制 Domain Contract 正文形成第二 SSOT；
- Verification/Review 只保存 identity/provenance/ref，不把原始 evidence 复制进第二 SSOT；
- 没有真实需求时不新增大 Schema；
- ref 指向 authority，不复制权威正文/事实。

需要一起对齐的 machine consumer：

1. `identity-envelope`；
2. Codex L2 Session Bootstrap；
3. `llm_agent` Runtime Pilot frozen inputs / comparison identity；
4. cross-repo responsibility projection metadata；
5. Verification / Review report identity/provenance contract。

退出条件：

从一个 `run_id` 能沿 refs 追到 materially-used 的 Digital Worker governance、project source/result、knowledge、ADK、runtime、engineering facts 与 exact decision reports；缺项时状态显式 BLOCKED/NEEDS_REVIEW。

### 阶段 2：四类真实 Pilot 闭环

#### Pilot A — Debug

验证：

- exact Digital Worker Domain/Governance identity；
- Knowledge Context；
- Material Manifest；
- Hypothesis Registry；
- Domain Skill + optional ADK assets；
- exact Runtime source set；
- 原始日志/复现/设备 facts；
- Verification bound to exact fix/result；
- 知识沉淀。

成功标准：根因结论、修复、回归和 Knowledge Candidate 均能追到原始 evidence，不依赖 synthetic evidence 替代真实产品事实。

#### Pilot B — Feature

验证：

```text
engineering-task-package
→ Runtime execution
→ delivery-receipt
→ build/test evidence
→ verification-report(exact subject/source set)
→ closure
```

成功标准：实现 owner 与 verifier 分离；Runtime receipt 不含 `verification_pass`；acceptance criteria 到 evidence 有完整映射；本次使用的 Domain Contract/Skill 版本可 exact trace；若修复后重跑，旧/new report provenance 明确区分。

#### Pilot C — Review / Release

验证：

- exact release candidate identity；
- Device/HIL/install/boot/resulting-version/rollback 或明确 scope exemption；
- Assurance Provider receipt（可以是 Codex Safe，也可以是其它 Provider）；
- Independent Review bound to exact release candidate；
- A6/A7 policy 与人工最终授权。

成功标准：Provider READY/PASS 不能绕过 Verification / Review / Human Gate；Review decision 不能自动等价于 Product Qualification；回滚或阻断路径真实可用。

#### Pilot D — Evolution

验证：

- `llm_agent` 捕获一个真实外部实践/Runtime 差异；
- 给出 evidence + recommendation；
- 正确路由到 DW / KH / ADK / Runtime / Assurance semantic owner；
- owner 可以 accept / reject / observe；
- 真实采用后再回灌 outcome evidence。

成功标准：`llm_agent` 不直接修改其它仓的 authority state，也不成为 production dependency。

阶段退出条件：四类 Pilot 都有至少一个真实、可重放、非 synthetic-only 的 terminal receipt/evidence chain；至少一个 Pilot 覆盖 Governance Escalation，至少一个 Pilot 覆盖 Decision Provenance rerun/supersession。

### 阶段 3：Replaceability / Failure Drill

目标：证明 Provider-neutral 不是文档口号，并严格区分“接口可替换”与“真实 Provider 已替换”。

#### R1 — Binding Conformance

允许使用 fake / controlled alternate adapter 验证：

- contract/input/output shape；
- exact identity；
- failure semantics；
- rollback/degradation；
- Domain semantics 未被 Binding 改写。

R1 只能证明 **binding/adapter conformance**，不能作为真实 Provider-neutral 已实证的终态证据。

#### R2 — Periodic Real Runtime Qualification

R2 不再是 repository closure、Product Release 或整体 Terminal Maturity 的持续阻塞条件。它是 Runtime Portability / Terminal Replaceability claim 的周期性资格认证。

Canonical policy：`manifests/runtime-r2-qualification-policy.json`。

每次 R2 campaign 只保留四个核心要求：

1. **same frozen task**：Codex 与 Claude 等真实 Runtime 对同一个 exact frozen task 独立执行；
2. **real provider execution**：不得用 fake/controlled adapter 代替真实 Provider；
3. **replay-complete result**：导出的结果树脱离 `.git`、runtime home、provider credential 后仍可由冻结 verifier 重放；
4. **independent qualification authority**：最终资格由 Digital Worker verifier 决定，Runtime receipt 不得自我声明 R2 PASS。

R2 采用 quarterly + material-change-triggered cadence。新 Runtime Binding、adapter 语义变化、Provider/model major change、ADK/runtime-contract major change 都触发重新资格认证。

R2 状态只使用 `qualified / blocked / stale / not_run`。其中 `blocked` 是有效失败证据：不允许为了得到 PASS 无限调 prompt/turn budget/人工修补 result tree；重复失败应先修 Runtime adapter，再进入下一次 fresh campaign。

Assurance Provider、Knowledge Provider、Interaction Provider 的替换/降级演练仍可独立存在，但不再塞进 Runtime R2 qualification，避免一个资格认证承担多个控制面的成熟度判断。

退出条件：

- R1 Binding conformance 可稳定执行；
- R2 periodic policy、freeze、真实 runtime execution、replay 与独立 verifier 路径可用；
- 只有在存在 fresh `qualified` receipt 时才声明当前 Runtime replaceability；
- `blocked/stale/not_run` 不会降低 repository health、Product Readiness 或其它 maturity axis；
- failure/drift/missing-evidence/state-isolation 仍保持 fail-closed。

### 阶段 4：Productionization Governance

目标：从“真实 Pilot 可用”升级为“长期生产可运营”。

必须闭环：

- server-side repository governance / ruleset / required checks；
- exact-head CI / release identity；
- release artifact digest / provenance；
- rollback procedure；
- branch lifecycle / branch GC；
- secrets / credentials / ACL boundary；
- dependency and action pinning；
- Knowledge freshness / owner review / promotion queue；
- Runtime drift / health；
- long-lived evidence retention；
- owner / escalation / exception / sunset policy；
- canonical-reference drift check：frozen docs 中的 Runtime/Profile/Provider examples 不得长期引用已退役值；
- report provenance retention：旧 Verification/Review report 在 rerun/supersede 后仍可追溯。

注意：repository-local CI 不能替代 server-side governance；Runtime-local health 不能替代 Product readiness；Product readiness 也不能替代 cross-repo Terminal Maturity。

退出条件：关键生产动作的权限、验证、发布、回滚、审计均有真实远端/环境证据，且不是人工口头流程。

### 阶段 5：Terminal Maturity / Steady State

只有以下条件同时满足，才可以声明整体 terminal maturity：

- Architecture 轴闭环；
- Identity 轴闭环，包含 exact Digital Worker Domain/Governance identity 与 exact reviewed subject provenance；
- Delivery 轴闭环，L1→L2 等 escalation 可重放；
- Assurance 轴闭环，Decision Provenance 与 supersession 可审计；
- Replaceability architecture 与 R1 Binding conformance 闭环；R2 periodic qualification capability 可重复运行，且当前 replaceability claim 不超过最新 R2 evidence；
- Operations 轴闭环；
- Product Readiness / Runtime Qualification / ADK Qualification / Knowledge Provider Qualification 不被用作 terminal maturity 的隐式替代；
- 没有高优先级未声明 owner 的 cross-repo semantic debt；
- 没有 active legacy compatibility/shadow control path；
- 没有用 synthetic evidence 冒充真实 product evidence；
- 没有将 Provider receipt/local gate 自动提升为 product qualification；
- 定期 drift/freshness/governance/canonical-reference 检查可重复执行；
- **Fresh-operator drill 通过**：至少一名未参与体系设计/实现的操作者，仅依赖 canonical docs + machine contract + runbook 完成一个代表性 L1/L2 governed/formal Run，并生成可审计 receipt/evidence，不需要作者口头补充隐藏规则；
- 对 Interaction / Knowledge Provider 的 replaceability 声明不超过实际取得的证据等级。

Terminal maturity 不是“不再变化”。进入 steady state 后仍允许 Provider、Runtime、Skill、模型和内部实现持续演进，但稳定 Contract 和 authority boundary 不应随供应商变化而重构。

## 9. 机器化 Ratchet 优先级

只有经过 Pilot 证明后，再把以下内容逐步 machine-check。

### P0 — 必须机器阻止

- Runtime Receipt 声称 Verification PASS；
- Runtime/Asset local gate 被映射为 Domain Gate PASS；
- Knowledge candidate 自动 active promotion；
- missing exact identity（含 materially-used Digital Worker governance identity）被判为 Formal PASS；
- retired legacy live path 回归；
- Runtime Binding 拥有 reusable asset SSOT；
- `llm_agent` 成为 production runtime dependency；
- fake/controlled Binding 被标记为 R2 real-provider substitution evidence；
- L1/current-provider session/context 被直接提升为 L2 Formal Evidence；
- Verification/Review report 在 reviewed result/source-set 变化后被静默复用；
- Product Readiness / Runtime / ADK / Knowledge Provider qualification 自动提升其它状态维度或 Terminal Maturity。

### P1 — 应机器检查

- semantic owner 唯一性；
- Domain / Reusable / Runtime artifact kind；
- artifact-level authority kind：contract / fact / decision；
- evidence layer：fact / receipt / report / qualification；
- Digital Worker provider commit / contract catalog / Domain-routing-skill refs 完整性；
- source-set composition completeness；
- L1→L2 escalation 是否生成新的 exact source-set/bootstrap provenance；
- Verification/Review report 是否绑定 exact source-set/result、actor identity、sequence/supersedes；
- verifier/reviewer independence fields；
- refs 指向的 exact identity 可解析；
- machine baseline 中 repository responsibility projection 与 architecture plane 语义不会被 consumer 混淆；
- frozen docs Runtime/Profile/Provider examples 是否仍可由 canonical owner 解析。

### P2 — 观察后再固化

- 自动 Runtime selection；
- 自动 Assurance Provider selection；
- 动态 Skill composition；
- 自动 Knowledge promotion；
- 自动扩大 A3-A7 权限；
- Terminal Maturity evaluator：仅在 Stage 2/3 真实 Pilot 后字段稳定时创建，并且只聚合已有 evidence，不重新执行子系统或成为新的超级控制面。

P2 在真实 adoption evidence 不足前保持建议/人工选择，不进入不可审计的自动 authority path。

## 10. 运行与维护节奏

### 每次 Formal Run

- 冻结 Digital Worker governance / project source / context / asset / runtime identities；
- 保留 delivery / execution / verification / review refs；
- Verification/Review 明确绑定 exact reviewed subject / source-set / actor identity；
- 对关键 artifact 保留可解析的 authority/evidence kind；
- closure 后产生 Knowledge Candidate，不直接 active promotion。

### 治理等级升级时

- 记录 escalation reason / target level；
- L1→L2 必须 re-bootstrap / re-freeze exact identities；
- current-provider Knowledge 必须重建为 exact-pinned L2 context；
- prior session/output 只作为 provisional/prior context；
- Formal Evidence 起点必须可定位。

### 每次 ADK / Runtime / Provider 升级

- 检查 consumer compatibility；
- 保留 immutable release/source-set identity；
- 运行受影响 Pilot/eval；
- 不继承上一版本 Product Qualification；
- 不让 provider latest/freshness 自动触发 cross-repo pin promotion。

### 周期性

- repository governance / branch lifecycle；
- Knowledge freshness / review queue；
- Runtime drift / health；
- unresolved semantic debt；
- evolution intake / adoption outcomes；
- R1/R2 replaceability evidence freshness 与 claim scope；
- canonical-reference drift；
- superseded Verification/Review report provenance retention。

### 正式发布/高风险动作前

- exact identity；
- fresh verification bound to exact release candidate；
- required independent review bound to exact release candidate；
- A6/A7 human gate；
- rollback evidence。

## 11. 终态验收清单

整体 terminal maturity 的最终评审只回答以下问题：

- [ ] 能否从 Work/Run 一跳跳追到所有 materially-used authority refs？
- [ ] 是否能 exact trace 到本次使用的 Digital Worker provider commit、contract/catalog、Domain/routing 与 materially-used Domain Skill refs？
- [ ] Git/CI/HIL/Device/Artifact facts 是否仍由原系统拥有？
- [ ] 对同一 producer 产生的不同 artifact，是否能显式区分 authority/evidence kind？
- [ ] Runtime receipt 是否与 Verification verdict 分离？
- [ ] Provider review receipt 是否与 Independent Review decision 分离？
- [ ] Verification/Review 是否绑定 exact Execution Source Set、result/source identity 和 actor identity？
- [ ] 结果变化后旧 report 是否不会静默复用，并存在可追溯 supersession？
- [ ] Review/approval decision 是否不会自动等价于 Product Qualification？
- [ ] L1→L2 是否会重新 freeze identities/context/source set，而不是自动提升旧 session evidence？
- [ ] Knowledge candidate 是否需要 owner lifecycle promotion？
- [ ] ADK asset release 是否不会自动提升 Product Qualification？
- [ ] Product Readiness、Terminal Maturity、Runtime/ADK/Knowledge qualification 是否彼此不继承？
- [ ] Runtime Profile 是否不会隐式改变 Asset Profile semantics？
- [ ] `llm_agent` 离线时 production delivery 是否仍可运行？
- [ ] 不使用 Codex Safe 时 assurance architecture 是否仍成立？
- [ ] 若声明当前 Runtime 已实证可替换，是否存在 fresh R2 qualified evidence；若 R2 blocked/stale/not_run，是否仅撤回该 claim 而不误伤其它成熟轴？
- [ ] fake/controlled alternate Binding 是否只被标记为 R1 conformance？
- [ ] 替换 Runtime Binding 时 Domain Contract 是否保持不变？
- [ ] 若声明 Interaction/Knowledge Provider 已“实证可替换”，是否有对应真实第二 Provider evidence？
- [ ] missing evidence / provider outage / drift / state-isolation 是否 fail-closed？
- [ ] release/rollback/repository governance 是否有真实 production evidence？
- [ ] 是否不存在第二套 live routing / compatibility / shadow authority？
- [ ] frozen docs 中的 Runtime/Profile/Provider 示例是否没有引用已退役值？
- [ ] fresh-operator drill 是否通过，并证明无需作者口头补充即可完成代表性 Run？
- [ ] 是否可以仅靠 canonical docs + contracts + runbooks 重放代表性任务？

任意答案为“否”时，不声明整体 terminal maturity。

## 12. 归档与演进规则

- 本文是当前成熟落地策略基线；被新的阶段策略替代时，从活动 `strategy/` 删除，由 Git history 保存，不保留 `_v2/_final` 平行活动副本；
- 长期语义改变进入 ADR，而不是直接改 Strategy 绕过架构评审；
- 机器语义改变优先修改 canonical contract/schema，并保留 compatibility / migration evidence；
- Digital Worker exact identity、artifact-level authority/evidence kind、repository responsibility projection marker、L1→L2 escalation provenance、Decision Provenance 与 state-isolation，应在真实 Pilot 证明字段需求后以向后兼容方式进入 machine contract；
- Verification/Review schema 自然演进时优先增加 exact subject/source-set/actor/supersession identity，不把原始 evidence 复制进报告；
- Delivery Receipt 后续演进应显式收窄 `validation` 为 execution/self-validation、`decisions` 为 engineering/implementation decisions，避免被 consumer 越权解释；
- 临时 Pilot adapter、one-shot migration、shadow scaffolding 完成后应物理退役，不长期留在活动面；
- 新 Provider 以 Adapter/Binding 接入，不因产品名称进入上位 Domain architecture；
- replaceability claim 必须携带 evidence level：至少区分 `R1 binding-conformance` 与 fresh `R2 periodic real-provider-substitution qualification`；
- Terminal Maturity evaluator 只在真实 Pilot 后字段稳定时建立，并只聚合已有 evidence/receipt/report，不执行新的 Domain/Provider 判定；
- frozen docs 中 provider/runtime/profile 示例必须服从 canonical owner；优先引用 category/manifest，而不是长期硬编码易漂移的具体 selector。

## 13. 最终结论

成熟落地的重点不再是增加新的 Agent、控制面或编排器，而是证明以下闭环长期成立：

> **正确语义由正确 owner 持有；本次执行通过包含 exact Digital Worker governance identity 的 Source Set 组合；治理升级会 re-bootstrap/re-freeze 而不会提升旧 evidence；真实 facts 保留在原系统；每个 artifact 的 authority/evidence kind 可解释；Provider 只提供受边界约束的 fact/receipt/report；Verifier/Reviewer/Approver 对 exact subject 做独立 run-specific decision 并保留 supersession provenance；Qualification 不从局部 PASS 或其它状态维度自动继承；Knowledge 经过生命周期沉淀；能力通过 `llm_agent` 的慢环持续演进，而生产快环不依赖该实验室；Provider-neutral 架构长期成立，只有“当前 Runtime 已实证可替换”这一 claim 需要 fresh R2 periodic qualification。**

达到本方案全部 terminal exit criteria 后，体系进入 steady-state evolution，而不是继续进行顶层架构重构。
