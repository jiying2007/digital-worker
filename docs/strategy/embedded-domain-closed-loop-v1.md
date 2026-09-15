# Embedded Domain Closed Loop V1

- Status: `current-stage-baseline`
- Date: 2026-09-11
- Scope: 嵌入式研发域内闭环
- Architecture: `provider-neutral`
- Responsibility model: `docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md`
- Canonical domain contract: `domains/edge-foundation/domain.yaml`
- Canonical execution surface: `domains/edge-foundation/`
- Canonical routing: `domains/edge-foundation/routing.yaml`

> 当前阶段主策略：**先让嵌入式研发自身形成可运行、可验证、可学习的 Domain Closed Loop；Enterprise Digital Thread 不是前置条件。**

## 1. 为什么先收敛域内闭环

企业级串联涉及产品、结构、硬件、测试、知识平台、MES、售后和多个 Provider，组织依赖大、周期长。嵌入式内部已经具备 Work Item、责任模型、Evidence、Hypothesis、Engineering Handoff、Verification、Review、Pilot 与 Git/CI/HIL 接口，因此优先证明一个领域自身能够持续产生真实收益。

外部模块暂时无法接入时，统一降级为 Intake/Delivery Adapter：人工录入、协作文档、Issue、NAS、文件等可以作为输入来源，但进入嵌入式域后必须统一到稳定 Work Item / Run / Evidence / Artifact Identity。

责任链：

```text
Edge Foundation Domain
├─ Edge Coordination Role
├─ Structure Expert
├─ Hardware Expert
└─ Embedded System Expert
   └─ Capability → Skill

Assurance
├─ Verification
├─ Independent Review
├─ Evidence
└─ Evaluation
```

Embedded 内部专业变化优先通过 Capability / Skill 演进，不按 Runtime、产品专项或工具数量增加 Expert。

## 2. Canonical runtime 与 Product readiness 解耦

Edge Foundation target runtime、routing、Skill、Gate、Golden Case、Pilot、Schema、Knowledge Registry 已构成 canonical execution surface。

Product readiness 是独立真实证据 Gate：

- Feature：已有 1 条 eligible real receipt；
- Debug：等待产品源码 exact identity + 原始日志/复现 + device/flash/kernel/test identity；
- Review/Release：等待实机 OTA install/boot/resulting-version/rollback/failure-path + required Verification + 适用时 A7。

因此当前 Product readiness 正确保持 BLOCKED 1/3，但不会控制或回退 canonical routing。

## 3. V1 成功定义

V1 不是“平台建设完成”，而是若干真实嵌入式任务能够稳定完成：

```text
External Input
→ Work Item / Task Brief
→ Edge Coordination
→ Canonical Routing
→ Embedded System Expert / Capability
→ Technical Decision / Engineering Package(s)
→ Engineer + Engineering Agent Runtime
→ Source / Artifact Identity
→ Verification
→ Review according to current-stage policy
→ Delivery / Closure
→ Knowledge Harvest
→ 下一任务可复用
```

并且不出现：incorrect PASS、unauthorized action、source/artifact/device identity 静默断链、Engineering 自签 Verification、Verification 跨层推导、Review unavailable substitute 被伪造成 Review PASS、Knowledge Source 被复制成第二未受控 SSOT。

## 4. V1 七个必做项

### V1-1 One Work Item / One Run Identity

真实任务必须有稳定 `work_item_id` 和 `run_id`。外部来源可变，但域内身份不可漂移。继续复用 task-brief、pilot-run、team-run-state，不建设新的需求管理系统。

### V1-2 Shared System Context

每个 real run 共享 Material/System Context，至少明确 repo / exact base commit、board revision、SoC/MCU、SDK/kernel/RTOS/toolchain、firmware/device/test environment，以及 missing/stale/conflicting material。

所有 Capability 消费同一版本事实；跨到 Hardware/Structure Expert 时也共享同一 Work Item 与 Evidence identity。

### V1-3 One Hypothesis Registry for Debug

Debug / stability / field incident 强制共享一份 Hypothesis Registry。`embedded.debug-reliability` 维护诊断主线；其他 Capability 向同一假设树补 Evidence、Experiment、Supported/Rejected/Confirmed，不允许并行制造互相冲突的 RCA。

