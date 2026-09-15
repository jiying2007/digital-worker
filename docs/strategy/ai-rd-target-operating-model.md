# AI R&D Target Operating Model — Final Baseline

- Status: `target-baseline / frozen-for-implementation`
- Date: 2026-09-14
- Last reviewed: 2026-09-15
- Scope: `digital-worker` / `knowledge-hub` / `agent-dev-kit` / `llm_agent` + N replaceable Runtime Bindings
- Parent architecture: `docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md`
- Semantic ownership authority: `docs/adr/ADR-005-cross-repo-semantic-ownership-and-evidence-federation.md`
- Domain implementation baseline: `docs/strategy/embedded-domain-closed-loop-v1.md`
- Trust baseline: `docs/strategy/r0-trust-closure.md`
- Authority: 本文冻结长期 Operating Model；ADR、机器 Contract、Schema、Action Policy 和真实 Evidence 在冲突时优先

## 1. 审查结论

最终方案不再继续扩展新的控制面。当前 repository responsibility model 继续兼容保留为：

> **4 个稳定 repository responsibility/control roles + N 个可替换 Runtime Binding + 1 个极薄 Session Bootstrap。**

这里的“4 个控制面”是当前跨仓责任投影，不等于 ADR-003 的 architecture plane，也不表示四个仓拥有同等级 production authority；长期 semantic ownership、Contract/Fact/Decision Authority 与 artifact-level evidence 边界以 ADR-005 为准。

用户侧只保留 Runtime CLI/IDE 入口；当前第一入口是 Codex CLI。`knowledge-hub` 作为外挂 Knowledge Control Plane；`llm_agent` 退出日常执行热链；`agent-dev-kit` 负责可复用 Agent 资产；`digital-worker` 负责研发 Operating Model、Domain Gate、Evidence Contract、Verification/Review Contract 与 Product Readiness 语义。

本次审查同时确认一项重要语义迁移：ADK → Codex 不再要求 provider-produced monolithic bundle。终态采用 **immutable ADK release + exact-source-set handoff + Runtime consumer assembly**。`asset_bundle_hash / BLOCKED_ASSET_BUNDLE_IDENTITY` 属于旧过渡模型，不得作为终态架构前提。

截至当前实施收敛，ADK provider contract、llm_agent Runtime Pilot contract、Codex Runtime Binding / L0-L1-L2 Session Bootstrap 和 digital-worker cross-repo identity spine 均已迁移到 source-set 语义。当前进入 `iterative-development`：main server-side protection 暂不作为真实 Pilot 前置，严格治理延后到 Productionization；现阶段主要缺口是 exact Digital Worker governance identity、L1→L2 escalation semantics、Decision Provenance、#6/#7/#8 真实 Pilot、#16 Knowledge reuse 和 #18 multi-runtime evidence，因此仍不得声明 Production Ready 或整体 Terminal Maturity。

## 2. 终态总图

```text
能力演进面（低频）
────────────────────────────────────────────────────────────
External Practices / GitHub / 官方资料 / 社区
                       │
                       ▼
                   llm_agent
            research / eval / adoption
                       │ approved practice
                       ▼
                 agent-dev-kit
          Agent / Skill / Asset Profile
          Workflow Asset / Release / Rollback
                       │
                       ▼
            immutable ADK release
                       │ exact-source-set handoff
                       ▼
                Runtime Binding
                       │ build / plan / apply
                       ▼
                    live runtime


任务执行面（高频）
────────────────────────────────────────────────────────────
Engineer
   │
   ▼
Runtime CLI / IDE（当前 Codex CLI）
   │
   ▼
Thin Session Bootstrap / Task Router
   │
   ├──────────► digital-worker
   │             Work / Expert / Gate / Acceptance
   │             Evidence Contract / Verification / Review Contract
   │
   ├──────────► Knowledge Provider Adapter
   │                    │
   │                    ▼
   │               knowledge-hub
   │        Context / Evidence / ACL / Authority
   │        Freshness / Lifecycle / Harvest
   │
   └──────────► ADK-derived Skills / Agents
                         │
                         ▼
                 Runtime Execution
                         │
                         ▼
              Git / Build / Test / HIL
                         │
                         ▼
               Evidence + Execution Receipt
                         │
                         ▼
              Verifier / Reviewer decision
                         │
                         ▼
                  Knowledge Harvest
                         │
                         └──────────► knowledge-hub
```

