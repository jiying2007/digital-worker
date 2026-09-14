# 任务生命周期与 Gate

## 1. 任务从哪里开始

任务可以来自产品评审、项目开发、现场缺陷、测试问题、代码评审或发布准备。入口系统可以不同，但进入嵌入式研发域后必须形成稳定的 `work_item_id / run_id` 和 Task Brief。

开始执行前，先做三件事：

1. 判断任务类型；
2. 判断资料是否足够；
3. 选择最短正确流程。

不要先调用所有专业角色再决定问题是什么。

## 2. 运行状态

机器状态包括：

`draft / needs_information / ready_for_analysis / in_analysis / ready_for_engineering / in_engineering / ready_for_verification / in_verification / ready_for_review / blocked / needs_rework / completed / cancelled`。

状态用于恢复和审计，不等同于业务口头状态。例如 `in_engineering` 只表示正在实施，不代表功能已经验证。

## 3. 主流程

```text
Gate K  知识是否可用
  ↓
Gate M  工程材料是否齐全
  ↓
Gate 0  目标/范围/边界/约束/验收是否清楚
  ↓
Triage  任务分类与专业路由
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

不是所有模式都包含 Execution/V/R，具体以 `config/workflow.yaml` 为准。

## 4. 各 Gate 的工程含义

|阶段|要回答的问题|Owner|主要输出|失败后怎么办|
|---|---|---|---|---|
|Gate K|需要的知识能否追到可信 Source？|主理人|knowledge-readiness|补资料、降级批准或 BLOCK|
|Gate M|repo/base/board/SDK/log/device 等是否足够？|主理人|material-manifest|补资料或明确缺口|
|Gate 0|目标、范围、边界、约束、验收是否清楚？|主理人|task-charter|返回澄清|
|Triage|该走什么 mode、由谁主责？|主理人|routing-decision|重新分类，不默认 full-chain|
|Analysis|专业结论和风险是什么？|领域 Owner|technical-analysis / hypothesis|继续取证或转交相关领域|
|Gate T|方案、影响、风险、验证和回滚是否足够？|主理人|technical-decision|回分析|
|Gate E|工程师能否按包直接执行？|主理人|engineering-task-package|补 exact identity/acceptance/动作边界|
|Gate V|证据证明到了哪一层？|验证|verification-report|回到 precise failed stage|
|Gate R|是否存在不能放行的风险？|独立审查|review-report|REQUEST_CHANGES/BLOCKED|
|Gate C|交付、blocker、风险、验证状态是否真实完整？|主理人|deliverable-manifest|不满足则不 completed|

## 5. 七种流程模式

### full_chain

跨多专业、风险较高、从分析到验证完整闭环。只有确有必要时使用。

### short_chain

已有平台上的常规功能、驱动、组件或优化。虽然名字叫 short，当前机器路径仍保留 T/E/V/R 等关键安全阶段；后续是否进一步缩短由真实 Pilot 决定。

### diagnostic_chain

缺陷、稳定性、现场问题。强制 Hypothesis Registry。

### bringup_chain

新板、新 SoC、新 BSP 或平台 Bring-up，强调 identity、资源、Boot、DT、设备链逐步建立。

### review_only

只评审和给建议，不隐式进入修改代码阶段。需要实施修复时必须建立新的工程执行链或显式扩 mode。

### release_chain

检查 Release/OTA/rollback/provenance/readiness；默认不执行生产发布。

### single_expert

边界清楚的单专业分析。禁止因为回答不完整就悄悄扩成整链。

## 6. 任务类型与默认路由

日常使用可按以下方式快速判断：

- 新功能/组件：`feature_development / component_development` → short_chain；
- 缺陷/现场/长稳：`defect_debugging / field_incident / stability_reliability` → diagnostic_chain；
- 新板/移植：`platform_bringup / bsp_porting` → bringup_chain；
- 架构/技术可行性：`architecture_design / technical_feasibility_review` → short/review_only；
- 代码审查：`code_review` → review_only；
- OTA/发布：`release_ota` → release_chain；
- 性能问题：先判断是改进型还是诊断型，再选 short/diagnostic。

详细映射以 `config/task-modes.yaml` 为准。

## 7. Gate K/M/0 为什么分开

三者看似都在“检查资料”，实际风险不同：

- K 关注知识来源是否可信；
- M 关注工程对象身份和材料是否齐；
- 0 关注需求本身是否说清楚。

界面可以一次展示，但底层不能合并成一个模糊的“资料完整度”，否则很难知道失败后该补什么。

## 8. 失败与恢复

### 缺资料

状态进入 `needs_information`，必须记录缺什么和如何恢复。允许经批准降级，但降级项需要带到后续 Verification/Review。

### Verification FAIL

返回**具体责任阶段**，例如：

- build 失败 → Execution；
- 验收定义错误 → Gate 0/T；
- 设备 identity 不清 → Gate M/E；
- 实现方向错误 → Analysis/T。

不因为一个失败默认整条链重跑。

### Review FAIL

按 finding 指向责任阶段。P0/P1 正确性或安全问题原则上不得只用“已知风险”绕过。

### Cross-stage reflow

自动跨阶段回流最多一次，超过后需要人做明确决策，防止流程在多个阶段之间无休止循环。

## 9. Completion 的含义

只有同时满足以下条件才进入 `completed`：

- deliverable manifest 存在；
- blocker 已解决或由明确责任人接受；
- 验证状态没有夸大；
- required artifact 完整；
- 真实 Run 的 evidence bundle 可复核。

“代码已提交”“CI 已绿”“问题暂时不出现”都不单独构成 Completion。
