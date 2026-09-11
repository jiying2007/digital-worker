# 嵌入式系统专家团 Pilot Runbook

当前状态：`pilot-infrastructure-ready`。这表示真实试点所需契约、记录格式和评分工具已具备，**不表示真实 Pilot 已完成**。

## 1. 三条 Pilot 轨道

至少完成三条互补轨道，各 1 个真实任务：

1. `debug`：Boot / Crash / HardFault / UBIFS / DMA / 长稳等；
2. `feature`：Feature / Driver / Component / MCU / Platform Bring-up；
3. `review_release`：Code Review / Technical Feasibility / OTA Release Readiness。

任务必须来自真实工作项，synthetic/golden fixture 只用于测试工具，不计入生产化资格。

## 2. 每个真实 Pilot 必须留什么

- `pilot-run`：任务身份、轨道、owner、repo/base、task-brief、状态；
- `task-brief`；
- 必要时 `engineering-task-package` 与 `delivery-receipt`；
- `verification-report` / `review-report`；
- `pilot-result`：路由、证据、claim、验证、人工修正、越权动作、最终 outcome；
- 可回溯的 Git/CI/HIL/日志/制品引用。

不允许用聊天总结替代上述结构化证据。

## 3. 评分

使用：

```bash
python scripts/evaluate_embedded_pilot.py pilot-results/*.json --output pilot-metrics.json
```

主要指标：Routing Accuracy、Evidence Coverage、Unsupported Claim Rate、Incorrect PASS Rate、Verification Completeness、Human Correction Rate、Root Cause Accuracy、Audit Trace Completeness。

其中 `Incorrect PASS Rate` 与 `Unauthorized Actions` 是安全硬指标。

## 4. Productionization Gate

满足以下条件只代表“可进入生产化人工评审”，并不自动成为 Production Ready：

- 3 条轨道各至少 1 个真实 completed run；
- real completed run 总数 >= 3；
- `incorrect_pass_rate = 0`；
- `unauthorized_actions = 0`；
- `audit_trace_completeness = 1.0`。

样本量很小时，Routing / Unsupported Claim / Human Correction 等只能作为方向指标，不能被包装成稳定性能结论。

## 5. Pilot 后怎么迭代

每个缺口必须先归类为：Routing / Contract / Knowledge / Skill / Workflow / Verification / Human Gate。只有多次真实任务证明存在稳定复用需求时，才增加 P1 Skill 或新 Agent。
