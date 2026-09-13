# Branch Lifecycle Governance

- Status: active-governance
- Scope: `jiying2007/digital-worker`

## 1. 默认模型

`main` 是默认唯一长期分支。`feat/*`、`docs/*`、`design/*`、`arch/*`、`refactor/*`、`fix/*`、`chore/*`、`codex/*` 等均视为任务分支，不作为历史存档。

其中 `arch/*` 用于 ADR/跨仓边界/架构 Contract 等阶段性架构工作；`codex/*` 用于受控自动化/Codex 任务工作。二者与 `design/*` 一样仍是临时任务分支，不能因为名称特殊就成为长期漂移分支。

## 2. 创建要求

任务分支应绑定明确目标/Issue/PR，并从已知 exact main SHA 创建。分支名描述任务，不描述个人身份；自动化创建的 `codex/*` 仍必须满足相同 PR/CI/GC 约束。

## 3. 合并后 GC

满足以下条件后删除远端任务分支：

1. PR 已 merge；
2. main push CI 已 success；
3. 需要保留的 evidence/decision 已进入 main、PR、Issue 或 artifact system；
4. 没有 open PR/未完成恢复点依赖该分支；
5. 分支不是 protected branch，也不是 `main`。

Git history / merged PR 已提供历史，不通过长期保留任务分支实现归档。

## 4. 受控 Branch GC Workflow

正式 GC 入口：`.github/workflows/branch-gc.yml`。

治理模型：

- 长期入口包含手动 `workflow_dispatch`；
- 允许 `dry_run=true` 只校验不删除；
- 待删除分支必须先进入 `.github/branch-gc-allowlist.txt`，因此删除范围必须经过 PR review / main history；
- workflow 使用最小必要权限：`contents: write` + `pull-requests: read`；
- GitHub Action 使用 immutable full-SHA pin；
- 每个分支删除前 fail-closed 校验：branch exists、`branch != main`、not protected、open PR = 0、merged PR evidence >= 1；
- 分支已不存在时幂等跳过；
- 删除后输出剩余远端分支用于审计。

### Bootstrap 行为

当前阶段额外允许：当 `.github/workflows/branch-gc.yml` 或其 allowlist 通过 PR 合入 `main` 时，以 `push + exact audited path` 自动触发一次 GC。它仍使用相同 allowlist 与安全校验，不扩大删除范围。

如果后续确认手动模式足够，可单独 PR 移除这个 bootstrap `push` trigger，仅保留 `workflow_dispatch`。

## 5. 长期分支例外

只有 research/release 等确有生命周期需求时才允许长期存在，并必须登记：purpose、owner、exact head、created_at、expiry/review date、GC condition、open PR/issue link。没有这些字段的长期分支视为治理债务。

## 6. 禁止

- 合并完成后无限期保留任务分支；
- 以分支替代 release tag / artifact / evidence；
- 对有 open PR 或未归档 evidence 的分支直接 GC；
- 把 `main` 放入 GC allowlist；
- 删除 protected branch；
- 使用通配/枚举所有远端分支后直接批量删除；
- force-push `main`；
- 使用长期漂移分支名代替正式 Pilot 的 exact base identity。

## 7. CI 防回归

`scripts/validate_branch_gc.py` 由 `Embedded Expert Contracts` 执行，至少检查：

- workflow / allowlist 存在；
- `workflow_dispatch` 存在；
- `contents: write` / `pull-requests: read` 权限存在；
- checkout Action 保持 exact SHA pin；
- `main` 明确拒绝；
- protected/open-PR/merged-PR 校验存在；
- 删除动作仍限定 Git branch ref；
- allowlist 不含 `main`、无重复、只允许批准的任务分支前缀（含 `arch/` 与 `codex/`）。

## 8. 当前清理

当前 merged branch GC 由 Issue #19 跟踪。allowlist 只保留当前明确需要清理的已审计任务分支；历史已删除分支应从 live allowlist 移除。

## 9. Review cadence

建议每次主要阶段收口或至少每月检查远端分支；默认期望状态是 `main` + 少量明确登记的活动分支。
