# docs 目录说明

`docs/` 承载跨专家团的架构决策、阶段策略、评审决策包、治理规则、运行手册、头脑风暴归档、历史归档和原始输入。专家团正式机器资产放 `expert-groups/`，共享 Schema 放根 `schemas/`。

## 目录

- `adr/`：Architecture Decision Record；
- `strategy/`：当前阶段已收敛、可指导实施但不覆盖 ADR/Contract 的策略基线；
- `review/`：正式架构评审前的 Pre-read、Decision Matrix、Evidence Gap、RACI、Walkthrough；
- `governance/`：跨仓治理规则，如 branch lifecycle；
- `runbooks/`：可执行运行手册；
- `brainstorm/`：有参考价值但尚未形成正式决策的设计备忘；
- `archive/`：退出活动设计的历史草案；
- `source-materials/`：原始 docx/外部输入，非机器运行 SSOT。

## 规则

1. 当前权威文档使用稳定路径，不复制 `_V2/_V3/_final`；
2. `strategy/` 规定阶段实施范围、顺序和退出条件，但不得覆盖 ADR / Contract / Schema；需要改变稳定架构语义时必须进入正式评审；
3. `review/` 是决策准备材料，不覆盖 ADR / Contract / Schema；评审结论必须回写正式权威资产或 Issue；
4. 历史由 Git history 提供，必要人工对照稿进 `archive/`；
5. 二进制输入统一放 `source-materials/`；
6. 原始材料只有在规范化、引用、来源核验后才能进入正式 Contract/ownership/decision；
7. 专家团解释性长文进入对应 `*-核心参考/`；
8. Provider-specific 事实不得覆盖 ADR-003 的 Provider-neutral 上位原则；
9. 任务分支生命周期遵循 `governance/branch-lifecycle.md`；
10. `brainstorm/` 允许保留未验证、互相竞争或最终被否决的想法，但不得覆盖正式资产。

## Current Stage Strategy

当前嵌入式落地基线：`strategy/embedded-domain-closed-loop-v1.md`。

核心原则：Enterprise Digital Thread 不是 Embedded Domain Closed Loop 的前置条件；当前先用真实 Pilot 验证 One Work Item/Run、共享 Context、Hypothesis、exact identity、Acceptance→Evidence、Knowledge Harvest 与 Knowledge Registry 七项最小闭环。

## Architecture Review

正式评审请从 `review/README.md` 开始，优先读 Pre-read 和 Decision Matrix；深层资料再回到 ADR、核心参考和机器 Contract。

## Brainstorm Archive

当前已归档企业 Digital Thread、渐进式 AI 落地和嵌入式内部 Engineering Thread 等非结论型备忘。
