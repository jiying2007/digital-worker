# Cross-Repo Terminal Maturity Landing — 终态成熟落地方案

- Status: `active / implementation-baseline`
- Date: 2026-09-15
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
2. 每次 Formal Run 有可重放的 exact identity spine；
3. source facts、provider receipts、verification/review reports 和 qualification 不混层；
4. Runtime / Assurance / Interaction / Knowledge Provider 都可以在不改变 Domain semantics 的前提下替换；
5. `llm_agent` 只影响下一代能力演进，不阻塞日常生产链；
6. 真实 Debug / Feature / Release / Evolution evidence 能长期被机器和人复核；
7. 缺关键 identity/evidence 时 fail-closed，不以 synthetic evidence 或“文件存在”冒充成熟。

## 2. 成熟度定义

本方案区分六个独立成熟轴，不再使用一个模糊的“已完成”覆盖全部状态。

| 轴 | 终态要求 |
| --- | --- |
| Architecture | ADR / semantic ownership / dependency direction 稳定，无第二控制面和 legacy live path |
| Identity | Work、Knowledge、ADK、Runtime、Engineering、Artifact、Device、Verification 均可 exact trace |
| Delivery | 代表性工程任务可从 intake 到 closure 重放，不依赖人工记忆补链 |
| Assurance | Fact / Receipt / Report / Qualification 分层稳定，Verifier/Reviewer 独立性有证据 |
| Replaceability | Runtime / Assurance / Knowledge Provider 替换不改变 Domain Contract，失败可退回 |
| Operations | repository governance、release、rollback、drift、freshness、knowledge lifecycle、owner 机制长期可运营 |

任何单轴未闭环时，只能声明对应轴已成熟，不得声明整体 terminal maturity。

## 3. 不做的事情

本阶段明确不做：

- 不合并六个仓；
- 不新增中央 Agent Gateway / Context Broker Service / Runtime Server；
- 不建立全局 Domain Skill ↔ ADK Skill 一一映射；
- 不把 Knowledge Hub 变成 Git/CI/HIL/Device 的事实副本；
- 不把 Codex Safe 变成强制 Assurance authority；
- 不让 `llm_agent` 进入 Formal Run 热路径；
- 不为尚无真实 consumer 的接口预建兼容层；
- 不为了“统一”复制 Skill、Workflow、Profile、Gate 或 Evidence 到多个仓。

## 4. 终态生产链

Formal Engineering Delivery Loop：

```text
Intent / Work Item
    ↓
Digital Worker task / domain / policy / acceptance
    ↓
Context resolution
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
Independent Verification
    ↓
Independent Review when required
    ↓
Decision / Closure
    ↓
Knowledge Candidate
    ↓
Knowledge Hub lifecycle / promotion
```

`llm_agent` 不出现在这条必经链路中。

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

## 6. 落地阶段

### 阶段 0：语义与活动面冻结

目标：停止继续产生第二架构、第二 SSOT、第二命名体系。

必须完成：

- ADR-003 / ADR-004 / ADR-005 形成稳定优先级；
- Repository Responsibility Map 在文档入口可发现；
- legacy 1+7、shadow routing、migration switch 等已退役 surface 不回到活动执行面；
- 同名对象在文档和机器 contract 中明确 Domain / Reusable / Runtime 语义；
- 新增 cross-repo 资产必须声明 canonical owner；
- 不再创建 `_final/_v2` 平行活动文档。

退出条件：

- 新任务不需要通过口头解释判断“哪个仓说了算”；
- 任意一个 Skill / Workflow / Profile / Gate / Evidence 对象能明确回答 semantic kind 与 owner。

### 阶段 1：Identity Spine / Source Set 闭环

目标：任何 Formal Run 都能回答“这次到底用了什么”。

必须具备：

- `work_item_id` / `run_id`；
- exact project source/base identity；
- Knowledge provider identity + context/evidence fingerprint；
- immutable ADK release identity；
- selected ADK asset/profile refs；
- exact Runtime Binding repository/commit/target/profile/host；
- runtime source-set / distribution / session-bootstrap / execution receipt refs；
- build/artifact/device/test identity；
- verification/review refs。

实施原则：

- 优先扩展现有 `identity-envelope` / source-set refs；
- 没有真实需求时不新增大 Schema；
- ref 指向 authority，不复制权威正文/事实。

退出条件：

