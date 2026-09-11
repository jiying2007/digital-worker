# digital-worker

研发中心 AI 数字员工主仓。这里同时承载研发流程总纲、专家团正式机器资产、跨团队共享 Contract/Schema、验证工具，以及面向内部评审的核心参考文档。

## 当前权威入口

- [研发中心 AI 数字员工研发流程规划](研发中心AI数字员工研发流程规划.md)：当前唯一活动流程提案，文档版本 2，状态 `proposed`。
- [ADR-001：WorkBuddy 与 Codex CLI 的集成边界](docs/adr/ADR-001-workbuddy-codex-integration-boundary.md)：一期采用输入/输出契约松耦合，不直接编排个人 Codex CLI。
- [ADR-002：嵌入式系统专家团架构与落地边界](docs/adr/ADR-002-embedded-system-expert-team-architecture.md)：冻结 digital-worker SSOT、1+7 组织、Evidence-first、独立验证与高风险动作边界。
- [嵌入式系统专家团机器资产](expert-groups/embedded-system/README.md)：当前 `0.6.0 / pilot-operations-ready`。
- [嵌入式系统专家团-核心参考](嵌入式系统专家团-核心参考/)：与产品专家团核心参考同类型的人工可读解释层，当前状态 `review-ready`。
- [真实 Pilot Runbook](docs/runbooks/embedded-pilot.md)：真实任务绑定、执行、证据打包、指标聚合和 productionization review 门槛。

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
├── 产品专家团-核心参考/      # 已落地产品专家团的人类可读参考
└── 嵌入式系统专家团-核心参考/# 嵌入式专家团内部评审/解释层
```

## 当前状态

|对象|状态|说明|
|---|---|---|
|研发中心研发流程|`proposed`|待组织责任方、权限、飞书接口和试点范围确认|
|嵌入式专家团架构|`architecture-frozen`|1+7、Workflow、Gate、Contract、Evidence、Autonomy 已冻结|
|嵌入式专家团实现|`pilot-operations-ready`|真实 Pilot 的 init/complete/validate/bundle/metrics 工具链已就绪|
|嵌入式核心参考|`review-ready`|已进入 main，可用于内部讨论；尚未标记 `reviewed-baseline`|
|真实 Pilot|`pending-real-binding`|#6/#7/#8 仍待真实 Debug / Feature / Review-Release 工作项|
|端侧底座 ownership|`evidence-needed`|#11；原始文档待规范化后逐域裁决|
|main 强制门禁|`admin-action-needed`|#12；现有 CI 已通过，但 branch protection/required check 仍需管理员启用|
|Production Ready|**禁止声明**|需真实 Pilot evidence + 独立 productionization review|

## 权威与历史规则

1. 活动设计只保留稳定路径；不再用 `_V3/_V4` 文件名复制当前文档。
2. 历史草案放 `docs/archive/`；更完整历史由 Git history 提供。
3. 原始 docx/二进制输入统一放 `docs/source-materials/`，不是运行时 SSOT。
4. 嵌入式专家团机器资产冲突时，以 [`governance/authority-index.md`](expert-groups/embedded-system/governance/authority-index.md) 的顺序裁决。
5. 两套“核心参考”是解释层/评审层，不得覆盖 Workflow、Policy、Contract、Schema 等机器契约。
6. `agent-dev-kit`、`knowledge-hub`、`codex` 等外部仓库只作方法参考或未来可选连接，不是本仓运行前置依赖。

## 历史与原始输入

- [历史草案索引](docs/archive/README.md)
- [原始输入材料索引](docs/source-materials/README.md)
- [产品专家团-核心参考](产品专家团-核心参考/)

下一步优先完成 #6/#7/#8 三条真实 Pilot、#11 ownership resolution 与 #12 main required CI；在真实证据出现前，不再无证据扩张 Agent/P1 Skill 或自动化权限。
