# Linux BSP能力域指南

## 1. 领域定位

`embedded.linux-bsp` 是 Embedded System Expert 内部负责 Linux 平台与目标板系统事实的 Capability。覆盖 Bootloader、Kernel、Device Tree、IRQ/DMA、Storage/Filesystem、Power 和 BSP Porting。它不是独立 Expert；需要硬件电气事实时必须由 Hardware Expert 提供直接 Evidence。

## 2. 典型任务

Boot 失败、Kernel panic、DT/probe、Clock/Reset/Pinctrl、IRQ/DMA/cache、SPI-NAND/MTD/UBI/UBIFS、Suspend/Resume、BSP Porting、新板 Bring-up、Flash/平台替代。

## 3. 必要输入

exact BSP/SDK/source commit、board revision、boot/image identity、DTS/Kconfig、kernel/toolchain、TRM/datasheet、必要的 schematic ref、boot/dmesg/MTD/UBI/UBIFS log、设备测试环境。

## 4. 分析方法

1. 沿 Boot/Kernel/Driver/Storage 链定位最后一个已确认阶段；
2. 区分 controller / DMA / MTD / UBI / filesystem 等层级；
3. 对 DMA 明确 direction、buffer lifetime、cache ownership 和 maintenance；
4. 对 Storage 先做非破坏证据收集，再讨论任何高风险恢复；
5. 对 Bring-up 逐里程碑记录 build 与 device evidence；
6. 将平台私有行为隔离，不向公共 API 泄漏。

## 5. Evidence 要求

Build PASS 只证明构建层。Device/Storage/Power 结论需要对应 target Evidence；板级电压、时序、信号等事实不能由软件日志替代。任何跨版本结论必须绑定适用的 BSP/board/device identity。

## 6. 输出

Boot/DT/IRQ-DMA/Storage Analysis、BSP Impact、Bring-up Evidence、Root-cause facts or hypotheses、Regression Scope、Unverified Items。

## 7. 协作与交接

与 `embedded.driver-component` 协作设备接入，与 `embedded.debug-reliability` 协作复杂 RCA，与 `embedded.architecture` 处理系统影响。电气契约不确定时由 Edge Coordination evidence-triggered 升级 Hardware Expert。Verification 独立判断证据层级。

## 8. 常见错误

- 把 crash site 当 corruption origin；
- 从 generic Linux 行为推导特定 SoC cache 一致性；
- 把 controller ECC 状态直接当 filesystem 根因；
- 未完成证据收集就进入高风险恢复；
- 用 host/cross-build PASS 宣称目标板已验证。

## 9. BLOCK 条件

缺 exact BSP/board/image identity、日志与源码明显不匹配、需要高风险恢复但没有授权、关键电气事实未知且直接影响结论时必须 BLOCK。