若 Evidence 指向板级电气、时钟、电源或结构事实，再触发相应 Domain Expert；跨域升级必须 Evidence-driven。

### V1-4 Exact Source + Artifact Identity

Engineering Execution 必须使用 exact source base，并能追踪：

```text
work_item
→ repo SHA
→ build/config
→ binary/firmware
→ device/test
→ evidence
```

首阶段使用 Engineering Task Package、Delivery Receipt、Evidence Bundle、Device/HIL evidence 与受控引用，不额外发明完整 Artifact Lineage 平台。

### V1-5 Acceptance → Evidence

每个 real Pilot 维护 Acceptance-Evidence Matrix，把每条 Acceptance Criterion 映射到 verification layer、artifact/device/test identity、evidence ref 以及 PASS/FAIL/BLOCKED/NOT_RUN。

字段未稳定前保持轻量运行产物，重复真实需求再 Schema 化。

### V1-6 Knowledge Harvest

每个 completed run 输出：`NO_KNOWLEDGE_DELTA` 或 `KNOWLEDGE_CANDIDATE`。

只检查是否形成新的 root cause、design rule、known issue、compatibility conclusion、checklist、test case、Skill candidate 或 stale knowledge。Knowledge Harvest 不是“每个任务必须写文档”的 KPI。

### V1-7 Embedded Knowledge Registry

Registry 记录 knowledge_id/title/domain/type、authority/source provider/source ref、owner、product/platform scope、version、ACL、freshness、tags。

本地 Registry 仅保存可核验 target contract 与高价值入口；外部 Source 由 Knowledge Hub/原 Source of Truth 管理，不复制正文形成第二权威源。

## 5. 内部运行模型

### Feature

```text
Task Brief
→ Context
→ Edge Coordination
→ Embedded System Expert
→ required Capability analysis
→ Integration Reconciliation
→ Technical Decision
→ Engineering Package(s)
→ Runtime / Engineer
→ Delivery + identity
→ Acceptance → Evidence
→ Verification
→ current-stage Review policy
→ Knowledge Harvest
```

### Debug

```text
Incident / Reproduction
→ Context
→ Evidence Normalize
→ embedded.debug-reliability
→ One Hypothesis Registry
→ evidence-driven Capability expansion
→ Root Cause / evidence insufficient
→ Fix Package
→ Regression / Stress / HIL as required
→ Verification
→ current-stage Review policy
→ Knowledge Harvest
```

### Review / Release

```text
Source / Artifact identity
→ Existing Verification evidence
→ Acceptance coverage
→ Risk / waiver / rollback
→ Independent Review when available/required
→ A7 human release authority where applicable
→ Knowledge Harvest
```

Release 不重新制造工程事实；无法回答哪个 SHA/binary/device/test 时记录 identity gap。

## 6. Integration Reconciliation

Integration 是动作，不新增 Expert。由 Edge Coordination + routed Domain Expert/Capability 在 Execution 前检查 interface、timing、resource、dependency/version、identity、ownership。

若多个真实任务证明该动作持续成为稳定独立工作量，优先评估 Skill 或 Capability；只有满足独立责任边界、独立任务入口、独立生命周期、独立交付物、稳定知识域、持续直达路由等条件，才讨论新 Domain Expert。

## 7. Multi-Repo

推荐 `One Run → Multiple Engineering Packages`，每个 Package 独立 exact base、scope、Acceptance、required Verification 和 Delivery Receipt。Run 层把多个 Package 的结果重新汇合到同一 Verification/Review，不把“多个仓库”误建模成“多个 Expert”。

## 8. Knowledge 分层

四层逻辑模型：

1. Authority Knowledge：Datasheet/TRM/SDK/Schematic/Git/CI-HIL evidence；
2. Engineering Knowledge：Architecture/Design Rule/Compatibility/Porting；
3. Operational Knowledge：RCA/Runbook/Known Issue/Checklist；
4. AI Execution Knowledge：Skill/Golden Case/Evaluation Fixture/Tool Rule。

Knowledge Registry 只索引/描述 Source，不改变 Source Authority。Golden Case 唯一 machine authority 是 `domains/edge-foundation/evaluation/golden-cases.yaml`。

## 9. 五个闭环

