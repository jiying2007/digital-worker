# Linux / BSP 领域指南

> 岗位职责与任职资格见 [《数字岗位与能力模型》](../01-数字组织与岗位/03%20数字岗位与能力模型.md)。本文只描述 **Linux/BSP 专业工作怎么做**。

## 1. 领域定位

Linux/BSP 负责目标板从 Boot 到 Kernel、Device Tree、板级资源、Storage/Filesystem 和 Power Management 的系统级事实与 Bring-up 支撑。

## 2. 典型任务

新板/新 SoC Bring-up、BSP Porting、Boot 失败、Kernel/early init 问题、driver probe fail、IRQ/DMA/cache、Storage/UBI/UBIFS、Suspend/Resume、平台 patch 与版本迁移。

任务路由和 Mode 只在 [任务类型运行矩阵](../03-流程与运行/05%20任务类型运行矩阵.md) 维护。

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

## 4. 分析方法

```text
BootROM / SPL / U-Boot
→ Kernel entry / early init
→ DT + Clock / Reset / Pinctrl / Regulator
→ Memory / IRQ / DMA / Storage
→ Driver / Subsystem
→ RootFS / Userspace / Device behavior
```

### Boot

定位最后可信阶段并记录输入镜像、控制权和关键参数，不跨阶段猜测。

### Probe

按 `match → resource → dependency → init order → runtime error` 排查，先证明资源链，再修改 driver 行为。

### IRQ / DMA / Cache

核对注册与触发、上下文、buffer ownership、cache maintenance、alignment、DMA addressability、completion/timeout 和硬件 ordering。

### Storage

按 `media/ECC → controller/driver → MTD → UBI → UBIFS/FS → app/power-loss` 分层；文件系统只读只是一种上层症状。

### Suspend / Resume

核 dependency order、clock/regulator、wakeup source、runtime PM、状态保存和 resume error recovery。

## 5. Evidence 要求

Bring-up 至少要能追到目标板 identity、Boot 关键阶段、必需设备 probe、关键 IRQ/DMA/Storage 资源、产品关键外设 smoke/device evidence 和必要恢复路径。涉及性能或时序的数字必须说明测量方法。

Build PASS 只能证明构建层，不代表目标板 Bring-up 完成。

## 6. 输出

最后可信阶段、资源/配置事实、Technical Analysis、影响文件、待验证项、Device Evidence、回归范围和平台 Known Issue/Knowledge Candidate。

## 7. 协作与交接

- 硬件团队：确认电压、时钟、reset pulse、信号完整性等板级事实；
- P02 架构：系统边界、资源冲突和平台迁移影响；
- P05 Driver/Component：设备协议、driver 生命周期和公共接口；
- P06 Debug/Reliability：Kernel panic、长稳和跨层偶发问题的 Hypothesis/RCA；
- P07 Verification：独立判断目标设备 evidence 的有效层级。

## 8. 常见错误

- 一次性大改 DTS，首个错误点不可定位；
- 使用另一 board revision 的 DTS/日志推导当前板；
- DMA 问题只加 delay，不核对 cache/lifetime/address；
- 只看 UBIFS 最后一条 error，不追底层首个异常；
- 设备能工作但 suspend/resume/error recovery 未覆盖；
- SDK patch、defconfig、DT、image 版本无法对应。

## 9. BLOCK 条件

board/SoC/BSP identity 不清、硬件资料与实际板不一致、关键 TRM/代码缺失却要求寄存器级结论、关键 image/hash 无法对应、设备现象来自未确认环境，或所需硬件测量尚未取得时，应 BLOCK 或显式降低结论等级。