两个面必须分开理解：

- **能力演进面**解决“哪些 AI Coding/Agent 实践值得进入下一版能力资产”；
- **任务执行面**解决“当前研发任务如何被正确执行、验证、审查和沉淀”。

不得把 `llm_agent → ADK → Runtime` 的发布链误写成每个工程任务的同步调用链。

## 3. 四个稳定 repository responsibility/control roles

### 3.1 digital-worker — R&D Operating Model / Domain Policy & Evidence Kernel

拥有：

- Work Item / Run；
- Task taxonomy；
- Expert identity / routing；
- Domain Workflow / Gate；
- Action Policy（A0-A7）；
- Material / System Context contract；
- Engineering Task Package / Handoff；
- Acceptance Criteria；
- Evidence contract；
- Verification / Independent Review contract；
- Pilot / Product Readiness / Productionization Gate semantics。

不得拥有：

- Runtime-specific exporter；
- Runtime Host 配置；
- Knowledge lifecycle；
- reusable Agent/Skill 实现 SSOT；
- cross-runtime effectiveness evaluator；
- CI/HIL/Device 原始事实；
- run-specific verifier/reviewer/approver identity 的替代判断。

一句话：**digital-worker 决定研发工作应该怎么做、需要什么证据，以及凭什么允许某类资格状态变化；具体运行级判断仍由相应 Decision Authority 作出。**

### 3.2 knowledge-hub — Knowledge Control Plane

拥有：

- Knowledge Registry；
- context assembly / retrieval；
- Evidence Pack；
- ACL / authority；
- freshness / conflict；
- lifecycle / owner review / promotion；
- proposal / Knowledge Harvest；
- Knowledge reuse evidence。

Runtime 只能通过公开 Provider Contract 消费，不得依赖 Hub 的 `.tmp`、cache、私有 receipt 路径、内部 Python module 或内部目录布局。

一句话：**knowledge-hub 决定什么知识可信、适用于哪里、是否新鲜、谁有权变更。**

### 3.3 agent-dev-kit — Agent Asset Control Plane

拥有：

- reusable Agent；
- Skill；
- Asset Profile；
- Workflow Asset；
- runbook / support tree；
- asset validation；
- immutable release；
- release / rollback。

不得拥有：

- `~/.codex` 或其他 Runtime live home；
- Runtime Profile；
- Runtime Host；
- Knowledge lifecycle；
- digital-worker Domain Verification PASS。

一句话：**ADK 决定可复用 Agent 能力资产是什么。**

### 3.4 llm_agent — Practice / Runtime Evaluation Lab

拥有：

- 外部 AI Coding / Agent 实践 intake；
- reference repository analysis；
- adopt / observe / reject recommendation；
- Runtime health；
- cross-runtime comparison；
- Loop Readiness；
- effectiveness evaluation；
- adoption recommendation。

不得成为日常 Runtime 网关，不负责 Knowledge retrieval，不拥有 Domain Gate / Verification PASS，也不直接修改其它仓的 authority state。

一句话：**llm_agent 评估哪些外部实践值得进入下一代能力资产，以及不同 Runtime 的实测差异；最终 Adoption Decision 由目标 semantic owner 作出。**

## 4. N 个 Runtime Binding

Runtime Binding 是可替换的 Runtime Distribution / Host Integration Adapter，不是第五个控制面。

当前第一套实现：

```text
jiying2007/codex
runtime_target = codex-cli
```

Runtime Binding 可以拥有：

- Runtime Profile；
- config rendering；
- Runtime target / host mapping；
- MCP / sandbox / permission binding；
- source → build → plan → dry-run → apply → rollback；
- live drift detection；
- Runtime Control / local conformance；
- Runtime Execution Receipt。

