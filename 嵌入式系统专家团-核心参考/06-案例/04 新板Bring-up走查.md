# 案例：新板 Bring-up 走查

> 流程示例，不计入 real Pilot evidence。

## 1. 场景

已有 SoC/BSP 要适配新 board revision。硬件变化包括电源、GPIO、Flash 和一个新增外设。目标是逐层建立可信事实，而不是一次性修改整份 DTS 后“看能不能起来”。

## 2. Gate M

准备：board revision、schematic、BOM/关键料号、SoC TRM、boot media、DDR/Flash 参数、BSP/kernel SHA、defconfig、DTS、toolchain、串口/调试接口和目标板唯一标识。

硬件资料和实际板 revision 不一致时先 BLOCK。

## 3. 分层 Bring-up

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

每层通过后记录直接 evidence，再扩大下一层。

## 4. Linux/BSP 与硬件协作

软件根据 log/TRM 提出假设；电压、时钟、reset pulse、信号完整性由硬件测量确认。不要用“driver probe fail”直接推导板级电气问题，也不要用“波形正常”替代软件资源映射检查。

## 5. 首个失败点

例如 Kernel 能启动但某外设 probe fail：

1. compatible/match；
2. reg/IRQ/clock/reset/pinctrl；
3. regulator/power；
4. dependency/init order；
5. bus transaction；
6. device response。

只有资源链确认后才改 driver 行为。

## 6. 验证

Bring-up 最低证据建议：Boot 关键阶段、rootfs、必需设备 probe、IRQ/DMA、Storage、网络/音频/传感器等产品关键外设 smoke，以及必要的 reboot/suspend/resume。

## 7. Completion

“能进 shell”只是一个阶段。真正的 Bring-up 完成定义来自产品所需的关键设备链和 Acceptance；未覆盖的外设明确保持 NOT_RUN/BLOCKED。

## 8. Knowledge Harvest

可沉淀 board delta、DTS resource mapping、已确认的电源/时序约束、bring-up checklist 和已验证的恢复路径；具体料号和敏感硬件资料仍按 ACL 保存原 Source。
