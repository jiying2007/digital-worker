# 文档入口

日常任务从[排查与修复](templates/debug-fix.md)、[功能与变更](templates/feature-change.md)、[审查与发布准备](templates/review-release.md)三份 Markdown 模板开始。复制到项目已有记录，沿用项目的 Runtime、ADK、Git 与 CI。

## 按需要阅读

| 用途 | 入口 |
|---|---|
| 采用方式和维护范围 | [小团队按需采用与资产保留](strategy/small-team-optional-adoption.md) |
| 专业方法、正式工具和历史证据 | [参考索引](reference-index.md) |
| 嵌入式排障、设计、验证案例 | [嵌入式核心参考](../嵌入式系统专家团-核心参考/) |
| 显式采用正式 Pilot 合同 | [Quickstart](runbooks/embedded-closed-loop-quickstart.md)、[本地工具操作](runbooks/tool-quality.md) |

## 保留资料的用途

- `templates/`：可直接放进项目记录的三类任务说明。
- `adr/`、`strategy/`、`governance/`：已接受的采用边界、架构决策和正式集成规则；按各自适用范围阅读。
- `runbooks/`：现有工具的操作手册。使用模板无需执行其中的正式证据流程。
- `source-materials/`、`archive/`、`brainstorm/`：原始输入、历史草案和探索记录；不作为当前任务已完成的证明。

显式使用正式集成时，Edge Foundation 的 canonical 合同仍由 `domains/edge-foundation/` 和相关 ADR 定义；专业参考解释这些合同，不产生第二份权威规则。Product readiness、Runtime 资格和项目交付按各自真实证据判断，采用范围收敛不会提升任何历史结果。

普通修订通过 Git history 追溯。已有原始证据保留原路径、ID、commit、digest 和结果语义；不为整理入口批量迁移、删除或重写状态。
