# 架构、Linux/BSP、MCU/RTOS 与驱动领域指南

本文把四个研发专业的判断边界放在一起，方便评审跨领域任务时快速定位责任人和需要的工程事实。

# 一、嵌入式架构

## 1. 关注对象

- Linux / MCU / RTOS 功能分配；
- 进程、线程、任务和中断模型；
- IPC / message / shared memory / 跨处理器协议；
- ROM/RAM/stack/buffer/CPU 预算；
- Boot、OTA、Power State、Watchdog；
- Fault containment / recovery；
- API/ABI 和版本兼容；
- platform abstraction；
- 性能、实时性、可靠性目标分解。

## 2. 典型输入

产品目标、平台/板卡、当前系统架构、接口、资源预算、性能/功耗/成本约束、关键 evidence。

缺资源事实时允许给出 target/budget 和待验证项，但不应把目标数字写成已经测得的数据。

## 3. 判断顺序

```text
目标/约束
 → 模块与责任边界
 → 接口/数据流
 → 资源和时序
 → 故障与恢复
 → 平台/兼容影响
 → 验证范围
```

## 4. 设计输出

至少回答：

- 改哪些模块；
- 哪些接口变化；
- 资源是否有预算；
- 哪些平台受影响；
- 有什么失败模式；
- 如何回滚；
- 哪些证据还缺；
- Verification 需要覆盖什么。

# 二、Linux / BSP

## 1. 领域模型

```text
BootROM / SPL / U-Boot
        ↓
Kernel + DT + Board Resources
        ↓
Clock / Reset / Pinctrl / Regulator
        ↓
IRQ / DMA / Memory / Storage
        ↓
Driver / Subsystem
        ↓
RootFS / Userspace / Device behavior
```

## 2. 必要材料

- exact BSP/kernel/SDK；
- board revision；
- DTS/DTB/Kconfig/defconfig；
- boot args / partition layout；
- schematic / datasheet / TRM；
- boot log / dmesg；
- driver source；
- image/firmware hash。

Clock、Reset、Pinctrl、Memory Map、DMA 等硬事实缺 TRM/代码时不要高置信度下结论。

## 3. 常见问题的分层方法

### Boot 卡死

定位“最后一个可信阶段”：BootROM、SPL、U-Boot、Kernel entry、early init、mount rootfs、userspace。不要一开始泛化成“可能电源/时序”。

### Probe fail

按 `match → resource → dependency → init order → runtime error` 分层。

### IRQ/DMA

分别检查注册/上下文、buffer ownership、cache sync、alignment、addressability、completion/timeout、硬件 ordering。

### Storage/UBI/UBIFS

按 `media/ECC → controller/driver → MTD → UBI → UBIFS → application/power-loss` 分层。

### Suspend/Resume

检查设备依赖顺序、clock/regulator、wakeup source、runtime PM、状态保存和 resume error recovery。

## 4. Bring-up 完成的最低标准

编译通过不等于 Bring-up 完成。至少要有：

- 目标板 identity；
- 关键 Boot 阶段证据；
- 必需设备 probe；
- IRQ/DMA/Storage 等关键资源实测；
- 必需外设 smoke/device evidence；
- 关键错误路径可诊断。

# 三、MCU / RTOS

## 1. 领域模型

```text
Reset / Vector
  → Clock / C runtime / data-bss
  → HAL/BSP / basic IO
  → ISR / Timer / DMA / Watchdog
  → RTOS Scheduler / Tasks / IPC
  → Application Control
  → Low Power / Bootloader / OTA
```

## 2. 资源重点

- ROM/RAM region；
- section placement；
- stack/heap/static buffer；
- task stack watermark；
- interrupt latency；
- critical section 时长；
- scheduler jitter；
- queue/mutex/semaphore；
- DMA ownership；
- watchdog window；
- flash layout。

## 3. Linker/Map 分析

遇到 ROM/RAM 不足时不要只看 binary 总大小。要看：

- memory region；
- section placement；
- large symbols；
- orphan section；
- load/run address；
- `.data/.bss` startup copy/zero；
- stack/heap 预留；
- map 与实际 binary 是否一致。

## 4. RTOS 并发

分析顺序：

1. task priority 与运行周期；
2. blocking call；
3. mutex/recursive mutex/semaphore/queue；
4. ISR-to-task handoff；
5. critical section；
6. priority inversion；
7. lock order / race；
8. watchdog 与 timeout。

实时性数字必须说明测量方法，不能只用代码路径长度估算为“已验证”。

## 5. MCU OTA

至少考虑：Boot/App version contract、image hash、flash layout、power-loss recovery、rollback、integrity/authenticity、boot success criteria、与主控 OTA 的协同。

生产签名、Fuse/OTP、生产 OTA 仍由人工 Gate 控制。

# 四、驱动与组件

## 1. 分层模型

```text
Hardware / Bus
   ↓
Low-level Driver
   ↓
Platform Adapter
   ↓
Stable Component API
   ↓
Application / Service
```

目标是把板级差异控制在明确层次，不让业务代码长期绑定 DTS 节点、寄存器地址或 GPIO 编号。

## 2. 驱动完整性检查

至少检查：

1. hardware/resource identity；
2. init/probe/deinit；
3. IRQ/DMA/thread context；
4. error/timeout/retry；
5. power/suspend/resume；
6. concurrency/lifetime；
7. API/ABI；
8. logging/diagnostics；
9. build/config；
10. test/rollback/field diagnosability。

## 3. 器件替代

Wi-Fi、Flash、Power、Sensor 等替代应形成 Compatibility Matrix：

|维度|需要确认|
|---|---|
|电气/板级|电压、电流、pin、复位、时序|
|总线/协议|I2C/SPI/UART/SDIO/USB 等|
|初始化|寄存器/firmware/NVM 差异|
|能力|缺失/新增 feature|
|性能|吞吐、时延、功耗|
|异常|timeout、reset、掉线、坏块等行为|
|接口|Linux/MCU/API 影响|
|生产|校准、烧录、测试、供应差异|
|回归|直接和间接范围|

“API 兼容、能编译”只能证明很小一部分兼容性。

# 五、四个领域如何配合

以“主控 Linux + MCU 新增一个带 DMA 的设备功能”为例：

- 架构：定义 Linux/MCU 分工、接口、资源、超时和恢复；
- Linux/BSP：确认 DT、clock/reset、IRQ/DMA、内核集成；
- MCU/RTOS：确认任务周期、ISR/DMA、buffer、watchdog；
- 驱动组件：确认设备协议、API、错误恢复和复用层；
- Verification：把系统验收拆成 build/device/HIL 证据；
- Review：检查版本兼容、残余风险和回滚。

专业边界的目的不是“划地盘”，而是让每类事实都有明确 Owner。
