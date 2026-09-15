# ADR-005：跨仓语义所有权、执行身份与证据联邦

- Status: accepted
- Date: 2026-09-15
- Scope: `digital-worker` / `knowledge-hub` / `agent-dev-kit` / `llm_agent` / Runtime Binding / Assurance Provider / Source Fact Systems
- Parent architecture: `ADR-003-provider-neutral-ai-rd-target-architecture.md`
- Domain architecture: `ADR-004-edge-foundation-digital-responsibility-architecture.md`
- Operating model: `../strategy/ai-rd-target-operating-model.md`
- Machine baseline: `../../contracts/cross-repo/embedded-ai-operating-system.yaml`
- Identity spine: `../../contracts/cross-repo/identity-envelope.yaml`

## 1. 决策目的

现有体系已经形成 Provider-neutral 总体架构、端侧责任模型、Knowledge Control Plane、Agent Asset Control Plane、Runtime Binding 和真实 Evidence/Verification 链路。继续增加新的顶层 Plane、中央 Broker 或仓库调用层，会重新制造双重控制面和第二套 SSOT。

本 ADR 不新增新的总体架构层级，而是冻结以下长期语义：

1. Repository role 不等于 architecture plane；
2. 各仓采用联邦式语义所有权（federated semantic ownership），只对自己的语义和制品负责；
3. 跨仓协同以 refs-first、immutable identity、exact source set、receipt 与 evidence 为主，不复制彼此 SSOT；
4. Contract Authority、Fact Authority 与 Decision Authority 必须分离；
5. Domain Skill / Reusable Skill / Runtime Skill，Domain Workflow / Reusable Workflow / Runtime Workflow，Domain Gate / Asset Gate / Runtime Gate 必须保持不同语义；
6. Runtime、Provider、Receipt、评测或本地 Gate 不得越权提升为 Domain Verification、Independent Review 或 Product Qualification。

## 2. 不改变的上位架构

本 ADR 不替代 ADR-003 的 Provider-neutral 七逻辑 Plane，也不替代 ADR-004 的责任、编排、执行、可信保障边界。

当前 `four-control-planes-plus-replaceable-runtime-bindings` 机器基线继续保留，作为当前 cross-repo repository responsibility model；本 ADR 对其中容易歧义的 `owns` 语义做进一步限定，而不触发新的架构命名迁移。

## 3. Repository Responsibility Map

| Repository / System | Canonical responsibility | 明确不拥有 |
| --- | --- | --- |
| `digital-worker` | Domain / Expert / Capability / Domain Skill、Work / Run、Domain Workflow、Gate、Action Policy、Engineering Handoff、Verification / Review Contract、Product Readiness 语义 | Knowledge lifecycle、Runtime host config、Reusable Agent Asset SSOT、provider-specific receipt truth |
| `knowledge-hub` | Knowledge Registry、Context / Evidence Pack、Authority、ACL、Freshness、Knowledge Lifecycle、Owner Review / Promotion | 源码/CI/HIL/设备事实、产品 Verification verdict、Runtime live state |
| `agent-dev-kit` | Reusable Agent / Skill / Workflow Asset、Asset Profile、Evaluation、Immutable Release、Distribution Contract | Product qualification、Domain Verification PASS、Runtime live home |
| `llm_agent` | External Practice Intake、Runtime Evaluation、Cross-runtime Comparison、Adoption Evidence / Recommendation | Production Runtime、Domain Gate、Adoption Authority、Verification PASS |
| Runtime Binding（当前 `codex`） | Exact source selection、Runtime Profile、Distribution、Host Integration、Thin Session Bootstrap、Runtime Execution Receipt | Domain semantics、Knowledge lifecycle、Reusable Asset SSOT、Product qualification |
| Assurance Provider（例如 Codex Safe） | Provider-specific Review / Diagnose / Commit / Change capability 与 receipt | Domain Verification Authority、Product Release Authority |
| Git / CI / HIL / Device / Artifact Store | Source / build / artifact / device / test / release facts | Domain policy、Knowledge promotion、Product qualification |
| Verifier / Reviewer / Approver | Run-specific judgment / approval | 重写原始事实或修改上游 Contract authority |

## 4. 三类 Authority

### 4.1 Contract Authority

回答“标准是什么”。

典型例子：

- `digital-worker` 定义 task/run、Gate、Action Policy、Verification / Review schema；
- `knowledge-hub` 定义 Knowledge Lifecycle / Promotion contract；
- ADK 定义 reusable asset / release contract；
- Runtime Binding 定义自己的 source-to-live / execution receipt contract。

