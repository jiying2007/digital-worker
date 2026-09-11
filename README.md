# digital-worker

研发中心 AI 数字员工主仓。这里承载研发流程总纲、专家团正式机器资产、跨团队 Contract/Schema、验证工具，以及内部架构/专家团评审资料。

## 当前权威入口

- [研发中心 AI 数字员工研发流程规划](研发中心AI数字员工研发流程规划.md)：当前唯一活动总体提案，文档版本 3；目标已确定，Provider/知识方案/总体产品组合尚未冻结。
- [ADR-003：Provider-neutral AI R&D Target Architecture](docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md)：当前总体架构上位提案；冻结能力边界与 Contract，不冻结 WorkBuddy/飞书/WeKnora/Codex/Claude 等具体 Provider。
- [ADR-001：WorkBuddy 与 Codex CLI 的集成边界](docs/adr/ADR-001-workbuddy-codex-integration-boundary.md)：`superseded-in-part`；保留“办公入口与工程执行通过 Contract 松耦合”的原则，不再承担总体 Provider 选型。
- [ADR-002：嵌入式系统专家团架构与落地边界](docs/adr/ADR-002-embedded-system-expert-team-architecture.md)：冻结 1+7、Evidence-first、独立 Verification/Review 与高风险 Action Gate，并已改为 Provider-neutral。
- [嵌入式系统专家团机器资产](expert-groups/embedded-system/README.md)：当前 `0.7.0 / pilot-operations-ready`；Engineering Agent Runtime / Knowledge Provider 未冻结。
- [嵌入式系统专家团-核心参考](嵌入式系统专家团-核心参考/)：内部讨论与评审解释层，当前状态 `review-ready`。
- [真实 Pilot Runbook](docs/runbooks/embedded-pilot.md)：真实任务绑定、执行、证据打包、指标聚合和 productionization review 门槛。

## 当前总体架构判断

当前目标已经明确，但总体产品方案**没有定**。

稳定的是：

- Task / Handoff Contract；
- Expert Team / Workflow / Gate；
- Evidence / Verification / Independent Review；
- A0-A7 Action Policy；
- Pilot / Evaluation / Productionization Gate。

尚未冻结的是：

- Work Item / Collaboration Provider：飞书是重要候选，但不是不可替换前提；
- Office / Interaction Provider：WorkBuddy 是候选之一，不是中央控制面；
- Knowledge Provider：WeKnora 是候选之一，知识方案待 PoC；
- Knowledge Sources：飞书/飞书知识库、NAS、Git、CI/HIL、Artifact Store 等按事实类型分别保持权威；
- Engineering Agent Runtime：Codex、Claude Code、IDE Agent、内部 Agent 等均可候选；
- Context Broker / Agent Runtime Gateway / Action Gateway：当前只冻结接口思想，不提前平台化。

总体原则：

> **Provider 可替换，Contract 稳定；Source of Truth stays at source；统一访问，不强制统一存储；Expert 与 Runtime 解耦。**

## 仓库结构

```text
digital-worker/
├── README.md
├── 研发中心AI数字员工研发流程规划.md
├── docs/
│   ├── adr/                 # 架构决策记录
│   ├── archive/             # 非活动历史草案
│   ├── runbooks/            # 运行手册
│   └── source-materials/    # 原始输入材料；非 SSOT
├── expert-groups/
│   └── embedded-system/     # 嵌入式专家团正式机器资产 SSOT
├── schemas/                 # 跨专家团共享 Contract Schema
├── scripts/                 # validator / evaluator / Pilot CLI
├── tests/                   # fixtures / regression
├── 产品专家团-核心参考/      # 产品专家团人工可读参考
└── 嵌入式系统专家团-核心参考/# 嵌入式专家团内部评审/解释层
```

## 当前状态

|对象|状态|说明|
|---|---|---|
|研发目标|`confirmed`|效率/质量/知识复用/安全可审计目标明确|
|总体能力架构|`proposed-for-review`|ADR-003；Provider-neutral 七层架构|
|Provider 选型|`not-frozen`|WorkBuddy/飞书/WeKnora/Codex/Claude 等待 PoC/评审|
|知识方案|`not-frozen`|先做 Source Inventory + Knowledge PoC|
|嵌入式专家团架构|`architecture-frozen`|1+7、Workflow、Gate、Contract、Evidence、Autonomy 已冻结|
|嵌入式专家团实现|`pilot-operations-ready`|Pilot CLI/validator/evaluator 已就绪|
|嵌入式核心参考|`review-ready`|已进入 main，用于内部讨论|
|真实 Pilot|`pending-real-binding`|#6/#7/#8 待真实 Debug / Feature / Review-Release 工作项|
|端侧底座 ownership|`evidence-needed`|#11；原始文档待规范化后逐域裁决|
|main 强制门禁|`admin-action-needed`|#12；CI 可用，branch protection/required check 仍需管理员启用|
|Production Ready|**禁止声明**|需真实 Pilot evidence + 独立 productionization review|

## 权威与历史规则

1. 活动设计只保留稳定路径，不用 `_Vn/_final` 副本表达版本。
2. 历史草案放 `docs/archive/`；完整演进由 Git history 提供。
3. 原始 docx/二进制输入统一放 `docs/source-materials/`，不是运行时 SSOT。
4. 总体架构以 `研发中心AI数字员工研发流程规划.md` + ADR-003 为上位提案。
5. 嵌入式机器资产冲突时，以 [`governance/authority-index.md`](expert-groups/embedded-system/governance/authority-index.md) 裁决。
6. 核心参考是解释/评审层，不覆盖 Workflow、Policy、Contract、Schema。
7. Provider-specific 配置不得反向变成总体架构前提。

## 下一步

当前优先级调整为：

1. 内部评审 ADR-003 / 总体架构原则；
2. 建立 Knowledge Source Inventory（飞书、NAS、Git、CI/HIL 等）；
3. 做 Knowledge Provider PoC，而不是先迁移知识；
4. 用统一 Contract 比较至少两个 Engineering Agent Runtime；
5. 同时完成 #6/#7/#8 三条真实 Pilot；
6. 推进 #11 ownership resolution 与 #12 main required CI。

在真实 PoC/Pilot evidence 出现前，不冻结唯一 WorkBuddy/WeKnora/Codex/Claude 方案，也不扩大 A3-A7 自动化权限。
