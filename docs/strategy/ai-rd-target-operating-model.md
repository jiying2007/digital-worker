# AI R&D Target Operating Model — Final Baseline

- Status: `target-baseline / frozen-for-implementation`
- Date: 2026-09-13
- Scope: `digital-worker` / `knowledge-hub` / `agent-dev-kit` / `llm_agent` + N replaceable Runtime Bindings
- Parent architecture: `docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md`
- Domain implementation baseline: `docs/strategy/embedded-domain-closed-loop-v1.md`
- Trust gate: `docs/strategy/r0-trust-closure.md`
- Authority: 本文冻结长期 Operating Model；ADR、机器 Contract、Schema、Action Policy 和真实 Evidence 在冲突时优先

## 1. 审查结论

最终方案不再继续扩展新的控制面。长期模型冻结为：

> **4 个稳定控制面 + N 个可替换 Runtime Binding + 1 个极薄 Session Bootstrap。**

用户侧只保留 Runtime CLI/IDE 入口；当前第一入口是 Codex CLI。`knowledge-hub` 作为外挂 Knowledge Control Plane；`llm_agent` 退出日常执行热链；`agent-dev-kit` 负责可复用 Agent 资产；`digital-worker` 负责研发 Operating Model、Domain Gate、Evidence、Verification 与 Review。

本次审查同时确认一项重要语义迁移：ADK → Codex 不再要求 provider-produced monolithic bundle。终态采用 **immutable ADK release + exact-source-set handoff + Runtime consumer assembly**。`asset_bundle_hash / BLOCKED_ASSET_BUNDLE_IDENTITY` 属于旧过渡模型，不得作为终态架构前提。

截至当前实施收敛，ADK provider contract、llm_agent Runtime Pilot contract、Codex Runtime Binding / L0-L1-L2 Session Bootstrap 和 digital-worker cross-repo identity spine 均已迁移到 source-set 语义。剩余阻塞属于 live server governance 与真实 Pilot / Knowledge reuse / multi-runtime evidence，不再属于 bundle-era 架构缺口；因此仍不得声明 Production Ready。

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
   │             Evidence / Verification / Review
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
             digital-worker Verification
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

## 3. 四个稳定控制面

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
- Verification；
- Independent Review；
- Pilot / Maturity / Productionization Gate。

不得拥有：

- Runtime-specific exporter；
- Runtime Host 配置；
- Knowledge lifecycle；
- reusable Agent/Skill 实现 SSOT；
- cross-runtime effectiveness evaluator。

一句话：**digital-worker 决定研发工作应该怎么做，以及凭什么算完成。**

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
- adopt / observe / reject；
- Runtime health；
- cross-runtime comparison；
- Loop Readiness；
- effectiveness evaluation；
- adoption recommendation。

不得成为日常 Runtime 网关，不负责 Knowledge retrieval，不拥有 Domain Gate / Verification PASS。

一句话：**llm_agent 决定哪些外部实践值得进入下一代能力资产，以及不同 Runtime 的实测差异。**

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

未来新增 Claude Code、IDE Agent、Internal Agent 时，只新增 Runtime Binding，不重写四个控制面的职责。

## 5. Thin Session Bootstrap

允许增加一个极薄的 `Session Bootstrap / Task Router`，但它属于 Runtime Binding，不形成新的控制面。

职责仅限：

1. 识别当前 repository / project；
2. 判断或接受显式执行等级 L0 / L1 / L2；
3. 读取显式 Engineering Task Package / project binding；
4. 解析 digital-worker contracts；
5. 选择 ADK-derived Skill / Agent；
6. 调 Knowledge Provider Adapter；
7. 检查 Runtime / Asset / Knowledge 身份是否满足当前等级；
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
+ exact source identity
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

因此不得强行把“当前最新 Hub”与“Formal pinned Hub”合并为一种模式。

## 8. Asset Profile 与 Runtime Profile 永久分离

```text
ADK Asset Profile
  example: embedded-fullstack

Runtime Profile
  example: codex/token-lean

Runtime Target / Host
  example: codex-cli / developer-workstation
```

Asset Profile 回答“带哪些可复用能力”；Runtime Profile 回答“具体 Runtime 如何装载、披露、并行和治理这些能力”。二者不得压缩成一个 `profile` 字段。

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

### Source

