# Skill 能力地图

> **本页是 P0 Skill ID、Owner、用途与输出的唯一完整人类来源。** 岗位说明书只引用 Skill Profile/数量，不复制第二份 Skill 清单；机器权威仍是 `expert-groups/embedded-system/config/p0-skills.yaml`。

## 1. Skill 的定位

Skill 是可重复使用的工程方法，不是“再造一个专家角色”。当前 P0 共 **23 个 Skill**，机器登记以 `expert-groups/embedded-system/config/p0-skills.yaml` 为准。

P0 Skill 默认最大动作等级为 A2：可以读取、分析和生成方案/产物；涉及工作树修改、构建、设备和发布时进入工程执行边界。

## 2. 23 个 P0 Skill

|Owner|Skill|什么时候用|主要输出|
|---|---|---|---|
|主理人|`embedded-task-classifier`|任务刚进入，需要判 task type/mode|routing-decision|
|主理人|`embedded-material-readiness`|检查 repo/board/SDK/log/device 等材料|engineering-material-manifest|
|主理人|`embedded-evidence-normalizer`|把分散证据整理成可引用集合|evidence-ref-set|
|架构|`architecture-impact-analysis`|新功能/变更影响系统边界|technical-analysis|
|架构|`interface-contract-review`|API/ABI/IPC/消息协议评审|interface-review|
|Linux/BSP|`boot-chain-analysis`|启动失败、Bring-up|technical-analysis|
|Linux/BSP|`device-tree-review`|DT/resource/driver 一致性|technical-analysis|
|Linux/BSP|`irq-dma-analysis`|IRQ/DMA/cache/buffer 问题|technical-analysis|
|Linux/BSP|`storage-filesystem-analysis`|Flash/MTD/UBI/UBIFS/FS|technical-analysis|
|MCU/RTOS|`mcu-startup-analysis`|Reset 到 scheduler 的启动链|technical-analysis|
|MCU/RTOS|`linker-map-analysis`|ROM/RAM/section/stack/heap|technical-analysis|
|MCU/RTOS|`rtos-concurrency-analysis`|task/mutex/ISR/deadlock/race|technical-analysis|
|驱动组件|`driver-integration-review`|设备驱动/组件是否完整接入|technical-analysis|
|调试可靠性|`log-triage`|复杂日志先建时间线|diagnostic-evidence|
|调试可靠性|`crash-hardfault-analysis`|panic/oops/core/HardFault|hypothesis-registry|
|调试可靠性|`memory-corruption-analysis`|OOB/UAF/stack/DMA/concurrency corruption|hypothesis-registry|
|调试可靠性|`performance-analysis`|CPU/RAM/latency/boot 等性能问题|technical-analysis|
|验证|`verification-plan-builder`|把 acceptance 转成验证计划|verification-plan|
|验证|`regression-scope-analysis`|确定直接/间接回归范围|regression-scope|
|验证|`build-evidence-check`|检查 build identity/evidence|verification-evidence|
|验证|`device-evidence-check`|检查设备测试身份和证据|verification-evidence|
|验证|`hil-evidence-check`|检查 HIL case/fixture/run|verification-evidence|
|独立审查|`release-readiness-check`|交付/发布前检查 readiness|review-report|

## 3. 使用原则

### 先有问题，再选 Skill

不要看到 Skill 列表就逐个调用。路由依据是任务风险和材料，不是“技能越多结果越好”。

### Skill 输出必须被消费

例如 `log-triage` 输出的时间线如果没有进入 Hypothesis Registry 或 Technical Analysis，就只是中间笔记。正式流程要求输出被后续阶段消费，或明确声明 terminal。

### Skill 不扩大权限

分析 Skill 不因为能生成补丁就自动获得 A3 修改权限。A3/A4 进入受控 Engineering Runtime；A5-A7 继续按 Action Policy。

## 4. P1 Skill 什么时候才新增

新增 Skill 前回答：

1. 是否至少在多个真实任务中重复出现？
2. 是否是跨项目方法，而不是某个项目知识？
3. 为什么不能作为现有 Skill 的参数/模式？
4. Owner 是谁？
5. 输入输出能否稳定定义？
6. 如何验证不会制造 unsupported claim？
7. 有什么 Golden Case / Pilot evidence？

## 5. 当前 P1 候选

以下是候选，不代表已经立项：

- SPI-NAND / ECC 深度分析；
- UBI/UBIFS recovery；
- Wi-Fi 连接/漫游/吞吐；
- power/suspend/wakeup；
- MCU stack usage / interrupt latency；
- MCU OTA；
- long-run / thermal / power profiling；
- Audio/AEC/NS；
- Motor/FOC；
- camera pipeline；
- secure boot / key handling；
- boot-time optimization。

这些专项优先形成领域知识和案例；只有重复方法稳定后才升级 Skill。

## 6. Skill 与知识的区别

- Skill：如何做，例如“如何分析 Linker Map”；
- Knowledge：事实是什么，例如“某平台 SRAM 分区和限制”；
- Case：某次任务发生了什么、如何验证；
- Workflow：什么时候调用谁、经过哪些 Gate。

四者分开，才能避免 Skill 文档被项目细节污染。
