# Verification责任与证据

Verification 属于 Assurance Plane，不是 Embedded System Expert 的 Capability。它回答：**Acceptance Criteria 是否被对应层级、对应对象的直接 Evidence 证明；哪些仍未证明。**

## 1. 稳定原则

- Engineering success ≠ Verification PASS；
- Runtime-local PASS ≠ Domain Verification PASS；
- Build / Static / SIL / Device / HIL / Release 不能跨层推导；
- required layer 应在实施前或最迟 Engineering Handoff 前明确；
- 失败后不能为了提高完成率把 required layer 改为 N/A；
- source / artifact / device / test identity 必须回到同一 Work Item / Run；
- Verification 不因 Review 当前可用性变化而降低自身 Evidence 标准。

## 2. 必要输入

- Task Brief / Acceptance Criteria；
- Material/System Context；
- Engineering Package / Delivery Receipt；
- exact source / artifact / firmware / device identity；
- test/HIL 原始结果；
- environment / fixture / case / run identity；
- open risks、required layer、已知限制。

## 3. Verification Plan

每条 Acceptance 至少记录：

```text
criterion
→ required layer
→ object identity
→ precondition
→ method / steps
→ expected result
→ direct evidence
→ result
→ failure handling
→ regression scope
→ remaining risk
```

计划的目标不是“测试越多越好”，而是避免错误层级证明错误 Claim。

## 4. Evidence Check

### 4.1 Build / Static

核 source/base、toolchain、config、command、target、artifact/hash、warning/error、static rule scope。Build PASS 只证明可构建/对应静态规则，不证明目标设备行为。

### 4.2 SIL / Host

核模拟对象、替代边界、输入数据、时间模型和未覆盖硬件行为。SIL 可以证明算法/状态机的一部分行为，但不能自动证明真实 IRQ/DMA/电气/Power。

### 4.3 Device

核 board/device identity、firmware/artifact hash、环境、步骤、原始 log/measurement、result、reset/power state。另一块板、另一版本或口头结果不能替代当前对象 Evidence。

### 4.4 HIL

核 case、fixture/environment、target identity、run identity、automation version、artifact/log hash、repeat count 和 failure artifact。HIL summary 必须可追到原始 run。

### 4.5 Release Candidate

核 exact candidate、manifest/provenance、download/install、upgrade/downgrade、boot、rollback/power-loss、required Device/HIL/soak、open risks 和 release owner。Package SHA 正确只证明包身份，不证明设备安装/启动成功。

## 5. Regression Scope

检查直接模块、接口/协议消费者、共享资源、并发/生命周期、Boot/OTA/Power、性能/长稳、负向和异常路径，形成最小充分集合。避免两个极端：只跑修改点，或没有风险模型地全量跑。

## 6. Verdict 语义

- `PASS`：required evidence 完整、对象 identity 一致、Acceptance 已直接证明；
- `PASS_WITH_RISK`：required evidence 达到基本要求，残余风险有明确 owner/acceptor/期限/缓解；
- `FAIL`：直接证据证明 Acceptance 不满足；
- `BLOCKED/NOT_RUN`：required layer、identity、环境或材料不足。

Risk acceptance 不能把 FAIL/NOT_RUN 改写成 PASS。

## 7. 当前 iterative Pilot

三条 Pilot track 均要求 traceable Verification Report。Independent Review 不可用时，可由 static checks + Hosted CI + traceable Verification evidence 满足当前 Pilot completion；这只是阶段性 completion policy，不改变 Verification 的直接 Evidence 要求。

Review/Release 尤其不能用 Hosted CI 代替真实 device install/boot/rollback、Device/HIL/soak 或 A7 human decision。

## 8. 输出 Contract

Verification Report 至少包含 implementation owner、verifier、independence/compensation、required layers、每层状态、overall verdict、evidence refs、failures、unverified items、regression scope、residual risks、对象 identity。

## 9. 常见错误

- case PASS 但 object identity 不清；
- 编译绿 = 设备绿；
- 单次 device smoke = HIL/long-run 充分；
- 复用另一块板/另一版本 Evidence；
- HIL 执行者口头说通过但无原始 run；
- Acceptance 无法映射到具体 Evidence；
- residual risk 在后续报告丢失；
- 为提高完成率事后把失败层改成 N/A；
- package hash 正确 = OTA install/boot 正确；
- 实施者修改后直接给自己更高层 PASS。

## 10. BLOCK 条件

Acceptance/Claim 不明确、required layer 未定义、source/artifact/device identity 不一致、required Evidence 缺失、测试环境/fixture 无法确认、出现跨层推导或关键未验证项被隐藏时，必须 FAIL/BLOCKED/保留风险，不能通过文字解释改写事实。

## 11. Knowledge Harvest 与质量指标

可沉淀 Verification Plan template、evidence checklist、HIL contract、regression rule、failure artifact requirement。主要指标：verification completeness、incorrect-pass rate、evidence traceability、escaped defect rate、required-layer drift rate。