### 4.2 Fact Authority

回答“实际发生了什么”。

典型例子：

- Git commit / tree；
- CI build/test result；
- HIL / Device behavior；
- Artifact digest；
- Release system fact。

任何控制仓、Agent 总结或 Knowledge projection 都不得制造第二份同等级事实源。

### 4.3 Decision Authority

回答“根据 Contract + Facts，本次 Run 的结论是什么”。

典型例子：

- Verifier 输出 Verification verdict；
- Independent Reviewer 输出 review decision；
- Authorized Human / Release Authority 完成 A7 或其它高风险最终授权。

**不变量：`Contract Authority ≠ Fact Authority ≠ Decision Authority`。**

## 5. 同名概念的规范语义

### 5.1 Skill

- **Domain Skill（领域技能）**：由 `digital-worker` 管理，描述领域责任体系需要完成的专业能力；
- **Reusable Skill（可复用技能）**：由 ADK 管理，描述可跨任务/项目/领域复用的 Agent 方法或执行资产；
- **Runtime Skill（运行时技能）**：由具体 Runtime Binding 管理，描述本次 Runtime 实际可发现/加载/调用的物化能力。

三者不得通过命名相同推导为同一身份，也不要求一一映射。一个 Domain Skill 可以组合多个 ADK 资产，也可以只依赖 Runtime 原生工具；一个 ADK Skill 可以服务多个 Domain。

### 5.2 Workflow

- **Domain Workflow**：产品/领域任务的阶段、状态、Gate、Evidence、Verification、Review、Closure；
- **Reusable Workflow Asset**：ADK 提供的通用 Agent 工作方法；
- **Runtime Workflow / Recipe**：具体 Runtime 的加载、触发、并行、命令、工具与上下文编排。

Runtime Workflow 可以实现 Domain Workflow 的一个或多个步骤，但不得定义 Domain lifecycle authority。

### 5.3 Profile

- **Asset Profile**：ADK 对 reusable assets 的组合；
- **Runtime Profile**：Runtime Binding 对 live 运行能力、预加载、并发、catalog 与 host integration 的组合。

Digital Worker 不新增第三种同名 Profile；领域选择使用 Domain / Capability / Workflow Mode / Risk Policy 表达。

### 5.4 Gate

- **Domain Gate**：是否满足领域证据、Verification、Review、Release 条件；
- **Asset Gate**：某个 ADK asset 是否验证/评测/发布合格；
- **Runtime Gate**：source set、build/apply、drift、sandbox、local conformance 是否满足运行条件。

Runtime-local PASS 或 Asset PASS 不得推导 Domain Gate PASS。

## 6. Evidence 四层模型

跨仓统一采用：

```text
FACT
  ↓
RECEIPT
  ↓
REPORT
  ↓
QUALIFICATION / DECISION
```

### FACT

原始事实，例如 Git SHA、CI PASS/FAIL、设备启动结果、artifact digest。

### RECEIPT

某次 Provider/Runtime 行为的不可变记录，例如 Runtime Execution Receipt、Review Safe Receipt、Diagnosis Receipt。

### REPORT

基于 facts/receipts 形成的专业判断，例如 `verification-report`、`review-report`。

### QUALIFICATION / DECISION

例如 Product Ready、Release Ready、高风险动作批准。

**不变量：`Fact ≠ Receipt ≠ Report ≠ Qualification`。**

## 7. Execution Source Set 是运行态唯一组合边界

跨仓不建立中央 Agent RPC 网络。Formal Run 通过 exact Execution Source Set 组合本次实际使用的来源：

```text
Work / Run identity
+ selected Digital Worker domain semantics
+ Knowledge Hub context/evidence refs
+ immutable ADK release identity
+ selected ADK assets / Asset Profile
+ exact Runtime Binding identity
+ Runtime Profile
+ project source identity
+ explicitly allowed local overlays
```

Runtime Binding 将该 Source Set 物化为 Runtime Distribution / Session Bootstrap，并产生 Execution Receipt。

`identity-envelope.yaml` 是跨 plane identity spine；它通过 ref 指向 authority，不复制 source fact 形成第二套 SSOT。

## 8. Assurance Provider 边界

Codex Safe、CI/HIL、Security Scanner、Human Reviewer 等都是可替换 Assurance Provider / Assurance Execution 实现。

允许：

```text
Provider-specific Receipt
    -> evidence_ref
    -> Verification / Review Contract
    -> run-specific judgment
```

禁止：

