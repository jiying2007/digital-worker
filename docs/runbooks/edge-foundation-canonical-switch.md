# 端侧底座规范路由切换干运行说明

> 本文只描述 phase-3 **规范路由（canonical routing）切换**的预演与评审边界，不执行真实切换。

## 1. 前置条件

必须先完成：

1. Debug / Feature / Review-Release 三轨真实 Pilot；
2. 每个真实 Pilot 生成合格的端侧底座影子凭证；
3. `phase3-readiness` 输出 `ELIGIBLE_FOR_REVIEW`；
4. 生成 `edge-foundation-phase3-review-package.json`；
5. 独立评审确认评审包证据充分。

任何一步仍为 `BLOCKED` 时，不得进入真实 canonical routing switch。

## 2. 生成干运行计划（Dry-run Plan）

```bash
python scripts/generate_edge_foundation_canonical_switch_plan.py \
  edge-foundation-phase3-review-package.json \
  --output edge-foundation-canonical-switch-plan.json
```

输出必须保持：

```text
status = DRY_RUN_ONLY
apply_allowed = false
canonical_routing_switched = false
```

干运行计划用于约束未来真实切换 PR 的变更范围，不是批准书，也不会修改仓库路由。

## 3. Phase-3 允许修改的内容

只允许以下三类变更：

- `canonical-routing-authority`：规范路由责任主体从旧嵌入式 `1+7` 切换到 `edge-foundation`；
- `migration-phase-status`：更新 phase-3 的迁移状态；
- `routing-selector-entrypoint`：把任务选择入口指向已经验证的新责任路由。

## 4. Phase-3 明确禁止夹带的内容

同一个切换 PR 不允许包含：

- 删除旧身份（legacy identity removal）；
- 废弃旧身份（legacy identity deprecation）；
- 大规模改写 Skill owner；
- 修改 Pilot 晋级阈值；
- 扩大 A0-A7 动作权限；
- 修改 Verification 独立性；
- 修改 Independent Review 独立性；
- 绑定 WorkBuddy、Codex 或其他具体 Provider；
- 改变 Source of Truth（权威来源）边界；
- 宣布 Production Ready。

旧 `1+7` 在 phase-3 后仍必须作为**旧版兼容表面（legacy compatibility surface）**保留。

## 5. 后续阶段必须分开

```text
Phase-3  canonical routing switch
   ↓
Phase-4  legacy identity deprecation（旧身份废弃标记）
   ↓
Phase-5  proven removal（证据充分后的删除）
```

Phase-4 / Phase-5 不得与 Phase-3 合并成一次大爆炸重构。

## 6. 必须保留的不变量

切换前后都必须保持：

- Engineering（工程实施）≠ Verification（验证）≠ Independent Review（独立审查）；
- Provider-neutral（供应商/运行时中立）；
- Source of Truth stays at source（权威事实保留在原始来源）；
- A0-A7 权限不因路由切换自动扩大；
- 真实 Pilot、Evidence（证据）与评审记录继续可追溯。

## 7. 回退

真实切换后若出现责任路由回归，回退 authority 为：

```text
legacy-embedded-1plus7
```

回退只恢复 canonical routing authority，不删除已经产生的 Pilot / readiness / review / switch evidence。失败必须留下可审计记录，不能通过 reset 历史来“假装未发生”。

## 8. 当前状态

当前仓库仍处于真实 Pilot 证据等待阶段，因此 dry-run Contract 可以被测试，真实 switch 不允许执行。
