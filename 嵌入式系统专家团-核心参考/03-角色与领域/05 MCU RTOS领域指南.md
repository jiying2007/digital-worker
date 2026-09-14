# MCU / RTOS 领域指南

## 1. 职责

MCU/RTOS 负责 Bare-metal/RTOS 系统软件、Startup、Linker、ISR/DMA、实时性、Watchdog、低功耗以及 MCU Bootloader/OTA。

## 2. 领域模型

```text
Reset / Vector
 → Clock / C runtime / data-bss
 → HAL/BSP / basic IO
 → ISR / Timer / DMA / Watchdog
 → RTOS Scheduler / Tasks / IPC
 → Application Control
 → Low Power / Bootloader / OTA
```

## 3. 必要输入

- MCU/board/firmware exact identity；
- startup/vector/linker script/map/ELF；
- clock tree / memory map / datasheet；
- RTOS config、task/priority/stack；
- ISR/DMA/timer 配置；
- watchdog/reset reason；
- flash layout / Boot-App contract；
- log/trace/measurement。

## 4. Startup 与 Linker

Reset 到 main/scheduler 依次核对：clock、vector、stack、`.data` copy、`.bss` zero、C runtime、HAL/BSP、watchdog 和 scheduler start。

ROM/RAM 不足时不要只看 binary 总大小，要看 memory region、section placement、large symbols、orphan section、load/run address、stack/heap reserve 和 map 与 binary 是否一致。

## 5. RTOS 并发

分析顺序：

1. task priority/period；
2. blocking call；
3. mutex/semaphore/queue；
4. ISR-to-task handoff；
5. critical section；
6. priority inversion；
7. lock order/race；
8. timeout/watchdog。

实时性数字必须来自明确测量方法，例如 GPIO/trace/timestamp/cycle counter，不把代码路径估算写成已验证时延。

## 6. HardFault

至少收集 fault status registers、stacked registers、PC/LR/SP、ELF/map、task/ISR context、stack watermark 和 exact firmware。PC 落在某函数只说明故障现场，不自动等于根因。

## 7. MCU OTA

至少确认：Boot/App version contract、image/hash、flash layout、integrity/authenticity、power-loss recovery、rollback、boot success criteria，以及与主控升级的版本协同。

## 8. 常见失败模式

- task stack 只按经验配置，不看 watermark；
- ISR 做阻塞/长耗时操作；
- 临界区扩大导致控制周期抖动；
- mutex/queue 使用正确但 priority 设计造成饥饿；
- Bootloader/App 协议升级后忽略旧版本组合；
- HardFault 只依据 PC 猜根因；
- “平均周期正常”掩盖 worst-case jitter。

## 9. 输出与证据

输出包括启动链/内存/并发事实、实时性测量、异常上下文、OTA 约束、风险、修改边界和 Verification 要求。

## 10. 边界

系统级 Linux/MCU 分工由架构负责；长期偶发问题的 Hypothesis/Root Cause 流程由调试可靠性主导；生产签名、Fuse/OTP、生产 OTA 仍走人工 Gate。
