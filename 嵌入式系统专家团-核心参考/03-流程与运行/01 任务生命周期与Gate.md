# 任务生命周期与 Gate

> **本页是任务状态、主流程、K/M/0/T/E/V/R/C Gate、失败回流和 Runtime Mode 阶段含义的唯一详细人类来源。** 机器权威是 `domains/edge-foundation/runtime/workflow.yaml`、`domains/edge-foundation/runtime/task-modes.yaml` 与 `domains/edge-foundation/gate-policy.yaml`。

## 1. 任务从哪里开始

任务可以来自产品评审、项目开发、现场缺陷、测试问题、代码评审或发布准备。进入嵌入式研发域后必须形成稳定的 `work_item_id / run_id` 和 Task Brief。

开始执行前先做三件事：判断任务类型、判断材料是否足够、选择最短正确流程。不要先调用所有能力再决定问题是什么。

## 2. 运行状态

状态包括：`draft / needs_information / ready_for_analysis / in_analysis / ready_for_engineering / in_engineering / ready_for_verification / in_verification / ready_for_review / blocked / needs_rework / completed / cancelled`。

状态用于恢复和审计，不等同于业务口头状态。例如 `in_engineering` 只表示正在实施，不代表功能已经验证。

## 3. 主流程

```text
Gate K  知识是否可用
  ↓
Gate M  工程材料是否齐全
  ↓
Gate 0  目标/范围/边界/约束/验收是否清楚
  ↓
Triage  任务分类与 canonical routing
  ↓
Analysis 专业分析 / Debug 假设
  ↓
Gate T  技术方案是否足以进入工程
  ↓
Gate E  工程任务包是否完整
  ↓
Execution 工程实施
  ↓
Gate V  验证证据是否满足要求
  ↓
Gate R  风险与放行审查
  ↓
Gate C  收口
```

并非所有 Runtime Mode 都执行全部阶段；具体阶段由 `runtime/workflow.yaml` 与 task/mode policy 决定。

## 4. 各 Gate 的工程含义

|阶段|要回答的问题|Owner|主要输出|失败后怎么办|
|---|---|---|---|---|
|Gate K|需要的知识能否追到可信 Source？|Edge Coordination|knowledge-readiness|补资料、降级批准或 BLOCK|
|Gate M|repo/base/board/SDK/log/device 等是否足够？|Edge Coordination|material-manifest|补材料或明确缺口|
|Gate 0|目标、范围、边界、约束、验收是否清楚？|Edge Coordination|task-charter|返回澄清|
|Triage|该走什么 route/mode/Capability？|Edge Coordination|routing-decision|重新分类，不默认 full-chain|
|Analysis|专业结论和风险是什么？|Routed Domain Expert / Capability|technical-analysis / hypothesis|继续取证或 evidence-driven handoff|
|Gate T|方案、影响、风险、验证和回滚是否足够？|Routed Domain Expert|technical-decision|回 Analysis|
|Gate E|工程师能否按包直接执行？|Edge Coordination|engineering-task-package|补 exact identity/acceptance/动作边界|
|Gate V|证据证明到了哪一层？|Verification|verification-report|回到 precise failed stage|
|Gate R|是否存在不能放行的风险？|Independent Review|review-report / decision|REQUEST_CHANGES/BLOCKED；当前阶段可按 policy 记录 unavailable waiver|
|Gate C|交付、blocker、风险、验证状态是否真实完整？|Edge Coordination|deliverable-manifest|不满足则不 completed|

## 5. Runtime Mode

### full_chain
跨多个 Capability、风险较高或需要完整分析→工程→验证链。只有必要时使用。

### short_chain
已有平台上的常规功能、驱动、组件或优化；仍保留必要的 Acceptance、Engineering Handoff 与 Verification。

### diagnostic_chain
缺陷、稳定性、现场问题；强制保留 Timeline、Hypothesis 与 discriminating evidence。

### bringup_chain
新板、新 SoC、新 BSP 或平台 Bring-up；强调 identity、Boot、资源、DT、设备链逐步建立。

### review_only
只评审和给建议，不隐式进入修改代码阶段；需要实施时必须显式建立执行链。

### release_chain
检查 Release/OTA/rollback/provenance/readiness；默认不执行生产发布，A7 仍需人工批准。

### single_expert
边界清楚的单 Domain Expert 任务，可在其内部组合多个 Capability；禁止因回答不完整悄悄扩成整链。

Runtime Mode 与责任模式映射以 `domains/edge-foundation/routing.yaml` 和 `runtime/task-modes.yaml` 为准。

## 6. Gate K/M/0 为什么分开

K 关注知识来源可信度；M 关注工程对象 identity 和材料；0 关注需求本身是否明确。界面可以一次展示，底层不能合并成模糊的“资料完整度”，否则失败后不知道该补什么。

## 7. 失败与恢复

缺资料进入 `needs_information` 或 `blocked`，必须记录缺什么以及恢复条件。允许经批准降级，但降级项必须带入 Verification/Review。

Verification FAIL 返回具体责任阶段：build 失败回 Execution；Acceptance 错误回 Gate 0/T；device identity 不清回 M/E；实现方向错误回 Analysis/T。不要因为单点失败默认整条链重跑。

Review Finding 同样按 Finding 指向责任阶段。P0/P1 正确性或安全问题原则上不得只用“已知风险”绕过。自动跨阶段 reflow 有限，超过阈值需要人做明确决策。

## 8. Completion 的含义

只有 deliverable manifest、required artifact、材料状态、Verification、open risk/unverified item 与 frozen evidence bundle 全部真实一致，Run 才可 completed。“代码已提交”“CI 已绿”“问题暂时不出现”都不单独构成 Completion。
