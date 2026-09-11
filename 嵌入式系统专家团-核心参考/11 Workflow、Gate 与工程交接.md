# 11 Workflow、Gate 与工程交接

## 1. 设计目标

Workflow 的价值不是把所有任务都拉长，而是确保不同风险/类型的任务走**最小正确链路**，并让每个关键状态有机器可读 artifact。

权威文件：

- `config/task-modes.yaml`
- `config/workflow.yaml`
- `config/gate-policy.yaml`
- `config/material-requirements.yaml`
- `contracts/engineering-handoff.yaml`

---

## 2. Mode Path

### full_chain

```text
K → M → 0 → Triage → Analysis → T → E → Execution → V → R → C
```

### short_chain

与 full_chain stage 类似，但专家数量与分析深度按任务范围裁剪。

### diagnostic_chain

强制 Hypothesis Registry，适用于 defect/stability/field incident。

### bringup_chain

强调 material readiness、board/platform identity、Device/HIL evidence。

### review_only

```text
K → M → 0 → Triage → Analysis → T → R → C
```

**禁止隐式进入 Execution。**

### release_chain

```text
K → M → 0 → Triage → Analysis → T → V → R → C
```

默认做 readiness；需要改代码时必须显式扩展 mode。

### single_expert

```text
K → M → 0 → Triage → Analysis → T → C
```

不自动扩链。

---

## 3. Gate K：Knowledge Readiness

回答“我们是否拥有足够可信的知识输入”。

可包括：

- datasheet/TRM；
- schematic；
- protocol/standard；
- coding/design rules；
- historical RCA；
- platform notes。

决策：PASS / BLOCKED / DEGRADED_WITH_APPROVAL / NOT_APPLICABLE。

## 4. Gate M：Engineering Material Readiness

回答“我们是否知道自己在分析哪个系统”。

重点：

- repo；
- exact base；
- board revision；
- SoC/MCU；
- SDK/kernel/toolchain；
- schematic revision；
- firmware/image identity；
- log/reproduction；
- device identity。

这是嵌入式任务与普通软件任务的重要差异。

## 5. Gate 0：Intake Clarity

五维：

- goal；
- scope；
- boundary；
- constraints；
- acceptance。

不清楚就不进入“看起来很专业”的分析。

## 6. Analysis

由 routed expert 产出 `technical-analysis`。调试类额外维护 `hypothesis-registry`。

## 7. Gate T：Technical Decision

至少包含：

- solution；
- impact；
- dependency；
- risks；
- verification plan；
- rollback；
- unresolved items。

## 8. Gate E：Engineering Handoff

这是 AI 专家团与工程执行的正式边界。

### 上游

Expert Team 形成 `engineering-task-package`。

### 执行

Engineer + Codex 按 package 执行，不由 WorkBuddy 直接遥控个人 Codex。

### 下游

返回 `delivery-receipt`：

- executor identity；
- exact base；
- change/patch；
- commands；
- build/test status；
- artifact/hash；
- evidence；
- blocker；
- risk；
- next action。

`delivery-receipt` 只能证明“执行发生了什么”，不能替代 Verification。

---

## 9. Gate V：Verification

独立判断层级状态；未跑=未验证，不能被默认 PASS。

## 10. Gate R：Independent Review

在 Verification 之后独立审查结论、风险和放行充分性。

## 11. Gate C：Closure

收口条件：

- deliverable manifest；
- blocker resolved/accepted；
- verification 未夸大；
- risk/unverified item 保留；
- knowledge candidate / next action 可追踪。

---

## 12. Transition / Recovery

### Missing Information

K/M/0 缺信息 → needs_information，不自动填空。

### Verification Fail

回到 precise failed stage，不整链重跑。

### Review Fail

回责任 stage；cross-stage reflow 自动最多一次，之后要求人工决策。

### Resume

`team-run-state + gate-ledger` 是恢复基线。

---

## 13. Engineering Handoff 的设计意义

如果让专家团直接在用户本机无限制执行，会造成：

- 企业编排层与开发机强耦合；
- 权限难以审计；
- repo/device identity 漂移；
- AI 分析、执行、验证混在一起；
- 高风险动作难管。

因此一期使用 Contract 边界：

```text
Expert Team = 判断/方案/约束
Engineer + Codex = 受控执行
Verification = 独立证据判断
Review = 独立放行审查
```

这是当前架构最重要的稳定点之一。

## 14. 评审重点

- K/M/0 三个前置 Gate 是否可以合并显示、但底层仍分开？
- short_chain 是否需要更短路径？
- review_only 是否应该允许生成 patch proposal 但禁止写 worktree？当前 A2 已支持生成建议。
- Gate V/R 在低风险任务是否允许简化？建议可裁剪内容，但不取消职责独立性。