Runtime Binding 不得拥有：

- digital-worker Domain Gate semantics；
- digital-worker Verification PASS；
- Knowledge lifecycle；
- reusable Agent/Skill SSOT；
- cross-runtime evaluation。

未来新增 Claude Code、IDE Agent、Internal Agent 时，只新增 Runtime Binding，不重写四个 repository responsibility/control roles 的职责。

WorkBuddy、飞书、Web 等默认属于 Interaction / Collaboration Provider；只有真实满足 Runtime Binding Contract 并承担 Engineering Runtime source-to-live/execution responsibility 时，才可作为 Runtime Binding 实现。

## 5. Thin Session Bootstrap

允许增加一个极薄的 `Session Bootstrap / Task Router`，但它属于 Runtime Binding，不形成新的控制面。

职责仅限：

1. 识别当前 repository / project；
2. 判断或接受显式执行等级 L0 / L1 / L2；
3. 读取显式 Engineering Task Package / project binding；
4. 解析 digital-worker contracts；
5. 选择 ADK-derived Skill / Agent；
6. 调 Knowledge Provider Adapter；
7. 检查 Digital Worker / Runtime / Asset / Knowledge 身份是否满足当前等级；
8. 建立 session envelope；
9. 进入 Runtime execution。

禁止拥有：

- Domain Gate semantics；
- Verification PASS；
- Knowledge lifecycle；
- Skill/Agent SSOT；
- cross-runtime evaluation；
- 自动扩大 A3-A7 权限。

原则：**Bootstrap 负责装配，不负责裁决。**

当前阶段不新增中央 Runtime Gateway、Context Broker Service、统一 Agent Server 或新的 Knowledge Gateway 平台；重复真实证据出现前，不扩大平台面。

## 6. 三个运行等级

### L0 — Quick Assist

适用：代码解释、日志分析、简单修改、API 查询、局部重构、一般问答。

默认能力：

```text
Runtime
+ ADK-derived Skills
+ current reviewed Knowledge Provider
```

不要求 Work Item、formal Run、Identity Envelope、Independent Review 或 terminal Evidence Bundle。

### L1 — Governed Engineering

适用：正式 Bug 修复、驱动开发、Boot/Kernel/RTOS/MCU 问题、性能优化、稳定性问题、系统重构等大多数工程任务。

启用：

```text
Digital Worker Task Contract
+ Expert Routing
+ Material/System Context
+ Knowledge Context
+ Acceptance Criteria
+ Action Policy
+ Engineering Evidence
```

L1 是未来最常用的生产工程模式；不应把所有日常任务都升级成 L2 ceremony。

### L2 — Formal Evidence

适用：Real Pilot、Release qualification、关键量产问题、高风险 OTA/设备动作、Multi-runtime comparison、正式成熟度证据。

要求完整身份与证据链：

```text
work_item_id / run_id
+ exact Digital Worker Domain/Governance identity
+ exact project source identity
+ exact Knowledge identity
+ exact ADK release/source-set identity
+ exact Runtime Binding identity
+ Runtime Execution Receipt
+ build/artifact/device/test identity
+ Acceptance -> Evidence
+ Independent Verification / Review
+ terminal evidence bundle
+ Knowledge Harvest
```

缺少任何 materially-used exact identity 时，只能显式 `BLOCKED / NEEDS_REVIEW`，不得降级为 PASS。

### L0/L1 → L2 Governance Escalation

治理等级升级不是证据等级提升。特别是 L1 运行中发现任务需要正式证据、关键量产/Release/HIL/设备写等场景而升级到 L2 时，必须重新执行受控 bootstrap：

```text
escalation decision
    ↓
freeze exact Digital Worker governance identity
    ↓
resolve exact-pinned Knowledge identity / rebuild context
    ↓
freeze ADK release + selected assets
    ↓
freeze Runtime Binding / profile / host
    ↓
freeze project source / dirty baseline
    ↓
create new exact Execution Source Set
    ↓
Formal Evidence begins here
```

