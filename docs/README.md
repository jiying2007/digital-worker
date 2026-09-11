# docs 目录说明

`docs/` 只承载跨专家团的架构决策、运行手册、历史归档和原始输入材料。专家团正式机器资产放在 `expert-groups/`，跨专家团共享 Schema 放在根 `schemas/`。

## 当前总体架构入口

- `../研发中心AI数字员工研发流程规划.md`：当前总体提案，文档版本 3；
- `adr/ADR-003-provider-neutral-ai-rd-target-architecture.md`：Provider-neutral 总体架构上位 ADR；
- `adr/ADR-001-workbuddy-codex-integration-boundary.md`：局部/历史 Provider 场景 ADR，已 `superseded-in-part`；
- `adr/ADR-002-embedded-system-expert-team-architecture.md`：嵌入式专家团正式架构边界。

## 目录

- `adr/`：Architecture Decision Record。对架构边界和长期决策负责。
- `runbooks/`：可执行运行手册，不承担架构裁决。
- `archive/`：已经退出活动设计的历史草案，仅供追溯。
- `source-materials/`：原始 docx/外部输入。它们是来源材料，不是机器运行 SSOT。

## 规则

1. 当前权威文档使用稳定路径，不通过 `_V2/_V3/_final` 复制文件实现版本管理。
2. 总体架构遵循 `Provider 可替换，Contract 稳定；Source of Truth stays at source`。
3. 历史版本由 Git history 提供；确需保留便于人工对照的历史草案时放入 `archive/`。
4. 二进制原始材料统一放 `source-materials/`，不得散落仓库根目录。
5. 原始材料中的事实只有在被规范化、引用并完成来源核验后，才可进入正式 Contract/ownership/decision。
6. 专家团解释性长文优先进入对应 `*-核心参考/`，避免在 `docs/architecture/` 再维护一份重复总设计。
7. WorkBuddy、飞书、WeKnora、Codex、Claude 等 Provider-specific 文档/配置不得反向覆盖 ADR-003 的总体边界。