```text
Provider PASS -> Domain Verification PASS
Provider Review APPROVE -> Product Independent Review 自动批准
Change Ready -> Product Release Ready
```

若某 Provider 被选作本次 Reviewer implementation，仍必须满足同一 `review-report` contract、independence 和 evidence 要求。

## 9. llm_agent 永久退出生产热路径

正式 Engineering Delivery Loop 不依赖 `llm_agent`：

```text
Intent -> Work -> Context -> Capability -> Source Set -> Execution
       -> Evidence -> Verification -> Review -> Closure -> Knowledge Candidate
```

`llm_agent` 只运行 Capability Evolution Loop：

```text
External Practice / Runtime Evidence / Failure / Adoption Evidence
    -> evaluate / compare / recommend
    -> semantic owner
    -> validate
    -> release / promote
    -> real usage evidence
```

Recommendation 不等于 Adoption Decision。Proposal 必须由拥有目标语义的仓库接受、拒绝或继续观察。

## 10. Risk-based Progressive Orchestration

治理按风险升级，而不是所有请求都进入 Formal Run。

- 低风险查询/解释：允许 Runtime-only；
- 一般工程修改：Runtime + build/test + bounded evidence；
- 正式工程交付：Work/Run + source-set identity + evidence + Verification；
- Device write / Release / 关键量产风险：再增加 Independent Review、Device/HIL/Release evidence 与 Human Gate。

Risk policy 只决定复用哪些现有 Contract，不创建第二套 L0/L1/L2/L3 workflow authority。

## 11. 长期不变量

1. `Responsibility ≠ Runtime`
2. `Expert ≠ Agent`
3. `Capability ≠ Agent`
4. `Domain Skill ≠ Reusable Skill ≠ Runtime Skill`
5. `Domain Workflow ≠ Reusable Workflow ≠ Runtime Workflow`
6. `Asset Profile ≠ Runtime Profile`
7. `Domain Gate ≠ Asset Gate ≠ Runtime Gate`
8. `Knowledge Index ≠ Source of Truth`
9. `Contract Authority ≠ Fact Authority ≠ Decision Authority`
10. `Fact ≠ Receipt ≠ Report ≠ Qualification`
11. `Runtime Receipt ≠ Verification PASS`
12. `Provider Review Receipt ≠ Independent Review approval`
13. `llm_agent Recommendation ≠ Adoption Decision`
14. `Session Bootstrap ≠ Control Plane`
15. `Product Readiness ≠ Routing Authority`
16. `Runtime Binding ≠ Product Qualification`

新实现、Adapter、Provider、Schema 或 Runtime 必须保持这些不变量。若需要打破其中任意一条，必须通过新的 ADR 明确改变体系语义，而不能通过局部实现绕过。

## 12. 成熟度与终态边界

“架构终态”只表示上述职责与语义可以冻结，不表示产品已经 Production Ready。

成熟落地仍必须由真实证据证明：

- Debug / Feature / Release 等代表性 Formal Run 能完整追溯；
- Knowledge reuse / freshness / authority 在真实 Run 中可验证；
- ADK release 与 Runtime source-set identity 可重放；
- Assurance Provider 可替换且不会改变 Domain semantics；
- 至少一次 Runtime Binding 替换/对比证明 Provider-neutral；
- Productionization 前 server-side repository governance、权限、发布、回滚和长期运营机制有真实 evidence。

具体落地路径见 `../strategy/cross-repo-terminal-maturity-landing.md`。

## 13. 被拒绝的替代方案

### 把六个仓排成固定调用链

拒绝。会把 evolution、knowledge、asset supply chain、runtime 和 assurance 混成同步生产依赖。

### 新增统一中央 Agent Gateway / Broker

拒绝。当前没有真实证据证明需要新的长期控制面；会形成新的任务状态、权限和 routing authority。

### 建全局 DW Skill ↔ ADK Skill 一一映射表

拒绝。两者语义不同且关系是 run-specific、多对多或零依赖。需要记录的是本次 Execution Source Set，而不是永久全局绑定。

### 让 Runtime / Safe / CI 的 PASS 直接提升产品状态

拒绝。违反 Contract / Fact / Decision 与 Evidence 四层边界。

## 14. 决策结果

从本 ADR 起，跨 `digital-worker`、`knowledge-hub`、ADK、`llm_agent`、Runtime Binding 与 Assurance Provider 的终态协同采用：

> **Provider-neutral logical architecture + federated semantic ownership + refs-first immutable identity + exact Execution Source Set + evidence federation + independent run-specific decision authority。**

不再通过新增顶层 Plane 或复制资产来表达协同关系。