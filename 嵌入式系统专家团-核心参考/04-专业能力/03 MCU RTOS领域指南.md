# MCU / RTOS 领域指南

> 岗位职责与任职资格见 [《数字岗位与能力模型》](../01-数字组织与岗位/03%20数字岗位与能力模型.md)。本文只描述 **MCU/RTOS 专业工作怎么做**。

## 1. 领域定位

MCU/RTOS 负责 Bare-metal/RTOS 系统软件、Startup、Linker/Memory、ISR/DMA、实时性、Watchdog、Low Power 和 MCU Bootloader/OTA 的直接技术事实。

## 2. 典型任务

MCU BSP、启动异常、ROM/RAM/Stack 优化、RTOS 并发、ISR/DMA 时序、HardFault 现场分析、Watchdog/Reset、Low Power、Bootloader/App 契约和 MCU OTA。

任务路由和 Mode 只在 [任务类型运行矩阵](../03-流程与运行/05%20任务类型运行矩阵.md) 维护。

## 3. 必要输入

- MCU / board / firmware exact identity；
- startup/vector/linker script/map/ELF；
- clock tree / memory map / datasheet；
- RTOS config、task/priority/stack；
- ISR/DMA/timer 配置；
- watchdog/reset reason；
- flash layout / Boot-App contract；
- log/trace/measurement。

## 4. 分析方法

```text
Reset / Vector
→ Clock / C runtime / data-bss
→ HAL/BSP / basic IO
→ ISR / Timer / DMA / Watchdog
→ RTOS Scheduler / Tasks / IPC
→ Application Control
→ Low Power / Bootloader / OTA
```

### Startup / Linker / Memory

Reset 到 main/scheduler 依次核对 clock、vector、stack、`.data` copy、`.bss` zero、C runtime、HAL/BSP、watchdog 和 scheduler start。ROM/RAM 问题必须看 memory region、section placement、large symbols、orphan section、load/run address、stack/heap reserve 和 map/ELF，而不是只看 binary 总大小。

### RTOS / ISR / DMA

按 task priority/period → blocking call → mutex/semaphore/queue → ISR-to-task handoff → critical section → priority inversion → lock order/race → timeout/watchdog 分析。

### HardFault

收集 fault status registers、stacked registers、PC/LR/SP、ELF/map、task/ISR context 和 stack watermark。PC 落点只说明现场，不自动等于 Root Cause。

### MCU OTA

核 Boot/App version contract、image/hash、flash layout、integrity/authenticity、power-loss recovery、rollback、boot success criteria 和与主控升级的版本协同。

## 5. Evidence 要求

实时性数字必须来自明确测量方法，例如 GPIO、trace、timestamp 或 cycle counter；ROM/RAM 结论绑定 MAP/ELF；HardFault 结论绑定 exact firmware 与 fault context；OTA 证据绑定 image/hash、目标设备和失败恢复路径。

## 6. 输出

Startup/Linker/Memory/Concurrency Technical Analysis、Timing/Jitter Evidence、Fault Context、OTA 约束、风险、修改边界、Regression Scope 和 Verification 要求。

## 7. 协作与交接

- P02：系统级 Linux/MCU 分工、接口和资源冲突；
- P05：MCU 侧设备 driver、协议和组件接口；
- P06：长期偶发故障、多假设 HardFault/并发问题的 Root Cause 闭环；
- P07：目标板时序、Device/HIL evidence 的独立判断；
- Release/生产：签名、Fuse/OTP 和生产 OTA 仍走明确人工 Gate。

## 8. 常见错误

- task stack 只按经验配置，不看 watermark；
- ISR 做阻塞或长耗时操作；
- critical section 扩大导致控制周期抖动；
- mutex/queue 正确但 priority 设计造成饥饿；
- Bootloader/App 协议升级后忽略旧版本组合；
- HardFault 只依据 PC 猜根因；
- 平均周期正常就忽略 worst-case jitter。

## 9. BLOCK 条件

firmware 与 ELF/map 不匹配、MCU/board identity 不清、实时性无测量条件却要求 verified 结论、HardFault 缺关键 context、Boot/App version contract 不明、OTA rollback/power-loss 路径未定义时，应 BLOCK 或保持 evidence insufficient。
