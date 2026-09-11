# 13 Pilot、评测与生产化评审

## 1. 为什么必须 Pilot

Golden Case 和 synthetic fixture 能证明结构、路由和安全工具是否工作，但不能证明专家团在真实研发环境中的价值。

真实环境有：

- 不完整材料；
- 历史债务；
- 多 repo；
- 硬件版本漂移；
- 环境不可复现；
- 人工判断；
- 真实 deadline；
- 敏感数据；
- HIL 资源限制。

因此 Productionization 必须由 real Pilot 证据驱动。

---

## 2. 三条 Pilot 轨道

### Debug

候选：Boot、Kernel Panic、HardFault、UBIFS、DMA、长稳、现场异常。

### Feature

候选：Feature、Driver、Component、MCU firmware、Platform Bring-up。

### Review / Release

候选：Code Review、Technical Feasibility、OTA Release Readiness。

每条至少 1 个 real completed run，总计至少 3 个。

---

## 3. Pilot Operations

当前已有统一 CLI：

```text
embedded_pilot.py init
→ status running
→ complete
→ validate
→ bundle
→ summary
→ evaluate_embedded_pilot.py
```

real Pilot 必须 exact base commit；synthetic 永远不计入 productionization eligibility。

---

## 4. Track-specific completed artifact

### Debug

- task brief；
- hypothesis registry；
- verification report；
- review report；
- pilot result；
- evidence bundle。

### Feature

- task brief；
- engineering task package；
- delivery receipt；
- verification report；
- review report；
- pilot result；
- evidence bundle。

### Review / Release

- task brief；
- verification report；
- review report；
- pilot result；
- evidence bundle。

---

## 5. 当前指标

Evaluator 聚合：

- Routing Accuracy；
- Evidence Coverage；
- Unsupported Claim Rate；
- Incorrect PASS Rate；
- Verification Completeness；
- Human Correction Rate；
- Root Cause Accuracy；
- Unauthorized Actions；
- Audit Trace Completeness。

小样本阶段，除安全硬指标外，其他只能作为方向指标，禁止包装成稳定性能结论。

---

## 6. Productionization Gate

硬门槛来自 `pilot-plan.yaml`，不是 Python 写死。

当前要求：

- real completed runs >= 3；
- 三轨均覆盖；
- incorrect_pass_rate = 0；
- unauthorized_actions = 0；
- audit_trace_completeness = 1.0。

通过后：

> **只获得进入人工 Productionization Review 的资格。**

不会自动修改 expert-group status，不会自动扩大 A3-A7，不会自动标 Production Ready。

---

## 7. Productionization Review 应看什么

建议输入：

1. 3+ real pilot-run / pilot-result；
2. aggregate metrics + Markdown report；
3. 人工修正清单；
4. incorrect/block/rework 案例；
5. P1 Skill 候选及重复证据；
6. edge-foundation ownership 结果；
7. Security/Autonomy 风险评审；
8. main required CI protection 状态；
9. 真实团队使用成本和收益。

---

## 8. 不应使用的“漂亮指标”

不建议把以下作为核心 KPI：

- 生成代码行数；
- Commit 数；
- Agent 调用次数；
- Prompt 数；
- Token 消耗越多越好；
- “回答满意度”单指标。

真正关心：周期、错误放行、证据完整、人工修正、复用、回归逃逸、MTTR。

---

## 9. 当前真实工作项

仓库已建立：

- #6 Debug Pilot；
- #7 Feature Pilot；
- #8 Review/Release Pilot；
- #9 总体 rollout tracker。

它们当前等待 real task binding，不能用 synthetic fixture 关闭。

---

## 10. Pilot 后能力扩展

每个缺口先分类：

- Routing；
- Contract；
- Knowledge；
- Skill；
- Workflow；
- Verification；
- Human Gate。

只有“多个真实任务重复出现且可以方法化”的问题，才进入 P1 Skill。

如果问题是材料缺失，不应通过新增 Skill 掩盖。

## 11. 评审重点

- 3 个 real Pilot 是否足以进入第一轮生产化评审？当前定义是“资格”，不是充分证明；
- 是否需要扩大到 5~10 个后再开放 A3/A4 自动执行；
- 哪类真实任务最适合第一批；
- Pilot 是否需要选一个“故意困难/材料不全”的案例验证 BLOCK 能力；
- 是否加入效率基线：人工纯做 vs Expert Team 辅助。
