# 案例：MCU HardFault 与 RTOS 并发问题走查

> 流程示例，**不计入 real Pilot evidence**。  
> 通用规则见 [任务类型运行矩阵](../03-流程与运行/05%20任务类型运行矩阵.md)、[任务生命周期与 Gate](../03-流程与运行/01%20任务生命周期与Gate.md)、[验证/评审/发布](../03-流程与运行/04%20验证评审发布与异常恢复.md)。专业方法见 [MCU/RTOS](../04-专业能力/03%20MCU%20RTOS能力域指南.md) 和 [调试与可靠性](../04-专业能力/05%20调试与可靠性能力域指南.md)。

## 1. Task

设备偶发重启，MCU reset reason 指向 HardFault，且高通信负载更容易出现。目标是判断 fault 与 stack、ISR/task 并发、buffer lifetime、DMA ownership 或非法地址的关系，而不是根据 PC 落点直接猜 Root Cause。

## 2. Context / Material

冻结 MCU 型号、board revision、firmware/source identity、ELF/map、编译优化、RTOS config 和故障设备。没有与故障固件匹配的 ELF/map 时，不做符号级最终结论。

现场 Evidence 至少包括 CFSR/HFSR/MMFAR/BFAR、stacked registers、MSP/PSP、current task/ISR、stack watermark、interrupt nesting、reset reason 和最近 DMA/queue/mutex 操作。

## 3. Routing

任务由 **Embedded System Expert** 负责，`embedded.debug-reliability` 维护唯一 Hypothesis Registry，`embedded.mcu-rtos` 证明 Startup、Stack、ISR/DMA、RTOS 与 firmware 事实。若 Evidence 指向 driver contract，则扩展 `embedded.driver-component`；若出现板级电气/时钟/电源不确定性，按跨域证据升级 Hardware Expert。Verification 属于 Assurance。

## 4. Analysis / Hypothesis

候选：

- H1：task stack overflow 破坏返回地址；
- H2：DMA completion 后 buffer 已被释放/重用；
- H3：ISR 与 task 同时修改非原子共享状态；
- H4：空指针/越界导致 BusFault；
- H5：HardFault 是 watchdog/clock/power 上游异常后的次生现象。

每个 Hypothesis 都必须写出可证伪条件和区分实验。

## 5. Evidence / 区分实验

针对 H1/H2/H3，可增加 stack watermark/guard、DMA buffer ownership state + generation ID、ISR-to-task sequence trace，并用固定 workload 重复压力。

“stack 加大后不再复现”只能支持 H1，不能证明 stack overflow；仍需直接 Evidence 说明 stack 确实越界以及为何越界。

## 6. Decision / Engineering

Root Cause 足够后只修改最小责任点，例如 buffer lifetime 或 ISR/task 共享状态。不要同时修改 task priority、stack、timeout 和 DMA 逻辑，否则无法确认因果。

Engineering Package 绑定 exact base、修改范围、复现 workload、timing/stack 基线和 rollback。

## 7. Verification

围绕原 Claim 建议覆盖 cross-build、原 workload、fault injection/边界 case、stack watermark、ISR latency/control-period regression、长稳和 watchdog/reset reason。

Verification 对直接 Evidence 做层级判断，不因压力跑了一段时间未复现就扩大 PASS。

## 8. Review

Independent Review 检查是否只是扩大 stack/加 delay 掩盖问题，是否引入 priority inversion，DMA ownership 是否完整，实时性是否退化，以及 HardFault handler 是否仍保留足够现场 Evidence。

## 9. Knowledge Harvest

可沉淀 HardFault 现场采集清单、RTOS wait-for/ownership 分析方法、stack watermark 基线和 DMA lifetime 检查规则；知识 owner 落 target Capability，若最终无稳定可复用规律则 `NO_KNOWLEDGE_DELTA`。
