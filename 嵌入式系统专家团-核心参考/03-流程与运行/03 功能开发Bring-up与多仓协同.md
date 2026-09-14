# 功能开发、Bring-up 与多仓协同

## 1. 适用范围

用于新功能、驱动、组件、MCU firmware、BSP 移植、新板 Bring-up、跨 Linux/MCU 的协同开发，以及需要多个仓库共同交付的任务。

这类任务的主要风险不是“代码写不出来”，而是接口、资源、版本和验收在不同模块之间逐渐分叉。

## 2. 功能开发主流程

```text
Task Brief
  ↓
共享 Material/System Context
  ↓
架构影响分析
  ↓
BSP / MCU / Driver 按需并行分析
  ↓
Integration Reconciliation
  ↓
Gate T 技术决策
  ↓
one run → one or more Engineering Packages
  ↓
工程实施
  ↓
各 package Delivery Receipt
  ↓
系统级 Acceptance → Evidence
  ↓
Verification / Review
  ↓
Knowledge Harvest
```

## 3. 架构影响分析先于大面积修改

功能进入实施前至少看：

- 模块/进程/任务分工是否变化；
- Linux/MCU 边界是否变化；
- API/ABI/IPC/消息协议是否变化；
- CPU、RAM、ROM、buffer、线程/任务是否有预算；
- Boot、OTA、power state 是否受影响；
- 失败隔离和恢复路径；
- 直接回归和间接回归范围。

只有局部、低风险变化时可以保持轻量，不为“架构完整”而强行写大方案。

## 4. Integration Reconciliation

当前不新增独立“系统集成专家”。在 Gate T 前由主理人 + 架构责任人检查：

- interface；
- timing；
- resource；
- dependency/version；
- identity；
- ownership。

典型检查项：

|问题|示例|
|---|---|
|接口语义|Linux 写 0 是否表示 stop，MCU 是否同义|
|时序|上电后 MCU 需要 300 ms ready，主控是否过早发命令|
|资源|新增 DMA buffer 是否挤压 CMA/MCU SRAM|
|版本|Bootloader 新旧版本是否都支持 App 新协议|
|错误恢复|MCU timeout 后 Linux 是 retry、reset 还是 fail|
|ownership|协议定义由谁改，谁通知另一个仓|

## 5. One Run → Multiple Engineering Packages

多仓任务不建议做成一个巨大的“全仓工程包”。推荐：

```text
RUN-FEATURE-001
  ├─ Package A: Linux repo @ exact SHA
  ├─ Package B: MCU repo @ exact SHA
  └─ Package C: HIL/config repo @ exact SHA（如需要）
```

每个 Package 独立记录：

- repo/base；
- scope；
- implementation plan；
- allowed actions；
- acceptance contribution；
- required verification；
- delivery receipt。

Run 层负责最终把多个 Package 汇合到同一系统验收和 Review。

## 6. 多仓部分失败怎么办

例如 Linux package 已完成，MCU package 失败：

- Run 不能标 completed；
- Linux receipt 保留，不要求重做已经验证的工作；
- MCU 记录 precise blocker 和 resume point；
- 如果接口条件发生改变，才回流 Linux package；
- 系统级 Acceptance 保持 `BLOCKED/NOT_RUN`，不能由单仓成功推导整体 PASS。

## 7. Bring-up 工作法

Bring-up 强调“逐层建立可信事实”，不建议一开始把所有 DTS/驱动/配置一起改完。

### Linux/BSP

```text
Board / SoC identity
  → Boot chain
  → Clock / Reset / Pinctrl / Regulator
  → Memory / Storage
  → Kernel / DT probe
  → IRQ / DMA
  → Driver / Subsystem
  → Device evidence
```

### MCU

```text
Reset / Clock
  → Vector / C runtime
  → basic IO / debug channel
  → timer / interrupt / watchdog
  → peripheral / DMA
  → RTOS scheduler
  → application protocol
  → power / OTA（如涉及）
```

每一层通过后再扩大范围，便于定位首个不可信阶段。

## 8. 驱动和组件开发

推荐分层：

```text
Hardware / Bus
  ↓
Low-level Driver
  ↓
Platform Adapter
  ↓
Stable Component API
  ↓
Application / Service
```

业务层尽量不直接依赖寄存器、DTS 节点、板级 GPIO 编号等平台事实。

## 9. 国产替代 / 器件替换

Wi-Fi、Flash、Power 等替换不能只看“API 能编译”。至少建立 Compatibility Matrix：

- electrical/board assumption；
- bus/protocol；
- init sequence；
- capability delta；
- timing/performance；
- error behavior；
- firmware/NVM；
- Linux/MCU interface；
- production calibration/test；
- regression scope。

可复用矩阵应进入知识体系；项目专有料号和供应信息按权限处理。

## 10. 完成定义

功能开发不能用“代码合入”作为结束条件。至少要有：

- 技术边界和接口无未决冲突；
- 各 Engineering Package exact identity 完整；
- required build/device/HIL 证据齐；
- Acceptance 每条有状态；
- 残余风险被 Review 明确处理；
- 多仓结果在 Run 层重新汇合；
- Knowledge Harvest 已完成。
