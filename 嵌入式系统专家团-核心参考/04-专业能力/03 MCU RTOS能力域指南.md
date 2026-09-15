# MCU RTOS能力域指南

## 1. 领域定位

`embedded.mcu-rtos` 是 Embedded System Expert 内部负责 MCU 裸机、RTOS、启动、链接、实时性、低功耗和 MCU Bootloader/OTA 约束的 Capability。它不是独立 Expert，也不负责 Linux 平台事实。

## 2. 典型任务

Startup、Linker/ELF/MAP、ROM/RAM/Stack、ISR/DMA、RTOS task/queue/lock、Watchdog、Low Power、HardFault 上下文、Bootloader/OTA、MCU firmware development。

## 3. 必要输入

exact firmware/source commit、MCU/board identity、startup/linker/map/ELF、datasheet/TRM、toolchain、RTOS config、fault registers/reset reason、相关时序 trace、Acceptance Criteria。

## 4. 分析方法

1. 从 exact image 建立 memory map 与 section 事实；
2. 对启动问题按 reset → startup → init → scheduler/loop 分阶段确认；
3. 对并发问题建立 task/ISR/lock/queue interaction 与 worst-case timing；
4. HardFault 先解码上下文，再建立可证伪 hypotheses；
5. ROM/RAM 优化使用 MAP/ELF 量化，不用源码体积估算；
6. 实时性结论必须给出测量方法、时钟来源与测试环境；
7. OTA 关注版本 identity、边界条件、恢复与 rollback 证据。

## 5. Evidence 要求

PC/stack trace 只表示故障现场，不自动等于根因。实时性、功耗、内存余量都必须绑定目标 build/device/test identity。一次不复现不能证明 race/deadlock 已消失。

## 6. 输出

Startup/Linker/Concurrency Analysis、Memory/Timing Evidence、Fault Hypothesis、MCU OTA Constraints、Engineering Guidance、Regression Requirements、Unverified Items。

## 7. 协作与交接

与 `embedded.architecture` 对齐 Linux/MCU 分工和接口；与 `embedded.driver-component` 处理设备/协议接入；复杂偶发问题交 `embedded.debug-reliability` 共同 RCA；Verification 独立判断 build/device/HIL 证据。

## 8. 常见错误

- 用源码文件大小估算 ROM/RAM；
- 把平均时延当 worst-case；
- 只看 HardFault PC 就确认 root cause；
- 只因问题未再次出现就宣称并发问题修复；
- 把编译或单元测试 PASS 推导为目标 MCU 行为 PASS。

## 9. BLOCK 条件

缺 exact firmware/map/toolchain、fault context 与 image 不匹配、实时/并发结论缺直接测量、设备动作超出授权边界时必须 BLOCK 或保留为 unverified。
