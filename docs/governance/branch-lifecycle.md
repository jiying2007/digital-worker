# Branch Lifecycle Governance

- Status: active-governance
- Scope: `jiying2007/digital-worker`

## 1. 默认模型

`main` 是默认唯一长期分支。`feat/*`、`docs/*`、`design/*`、`refactor/*`、`fix/*` 等均视为任务分支，不作为历史存档。

## 2. 创建要求

任务分支应绑定明确目标/Issue/PR，并从已知 exact main SHA 创建。分支名描述任务，不描述个人。

## 3. 合并后 GC

满足以下条件后删除远端任务分支：

1. PR 已 merge；
2. main push CI 已 success；
3. 需要保留的 evidence/decision 已进入 main、PR、Issue 或 artifact system；
4. 没有 open PR/未完成恢复点依赖该分支。

Git history / merged PR 已提供历史，不通过长期保留任务分支实现归档。

## 4. 长期分支例外

只有 research/release 等确有生命周期需求时才允许长期存在，并必须登记：purpose、owner、exact head、created_at、expiry/review date、GC condition、open PR/issue link。没有这些字段的长期分支视为治理债务。

## 5. 禁止

- 合并完成后无限期保留任务分支；
- 以分支替代 release tag / artifact / evidence；
- 对有 open PR 或未归档 evidence 的分支直接 GC；
- force-push `main`；
- 使用长期漂移分支名代替正式 Pilot 的 exact base identity。

## 6. 当前清理

现有历史残留由 Issue #19 跟踪。当前连接不提供 delete-ref 能力，因此实际删除需要 GitHub UI 或本地 `git push origin --delete <branch>` 完成。

## 7. Review cadence

建议每次主要阶段收口或至少每月检查远端分支；默认期望状态是 `main` + 少量明确登记的活动分支。
