# MCU RTOS能力域指南

`embedded.mcu-rtos` 是 Embedded System Expert 内负责 Bare-metal/RTOS、Startup、Linker/Memory、ISR/DMA、实时性、Watchdog、Low Power 和 MCU Bootloader/OTA 的 Capability。

## 1. 典型任务

MCU BSP、启动异常、ROM/RAM/Stack 优化、RTOS 并发、ISR/DMA 时序、HardFault、Watchdog/Reset、Low Power、Bootloader/App 契约、MCU OTA 与实时控制路径。

## 2. 必要输入与 Context

- MCU / board / firmware exact identity；
- startup/vector/linker script/MAP/ELF；
- clock tree / memory map / datasheet；
- RTOS config、task/priority/stack；
- ISR/DMA/timer 配置；
- watchdog/reset reason；
- flash layout / Boot-App version contract；
- fault context / log / trace / measurement；
- toolchain 与编译配置。

## 3. 分析主链

```text
Reset / Vector
→ Clock / C runtime / data-bss
→ HAL/BSP / basic IO
→ ISR / Timer / DMA / Watchdog
→ RTOS Scheduler / Tasks / IPC
→ Application Control
→ Low Power / Bootloader / OTA
```

### 3.1 Startup / Linker / Memory

Reset 到 main/scheduler 依次核对 vector、stack、clock、`.data` copy、`.bss` zero、C runtime、HAL/BSP、watchdog、scheduler start。ROM/RAM 必须看 memory region、section placement、large symbols、orphan section、load/run address、stack/heap reserve 和 MAP/ELF，而不是只看 binary 总大小。

### 3.2 RTOS / ISR / DMA

按 task priority/period → blocking call → mutex/semaphore/queue → ISR-to-task handoff → critical section → priority inversion → lock order/race → timeout/watchdog 分析。明确 ISR 可调用 API、DMA buffer lifetime/cache、共享资源 owner 和 worst-case blocking。

### 3.3 HardFault / Exception

收集 fault status registers、stacked registers、PC/LR/SP、ELF/MAP、task/ISR context、stack watermark 和最近事件。PC 落点只说明现场，不自动等于 Root Cause；需要结合调用链、内存破坏、栈、DMA 和并发证据。

### 3.4 实时性与控制周期

对 deadline、jitter、ISR latency、task execution time、queue latency 说明测量方法，例如 GPIO、trace、timestamp、cycle counter。平均值不能替代 worst-case；优化前后必须同条件对比。

### 3.5 Watchdog / Reset / Low Power

明确 watchdog feed ownership、超时条件、reset reason、故障快照、sleep entry/exit、clock/peripheral restore、wakeup source 和恢复失败路径。

### 3.6 MCU OTA

核 Boot/App version contract、image/hash、flash layout、integrity/authenticity、power-loss recovery、rollback、boot success criteria、升级状态机和与主控版本协同。生产签名、Fuse/OTP、发布仍由人工 Gate 控制。

## 4. Evidence 模型

实时性数字绑定测量方法；ROM/RAM 结论绑定 MAP/ELF；HardFault 结论绑定 exact firmware + fault context；OTA 绑定 image/hash、设备和失败恢复路径。Host 模拟或单元测试不能外推为 Device/HIL PASS。

## 5. 输出 Contract

Startup/Linker/Memory Analysis、Concurrency/Timing Analysis、Fault Context/Hypothesis、Watchdog/Power Constraint、OTA Contract、Regression Scope、Unverified Items、Residual Risk。

## 6. 协作与交接

- `embedded.architecture`：Linux/MCU 分工、接口、资源和生命周期；
- `embedded.driver-component`：MCU device driver、协议、adapter；
- `embedded.debug-reliability`：长期偶发、多假设 HardFault/并发问题；
- Hardware Expert：clock、电源、波形、引脚、电气和器件事实；
- `assurance.verification`：目标板时序、Device/HIL evidence 独立判断。

## 7. Verification 要求

至少根据 scope 覆盖 startup、memory budget、ISR/DMA、并发/timeout、worst-case timing、watchdog/reset、low-power、OTA happy/failure/power-loss/rollback。涉及电机/控制闭环时还应验证低速、带载、正反切换、异常保护和长期温升等产品相关工况。

## 8. 常见错误

- task stack 只按经验配置，不看 watermark；
- ISR 做阻塞或长耗时操作；
- critical section 扩大导致控制周期抖动；
- mutex/queue 正确但 priority 设计造成饥饿；
- Bootloader/App 协议升级忽略旧版本组合；
- HardFault 只依据 PC 猜根因；
- 平均周期正常就忽略 worst-case jitter；
- OTA 只验证正常升级，不验证掉电/回滚。

## 9. BLOCK 条件

firmware 与 ELF/MAP 不匹配、MCU/board identity 不清、实时性无测量条件却要求 verified 结论、HardFault 缺关键 context、Boot/App contract 不明、OTA rollback/power-loss 路径未定义时，应 BLOCK 或保持 evidence insufficient。

## 10. Knowledge Harvest 与质量指标

可沉淀 startup/linker checklist、memory rule、RTOS concurrency pattern、fault capture template、timing method、Boot-App contract、OTA recovery rule。主要指标：evidence coverage、deadline/jitter compliance、unsupported claim rate、correct block rate、复现与回归稳定性。