升级前的 session/context/output 可以作为 prior observation、hypothesis 或 provisional context 引用，但不得自动提升为 L2 Fact/Receipt/Report/Qualification。若 materially-used 的旧信息需要进入 L2，必须从其 authority 重新解析/引用并纳入新的 frozen Source Set。

**不变量：`Governance escalation ≠ evidence promotion`。**

## 7. Knowledge 的双模式

### 日常 L0/L1

默认消费当前已审核 Knowledge Provider：

```text
Runtime Provider Adapter
        ↓
current reviewed knowledge-hub
```

目标是新鲜、低摩擦、低延迟。Provider unavailable 或 route/authority unresolved 时必须显式降级，不得用本地 cache/path 猜测冒充事实。

### Formal L2

必须绑定 digital-worker cross-repo lock 中的 exact Knowledge Provider identity：

```text
exact provider commit
+ contract version/digest
+ source/context fingerprint
+ Evidence Pack ref
```

目标是可复现、可审计、可比较。

因此不得强行把“当前最新 Hub”与“Formal pinned Hub”合并为一种模式；L1→L2 时必须重建 exact-pinned Knowledge context，不能把 current-provider session context 直接升级为 Formal Evidence。

## 8. Asset Profile 与 Runtime Profile 永久分离

```text
ADK Asset Profile
  example: embedded-fullstack

Runtime Profile
  example: codex/default
  canonical values: owned by the selected Runtime Binding

Runtime Target / Host
  example: codex-cli / developer-workstation
```

Asset Profile 回答“带哪些可复用能力”；Runtime Profile 回答“具体 Runtime 如何装载、披露、并行和治理这些能力”。二者不得压缩成一个 `profile` 字段。文档示例不得作为 Runtime Profile 的第二 SSOT；具体合法值始终以 Runtime Binding 的 canonical manifest 为准。

## 9. ADK → Runtime 的终态身份语义

终态不要求 ADK 为每个 Runtime 生产 monolithic target bundle。

ADK 发布稳定身份：

```text
repository
release version
release tag
exact release commit
release tree
manifest blob
release artifact SHA-256
asset profile
```

Runtime Binding 再绑定 exact source set：

```text
source_repo
source_ref / release commit
source_path
source_blob
vendor_rel
asset version
```

Runtime consumer 自己负责 Runtime distribution assembly，并记录 build/apply/live identity。

因此以下属于退役语义，不得作为新合同的 required identity：

```text
asset_bundle_hash
BLOCKED_ASSET_BUNDLE_IDENTITY
provider-produced monolithic Codex bundle
consumer lock hash as provider identity
short SHA / unpeeled tag
```

任何历史合同中的上述字段必须通过受控版本迁移退役，不能只在文档中改名后继续使用旧判定。

## 10. Formal Identity Spine

L2 的 refs-first identity spine 冻结为：

### Work

```text
work_item_id
run_id
task_type
workflow_mode
```

### Digital Worker Governance

```text
provider repository / exact commit
contract catalog ref / digest
Domain ref / digest
routing ref / digest
materially-used Domain Skill refs / digests
Action Policy / workflow-mode refs when materially used
```

### Source

```text
repo
base_commit
result_commit / exact reviewed subject
```

### Knowledge

```text
provider
provider_commit
contract version/digest
source/context fingerprint
evidence_pack_ref
knowledge_ids
```

### Agent Assets

```text
provider = agent-dev-kit
release version/tag/commit/tree
manifest blob
release artifact SHA-256
asset_profile
source_set_ref
```

### Runtime Binding

```text
repository
commit
runtime_target
runtime_profile
runtime_host
source_set_identity_ref
runtime_distribution_identity_ref
session_bootstrap_ref
execution_receipt_ref
```

### Runtime Execution

```text
runtime version
model / model provider
MCP fingerprint
sandbox identity
approval identity
```

### Engineering

```text
build identity
artifact hashes
device identities
test identities
```

### Verification / Review / Evaluation

```text
verification report id / run id
review report id / run id
exact execution_source_set_ref
exact reviewed result/source identity
verifier/reviewer identity ref
report sequence / supersedes ref when rerun
evidence refs
llm_agent evaluator commit
comparison evidence ref
```

