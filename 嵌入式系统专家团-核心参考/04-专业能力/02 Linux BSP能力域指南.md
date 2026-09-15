# Linux BSP能力域指南

## 1. 领域定位

`embedded.linux-bsp` 是 Embedded System Expert 内负责 Linux 平台与目标板系统事实的 Capability，覆盖 Bootloader、Kernel、Device Tree、Clock/Reset/Pinctrl、IRQ/DMA、Storage/Filesystem、Power 与 BSP Porting。需要电气事实时必须取得 Hardware Expert 的直接 Evidence。

## 2. 典型任务

新板/新 SoC Bring-up、BSP Porting、Boot 失败、Kernel/early init、driver probe fail、IRQ/DMA/cache、SPI-NAND/MTD/UBI/UBIFS、Suspend/Resume、Flash/平台替代、SDK patch 与版本迁移。

## 3. 必要输入

- exact BSP / kernel / SDK / source commit；
- board revision / SoC / device identity；
- DTS/DTB/Kconfig/defconfig；
- boot args / partition layout / image hash；
- schematic ref / datasheet / TRM；
- boot log / dmesg / MTD / UBI / UBIFS log；
- relevant driver source；
- toolchain、测试环境与关键外设版本。

Clock、Reset、Pinctrl、Memory Map、DMA、ECC 等硬事实缺 TRM/代码/测量时不做高置信寄存器级结论。

## 4. 分析方法

```text
BootROM / SPL / U-Boot
→ Kernel entry / early init
→ DT + Clock / Reset / Pinctrl / Regulator
→ Memory / IRQ / DMA / Storage
→ Driver / Subsystem
→ RootFS / Userspace
→ Device behavior / Power / Recovery
```

### 4.1 Boot

从 reset 开始定位最后可信阶段，绑定输入镜像、load address、控制权、command line、关键 clock/reset 和 handoff state。跨阶段推断必须明确标成 hypothesis。

### 4.2 Device Tree / Probe

按 `match → resource → dependency → init order → runtime error` 排查；先证明资源链和依赖，再修改 driver 行为。核对 compatible、reg/irq/gpio/clock/reset/regulator、defer、alias、memory reservation 与 board revision。

### 4.3 IRQ / DMA / Cache

核对注册与触发、上下文、buffer ownership/lifetime、direction、cache maintenance、alignment、DMA addressability、IOMMU/CMA（如适用）、completion/timeout 和硬件 ordering。不能用“加 delay 后好了”替代一致性分析。

### 4.4 Storage / SPI-NAND / UBI / UBIFS

按以下层级建立时间线，而不是只看最后一条 filesystem error：

```text
media / bad block / ECC
→ controller / SPI-NAND driver
→ MTD
→ UBI attach / volume
→ UBIFS / filesystem
→ application write pattern
→ reset / power-loss / concurrency
```

记录 on-die/controller ECC 模式、read/write/erase 返回值、bad block、UBI/UBIFS 错误前后文、并发写模型、掉电/复位条件。恢复动作前先完成非破坏取证；修复必须说明数据风险和回退路径。

### 4.5 Suspend / Resume / Power

核 dependency order、clock/regulator、wakeup source、runtime PM、state save/restore、driver suspend/resume、error recovery 与 wakeup race。正常启动 PASS 不能替代 suspend/resume。

### 4.6 Bring-up

逐里程碑保存 Build + Device Evidence：启动、console、storage、network、关键总线、产品关键外设、power/reboot/recovery。每个里程碑绑定 board/image/source identity。

## 5. Evidence 要求

Build PASS 只证明构建层。Device/Storage/Power 结论要求对应 target Evidence。性能/时序数字必须说明测量方法；日志必须保留上下文和对象 identity；另一块板、另一 SDK、另一 image 的结果不能自动外推。

## 6. 输出

Last Confirmed Stage、Boot/DT/IRQ-DMA/Storage Analysis、BSP Impact、Root-cause Facts/Hypotheses、Bring-up Evidence、Affected Files、Regression Scope、Unverified Items、Known Issue / Knowledge Candidate。

## 7. 协作与交接

- `embedded.driver-component`：设备协议、driver 生命周期和 stable interface；
- `embedded.debug-reliability`：Kernel panic、长稳、跨层偶发问题的 hypothesis/RCA；
- `embedded.architecture`：系统边界、资源冲突、平台迁移影响；
- Hardware Expert：电压、时钟、reset pulse、信号、电气和器件事实；
- `assurance.verification`：独立判断 Build/Device/HIL evidence 层级。

### 7.1 Verification 关注点

按实际 scope 覆盖目标板启动、关键 probe、IRQ/DMA/Storage、错误恢复、Power、必要长稳和负向路径。Flash/Filesystem 修复不得只验证“重新挂载成功”，还要验证数据完整性、重复写、异常复位与目标 workload。

## 8. 常见错误

- 一次性大改 DTS，首个错误点不可定位；
- 使用另一 board revision 的 DTS/日志推导当前板；
- DMA 问题只加 delay，不核 cache/lifetime/address；
- 只看 UBIFS 最后一条 error，不追底层首个异常；
- controller ECC 状态直接被写成 filesystem 根因；
- 设备能工作但 suspend/resume/error recovery 未覆盖；
- SDK patch、defconfig、DT、image 版本无法对应；
- 未完成取证就执行高风险恢复。

## 9. BLOCK 条件

board/SoC/BSP/image identity 不清、硬件资料与实际板不一致、关键 TRM/代码缺失却要求寄存器级结论、日志截断无法恢复关键上下文、高风险恢复未授权、需要硬件测量但尚未取得时必须 BLOCK 或显式降低结论等级。

## 10. Knowledge Harvest 与质量指标

可沉淀 boot/probe checklist、DMA/cache rule、Storage known issue、BSP compatibility matrix、bring-up milestone 和 recovery runbook。主要指标：target-device evidence coverage、unsupported claim rate、correct block rate、回归逃逸率、平台问题复用率。
