# Capability 能力与质量模型

本页补充“目标责任模型如何落到可执行专业能力”，避免把 Expert/Capability 只写成组织名词。机器 ownership 仍以 `domains/edge-foundation/**` 为准；本页不创建第二份路由或 Skill Registry。

## 1. 通用能力维度

每个 Role / Capability / Assurance responsibility 都应从以下维度评价：

| 维度 | 要求 |
|---|---|
| Knowledge | 能定位权威 Source，区分稳定知识、平台私有知识和待验证经验 |
| Context | 能确认 repo/base/board/device/artifact/test identity 与关键约束 |
| Method | 有可重复分析链，而不是自由文本猜测 |
| Tool/Runtime | 能使用可替换 Runtime，不把 Provider 当责任模型 |
| Action | 遵守 A0–A7，不因能力强或模型强自动扩大权限 |
| Evidence | 实质判断可追到直接 Evidence，Observed/Inferred/Confirmed 分离 |
| Handoff | 输入/输出/责任边界明确，跨域升级由 Evidence 触发 |
| Verification | 能说明什么需要在哪一层证明，以及未验证项 |
| Failure Handling | 缺关键材料时正确 BLOCK，失败回到精确责任阶段 |
| Knowledge Harvest | 复用/沉淀有证据的知识；无增量时允许 `NO_KNOWLEDGE_DELTA` |

## 2. Edge Coordination

**目标**：让任务具备清楚目标、正确路由、完整材料、受控工程交接和真实收口。

**核心能力**：Task classification、Material readiness、Context normalization、Gate control、cross-domain coordination、closure。

**必须做到**：

- Task Type / Workflow Mode 与 scope 一致；
- 缺 source/device/material 时诚实 BLOCK；
- 只选择最小必要 Expert/Capability；
- 不替专业责任方编造事实；
- Engineering Package 绑定 exact source、Acceptance、Action ceiling 与 rollback；
- Verification/Review 事实不被协调角色改写。

**质量指标**：routing accuracy、correct block rate、audit trace completeness、unnecessary mode expansion rate。

## 3. `embedded.architecture`

**目标**：把工程目标转成可实现、可验证的系统边界、接口、资源和生命周期约束。

**资格重点**：系统分层、接口/ABI/versioning、资源预算、实时性、Power/OTA/Recovery、兼容性、故障隔离。

**质量指标**：unsupported claim rate、evidence coverage、cross-interface defect discovery、architecture rework rate。

## 4. `embedded.linux-bsp`

**目标**：建立从 Boot 到 Kernel、DT、Storage、Power 与目标设备行为的可信平台事实。

**资格重点**：Boot、Kernel/DT、Clock/Reset/Pinctrl、IRQ/DMA/cache、MTD/UBI/UBIFS、Power、BSP Porting、Bring-up。

**质量指标**：target-device evidence coverage、correct block rate、platform regression escape、known-issue reuse。

## 5. `embedded.mcu-rtos`

**目标**：建立 MCU startup、memory、real-time、concurrency、watchdog、low-power 和 Bootloader/OTA 的直接事实。

**资格重点**：startup/vector/linker/MAP/ELF、ISR/DMA、RTOS scheduling/IPC、fault context、worst-case timing、power/OTA。

**质量指标**：deadline/jitter compliance、evidence coverage、fault diagnosis accuracy、regression stability。

## 6. `embedded.driver-component`

**目标**：可靠接入设备，并在真实复用需求下形成 stable API / adapter / compatibility contract。

**资格重点**：bus/protocol、driver lifecycle、error/recovery、concurrency/lifetime、Power、器件替代、生产校准测试、组件化。

**质量指标**：error-path coverage、compatibility coverage、API stability、target-device escape rate、reuse benefit。

## 7. `embedded.debug-reliability`

**目标**：从现象与证据推进到可证伪 Hypothesis、可复核 Root Cause、最小修复和充分回归。

**资格重点**：timeline、Observed/Inferred/Confirmed、Hypothesis Registry、discriminating experiment、Crash/Memory/Deadlock/DMA/Storage/Performance/Long-run。

**质量指标**：root-cause accuracy、incorrect-pass rate、time-to-discriminating-evidence、recurrence rate。

## 8. `assurance.verification`

**目标**：证明 Acceptance 在正确层级被正确对象的直接 Evidence 覆盖。

**资格重点**：Verification Plan、Build/Static/SIL/Device/HIL/Release layer、Regression Scope、Evidence identity、PASS_WITH_RISK/BLOCK 语义。

**质量指标**：verification completeness、evidence traceability、incorrect-pass rate、escaped defect rate。

## 9. `assurance.review`

**目标**：独立检查 Evidence、Risk、错误放行、rollback/provenance 和 Release Readiness，不替代 Verification 或 A7 Release Owner。

**资格重点**：correctness/safety finding、risk acceptance、review-only boundary、release/OTA readiness、authority check。

**质量指标**：incorrect-pass interception、finding recurrence、risk expiry compliance、release escape rate。

## 10. 成熟度原则

- Expert 数量不随 Skill 数增长；优先增长 Capability/Skill；
- Capability 不因为由独立 Agent 执行就升级成 Expert；
- Skill 可增加、合并、淘汰，Skill 数量不是架构 KPI；
- 高能力不自动扩大 Action Level；
- Evidence quality、correct blocking、可复核性比文本长度或“看起来完成”更重要；
- Product Pilot 评价真实工程成熟度；Architecture/Runtime retirement 评价旧执行面的可删除性，两者分开治理。