Envelope 只记录 identity/ref；事实正文继续保留在权威 Source，不创建第二 SSOT。

## 11. Decision Provenance

L2 / Release 级 Verification 与 Review 必须能够证明“谁、基于哪一版规则、对哪个精确候选、依据哪些 evidence 作出了什么判断”。仅有 `run_id + verifier/reviewer string + evidence_refs` 不足以支撑最终 terminal maturity。

Decision Provenance 至少应具备：

```text
report_id
run_id
execution_source_set_ref
exact reviewed subject/result identity
decision_actor_identity_ref
independence evidence
input evidence refs
decision/report sequence
supersedes / previous report ref when rerun
```

报告重跑、修复后复核或同一 Run 内产生新 result commit 时，旧报告保持历史 provenance，不得静默“指向最新结果”。

Delivery Receipt 中的 `validation` 只表示 Engineering self-validation / execution observation；`decisions` 只表示 implementation/engineering decisions，不得被解释成 Independent Verification、Review、Qualification 或 Release approval。未来 Schema 自然演进时应显式收窄这些字段语义，而不是让 consumer 猜测。

## 12. Knowledge Harvest

Runtime / digital-worker 只能产生 `NO_KNOWLEDGE_DELTA` 或 evidence-backed candidate/proposal；不得直接创建 active knowledge。

```text
Engineering Session
       ↓
Knowledge Delta?
   ┌───────┴────────┐
   │                │
  NO             CANDIDATE
   │                │
   ▼                ▼
record          proposal
NO_DELTA            │
                    ▼
             knowledge-hub
          authority / owner / review
             ┌──────┴─────┐
             ▼            ▼
          active        reject
```

Knowledge lifecycle 的最终裁决只属于 Knowledge Control Plane。

## 13. 独立状态模型

以下状态彼此正交，不得自动继承：

```text
Product Readiness
≠ Cross-repo Terminal Maturity
≠ Runtime Binding / Runtime Qualification
≠ ADK Asset / Release Qualification
≠ Knowledge Provider Qualification
```

例如产品 Debug/Feature/Review-Release 三轨全部 eligible，只能说明该产品进入相应 Productionization Review 条件；如果 Replaceability、Operations 或 cross-repo identity 尚未闭环，Cross-repo Terminal Maturity 仍为 false。反之，跨仓平台进入 steady state 也不能替代新产品自己的 Device/HIL/Release evidence。

任何 evaluator 只能升级自己拥有的状态维度；不得通过字段映射、默认继承或“上游已 PASS”自动提升其它维度。

## 14. 当前实现状态（2026-09-15 迭代基线）

代码侧终态迁移已经从“目标语义”推进为机器合同事实，但最新架构审核进一步识别出 machine-semantics gap：

1. `agent-dev-kit` 已发布 digital-worker integration v2：immutable ADK 5.1.0 release + `exact-source-set-reference`，不再要求 monolithic Runtime bundle；
2. `llm_agent` Runtime Pilot contract 已升级到 v1.2/schema v3，frozen inputs/hard rules 使用 ADK release、Runtime source-set、Runtime distribution identity，但尚未固定 exact Digital Worker governance identity，也尚未区分 R1/R2 replaceability evidence；
3. Codex Runtime Binding v2 已 `SOURCE_SET_BOUND`，source identity 为 `exact-release-source-blobs`，并实现 L0/L1/L2 Thin Session Bootstrap，但 L2 required inputs 尚未完整绑定 exact Digital Worker governance identity，且 L1→L2 re-bootstrap/re-freeze 尚需机器化；
4. `digital-worker` cross-repo lock v4、Identity Envelope v3 已迁移到 immutable-release + source-set/distribution/bootstrap identity，但 Identity Envelope 尚缺显式 Digital Worker governance identity；
5. `verification-report` / `review-report` 已有 run/evidence/independence 语义，但 L2/Release 所需的 exact reviewed subject / execution source set / actor identity / supersession provenance 尚待 Schema 演进；
6. permanent cross-repo CI 负责 fresh exact checkout、canonical digest、ADK release tree/manifest/tag 和 Codex Session Bootstrap contract verification；
7. Knowledge Hub Formal L2 仍坚持 exact-pinned provider identity；当前 pin 可落后 provider main，route/真实 reuse 未完成前不升级为默认；
8. 当前 repository stage 为 `iterative-development`：GitHub `main` server-side protection 暂不要求，不阻塞 real Pilot；strict governance 保留为 Productionization 前置；
9. #6/#7/#8 真实 Pilot evidence、#16 Knowledge reuse、#18 real multi-runtime/R2 evidence 仍未完成；
10. 因此当前不得声明 Production Ready 或整体 Terminal Maturity。

