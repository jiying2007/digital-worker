# 嵌入式系统专家团真实 Pilot 执行说明

本 Runbook 用于将真实嵌入式研发任务接入已经冻结的 Expert Team Contract。Pilot 的目标是发现运行模型问题，不是证明 AI 永远正确。

## 入口

真实任务先形成 `task-brief v1`，再登记 `pilot-run v1`。缺 owner、repo/base、验收或验证层级时，不进入执行。

## 推荐首批三个真实任务

- Debug：Boot / UBIFS / HardFault / DMA / 长稳中的一个真实缺陷；
- Feature：一个真实 Driver/Component/MCU/Bring-up 变更；
- Review/Release：一个真实 Code Review、技术可行性或 OTA Release Readiness。

优先选择已有人工结论或可验证结果的任务，便于对比 AI route、claim、root cause 和 verification。

## 执行边界

- Expert Team 默认 A0-A2；
- 代码修改和构建继续经 Engineering Handoff 交给 Engineer + Codex；
- 设备写与 Release 仍需人工 Gate；
- 任何未验证层不得被上推成 PASS；
- 人工纠正必须记录，不能在最终报告中隐藏。

## 收口

每个 Pilot 生成 `pilot-result v1`，然后用 `evaluate_embedded_pilot.py` 聚合。Synthetic fixture 只验证工具链，绝不计入 real completed runs。

Productionization eligibility 只代表可以提交一次单独的人工评审；仓库不会因为指标过门自动把状态改成 Production Ready。
