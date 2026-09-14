# 组织模型、职责与 RACI

## 1. 组织方式

专家团采用 **1 名主理人 + 7 个专业角色**。这里的“角色”表示稳定职责，不要求每个角色由独立人员或独立模型永久占用。关键是任务进入系统后，谁对哪类判断负责必须清楚。

```text
                    主理人
                      │
      ┌───────┬───────┼───────┬────────┐
      ▼       ▼       ▼       ▼        ▼
    架构   Linux/BSP MCU/RTOS 驱动组件 调试可靠性
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                       验证                     独立审查
```

## 2. 主理人

主理人是唯一流程入口，负责把任务送到正确的人、正确的 Gate 和正确的工程边界。

### 主要职责

- 建立任务 charter 和 Run；
- 判 task type / workflow mode；
- 组织 Gate K/M/0；
- 路由最小必要专业角色；
- 维护 run state / gate ledger；
- 汇总 Gate T 技术决策；
- 组装 Engineering Package；
- 记录 Runtime/执行身份；
- 调度 Verification / Review；
- 处理 blocker、降级、恢复和收口。

### 明确不做

- 不替 Linux/MCU/Driver 等专业 Owner 编结论；
- 不因为 Runtime 输出“成功”就签 Verification PASS；
- 不默认把所有任务扩成 full-chain；
- 不把缺失材料用常识补齐；
- 不绕过 A6/A7 人工批准。

## 3. 七个专业角色

### 嵌入式架构

负责系统分层、Linux/MCU 职责、资源预算、接口、实时性、生命周期、故障隔离和平台影响。

### Linux/BSP

负责 Boot、Kernel、Device Tree、Clock/Reset/Pinctrl、IRQ/DMA、Storage/Filesystem 和板级资源事实。

### MCU/RTOS

负责 Startup、Linker、ROM/RAM、ISR/DMA、RTOS、Watchdog、低功耗、Bootloader/OTA 和 MCU 侧实时性。

### 驱动与组件

负责设备协议、驱动集成、组件接口、错误恢复、跨平台适配、国产替代和可复用能力。

### 调试与可靠性

负责 Evidence timeline、Hypothesis Registry、Root Cause、长稳、内存/并发/性能诊断和回归范围。

### 验证

负责 Verification Plan、required layer、build/device/HIL evidence identity、回归充分性和验证报告。

### 独立审查

负责风险、错误放行、P0/P1 finding、Release Readiness 和最终审查意见。

## 4. 核心 RACI

R=Responsible，A=Accountable，C=Consulted，I=Informed。

|活动|主理人|架构|BSP|MCU|驱动|调试|验证|审查|
|---|---|---|---|---|---|---|---|---|
|任务分类/Gate K/M/0|A/R|C|C|C|C|C|I|I|
|系统架构/接口方案|A|R|C|C|C|C|C|I|
|Linux/BSP 技术结论|A|C|R|C|C|C|C|I|
|MCU/RTOS 技术结论|A|C|C|R|C|C|C|I|
|驱动/组件方案|A|C|C|C|R|C|C|I|
|Debug Hypothesis/Root Cause|A|C|C|C|C|R|C|I|
|Engineering Package|A/R|C|C|C|C|C|C|I|
|代码/工程实施|I|I|I|I|I|I|I|I|
|Verification Plan/Report|I|C|C|C|C|C|A/R|I|
|Independent Review|I|C|C|C|C|C|C|A/R|
|Closure|A/R|I|I|I|I|I|C|C|

工程实施由工程师 + 受控 Engineering Runtime 负责，不归任何“专家角色”自动所有。

## 5. 冲突怎么处理

### 专业结论冲突

先比较：

1. 是否使用同一 System Context；
2. evidence 是否来自同一版本/设备；
3. 结论属于哪个领域的最终判断权；
4. 是否需要新的 discriminating experiment。

主理人负责推动收敛，但不通过“投票”替代证据。

### 架构与领域实现冲突

架构负责系统边界和约束，领域 Owner 负责证明具体平台事实。如果架构假设与 TRM/代码/测试事实冲突，应更新技术决策，而不是要求领域事实服从设计文档。

### Verification 与实现冲突

Verification 对证据覆盖有最终判断权。实现者可以补证据或质疑验证方法，但不能自行把失败改为 PASS。

### Review 与项目进度冲突

进度压力不能删除 finding。若业务确需承担残余风险，使用显式 Risk Acceptance/APPROVE_WITH_RISK，并写责任人和期限。

## 6. 简单任务如何减负

不是所有任务都需要七个角色参与。

- 单一 DTS 问题：主理人 + BSP，必要时 Verification；
- 明确 MCU Linker overflow：主理人 + MCU，按风险决定是否进入工程链；
- 单纯 Code Review：Review Governor 主责，需要领域事实时再拉 BSP/MCU/Driver；
- 技术可行性评审：架构主责，不自动进入 Execution。

组织模型稳定，不代表每次任务都把全员叫齐。

## 7. 人与工具的关系

这些角色可以由人、受控模型或混合方式承担分析辅助，但责任边界不随工具变化：

- 人负责组织授权和最终责任；
- Runtime/模型可以读资料、分析、生成方案和执行受控工程动作；
- 关键设备写入、发布、风险接受仍由明确人员批准；
- Verification/Review 的独立性要从任务记录和证据上体现，而不是只看“用了不同模型”。
