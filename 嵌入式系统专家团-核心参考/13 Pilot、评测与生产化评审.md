# 13 Pilot、评测与生产化评审

> 同步基线：`v0.7.0 / provider-neutral`

## 1. 为什么必须 real Pilot

Golden Case / synthetic fixture 只能证明结构与安全工具工作，不能证明真实研发价值。Productionization 必须由真实任务、真实材料缺口、真实工程环境和人工 Verification/Review 证据驱动。

## 2. 三条业务 Pilot 轨道

- Debug：Boot/Panic/HardFault/UBIFS/DMA/长稳/现场异常；
- Feature：Feature/Driver/Component/MCU firmware/Bring-up；
- Review/Release：Code Review/Feasibility/OTA readiness。

每条至少 1 个 real completed run，总计至少 3 个。

## 3. Pilot Operations

`init → running/blocked → complete → validate → bundle → summary → evaluate`。

real run 必须 exact base commit；synthetic 永不计入 productionization eligibility。

## 4. Completed Evidence

Debug：task brief + hypothesis registry + verification + review + pilot result + bundle。

Feature：task brief + engineering task package + delivery receipt + verification + review + pilot result + bundle。

Review/Release：task brief + verification + review + pilot result + bundle。

## 5. 指标

Routing Accuracy、Evidence Coverage、Unsupported Claim、Incorrect PASS、Verification Completeness、Human Correction、Root Cause Accuracy、Unauthorized Actions、Audit Trace Completeness。

小样本阶段除安全硬指标外，只做方向判断。

## 6. Productionization Gate

至少 3 个 real completed、三轨覆盖、incorrect_pass_rate=0、unauthorized_actions=0、audit_trace_completeness=1.0。

通过后只获得进入人工 Productionization Review 的资格，不自动扩大 A3-A7，也不自动标 Production Ready。

## 7. Multi-runtime Pilot

Provider-neutral 架构新增一个横向验证维度：对同一个 task-brief / engineering-task-package / repo / exact base / acceptance，至少比较两个 Engineering Agent Runtime（首轮可选 Codex 与 Claude Code）。

固定输入、动作上限和 Verification 标准，比较：

- Contract adherence；
- 代码/分析正确性；
- build/test；
- evidence completeness；
- unsupported claims；
- human correction；
- cancel/recovery；
- runtime identity traceability；
- latency / usage cost / engineering time。

Runtime 输出不能互相泄漏最终答案/patch。该实验由 #18 跟踪。

## 8. Schema 观察项

真实 Pilot 专门记录：

- `executor_identity` 是否需要拆 runtime/provider/model/version；
- `knowledge_refs` 是否需要 source/revision/ACL/provenance；
- 是否需要 Context Package；
- 是否需要独立 Agent Runtime Receipt。

只有出现真实需求才升级共享 Schema。

## 9. Productionization Review

输入至少包括：real runs、aggregate metrics、human corrections、incorrect/block/rework 案例、P1 Skill 候选、ownership、安全/自治、main protection、团队收益/成本、Provider PoC 结果。

## 10. 不应使用的 KPI

代码行数、Commit 数、Agent 调用次数、Prompt 数、Token 多寡、单一“满意度”。真正关心周期、错误放行、证据、人工修正、复用、回归逃逸、MTTR。

## 11. 当前工作项

#6 Debug、#7 Feature、#8 Review/Release、#9 rollout；#16 Knowledge PoC、#17 Provider Matrix、#18 Multi-runtime Pilot。

## 12. Pilot 后扩展

缺口先归类 Routing / Contract / Knowledge / Skill / Workflow / Verification / Human Gate / Provider Adapter。只有多个真实任务重复且可方法化的问题进入 P1 Skill。
