# Linux / BSP 领域指南

## 1. 职责

Linux/BSP 负责目标板从 Boot 到 Kernel、Device Tree、板级资源、Storage/Filesystem 的系统级事实与 Bring-up 支撑。

## 2. 领域模型

```text
BootROM / SPL / U-Boot
        ↓
Kernel entry / early init
        ↓
DT + Clock / Reset / Pinctrl / Regulator
        ↓
Memory / IRQ / DMA / Storage
        ↓
Driver / Subsystem
        ↓
RootFS / Userspace / Device behavior
```

## 3. 必要输入

- exact BSP/kernel/SDK/source SHA；
- board revision / SoC；
- DTS/DTB/Kconfig/defconfig；
- boot args / partition layout；
- schematic / datasheet / TRM；
- boot log / dmesg；
- relevant driver source；
- image/firmware hash。

Clock、Reset、Pinctrl、Memory Map、DMA 等硬事实缺 TRM/代码时不做高置信度结论。

## 4. 常用分析路径

### Boot

先定位最后可信阶段：BootROM → SPL → U-Boot → Kernel entry → early init → mount rootfs → userspace。每个阶段记录输入镜像、控制权和关键参数。

### Probe

按 `match → resource → dependency → init order → runtime error` 排查，而不是直接改 DTS。

### IRQ/DMA

分别确认：注册/触发/上下文、buffer ownership、cache maintenance、alignment、DMA addressability、completion/timeout、硬件 ordering。

### Storage

按 `media/ECC → controller/driver → MTD → UBI → UBIFS/FS → app/power-loss` 分层，避免把文件系统只读直接等同“Flash 坏”。

### Suspend/Resume

确认 dependency order、clock/regulator、wakeup source、runtime PM、状态保存、resume error recovery。

## 5. Bring-up 最低完成标准

- 目标板 identity 清楚；
- Boot 关键阶段有直接 evidence；
- 必需设备 probe；
- IRQ/DMA/Storage 等关键资源经过目标板验证；
- 必需外设 smoke/device evidence；
- 关键失败路径可诊断；
- Build PASS 不能单独代表 Bring-up 完成。

## 6. 常见失败模式

- 一次性大改 DTS，首个错误点无法定位；
- 使用另一个 board revision 的 DTS/日志推导当前板；
- DMA 问题只改 delay，不核对 cache/lifetime/address；
- 只看 UBIFS 最后一条 error，不追底层首个异常；
- 设备可工作但 suspend/resume、error recovery 完全未覆盖；
- SDK patch、defconfig、DT、image 版本无法对应。

## 7. 输出与证据

输出应包含：最后可信阶段、资源/配置事实、技术结论、影响文件、待验证项、设备证据和回归范围。涉及性能或时序的数字必须说明测量方法。

## 8. 边界

BSP 不替硬件工程师确认电压/波形事实；Kernel panic 的平台事实由 BSP 支撑，但整体 Hypothesis/Root Cause 流程由调试可靠性主导；设备协议和组件复用由 Driver/Component 主责。
