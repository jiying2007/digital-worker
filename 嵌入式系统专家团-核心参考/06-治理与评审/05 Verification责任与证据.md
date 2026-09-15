# Verification责任与证据

Verification 属于 Assurance Plane，不是 Embedded System Expert 的 Capability。它回答的核心问题是：**Acceptance Criteria 是否被对应层级的直接 Evidence 证明。**

## 1. 基本原则

- Engineering success 不等于 Verification PASS；
- Runtime-local PASS 不等于 Domain Verification PASS；
- Host / cross-build / SIL / Device / HIL / Release 各层不能跨层推导；
- required layer 必须在实施前或最迟 Engineering Handoff 前明确；
- 失败后不能为了提高完成率把 required layer 改成 N/A；
- source / artifact / device / test identity 必须能回到同一 Work Item / Run。

## 2. 输入

Verification 至少消费：

- Task Brief / Acceptance Criteria；
- Material/System Context；
- Engineering Package 与 Delivery Receipt；
- exact source / artifact / device identity；
- direct build/test/device/HIL evidence；
- open risks / unverified items。

## 3. Verification Plan

每条 Acceptance 至少记录：

```text
criterion
→ required verification layer
→ test / observation method
→ evidence identity
→ result
→ remaining risk / unverified item
```

计划不是“多跑测试”，而是避免错误层级证明错误结论。

## 4. 当前 iterative Pilot

所有三条 Pilot track 仍要求 traceable `verification_report_ref`。Independent Review 不可用时，static checks + Hosted CI + Verification Report 可以作为当前阶段的 completion substitute；这不会降低 Verification 本身的直接 Evidence 要求。

尤其 Review/Release：Hosted CI 只证明 hosted 层；真实 device install/boot/rollback、Device/HIL/soak 等 required layer 仍必须由对应 Evidence 证明。

## 5. 输出

Verification Report 应明确：

- 每层状态；
- overall verdict；
- evidence refs；
- failures；
- unverified items；
- residual risks；
- verifier / implementation owner identity。

## 6. 常见错误

- 编译绿 = 设备绿；
- 单次 device smoke = HIL/long-run 充分；
- package SHA 正确 = OTA install/boot 正确；
- 把“没有测试”记录成 pass；
- 验证对象版本和实现对象版本不一致；
- 实施者修改后直接给自己更高层 PASS。

## 7. BLOCK 条件

required evidence 缺失、对象 identity 不匹配、Acceptance 无对应证据、存在跨层推导或关键未验证项被隐藏时，Verification 必须 FAIL/BLOCKED/保留风险，不能通过文字解释改写事实。
