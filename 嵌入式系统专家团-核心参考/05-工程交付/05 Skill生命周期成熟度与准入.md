# Skill 生命周期、成熟度与准入

本页解决两个评审问题：

1. Skill 文件存在，是否就代表能力成熟？
2. 什么时候应该新增、拆分、合并、废弃一个 Skill？

答案都是否定“凭印象”。Skill 成熟度必须由定义完整性、评测、真实工程证据和治理共同决定。

当前 23 个 canonical Skill 的逐项真实状态见 [Skill 评审成熟度台账](06%20Skill评审成熟度台账.md)。该台账刻意把 `DEFINED` 与 `EVALUATED / PILOTED / REPEATABLE` 分开，避免把文档完整度误写成工程成熟度。

## 1. 生命周期状态

```text
OBSERVED_GAP
    ↓
CANDIDATE
    ↓
DEFINED
    ↓
EVALUATED
    ↓
PILOTED
    ↓
REPEATABLE
    ↓
GOVERNED
    ↓
CANONICAL-STABLE
    ↓
DEPRECATED → RETIRED
```

说明：

- `OBSERVED_GAP`：发现重复方法缺口，但还不能证明应独立成 Skill；
- `CANDIDATE`：owner、scope、与现有 Skill 区别已有初步裁决；
- `DEFINED`：满足 Skill Contract 最低定义；
- `EVALUATED`：有正例、负例/BLOCK case、Golden Case；
- `PILOTED`：至少在真实任务中使用；
- `REPEATABLE`：跨多个任务/对象表现稳定；
- `GOVERNED`：有版本、变更、action、评测、回退治理；
- `CANONICAL-STABLE`：可作为长期稳定资产；
- `DEPRECATED / RETIRED`：已有替代或不再产生独立价值。

当前 `skills.yaml status: target-v1` 表达 registry 的目标执行状态，**不等价于每个 Skill 已经达到 CANONICAL-STABLE 的工程成熟度**。

## 2. 成熟度五维模型

正式评审建议对 Skill 分别看五个维度，不给一个模糊总分。

| 维度 | L0 | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|
| Definition | 只有名称 | purpose/method | 完整 input/output/block | limits/handoff/version 完整 | 变更可审计 |
| Evaluation | 无 | 示例 | positive + negative | Golden Cases | regression suite |
| Real Evidence | 无 | synthetic | 单个 real Pilot | 多个 real runs | 跨项目稳定复用 |
| Portability | 单一实现假设 | provider-neutral 文本 | 第二 Runtime 可执行 | 结果一致性可测 | runtime qualification 持续 |
| Governance | 无 | owner | action/ownership 校验 | version/deprecation | lifecycle metrics + retirement |

评审结论必须指出“哪一维不足”，而不是简单写“Skill 成熟/不成熟”。

## 3. Canonical 准入 Gate

一个新 Skill 要进入 `domains/edge-foundation/skills.yaml`，至少应满足：

### G1 — Responsibility
- owner 落到已存在 Role / Capability / Assurance；
- 不因“想独立跑 Agent”而创建 owner；
- 与相邻 Skill 的边界能用例子解释。

### G2 — Repetition
- 真实任务中重复出现；
- 不是一次性项目技巧；
- 能说明不独立建 Skill 会造成什么稳定问题。

### G3 — Contract
- Required Inputs / Outputs / BLOCK / Action ceiling 明确；
- 缺输入时不会靠猜测继续；
- output 能被后续流程消费。

### G4 — Evaluation
- 至少有 positive case；
- 至少有 missing-evidence 或错误假设的 negative/BLOCK case；
- 关键结论可检查。

### G5 — Integration
- registry、物理路径、owner frontmatter 一致；
- 若 routing 需要显式引用，已更新；
- 不破坏 Engineering / Verification / Review 分离。

### G6 — Change Safety
- 不扩大权限或已完成对应 security review；
- 有兼容/迁移/rollback 说明；
- 新 Skill 不制造第二份 Source of Truth。

任一 Gate 不满足，应停留在 planning candidate，而不是为了“目录齐全”提前注册。

## 4. 拆分 Gate

只有同时满足以下信号，才考虑把一个 Skill 拆成两个：

- 单个 Skill 的 Required Inputs 已明显出现两套不同集合；
- Method 长期分叉为两条几乎独立的路径；
- Evidence contract 不同；
- owner 发生真实责任分界；
- Golden Case 很难共用；
- 拆分能减少误加载，而不是只是让文件更短。

例如 `storage-filesystem-analysis` 是否要拆 `flash-ecc-badblock-analysis`，应由真实 NAND/ECC 任务长期证明，而不是因为 NAND 看起来“很专业”。

## 5. 合并 Gate

以下情况优先合并：

- 两个 Skill 总是成对加载；
- 输入输出高度重复；
- owner 相同；
- 无法设计各自独立 negative case；
- 拆开后只增加 orchestration cost；
- 真实任务无法说明分别加载的价值。

## 6. Deprecated / Retired Gate

Skill 可退役的常见原因：

- 能力已被另一个 Skill 完整覆盖；
- 平台/技术已退出支持范围；
- 长期无真实使用；
- 方法已被更高层 Contract 固化，无需独立 Skill；
- 误用率高且独立价值低。

退役必须：

- 标明 replacement；
- routing/registry 不再引用；
- Golden Cases 迁移或删除；
- 保留 Git history；
- 不在活动执行面维持 shadow compatibility。

## 7. 评审指标

Skill 体系建议长期观察：

- correct block rate；
- unsupported claim rate；
- evidence coverage；
- false confidence / incorrect pass；
- unnecessary skill load rate；
- average skills per task；
- repeated-method gap frequency；
- real reuse count；
- regression escape；
- cross-runtime outcome consistency；
- deprecated-but-still-invoked count。

不要把 token、回答长度、Skill 数量、Agent 数量当成核心成熟度 KPI。

## 8. 当前阶段建议

当前最合理的顺序：

1. 保持 23 个 canonical Skill 的 Definition Hardening 作为 CI 基线；
2. 让 Golden Case 显式绑定 Skill ID / contract version / input-output identity，并补 positive + BLOCK negative case；
3. 从真实 Feature/Debug/Release Pilot 生成可冻结的 Skill invocation / output receipt；
4. 统计“被迫在 Skill 外自由发挥”的重复方法；
5. 再决定候选 Skill 是否晋级；
6. 当第二 Runtime 有可比证据后，再评价 Portability；
7. Productionization 前补 lifecycle metrics、严格 governance 和退役机制。

这能保证 Skill 体系是被真实工程问题“拉出来”的，而不是被架构图“推出来”的。
