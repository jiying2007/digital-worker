# 案例：Linux + MCU 多仓功能与 OTA 发布走查

> 示例说明“一次跨仓功能如何进入 Release/OTA readiness”，**不计入 real Pilot evidence**。  
> 通用规则见 [任务类型运行矩阵](../03-流程与运行/05%20任务类型运行矩阵.md)、[任务生命周期与 Gate](../03-流程与运行/01%20任务生命周期与Gate.md)、[验证/评审/发布](../03-流程与运行/04%20验证评审发布与异常恢复.md)。专业方法见 [嵌入式架构](../04-专业能力/01%20嵌入式架构能力域指南.md)、[MCU/RTOS](../04-专业能力/03%20MCU%20RTOS能力域指南.md)；Release 风险边界见 [Independent Review 与发布边界](../06-治理与评审/06%20Independent%20Review与发布边界.md)。

## 1. Task

主控 Linux 通过串口/IPC 控制 MCU。新功能要增加一个 command 和状态回报，Linux 与 MCU 分属不同仓库，升级时两侧版本可能不同步。

目标不是“两仓各自编译通过”，而是形成明确接口契约、兼容矩阵、双仓 Engineering Package、系统 Evidence 和可恢复的 OTA/Release 路径。

## 2. Context / Material

冻结 Linux/MCU repo 与 exact base、当前协议、Bootloader/App contract、目标 board/product、现有 OTA 流程和 Acceptance。

接口至少明确 command ID/payload/unit、sync/async、timeout/retry、busy/error、ready 时序、版本协商、old/new 组合行为和 recovery。

## 3. Routing

任务由 **Embedded System Expert** 负责，`embedded.architecture` 收敛跨仓接口与系统约束；按实际修改面组合 `embedded.linux-bsp`、`embedded.mcu-rtos`、`embedded.driver-component`。一个 Run 可以生成多个 repo-specific Engineering Package，但共享同一 Acceptance、Work Item 与系统 identity。Verification 属于 Assurance；进入 release readiness 时再按政策触发 Independent Review / human A7 decision。

示例：

```text
RUN-FEATURE-021
  ├─ PKG-LINUX  repo=linux-app  base=<40-hex SHA>
  └─ PKG-MCU    repo=mcu-fw     base=<40-hex SHA>
```

## 4. Analysis / Compatibility

在实施前和集成后都做一致性 reconciliation，例如 command、unit、timeout、unsupported 行为、启动 ready、版本协商和故障恢复。

兼容组合至少考虑：新 Linux + 新 MCU、新 Linux + 旧 MCU、旧 Linux + 新 MCU。任何关键语义未决都不能直接写系统 PASS。

## 5. Evidence

功能阶段保留两仓独立 build identity、最终 image/hash、接口 trace、timeout/retry、MCU reset during request、跨版本组合和 required HIL/long-run evidence。

进入 OTA/Release 前，再冻结 Linux/MCU source/tag/commit、binary hash、Bootloader、manifest/provenance 和目标 product/board revision。

## 6. Decision / Engineering

系统要明确升级顺序和中间状态行为：Linux 已升级但 MCU 未升级、MCU 升级失败、升级中掉电、回滚 Linux 时 MCU 已是新版本、Bootloader/App contract 不满足。

如果系统无法在中间状态安全工作，就需要 transaction/rollback 或明确产品限制，不能依赖“正常升级一般很快”。

## 7. Verification

功能 Claim 验证正向、跨版本兼容、timeout/retry/reset；Release candidate 再验证 exact manifest、normal upgrade、downgrade/rollback、power-loss、incompatible negative case、required device/HIL 和 open issue/waiver。

Acceptance 每条映射直接 Evidence；单一 HIL case PASS 不扩写为“Release 已验证”。

## 8. Review

Independent Review 核对多仓 source 与 binary 是否一一对应、兼容矩阵是否覆盖真实升级路径、失败后设备是否可恢复、residual risk 是否显式、Release Owner/A7 approval 是否满足。

若 power-loss case FAIL，Verification 保持 FAIL，Review 不 APPROVE；定位 Bootloader、MCU App、Linux orchestration 或 test environment 的责任阶段后增量修复和复验。

## 9. Knowledge Harvest

可沉淀 protocol compatibility matrix、OTA version contract、power-loss recovery checklist、multi-repo release identity checklist 和跨版本 HIL case。知识必须带适用产品/版本和 Source，不能脱离 identity 长期流传成口头规则。
