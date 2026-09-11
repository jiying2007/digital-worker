# 11 Workflow、Gate 与工程交接

> 同步基线：`v0.7.0 / provider-neutral`

## 1. 设计目标

Workflow 确保不同风险任务走**最小正确链路**，并让关键状态有机器可读 artifact；它不绑定某个 Interaction、Knowledge 或 Engineering Runtime Provider。

权威文件：`task-modes.yaml / workflow.yaml / gate-policy.yaml / material-requirements.yaml / engineering-handoff.yaml`。

## 2. Mode Path

- full/short/diagnostic/bringup：K → M → 0 → Triage → Analysis → T → E → Execution → V → R → C；
- review_only：K → M → 0 → Triage → Analysis → T → R → C；
- release_chain：K → M → 0 → Triage → Analysis → T → V → R → C；
- single_expert：K → M → 0 → Triage → Analysis → T → C。

`review_only` 禁止隐式 Execution；`single_expert` 不自动扩链；release 需要代码修改时显式扩 mode。

## 3. Gate K / M / 0

- K：所需知识 source 是否可信、可定位、版本/权限是否满足；
- M：repo/base/board/SDK/schematic/firmware/log/device identity 是否足够；
- 0：goal/scope/boundary/constraints/acceptance 是否清楚。

三个 Gate 可以在 UI 合并呈现，但底层风险语义保持分离。

## 4. Gate T

输出 solution、impact、dependency、risk、verification plan、rollback、unresolved items。

## 5. Gate E：Engineering Handoff

```text
Expert Team
  → engineering-task-package
  → Engineer + Engineering Agent Runtime
  → delivery-receipt
```

Runtime Provider 为 `selectable`。Codex、Claude Code、IDE Agent、内部 Agent 都只是候选实现。

Handoff 的稳定约束：

- exact repo/base；
- work item identity；
- acceptance；
- action ceiling；
- required verification；
- evidence / blocker / unverified items；
- runtime/provider 更换不得改变上述语义。

办公/协作入口不得因“能调用工具”就直接获得开发机、设备或 Release 控制权；任何自动执行都必须进入相同 Action Policy 与审计链。

## 6. Delivery Receipt 的含义

Receipt 记录“执行发生了什么”，至少涵盖 executor identity、base、change、commands、build/test status、artifact/hash、evidence、blocker、risk、next action。

它不是 Verification Report。当前 `executor_identity` 仍是轻量字段；是否拆成 runtime/provider/model/version，由 #18 Multi-runtime Pilot 的真实需求决定。

## 7. Gate V / R / C

- V：按 implemented/host/cross-build/SIL/device/HIL/release 分层验证；
- R：独立审查风险和放行充分性；
- C：manifest 完整、blocker resolved/accepted、状态未夸大才收口。

## 8. Recovery

缺信息回 `needs_information`；Verification/Review 失败返回 precise responsible stage；run-state + gate-ledger 支持断点恢复，禁止无意义整链重跑。

## 9. Provider-neutral 的稳定点

```text
Expert Team = 判断/方案/约束
Engineering Agent Runtime = 受控工程执行
Verification = 独立证据判断
Review = 独立放行审查
```

Runtime 可换，Contract/Gate/Evidence 不换。这是当前最重要的稳定接口之一。

## 10. 评审重点

- 是否至少维持两个可替换 Runtime；
- Runtime fallback / cancel / retry 如何纳入 receipt；
- 是否需要独立 `agent-runtime-receipt`；
- short_chain 是否还能进一步缩短而不削弱 V/R 安全边界。
