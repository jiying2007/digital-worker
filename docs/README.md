# docs 目录说明

`docs/` 承载跨专家团的架构决策、治理规则、运行手册、历史归档和原始输入。专家团正式机器资产放 `expert-groups/`，共享 Schema 放根 `schemas/`。

## 目录

- `adr/`：Architecture Decision Record；
- `governance/`：跨仓治理规则，如 branch lifecycle；
- `runbooks/`：可执行运行手册；
- `archive/`：退出活动设计的历史草案；
- `source-materials/`：原始 docx/外部输入，非机器运行 SSOT。

## 规则

1. 当前权威文档使用稳定路径，不复制 `_V2/_V3/_final`；
2. 历史由 Git history 提供，必要人工对照稿进 `archive/`；
3. 二进制输入统一放 `source-materials/`；
4. 原始材料只有在规范化、引用、来源核验后才能进入正式 Contract/ownership/decision；
5. 专家团解释性长文进入对应 `*-核心参考/`；
6. Provider-specific 事实不得覆盖 ADR-003 的 Provider-neutral 上位原则；
7. 任务分支生命周期遵循 `governance/branch-lifecycle.md`。
