# 案例：MCU HardFault 与 RTOS 并发问题走查

> 流程示例，不计入 real Pilot evidence。

## 1. 场景

设备偶发重启，MCU reset reason 指向 HardFault。故障多出现在通信高负载时，现场只能拿到 fault registers、少量日志和当前 firmware。目标不是“根据 PC 猜函数”，而是判断是否与 stack、ISR/task 并发、buffer lifetime 或非法地址有关。

## 2. 先冻结身份

至少确认 MCU 型号、board revision、firmware 40-hex/source identity、ELF/map、编译优化、RTOS 配置和故障设备。没有与固件匹配的 ELF/map 时，不做符号级最终结论。

## 3. 现场证据

收集：

- CFSR/HFSR/MMFAR/BFAR 等 fault status；
- stacked R0-R3/R12/LR/PC/xPSR；
- MSP/PSP；
- 当前 task/ISR；
- task stack watermark；
- interrupt mask/nesting；
- reset reason；
- 最近 DMA/queue/mutex 操作。

## 4. Hypothesis

- H1：某 task stack overflow 破坏返回地址；
- H2：DMA completion 后 buffer 已被另一个 task 释放/重用；
- H3：ISR 与 task 同时修改非原子共享状态；
- H4：空指针/越界导致 BusFault；
- H5：HardFault 是上游 watchdog/clock/power 异常后的次生现象。

每个假设都要写能够区分它的实验。

## 5. 区分实验

例如 H1/H2/H3：

- 增加 stack watermark/guard，而不是只把 stack 翻倍；
- 对 DMA buffer 增加 ownership state 和 generation ID；
- 在 ISR-to-task handoff 处记录 sequence；
- 使用固定 workload 重复压力；
- 比较 fault PC/LR 与被破坏对象的时间关系。

如果“stack 加大后不再复现”，只能支持 H1，仍需证明 stack 真的越界以及为何越界。

## 6. Engineering Package

Root Cause 确认后只修改最小责任点，例如修复 buffer lifetime 或 ISR/task 共享状态；不要同时调整 task priority、stack、timeout 和 DMA 逻辑，否则无法确认因果。

## 7. Verification

建议包括：

- cross-build；
- 原 workload 复现；
- fault injection/边界 case；
- stack watermark；
- ISR latency/control-period regression；
- 长稳；
- watchdog/reset reason 无新增异常。

## 8. Review

重点看：是否只通过扩大 stack/加 delay 掩盖问题；是否引入 priority inversion；DMA ownership 是否有完整释放路径；实时性是否退化；HardFault handler 是否保留足够现场证据。

## 9. Knowledge Harvest

可复用内容包括 HardFault 现场采集清单、RTOS wait-for/ownership 分析方法、stack watermark 基线和 DMA lifetime 检查规则。