```text
repo
base_commit
result_commit
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

### Verification / Evaluation

```text
verification_run_id
evidence refs
review ref
llm_agent evaluator commit
comparison evidence ref
```

Envelope 只记录 identity/ref；事实正文继续保留在权威 Source，不创建第二 SSOT。

## 11. Knowledge Harvest

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

## 12. 当前实现状态（2026-09-13 收敛基线）

代码侧终态迁移已经从“目标语义”推进为机器合同事实：

1. `agent-dev-kit` 已发布 digital-worker integration v2：immutable ADK 5.1.0 release + `exact-source-set-reference`，不再要求 monolithic Runtime bundle；
2. `llm_agent` Runtime Pilot contract 已升级到 v1.2/schema v3，frozen inputs/hard rules 使用 ADK release、Runtime source-set、Runtime distribution identity；
3. Codex Runtime Binding v2 已 `SOURCE_SET_BOUND`，source identity 为 `exact-release-source-blobs`，并实现 L0/L1/L2 Thin Session Bootstrap；
4. `digital-worker` cross-repo lock v4、Identity Envelope v3、ownership/capability/Quickstart 已迁移到 immutable-release + source-set/distribution/bootstrap identity；
5. permanent cross-repo CI 负责 fresh exact checkout、canonical digest、ADK release tree/manifest/tag 和 Codex Session Bootstrap contract verification；
6. Knowledge Hub Formal L2 仍坚持 exact-pinned provider identity；当前 pin 可落后 provider main，route/真实 reuse 未完成前不升级为默认；
7. GitHub `main` server-side governance 仍是外部 blocker；repository-local CI 不能替代 branch/ruleset enforcement；
8. #6/#7/#8 真实 Pilot evidence、#16 Knowledge reuse、#18 multi-runtime evidence 仍未完成；
9. 因此当前不得声明 Production Ready。

## 13. 后续唯一执行顺序

终态架构与代码侧 source-set contract 已冻结并收敛，后续不再新增控制面：

1. 让 GitHub Repository Governance Audit PASS；
2. 使用 L2 Session Bootstrap + Embedded Domain Closed Loop V1 执行 #6 Debug real Pilot；
3. 执行 #7 Feature real Pilot；
4. 执行 #8 Review/Release real Pilot；
5. #16 引入真实 Knowledge Source 并形成至少一次 evidence-backed reuse；
6. #18 增加第二个健康 Runtime Binding，以相同 Work/Context/Acceptance/Verification 完成隔离对照；
7. 满足 E2/Knowledge foundation 后进入独立 Productionization Review。

任何不能由当前权限或真实工程输入完成的步骤必须保持 `BLOCKED/PENDING`，不得用合成证据替代。

## 14. 终态验收标准

### Architecture Closed

- 四个控制面职责无重叠；
- Runtime Binding 可替换；
- Thin Bootstrap 不形成第五控制面；
- 无 Runtime-specific path 泄入 domain contracts；
- 无 active bundle legacy semantics。

### Identity Closed

- source exact；
- Knowledge exact；
- ADK release exact；
- source-set exact；
- Runtime Binding exact；
- build/artifact/device/test identity exact 或显式 unresolved。

### Execution Closed

- Runtime CLI/IDE 是用户主入口；
- L0/L1/L2 可显式或确定性路由；
- Knowledge Provider、ADK-derived Skill、Runtime Receipt 正常；
- Runtime local PASS 不越权成为 Domain PASS。

### Verification Closed

- Acceptance 全量映射 concrete Evidence；
- Independent Verification / Review 保持独立；
- `incorrect_pass = 0`；
- 无 unauthorized action。

### Knowledge Closed

- context/evidence/authority/freshness/lifecycle 可用；
- Knowledge Harvest 可路由；
- 至少一次真实 evidence-backed reuse。

### Multi-runtime Closed

- 至少两个健康 Runtime Binding；
- 相同 Work / Context / Acceptance / Verification；
- 独立 Execution Receipt；
- 后一个 Runtime 不接收前一个 Runtime 的最终 answer/patch。

### Governance Closed

- `main` server-side PR enforcement；
- required status check；
- block force push / non-fast-forward；
- block default-branch deletion；
- bounded bypass；
- live audit PASS。

## 15. 永久禁止的反模式

```text
digital-worker
  × copy Knowledge corpus
  × vend reusable ADK assets
  × write Runtime live home
  × own Runtime-specific exporter

knowledge-hub
  × own Domain Verification PASS
  × own Runtime Profile
  ×把 retrieval success 当 engineering fact

agent-dev-kit
  × direct-write ~/.codex
  × own digital-worker Gate
  × own Knowledge lifecycle
  × require Runtime-specific monolithic bundle as universal identity

llm_agent
  × become daily Runtime gateway
  × own Knowledge retrieval
  × own Domain PASS

Runtime Binding
  × own Knowledge lifecycle
  × own digital-worker semantics
  × claim Product Release Ready from local gate
```

## 16. 最终冻结原则

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
11. **缺失身份、权限、证据时 fail closed，不用推断补齐。**
12. **在重复真实证据出现前，不新增第五控制面、中央 Runtime Gateway、Context Broker Service 或大一统知识平台。**
13. **Production Ready 只能由真实工程、Knowledge reuse、multi-runtime、治理与生产化证据共同支持。**

对研发人员的目标体验最终收敛为：

```bash
cd <project>
codex
```

后台由 Runtime Binding 完成薄装配；四个控制面分别提供稳定职责。研发人员不需要把五个仓库理解为一条同步 Runtime pipeline。
