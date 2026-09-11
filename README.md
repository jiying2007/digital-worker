# digital-worker

研发中心 AI 数字员工主仓。承载总体研发流程、专家团机器资产、共享 Contract/Schema、验证工具和内部评审资料。

## 当前权威入口

- [研发中心 AI 数字员工研发流程规划](研发中心AI数字员工研发流程规划.md)：文档版本 3；目标确定，Provider/知识方案/产品组合未冻结；
- [ADR-003：Provider-neutral AI R&D Target Architecture](docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md)：当前总体架构上位提案；
- [Embedded Domain Closed Loop V1](docs/strategy/embedded-domain-closed-loop-v1.md)：当前阶段嵌入式落地终版策略基线；
- [Architecture Review Readiness Pack](docs/review/)：正式架构评审前的 Pre-read、Decision Matrix、Evidence Gap、RACI 和端到端 Walkthrough；
- [ADR-001](docs/adr/ADR-001-workbuddy-codex-integration-boundary.md)：`superseded-in-part`，保留 Contract 松耦合原则；
- [ADR-002](docs/adr/ADR-002-embedded-system-expert-team-architecture.md)：1+7、Evidence-first、Verification/Review、Action Gate；
- [嵌入式系统专家团机器资产](expert-groups/embedded-system/README.md)：`0.7.0 / pilot-operations-ready / provider-neutral`；
- [嵌入式系统专家团-核心参考](嵌入式系统专家团-核心参考/)：01~16 已同步到 v0.7.0 Provider-neutral 评审基线；
- [Branch Lifecycle](docs/governance/branch-lifecycle.md)：默认只长期保留 main，任务分支由受控 Branch GC 收口；
- [真实 Pilot Runbook](docs/runbooks/embedded-pilot.md)。

## 当前阶段重点

> **先形成 Embedded Domain Closed Loop；Enterprise Digital Thread 不是当前落地前置条件。**

V1 最小执行集：

```text
One Work Item / Run
+ Shared Material/System Context
+ One Hypothesis Registry for Debug
+ Exact Source / Artifact Identity
+ Acceptance -> Evidence
+ Knowledge Harvest
+ Embedded Knowledge Registry
```

当前只推进到 E2 Engineering Closed Loop，并为 E3 Knowledge Closed Loop 建基础；不因基础设施完成声明 Production Ready。

## 非结论型设计备忘

- [Brainstorm Archive](docs/brainstorm/)：保存有参考价值但尚未形成正式决策的设计思路；不会覆盖 ADR / Contract / Schema / Governance。
- [企业—研发—嵌入式 AI Digital Thread 头脑风暴](docs/brainstorm/enterprise-ai-rd-embedded-digital-thread.md)。
- [渐进式 AI 落地策略](docs/brainstorm/incremental-enterprise-ai-landing-strategy.md)。
- [嵌入式内部 Engineering Thread](docs/brainstorm/embedded-internal-engineering-thread.md)。

## 稳定架构原则

> **Provider 可替换，Contract 稳定；Source of Truth stays at source；统一访问，不强制统一存储；Expert 与 Runtime 解耦。**

稳定层：Task/Handoff Contract、Expert/Workflow/Gate、Evidence/Verification/Review、A0-A7、Pilot/Evaluation。

未冻结层：Work Item/Interaction Provider、Knowledge Provider、默认 Engineering Runtime、Context Broker/Runtime Gateway/Action Gateway。

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
|Architecture Review Pack|`review-candidate`|
|Embedded Domain Closed Loop V1|`current-stage-baseline`|
|Provider / Knowledge 选型|`not-frozen`|
|嵌入式专家团|`0.7.0 / pilot-operations-ready`|
|Embedded Knowledge Registry|`internal-seed / 50 entries`|
|核心参考|`review-ready / synchronized-v0.7.0`|
|真实 Pilot|`pending-real-binding` (#6/#7/#8)|
|Knowledge PoC|open (#16)|
|Provider Capability Matrix|open (#17)|
|Multi-runtime Pilot|open (#18)|
|merged branch GC|`completed` (#19)|
|端侧底座 ownership|`evidence-needed` (#11)|
|main protection|`deferred` (#12)|
|Production Ready|**禁止声明**|

## 权威与治理规则

1. 总体架构以研发流程总纲 + ADR-003 为上位提案；
2. `docs/strategy/` 规定当前阶段实施范围和退出条件，不覆盖 ADR / Contract / Schema；
3. `docs/review/` 是评审决策包，不覆盖 ADR / Contract / Schema；
4. 机器资产冲突按 `expert-groups/embedded-system/governance/authority-index.md` 裁决；
5. 核心参考只做解释/评审，不覆盖机器 Contract；
6. Provider-specific 配置不得反向变成总体架构前提；
7. 历史草案进 `docs/archive/`，原始输入进 `docs/source-materials/`；
8. Brainstorm 进 `docs/brainstorm/`，不产生架构权威；
9. `main` 默认唯一长期分支，任务分支按 Branch Lifecycle + Branch GC 收口。

## 下一步

1. 使用 Embedded Domain Closed Loop V1 绑定并执行 #6/#7/#8 real Pilot；
2. #16 基于现有 internal-seed Registry 扩展真实 NAS / 飞书 / CI-HIL Source；
3. #18 Multi-runtime Pilot；
4. #17 用 #16/#18 evidence 完成 Provider Capability Matrix；
5. #11 ownership；
6. 完成 Architecture Review，并在 real Pilot evidence 充分后再进入 Productionization Review。

在真实 PoC/Pilot evidence 出现前，不冻结唯一 WorkBuddy/WeKnora/Codex/Claude 方案，也不扩大 A3-A7 自动化权限。