## 15. 后续唯一执行顺序

后续不再新增控制面，优先消除 machine-semantics gap，再扩大 Formal Pilot：

1. **Identity Semantics Alignment**：以向后兼容方式让 Identity Envelope、Codex Session Bootstrap、llm_agent Runtime Pilot 与 cross-repo responsibility marker 共同理解 exact Digital Worker governance identity；
2. **Governance Escalation**：固定 L1→L2 re-bootstrap/re-freeze，禁止旧 session/context 自动提升为 Formal Evidence；
3. **Decision Provenance**：让 Verification/Review 精确绑定 execution source set、reviewed result/source identity、actor identity 和 supersession；
4. **State Orthogonality**：永久阻止 Product Readiness、Terminal Maturity、Runtime Qualification、ADK Qualification 等状态互相继承；
5. 修正静态文档 canonical-reference 漂移，并建立最小 reference/lint 防止已退役 Runtime/Profile 名称重新进入 frozen docs；
6. 在上述边界可机器验证后执行 #6 Debug real Pilot、#7 Feature real Pilot、#8 Review/Release real Pilot；
7. #16 引入真实 Knowledge Source 并形成至少一次 evidence-backed reuse；
8. #18 增加第二个真实健康 Runtime/Provider Binding，以相同 Work/Context/Acceptance/Verification 完成 R2 隔离对照；
9. 满足 E2/Knowledge foundation 后进入独立 Productionization Review；
10. Productionization 前启用 GitHub server-side ruleset，并让 `Repository Governance Audit --strict` PASS；
11. Stage 2/3 字段经过真实 Pilot 稳定后，再建立只聚合现有 evidence 的 Terminal Maturity evaluator，不提前制造新的超级控制面。

任何不能由当前权限或真实工程输入完成的步骤必须保持 `BLOCKED/PENDING`，不得用合成证据替代。main protection 当前为 stage-deferred，不得继续误报为 real Pilot blocker。

## 16. 终态验收标准

### Architecture Closed

- 四个 repository responsibility/control roles 的职责无语义重叠；
- Runtime Binding 可替换；
- Thin Bootstrap 不形成第五控制面；
- 无 Runtime-specific path 泄入 domain contracts；
- 无 active bundle legacy semantics；
- repository responsibility projection 不被误读成 architecture plane authority。

### Identity Closed

- exact Digital Worker governance identity；
- project source exact；
- Knowledge exact；
- ADK release exact；
- source-set exact；
- Runtime Binding exact；
- build/artifact/device/test identity exact 或显式 unresolved。

### Execution Closed

- Runtime CLI/IDE 是用户主入口；
- L0/L1/L2 可显式或确定性路由；
- L1→L2 会 re-bootstrap/re-freeze；
- Knowledge Provider、ADK-derived Skill、Runtime Receipt 正常；
- Runtime local PASS 不越权成为 Domain PASS。

### Verification Closed

- Acceptance 全量映射 concrete Evidence；
- Verification/Review report 绑定 exact Execution Source Set 和 reviewed result/source identity；
- verifier/reviewer identity 与 independence 可审计；
- 修复后重跑通过 supersession/sequence 保留 provenance；
- `incorrect_pass = 0`；
- 无 unauthorized action。

### Knowledge Closed

