# 案例：新板 Bring-up 走查

> 流程示例，**不计入 real Pilot evidence**。  
> 通用规则见 [任务类型运行矩阵](../03-流程与运行/05%20任务类型运行矩阵.md)、[任务生命周期与 Gate](../03-流程与运行/01%20任务生命周期与Gate.md)、[验证/评审/发布](../03-流程与运行/04%20验证评审发布与异常恢复.md)。专业方法见 [Linux/BSP](../04-专业能力/02%20Linux%20BSP能力域指南.md) 和 [驱动与组件](../04-专业能力/04%20驱动与组件能力域指南.md)。

## 1. Task

已有 SoC/BSP 要适配新 board revision，硬件变化包括电源、GPIO、Flash 和新增外设。目标是逐层建立可信平台事实，而不是一次性修改整份 DTS 后“看能不能起来”。

## 2. Context / Material

冻结 board revision、schematic、BOM/关键料号、SoC TRM、boot media、DDR/Flash 参数、BSP/kernel SHA、defconfig、DTS、toolchain、串口/调试接口和目标板唯一 identity。

硬件资料与实际 board revision 不一致时先 BLOCK。

## 3. Routing

任务类型为 `platform_bringup`，目标默认仍是由 **Embedded System Expert** 承担：以 `embedded.linux-bsp` 为主，按修改面组合 `embedded.driver-component`、`embedded.mcu-rtos`。只有出现 `board-electrical-state-uncertain`、原理图/电源时序矛盾或外设电气接口不确定等直接 Evidence，才升级到 **Hardware Expert + Embedded System Expert** 的 `multi_domain` 协作。Verification 属于 Assurance。

## 4. Analysis

```text
Power / Reset / Clock assumption
→ BootROM / SPL
→ U-Boot + memory/storage
→ Kernel entry / early console
→ DT / clock/reset/pinctrl/regulator
→ rootfs
→ IRQ/DMA
→ critical peripherals
→ suspend/resume / recovery
```

每层只在前一层有直接 Evidence 后扩大下一层。

例如 Kernel 能启动但外设 probe fail，按 compatible/match → reg/IRQ/clock/reset/pinctrl → regulator/power → dependency/init order → bus transaction → device response 顺序定位首个失败点，先证明资源链，再改 driver 行为。

## 5. Evidence

软件 log/TRM 用于提出和验证软件假设；电压、时钟、reset pulse、信号完整性由硬件测量确认。不要用 `probe fail` 直接推导板级电气问题，也不要用“波形正常”替代软件资源映射检查。

每个 Bring-up 阶段记录 board/image/source identity 与直接 Evidence。

## 6. Decision / Engineering

Technical Decision 只解决当前首个失败阶段，并明确下一层进入条件。DTS/driver/boot 参数修改绑定 exact base，不进行无边界大改；硬件事实变化时相关软件分析必须重新确认适用性。

## 7. Verification

最低 Evidence 通常包括 Boot 关键阶段、rootfs、必需设备 probe、IRQ/DMA、Storage 和产品关键外设 smoke；reboot/suspend/resume 是否 required 由 Acceptance/Verification Plan 决定。

“能进 shell”只说明达到一个阶段，未覆盖外设继续保持 NOT_RUN/BLOCKED，而不是整体 Bring-up PASS。

## 8. Review

Independent Review 检查 board/source/image 是否一致、关键失败路径是否可诊断、是否把 Build/Boot 阶段成功夸大为系统完成、未覆盖设备是否显式，以及新增 workaround 是否有适用边界和退出条件。

## 9. Knowledge Harvest

可沉淀 board delta、DTS resource mapping、已确认电源/时序约束、Bring-up checklist 和恢复路径；具体料号、schematic 等敏感硬件资料仍按 ACL 保留在原 Source。知识条目只引用真实硬件 Evidence，不把一次跨域协作固化成默认多 Expert 路由。
