# 工程交接、Runtime 与关键产物

## 1. 工程交接解决什么问题

专家分析的结果如果只是一段建议，工程师接手后仍要重新理解目标、版本、验收和风险。Engineering Handoff 的目标是把技术判断整理成一个能直接进入工程执行的任务包。

## 2. Engineering Package 至少包含

- work_item / run identity；
- repo root + exact base commit；
- dirty baseline；
- goal / non-goal；
- implementation plan；
- interface/constraint；
- acceptance criteria；
- allowed / forbidden actions；
- required verification；
- evidence / knowledge refs；
- risks / blockers / unverified items；
- rollback/containment（需要时）。

如果工程师拿到 package 后仍必须追问“到底改哪个版本、什么叫完成”，Gate E 就没有通过。

## 3. Runtime 是执行环境，不是工程结论

可使用 Codex、Claude Code、IDE Agent、内部 Runtime 或其他受控工具。它们之间可以能力不同，但都必须遵守同一 Package 和 Action Policy。

### L0 Quick Assist

适合低风险解释、阅读、局部分析。通常停留在 A0-A2。

### L1 Governed Engineering

日常正式工程模式。允许在确认 repo/base/dirty baseline 后执行 A3/A4，并保留工程 receipt。

### L2 Formal Evidence

用于真实 Pilot、Release、高风险、多 Runtime 对照。除 L1 内容外，还要求更完整的 source-set/runtime/session identity、Evidence 和独立 Verification/Review。

运行等级描述的是治理深度，不代表模型“智力等级”。

## 4. Session Bootstrap

会话启动时装配：

- project/repo；
- mode；
- contract；
- ADK asset/release；
- provider/runtime identity；
- knowledge access；
- action ceiling。

Bootstrap 只负责把一次任务的环境装对，不能在里面保存长期 Gate、Verification 或知识 SSOT。

## 5. Delivery Receipt

Receipt 记录“实际做了什么”，至少包括：

- executor/runtime identity；
- base；
- changed files/patch identity；
- commands；
- build/test 状态；
- artifact/hash；
- evidence；
- blocker/risk；
- next action；
- 仍需哪些 Verification。

它不是 Verification Report。

## 6. Runtime 切换

当 Runtime 中断、表现不佳或需要对照时：

1. 冻结当前 worktree/receipt；
2. 记录已完成和未完成步骤；
3. 保留原 Engineering Package；
4. 新 Runtime 从明确 resume point 开始；
5. 不把前一个 Runtime 的最终答案/patch 泄漏给对照 Runtime（正式对比场景）；
6. 最终使用相同 Verification 标准。

## 7. 关键产物关系

```text
task-brief
   ↓
material-manifest / knowledge-readiness
   ↓
task-charter
   ↓
routing-decision
   ↓
technical-analysis
   └─ debug: hypothesis-registry
   ↓
technical-decision
   ↓
engineering-task-package
   ↓
delivery-receipt
   ↓
verification-report
   ↓
review-report
   ↓
deliverable-manifest
   ↓
knowledge-harvest
```

## 8. 关键字段示例

以下只帮助人理解，完整字段以 Schema 为准。

### Task Brief

```yaml
work_item_id: EMB-2026-001
owner: embedded-team
repo_roots: [firmware/linux]
goal: 修复目标板 UBIFS 异常只读
non_goals: [不修改量产分区布局]
acceptance:
  - 原复现条件不再触发只读
  - 24h stress 无新增 ECC/UBI error
allowed_actions: [A0_READ, A1_ANALYZE, A2_GENERATE]
```

### Hypothesis Registry

```yaml
- id: H1
  statement: 底层返回了不可纠正 ECC，触发上层错误路径
  status: open
  evidence_for: [log-ref-01]
  evidence_against: []
  experiment: 对齐 ECC status 与 MTD return code
```

### Engineering Package

```yaml
repo: firmware/linux
base_commit: 0123456789abcdef0123456789abcdef01234567
scope: [drivers/mtd/...]
action_ceiling: A4_BUILD_TEST
required_verification:
  - cross_build_verified
  - device_verified
```

### Acceptance → Evidence

```text
AC-01 原复现条件不再只读
  → device_verified
  → board A3 + firmware sha256:...
  → evidence HIL/DEVICE-RUN-123
  → PASS
```

## 9. 产物“存在”不等于“有效”

文档或 JSON 文件存在只能说明生成过。有效性还要看：

- identity 是否对得上；
- required field 是否完整；
- evidence ref 是否可访问；
- hash 是否匹配；
- 状态是否与事实一致；
- 是否经过所需 Verification/Review。

因此系统既需要 Schema，也需要真实运行证据。