- context/evidence/authority/freshness/lifecycle 可用；
- Knowledge Harvest 可路由；
- 至少一次真实 evidence-backed reuse。

### Multi-runtime / Replaceability Closed

- R1 binding conformance 与 R2 real-provider substitution 明确分离；
- 至少两个真实健康 Runtime/Provider Binding；
- 相同 exact Digital Worker governance / Work / Context / Acceptance / Verification semantics；
- 独立 Execution Receipt；
- 后一个 Runtime 不接收前一个 Runtime 的最终 answer/patch。

### State Isolation Closed

- Product Readiness 不继承 Terminal Maturity；
- Terminal Maturity 不继承 Product Readiness；
- Runtime/ADK/Knowledge Provider qualification 不自动提升 Product 或 Terminal 状态；
- 每个 evaluator 只写自己拥有的状态维度。

### Governance Closed — Productionization Gate

- `main` server-side PR enforcement；
- required status check；
- block force push / non-fast-forward；
- block default-branch deletion；
- bounded bypass；
- strict live audit PASS。

## 17. 永久禁止的反模式

```text
digital-worker
  × copy Knowledge corpus
  × vend reusable ADK assets
  × write Runtime live home
  × own Runtime-specific exporter
  × synthesize CI/HIL/Device facts

knowledge-hub
  × own Domain Verification PASS
  × own Runtime Profile
  × 把 retrieval success 当 engineering fact

agent-dev-kit
  × direct-write ~/.codex
  × own digital-worker Gate
  × own Knowledge lifecycle
  × require Runtime-specific monolithic bundle as universal identity
  × let asset qualification imply product qualification

llm_agent
  × become daily Runtime gateway
  × own Knowledge retrieval
  × own Domain PASS
  × let comparison result imply terminal replaceability without R2 evidence

Runtime Binding
  × own Knowledge lifecycle
  × own digital-worker semantics
  × claim Product Release Ready from local gate
  × promote L1 context/session into L2 evidence without re-freeze

Verifier / Reviewer
  × review an unspecified/latest result instead of an exact subject
  × silently retarget an old report after result changes
```

## 18. 最终冻结原则

1. **Provider 可替换，Contract 稳定。**
2. **Source of Truth stays at source；统一访问，不强制统一存储。**
3. **Expert identity 与 Runtime 解耦。**
4. **Asset Profile 与 Runtime Profile 永久分离。**
5. **能力演进链与任务执行链分离。**
6. **Knowledge Hub 是外挂 Control Plane，不复制进 Runtime live home。**
7. **Session Bootstrap 只装配，不裁决。**
8. **ADK → Runtime 使用 immutable release + exact-source-set，不依赖 monolithic bundle。**
9. **Runtime Execution Receipt 只证明执行事实，不证明 Domain Verification PASS。**
10. **L0 降低日常摩擦，L1 承担主要工程治理，L2 承担正式可审计证据。**
11. **Governance escalation 不自动提升 evidence；L1→L2 必须重新冻结 exact identities 与 Source Set。**
12. **Decision report 必须绑定 exact subject / Source Set / actor identity；结果变化后旧报告不得静默复用。**
13. **Product Readiness、Terminal Maturity、Runtime Qualification、ADK Qualification、Knowledge Provider Qualification 彼此正交，不自动继承。**
14. **缺失身份、权限、证据时 fail closed，不用推断补齐。**
15. **在重复真实证据出现前，不新增第五控制面、中央 Runtime Gateway、Context Broker Service 或大一统知识平台。**
16. **Production Ready 只能由对应产品真实工程证据支持；Cross-repo Terminal Maturity 只能由 Architecture/Identity/Delivery/Assurance/Replaceability/Operations 六轴证据支持。**
17. **Frozen docs 的 Runtime/Profile/Provider 示例必须引用或服从 canonical owner，不形成静态第二 SSOT。**

对研发人员的目标体验最终收敛为：

```bash
cd <project>
codex
```

后台由 Runtime Binding 完成薄装配；各 repository responsibility/control roles 分别提供稳定职责。研发人员不需要把多个仓库理解为一条同步 Runtime pipeline。
