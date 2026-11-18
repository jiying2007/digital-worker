# digital-worker

> **日常采用收敛 / 退役候选**（2026-11-18）：本仓已不应成为个人或小团队研发的执行依赖。三类任务模板已通过 [engineering-platform PR #308](https://github.com/jiying2007/engineering-platform/pull/308) 合入 `tool/examples/templates/`，并经过 PR 的发行包安装烟测；现在直接从 `eng` 发行包使用模板，或继续直接用已有 CLI + ADK。**本仓保留的 Formal L2 证据集成、历史记录和唯一来源资料尚未完成退出核验，暂时不能删除仓库。** 具体边界见[退役与证据保全清单](docs/strategy/retirement-path.md)。

给个人和小团队使用的工程任务模板、嵌入式工作方法与证据参考。选择下面一种模板，放进现有项目的 Issue、PR/MR 或任务文件，即可沿用自己的模型 CLI、ADK、Git 和项目 CI 开始工作。

## 从一个实际任务开始

| 任务 | 最少提供什么 | 交付什么 |
|---|---|---|
| [排查与修复](docs/templates/debug-fix.md) | 现象、环境、日志或复现、期望行为 | 已确认事实、待验证假设、修复或下一项验证 |
| [功能与变更](docs/templates/feature-change.md) | 目标、影响范围、约束、验收命令 | 可审查 diff、实际构建/测试结果、使用说明 |
| [审查与发布准备](docs/templates/review-release.md) | 目标分支或 commit、关注范围、发布条件 | 按严重程度排列的发现、检查结果、发布准备情况 |

1. 复制所选模板到项目已有的任务记录，填写目标、已有材料和验收范围；不相关项可删除。
2. 在已获准的项目和 Runtime 中执行。沿用现有 ADK 方法，源码修改、构建和测试留在项目工作区。
3. 把 diff、实际检查结果、日志/产物引用和未验证项写回同一任务或 PR，按项目规则接受交付。

使用模板只需要阅读或复制 Markdown，无需安装本仓工具，也无需注册 Digital Worker Work/Run 或手写回执 JSON。项目 Issue/PR 是原有业务记录；一次执行的本地编号只用于定位日志和现场。多个仓库的需求可拆成有关联的任务，明确接口、依赖顺序和各自结果。

## 按任务范围判断完成

文档或普通代码修改使用项目约定的检查；驱动修改可以先交付 patch 和主机编译结果，并明确待设备验证。若任务原本要求验证设备行为，缺少设备时仍为待处理，只有责任人明确缩小范围后才能按较小范围接受。

记录检查的**通过、失败、跳过、未运行或未知**，以及实际命令和结果引用。模型退出成功、主机测试通过、硬件验证通过和产品发布是不同事实。个人任务按风险和仓库规则审核；声称独立审核时，必须存在相应审核。设备写入、生产 OTA、OTP/Fuse 或破坏性操作按具体任务授权处理。

## 需要深入时再查参考

- [采用方式与维护范围](docs/strategy/small-team-optional-adoption.md)：日常项目入口、方法去重和现有资产的处理方式。
- [方法、正式工具与历史证据索引](docs/reference-index.md)：按用途查找现有专业资料、显式选用的正式流程和原始证据。
- [嵌入式核心参考](嵌入式系统专家团-核心参考/)：Linux/BSP、MCU/RTOS、驱动、排障和验证方法，按当前问题选读。
- [SKILLS.md](SKILLS.md)：保留的 Skill 定义与评测状态；[当前机器 Review Snapshot](嵌入式系统专家团-核心参考/00-评审导览/03%20当前机器状态快照.md) 是派生视图，不能替代实际任务效果。

## 显式选择正式证据集成

已有 Edge Foundation、canonical routing、Pilot、Runtime R2 和 Product readiness 工具继续服务于**显式采用这些合同的任务**。它们校验输入、引用和冻结证据，工程执行、设备验证和责任人的接受仍需实际发生。入口是[正式 Pilot Quickstart](docs/runbooks/embedded-closed-loop-quickstart.md)和[本地工具操作](docs/runbooks/tool-quality.md)。

保留的 `FEATURE-PCR02-OTA-001` 证明过 OTA 包身份校验这一具体 Feature；它不证明设备安装、boot、rollback 或整套 Skills 的实际效果。原始证据、SHA、Run ID 和未完成状态按原范围保留，详见[历史证据索引](docs/reference-index.md#历史证据与版本边界)。

`engineering-platform` 是独立工具方案。采用本仓模板不依赖它，使用它也不要求部署本仓。ADK 继续负责可复用方法和资源分发；有价值的经验按需进入 Knowledge Hub。维护重点是可直接使用的方法、准确入口和现有消费者的问题，不扩建第二套日常执行器或需求台账。
