# docs 目录说明

`docs/` 承载跨专家团的架构决策、治理规则、运行手册、头脑风暴归档、历史归档和原始输入。专家团正式机器资产放 `expert-groups/`，共享 Schema 放根 `schemas/`。

## 目录

- `adr/`：Architecture Decision Record；
- `governance/`：跨仓治理规则，如 branch lifecycle；
- `runbooks/`：可执行运行手册；
- `brainstorm/`：有参考价值但尚未形成正式决策的设计备忘；
- `archive/`：退出活动设计的历史草案；
- `source-materials/`：原始 docx/外部输入，非机器运行 SSOT。

## 规则

1. 当前权威文档使用稳定路径，不复制 `_V2/_V3/_final`；
2. 历史由 Git history 提供，必要人工对照稿进 `archive/`；
3. 二进制输入统一放 `source-materials/`；
4. 原始材料只有在规范化、引用、来源核验后才能进入正式 Contract/ownership/decision；
5. 专家团解释性长文进入对应 `*-核心参考/`；
6. Provider-specific 事实不得覆盖 ADR-003 的 Provider-neutral 上位原则；
7. 任务分支生命周期遵循 `governance/branch-lifecycle.md`；
8. `brainstorm/` 允许保留未验证、互相竞争或最终被否决的想法，但不得覆盖 ADR / Contract / Schema / Governance；正式采纳时应回链到对应 ADR 或机器资产。

## Brainstorm Archive

当前已归档：

- `brainstorm/enterprise-ai-rd-embedded-digital-thread.md`：企业经营 → 产品研发 → 嵌入式上下游 → Verification / Manufacturing / Field → RCA / Knowledge 的 Digital Thread 设想，以及 Business / Engineering / Learning 三闭环、企业对象图和候选跨团队 Contract。
