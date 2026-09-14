# 案例：Linux + MCU 多仓功能与 OTA 发布走查

> 本文包含两个相连的示例：先开发一个 Linux+MCU 跨仓功能，再看它进入 OTA/发布评审时需要哪些证据。示例不计入真实 Pilot。

# 一、多仓功能开发

## 1. 场景

主控 Linux 通过串口/IPC 控制 MCU，新功能需要新增一个命令并增加状态回报。Linux 和 MCU 分属不同仓库，设备升级时两侧版本可能不完全同步。

## 2. 架构先确认接口

需要明确：

- command ID / payload / unit；
- request/response 还是 async event；
- timeout/retry；
- MCU busy/error 的返回；
- old Linux + new MCU / new Linux + old MCU 的行为；
- 上电 ready 时序；
- 版本协商；
- 故障恢复。

如果这些问题没定，两个仓分别开工很容易在集成时才发现语义不一致。

## 3. One Run → Two Packages

```text
RUN-FEATURE-021
  ├─ PKG-LINUX
  │   repo: linux-app
  │   base: <40-hex SHA>
  │   scope: protocol client + service API
  │
  └─ PKG-MCU
      repo: mcu-fw
      base: <40-hex SHA>
      scope: protocol parser + state machine
```

两个 Package 共用同一 Acceptance，但各自只负责其中一部分实现。

## 4. Integration Reconciliation

实施前和合入后都检查：

|项目|Linux|MCU|最终判断|
|---|---|---|---|
|命令号|0x31|0x31|一致|
|单位|rad/s|rad/s|一致|
|timeout|500 ms|保证 300 ms 内响应|有余量|
|版本不支持|返回 UNSUPPORTED|识别旧 command set|可回退|
|启动时序|等待 READY|上电后发 READY|一致|

任何一项未决都不应直接进入系统 PASS。

## 5. 验证

- 两仓分别 build；
- 新 Linux + 新 MCU 正向功能；
- 新 Linux + 旧 MCU 兼容；
- 旧 Linux + 新 MCU 兼容；
- timeout/retry；
- MCU reset during request；
- 必要的长稳/HIL；
- Acceptance 每条绑定 evidence。

# 二、进入 OTA / Release Readiness

## 1. Release 候选身份

发布评审不能只写“V1.2.0”。应明确：

- Linux source/tag/commit；
- Linux image hash；
- MCU source/tag/commit；
- MCU image hash；
- Bootloader 版本；
- manifest/provenance；
- 目标产品/board revision。

## 2. 升级路径

至少考虑：

```text
旧 Linux + 旧 MCU
   ↓ OTA
新 Linux + 新 MCU
```

还要考虑中间异常：

- Linux 升完、MCU 尚未升级；
- MCU 升级失败；
- 升级中掉电；
- 回滚 Linux 时 MCU 已是新版本；
- Bootloader/App version contract 不满足。

如果系统无法在这些中间状态安全工作，就需要定义升级顺序、transaction/rollback 或明确产品限制。

## 3. Release Verification

建议证据：

- exact artifact manifest；
- normal upgrade；
- downgrade/rollback；
- power-loss recovery；
- incompatible version negative case；
- target device/HIL；
- open issue/waiver；
- release note 对应 exact candidate。

## 4. Independent Review

审查重点：

- 多仓 source 和最终 binary 是否仍一一对应；
- 兼容矩阵是否覆盖真实升级路径；
- 失败后设备是否可恢复；
- Release Owner 是否清楚 residual risk；
- A7 是否已有人工批准；
- “某个 HIL case PASS”是否被错误扩写成“发布已验证”。

## 5. 如果发现问题怎么回流

例如 power-loss case 失败：

- Verification 标 FAIL；
- Review 不得 APPROVE；
- 判断失败属于 Bootloader、MCU App、Linux orchestration 还是测试环境；
- 回到对应 Engineering Package；
- 修复后重跑受影响的 upgrade/rollback case；
- 不要求无关功能全部从零重跑，但 regression scope 必须明确。

## 6. 可沉淀知识

- Linux/MCU protocol compatibility matrix；
- OTA 版本契约；
- power-loss recovery checklist；
- multi-repo release identity checklist；
- 跨版本 HIL case。

这些知识必须带适用产品/版本和 Source，不能脱离版本长期流传成口头规则。