从一个 `run_id` 能沿 refs 追到 materially-used source、knowledge、ADK、runtime、engineering facts 与 decision reports；缺项时状态显式 BLOCKED/NEEDS_REVIEW。

### 阶段 2：四类真实 Pilot 闭环

#### Pilot A — Debug

验证：

- Knowledge Context；
- Material Manifest；
- Hypothesis Registry；
- Domain Skill + optional ADK assets；
- exact Runtime source set；
- 原始日志/复现/设备 facts；
- Verification；
- 知识沉淀。

成功标准：根因结论、修复、回归和 Knowledge Candidate 均能追到原始 evidence，不依赖 synthetic evidence 替代真实产品事实。

#### Pilot B — Feature

验证：

```text
engineering-task-package
→ Runtime execution
→ delivery-receipt
→ build/test evidence
→ verification-report
→ closure
```

成功标准：实现 owner 与 verifier 分离；Runtime receipt 不含 `verification_pass`；acceptance criteria 到 evidence 有完整映射。

#### Pilot C — Review / Release

验证：

- exact release candidate identity；
- Device/HIL/install/boot/resulting-version/rollback 或明确 scope exemption；
- Assurance Provider receipt（可以是 Codex Safe，也可以是其它 Provider）；
- Independent Review；
- A6/A7 policy 与人工最终授权。

成功标准：Provider READY/PASS 不能绕过 Verification / Review / Human Gate；回滚或阻断路径真实可用。

#### Pilot D — Evolution

验证：

- `llm_agent` 捕获一个真实外部实践/Runtime 差异；
- 给出 evidence + recommendation；
- 正确路由到 DW / KH / ADK / Runtime / Assurance semantic owner；
- owner 可以 accept / reject / observe；
- 真实采用后再回灌 outcome evidence。

成功标准：`llm_agent` 不直接修改其它仓的 authority state，也不成为 production dependency。

阶段退出条件：四类 Pilot 都有至少一个真实、可重放、非 synthetic-only 的 terminal receipt/evidence chain。

### 阶段 3：Replaceability / Failure Drill

目标：证明 Provider-neutral 不是文档口号。

至少完成：

1. **Runtime Binding 替换/对比演练**：同一受控任务在当前 Codex Binding 与第二实现/受控替代 Binding 上执行，Domain acceptance / verification semantics 不变；
2. **Assurance Provider 替换演练**：至少一次不依赖 Codex Safe 的 Verification/Review 仍能完成；
3. **Knowledge Provider degradation drill**：Provider unavailable/stale/ACL unresolved 时显式 degrade/BLOCKED，不回退到未治理 cache 冒充事实；
4. **Runtime drift / rollback drill**：source set、distribution 或 live state 漂移可检测并可回滚；
5. **Missing evidence drill**：删除/缺失关键 fact/receipt 后，terminal qualification 必须 fail-closed。

退出条件：Provider 替换只改变 Adapter/Binding identity，不要求改 Domain Contract；失败路径可恢复且有 receipt。

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
- owner / escalation / exception / sunset policy。

注意：repository-local CI 不能替代 server-side governance；Runtime-local health 不能替代 Product readiness。

退出条件：关键生产动作的权限、验证、发布、回滚、审计均有真实远端/环境证据，且不是人工口头流程。

### 阶段 5：Terminal Maturity / Steady State

只有以下条件同时满足，才可以声明整体 terminal maturity：

- Architecture 轴闭环；
- Identity 轴闭环；
- Delivery 轴闭环；
- Assurance 轴闭环；
- Replaceability 轴闭环；
- Operations 轴闭环；
- 没有高优先级未声明 owner 的 cross-repo semantic debt；
- 没有 active legacy compatibility/shadow control path；
- 没有用 synthetic evidence 冒充真实 product evidence；
- 没有将 Provider receipt/local gate 自动提升为 product qualification；
- 定期 drift/freshness/governance 检查可重复执行；
- 新成员仅依赖文档 + machine contract + runbook 就能完成代表性 Run，而不需要作者口头补充隐藏规则。

Terminal maturity 不是“不再变化”。进入 steady state 后仍允许 Provider、Runtime、Skill、模型和内部实现持续演进，但稳定 Contract 和 authority boundary 不应随供应商变化而重构。

## 7. 机器化 Ratchet 优先级

只有经过 Pilot 证明后，再把以下内容逐步 machine-check：

