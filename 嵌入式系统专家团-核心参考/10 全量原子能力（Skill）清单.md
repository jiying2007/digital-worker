# 10 全量原子能力（Skill）清单

> 当前 P0 baseline 共 **23 个 Skill**，登记权威为 `config/p0-skills.yaml`。
>
> 规则：P0 Skill 默认最大动作等级 `A2_GENERATE`；未注册 Skill 禁止正式调用；Skill 输出必须被消费或声明 terminal。

## 1. 一图看懂

|归属|数量|Skill|
|---|---:|---|
|Team Lead|3|task classifier / material readiness / evidence normalizer|
|Architecture|2|architecture impact / interface contract|
|Linux/BSP|4|boot / device tree / IRQ-DMA / storage-filesystem|
|MCU/RTOS|3|startup / linker-map / RTOS concurrency|
|Driver/Component|1|driver integration review|
|Debug/Reliability|4|log triage / crash-hardfault / memory corruption / performance|
|Verification|5|plan / regression / build / device / HIL evidence|
|Review Governor|1|release readiness|
|**合计**|**23**|—|

---

## 2. Team Lead（3）

### `embedded-task-classifier`

**作用**：把输入映射为正式 task_type、workflow_mode 和 primary expert。

**关键纪律**：不默认 full_chain；不确定时返回 clarification，而不是猜。

**输出**：routing-decision。

### `embedded-material-readiness`

**作用**：按任务类型检查 repo/base、board、SoC/MCU、SDK/kernel/toolchain、schematic、log、firmware 等工程材料。

**关键纪律**：关键 identity 缺失时 BLOCK 或显式降级。

**输出**：engineering-material-manifest。

### `embedded-evidence-normalizer`

**作用**：把 log/code/datasheet/TRM/schematic/build/HIL 等输入统一成 evidence-ref set，便于 claim 引用和审计。

**关键纪律**：引用不等于验证；来源、identity 和状态必须明确。

---

## 3. Architecture（2）

### `architecture-impact-analysis`

评估功能/变更对模块、接口、资源、线程/任务、IPC、平台、Boot/OTA、验证范围的影响。

### `interface-contract-review`

检查 API/ABI/消息/IPC 接口的方向、语义、lifetime、context、timeout/error/versioning。

---

## 4. Linux/BSP（4）

### `boot-chain-analysis`

梳理 BootROM/SPL/U-Boot/Kernel/RootFS/userspace 控制权、镜像、参数和失败点。

### `device-tree-review`

检查 DT resource 与 board/driver 是否一致：compatible/reg/IRQ/clock/reset/pinctrl/DMA/reserved-memory 等。

### `irq-dma-analysis`

检查 IRQ context、DMA address/buffer/cache/alignment/completion/timeout 与 ownership。

### `storage-filesystem-analysis`

覆盖 Flash/MTD/UBI/UBIFS/FS，按介质→ECC→MTD→UBI→FS 分层，不跨层猜根因。

---

## 5. MCU/RTOS（3）

### `mcu-startup-analysis`

分析 reset/vector/C runtime/data-bss/clock/HAL/watchdog/RTOS scheduler 启动链。

### `linker-map-analysis`

分析 ROM/RAM、section、symbol、stack/heap、load/run address、overflow/orphan。

### `rtos-concurrency-analysis`

分析 task priority、mutex/semaphore/queue、ISR handoff、critical section、deadlock/race/priority inversion。

---

## 6. Driver/Component（1）

### `driver-integration-review`

检查设备驱动是否完成平台资源、错误恢复、并发、power state、API 稳定、诊断、构建和验证的完整集成。

---

## 7. Debug/Reliability（4）

### `log-triage`

构建事件时间线、错误上下文和版本 identity，只整理 diagnostic evidence，不直接宣布 root cause。

### `crash-hardfault-analysis`

分析 core/backtrace/register/panic/oops/ELF/map，产出 hypothesis registry。

### `memory-corruption-analysis`

覆盖 OOB/UAF/double-free/stack/DMA ownership/cache/concurrency corruption。

### `performance-analysis`

严格执行 baseline→measurement→bottleneck→change→remeasurement。

---

## 8. Verification（5）

### `verification-plan-builder`

把 acceptance 转换为验证层、case、环境、步骤、预期、证据和 failure recovery。

### `regression-scope-analysis`

根据 change impact 确定直接与间接回归范围。

### `build-evidence-check`

核对 source/base/toolchain/config/command/artifact/hash。

### `device-evidence-check`

核对 board/device/firmware/environment/run/log identity。

### `hil-evidence-check`

核对 HIL case/fixture/target/run/result/artifact identity。

---

## 9. Review Governor（1）

### `release-readiness-check`

检查 source/artifact identity、verification、rollback、provenance、open risk、human gate，输出 release/readiness review。

---

## 10. 当前为什么只有 23 个

当前 Skill 集合刻意保持小而硬：

- 覆盖最常见嵌入式任务；
- 能支撑 12 个 Golden Cases；
- 能支撑 Debug/Feature/Review-Release 三轨 Pilot；
- 不在真实 Pilot 前预判所有专项能力。

## 11. P1 候选（未落地，必须有真实证据才立项）

候选包括但不限于：

- SPI-NAND / ECC 深度分析；
- UBI/UBIFS recovery；
- Wi-Fi 连接/漫游/吞吐诊断；
- power/suspend/wakeup；
- MCU stack usage / interrupt latency；
- MCU OTA；
- long-run / thermal / power profiling；
- Audio/AEC/NS；
- Motor/FOC；
- camera pipeline；
- secure boot / key handling；
- boot-time optimization。

**只有多个 real Pilot/真实项目重复证明稳定复用需求时才新增。**

## 12. Skill 评审标准

新增 Skill 必须回答：

1. 是否是跨项目可复用方法，而非一次性项目知识？
2. 为什么不能作为现有 Skill 的模式/参数？
3. owner Agent 是谁？
4. 输入输出是什么？
5. 动作权限上限是什么？
6. 如何验证它不会产生 unsupported claim？
7. Golden Case / Pilot evidence 是什么？
