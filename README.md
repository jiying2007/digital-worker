# 数字员工方案索引

## 当前提案

- [研发中心 AI 数字员工研发流程规划 V2](研发中心AI数字员工研发流程规划_V2.md)：结合 WorkBuddy 企业版、飞书、飞书知识库、内网 WeKnora 和 Codex CLI 的总体方案。
- [ADR-001：WorkBuddy 与 Codex CLI 的集成边界](docs/adr/ADR-001-workbuddy-codex-integration-boundary.md)：一期采用输入/输出契约松耦合、暂不直接编排个人 Codex CLI。
- [嵌入式系统专家团当前阶段终版设计 V1](docs/architecture/embedded-system-expert-team-v1.md)：冻结嵌入式专家团架构基线。
- [ADR-002：嵌入式系统专家团架构与落地边界](docs/adr/ADR-002-embedded-system-expert-team-architecture.md)：记录 digital-worker SSOT、1+7、契约式交接和独立验证等核心决策。
- [嵌入式系统专家团目录](expert-groups/embedded-system/README.md)：当前已具备 Governance、1+7 Core Experts、23 个 P0 Skills、Engineering Handoff、跨团队 Contract、Golden Cases、Pilot Contracts/Evaluator 和自动 CI。
- [嵌入式系统专家团真实 Pilot Runbook](docs/runbooks/embedded-pilot.md)：真实试点接入、证据留存和生产化资格门槛。

## 历史与参考材料

- [研发中心 AI 数字员工研发流程规划 V1](研发中心AI数字员工研发流程规划_V1.md)：前一版规划草案。
- `研发中心AI数字员工办公体系改造方案（预案）.docx`：办公体系预案。
- `端侧底座专家团创建.docx`：端侧专家团场景参考；当前具体 ownership 尚待原文规范化后逐项裁决。
- [`产品专家团-核心参考/`](产品专家团-核心参考/)：已在落地应用中的专家团工程化参考。
- `硬件电路-举例/硬件电路开发模块（举例）.docx`：硬件研发场景参考。

## 状态说明

- 研发中心研发流程 V2 与 ADR-001 当前仍为 `proposed`。
- 嵌入式系统专家团架构为 `architecture-frozen`；实现状态为 `pilot-infrastructure-ready`。这表示真实 Pilot 所需契约、模板、评分和 CI 已具备，但尚无 3 条真实轨道的 completed evidence，因此仍不是 Production Ready。
- 嵌入式系统专家团正式资产以本仓为 SSOT；其他外部仓库仅作参考或未来可选集成。

下一步不是继续堆 Agent/Skill，而是绑定真实 Debug、Feature、Review/Release 三类工作项完成 Pilot；通过安全门槛后也只能进入单独的人工 productionization review。