### P0 — 必须机器阻止

- Runtime Receipt 声称 Verification PASS；
- Runtime/Asset local gate 被映射为 Domain Gate PASS；
- Knowledge candidate 自动 active promotion；
- missing exact identity 被判为 Formal PASS；
- retired legacy live path 回归；
- Runtime Binding 拥有 reusable asset SSOT；
- `llm_agent` 成为 production runtime dependency。

### P1 — 应机器检查

- semantic owner 唯一性；
- Domain / Reusable / Runtime artifact kind；
- authority kind：contract / fact / decision；
- evidence layer：fact / receipt / report / qualification；
- source-set composition completeness；
- verifier/reviewer independence fields；
- refs 指向的 exact identity 可解析。

### P2 — 观察后再固化

- 自动 Runtime selection；
- 自动 Assurance Provider selection；
- 动态 Skill composition；
- 自动 Knowledge promotion；
- 自动扩大 A3-A7 权限。

P2 在真实 adoption evidence 不足前保持建议/人工选择，不进入不可审计的自动 authority path。

## 8. 运行与维护节奏

### 每次 Formal Run

- 冻结 source / context / asset / runtime identities；
- 保留 delivery / execution / verification / review refs；
- closure 后产生 Knowledge Candidate，不直接 active promotion。

### 每次 ADK / Runtime / Provider 升级

- 检查 consumer compatibility；
- 保留 immutable release/source-set identity；
- 运行受影响 Pilot/eval；
- 不继承上一版本 Product Qualification。

### 周期性

- repository governance / branch lifecycle；
- Knowledge freshness / review queue；
- Runtime drift / health；
- unresolved semantic debt；
- evolution intake / adoption outcomes。

### 正式发布/高风险动作前

- exact identity；
- fresh verification；
- required independent review；
- A6/A7 human gate；
- rollback evidence。

## 9. 终态验收清单

整体 terminal maturity 的最终评审只回答以下问题：

- [ ] 能否从 Work/Run 一跳跳追到所有 materially-used authority refs？
- [ ] Git/CI/HIL/Device/Artifact facts 是否仍由原系统拥有？
- [ ] Runtime receipt 是否与 Verification verdict 分离？
- [ ] Provider review receipt 是否与 Independent Review decision 分离？
- [ ] Knowledge candidate 是否需要 owner lifecycle promotion？
- [ ] ADK asset release 是否不会自动提升 Product Qualification？
- [ ] Runtime Profile 是否不会隐式改变 Asset Profile semantics？
- [ ] `llm_agent` 离线时 production delivery 是否仍可运行？
- [ ] 不使用 Codex Safe 时 assurance architecture 是否仍成立？
- [ ] 替换 Runtime Binding 时 Domain Contract 是否保持不变？
- [ ] missing evidence / provider outage / drift 是否 fail-closed？
- [ ] release/rollback/repository governance 是否有真实 production evidence？
- [ ] 是否不存在第二套 live routing / compatibility / shadow authority？
- [ ] 是否可以仅靠 canonical docs + contracts + runbooks 重放代表性任务？

任意答案为“否”时，不声明整体 terminal maturity。

## 10. 归档与演进规则

- 本文是当前成熟落地策略基线；被新的阶段策略替代时，从活动 `strategy/` 删除，由 Git history 保存，不保留 `_v2/_final` 平行活动副本；
- 长期语义改变进入 ADR，而不是直接改 Strategy 绕过架构评审；
- 机器语义改变优先修改 canonical contract/schema，并保留 compatibility / migration evidence；
- 临时 Pilot adapter、one-shot migration、shadow scaffolding 完成后应物理退役，不长期留在活动面；
- 新 Provider 以 Adapter/Binding 接入，不因产品名称进入上位 Domain architecture。

## 11. 最终结论

成熟落地的重点不再是增加新的 Agent、控制面或编排器，而是证明以下闭环长期成立：

> **正确语义由正确 owner 持有；本次执行通过 exact Source Set 组合；真实 facts 保留在原系统；Provider 只提供 receipt/evidence；Verifier/Reviewer/Approver 独立做 run-specific decision；Knowledge 经过生命周期沉淀；能力通过 `llm_agent` 的慢环持续演进，而生产快环不依赖该实验室。**

达到本方案全部 terminal exit criteria 后，体系进入 steady-state evolution，而不是继续进行顶层架构重构。