- Task Loop：需求/问题 → Delivery；
- Engineering Loop：Analysis → Execution → Verification；
- Quality Loop：Failure → RCA → Regression；
- Knowledge Loop：Experience → Reviewed Knowledge → Reuse；
- Capability Loop：Repeated Gap → Skill/Capability Candidate → Evaluation。

## 10. Real Pilot / Product readiness

所有 real run 强制 Material Manifest、Acceptance-Evidence Matrix、Knowledge Harvest；Debug 强制 Hypothesis Registry。

Canonical Pilot receipt 必须绑定 `routing_authority=edge-foundation`、`canonical_routing=true`、task/mode/Expert/Capability/Assurance 和 eligibility checks。

Product readiness 聚合 Debug / Feature / Review-Release 三轨，每轨至少 1 个 eligible real receipt、总计至少 3，并要求 incorrect PASS=0、unauthorized actions=0、audit trace completeness=1.0。

满足这些条件也只允许进入 Productionization Review，不自动 Release/Production Ready。

## 11. Current-stage Review policy

Independent Review 属于 Assurance，但当前 iterative Pilot 若 Review tool/reviewer unavailable，可用 traceable Verification + static checks + Hosted CI 作为 completion substitute，并记录 unavailable 原因。

替代不等价于 Independent Review PASS；Review/Release 仍必须保留真实 device/release evidence 和 A7 human authority。

## 12. Knowledge 最小闭环

Knowledge Registry 保持高价值、小规模、可追溯，并逐步加入真实 Source。重点验证 citation、authority、freshness、ACL negative case 和真实 reuse。

退出条件不是“登记数量达到目标”，而是 Knowledge 能在下一真实任务被实际引用且保持 Source authority。

## 13. 后续候选只由真实 Evidence 触发

重点观察 context rebuild、duplicate analysis、cross-domain interface mismatch、multi-repo reconciliation、artifact identity gap、Acceptance-Evidence coverage、Review 时重新追问上下文、Knowledge reuse。

重复出现的信息断点才允许升级正式 Schema / Skill / Capability；Runtime、Knowledge Platform、Context Broker 等继续 not-frozen。

## 14. 指标

### Safety / Quality
- incorrect_pass_rate = 0；
- unauthorized_actions = 0；
- unsupported_claim_rate；
- late interface mismatch；
- regression escape。

### Efficiency
- task lead time；
- debug MTTR；
- context rebuild count；
- duplicate analysis；
- human correction time。

### Traceability
- exact source coverage；
- artifact identity coverage；
- device identity coverage；
- Acceptance → Evidence coverage；
- audit trace completeness。

### Knowledge
- registry coverage；
- citation correctness；
- knowledge reuse count；
- stale knowledge detection；
- RCA → reusable knowledge conversion。

## 15. 成熟度

- E0 Defined：Contract / Gate / Policy 已定义；
- E1 Assisted：AI 辅助分析；
- E2 Engineering Closed Loop：真实 Task → Execution → Verification 完整，Review 按当前阶段策略执行；
- E3 Knowledge Closed Loop：Knowledge 真正重新进入后续任务；
- E4 Self-improving：真实任务驱动 Skill/Tool/Knowledge 改进；
- E5 Controlled Automation：低风险流程在 Evidence 支撑下受控自动化。

当前目标推进到 **E2，并为 E3 建基础**。Canonical runtime 完成不等于 E3/E4/E5 或 Production Ready。

## 16. 反向审查与当前结论

持续避免统一知识平台、Context Broker、Knowledge Graph、大批新 Schema/Agent/Expert 等过度设计。重点警惕流程负担超过收益、Knowledge Harvest KPI 化、Registry 复制资料、Pilot 脱离真实研发任务、Schema 爆炸、Runtime 品牌反向污染责任模型。

当前最小执行集固定为：

```text
One Work Item / Run
+ Shared Material/System Context
+ One Hypothesis Registry for Debug
+ Exact Source / Artifact Identity
+ Acceptance → Evidence
+ Knowledge Harvest
+ Embedded Knowledge Registry
```

先建设 Embedded Domain Closed Loop，再向外连接 Enterprise Digital Thread；所有后续扩展都必须由重复真实 Evidence 触发。
