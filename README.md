# 数字员工方案索引

## 当前提案

- [研发中心 AI 数字员工研发流程规划 V2](研发中心AI数字员工研发流程规划_V2.md)：结合 WorkBuddy 企业版、飞书、飞书知识库、内网 WeKnora 和 Codex CLI 的总体方案。
- [ADR-001：WorkBuddy 与 Codex CLI 的集成边界](docs/adr/ADR-001-workbuddy-codex-integration-boundary.md)：记录一期采用输入/输出契约松耦合、暂不直接编排个人 Codex CLI 的决策依据。
- [嵌入式系统专家团当前阶段终版设计 V1](docs/architecture/embedded-system-expert-team-v1.md)：冻结嵌入式软件专家团的组织、任务分类、Workflow、Gate、Contract、Evidence、自治边界与评测基线。
- [ADR-002：嵌入式系统专家团架构与落地边界](docs/adr/ADR-002-embedded-system-expert-team-architecture.md)：记录 digital-worker 作为专家团 SSOT、1+7 组织模型、契约式工程交接和独立验证等核心架构决策。
- [嵌入式系统专家团目录](expert-groups/embedded-system/README.md)：机器可读 manifest、任务路由与 workflow skeleton 的正式落地点。

## 历史与参考材料

- [研发中心 AI 数字员工研发流程规划 V1](研发中心AI数字员工研发流程规划_V1.md)：前一版规划草案。
- `研发中心AI数字员工办公体系改造方案（预案）.docx`：办公体系预案。
- `端侧底座专家团创建.docx`：端侧专家团场景参考。
- [`产品专家团-核心参考/`](产品专家团-核心参考/)：已在落地应用中的专家团工程化参考，供嵌入式系统专家团复用 Team Lead、Gate、run-state、I/O Contract、Schema、断点恢复和交付治理方法。
- `硬件电路-举例/硬件电路开发模块（举例）.docx`：硬件研发场景参考。

## 状态说明

- 研发中心研发流程 V2 与 ADR-001 当前仍为 `proposed`。
- 嵌入式系统专家团 V1 为 `frozen-for-implementation` / `architecture-frozen`：表示当前阶段架构基线已冻结，可进入实现，不代表生产能力已经完成。
- 嵌入式系统专家团的 Agent、Skill、Workflow、Schema 等正式资产以本仓为 SSOT；其他外部仓库仅作参考或未来可选集成，不构成当前运行前置依赖。

完成身份映射、知识权限、飞书工作项接口和试点产品范围确认后，再由决策人评审研发流程 V2/ADR-001 是否转为 `accepted`。嵌入式专家团后续按 Governance Skeleton → Core Experts → P0 Skills → Engineering Handoff → Cross-Team Contract → Golden Cases/Pilot 顺序推进。
