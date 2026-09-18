# 嵌入式系统开发 Skill 全景与目标覆盖

> **用途：回答“如果要覆盖完整嵌入式系统开发，需要哪些 Skill”**  
> **性质：目标覆盖清单（coverage inventory），不是第二份 canonical Registry**  
> **机器权威：`domains/edge-foundation/skills.yaml`**  
> **当前 canonical：23 个；当前 evidence-backed OBSERVED_GAP：9 个**
>
> 本页把“当前已经注册的 Skill”和“完整嵌入式研发最终需要覆盖的方法空间”分开。  
> **列入本页不等于已经实现、不等于已经成熟、更不等于允许 Runtime 调用。**

## 1. 为什么需要这张全景图

当前 23 个 canonical Skill 已经覆盖核心分析、Evidence、Verification 与 Release readiness，但它们是当前最小稳定 invocation surface，**不能被解释为已经穷尽完整嵌入式研发生命周期**。

完整嵌入式开发通常还会经过：

```text
需求与约束
→ 系统/软件架构
→ Linux / BSP / MCU / RTOS Bring-up
→ Driver / Component 实现与集成
→ Build / Configuration / Packaging
→ Debug / Reliability / Performance
→ Verification / HIL / Regression
→ Security
→ OTA / Release
→ Production / Calibration / Factory
→ Field Incident / RMA / Lifecycle
→ 产品专项（电机、音频、视频、AI、无线、电源等）
```

因此需要一张稳定的**目标覆盖地图**，用于发现长期缺口；但是否把某一项真正晋级为 canonical Skill，仍由真实重复任务和 Evidence 决定。

## 2. 状态语义

| 状态 | 含义 | 是否可 canonical invocation |
|---|---|---|
| `CURRENT_CANONICAL` | 已在 `skills.yaml` 注册，有正式 `SKILL.md` | **可以**，仍受 Runtime / Action Policy / Evidence Gate 约束 |
| `OBSERVED_GAP` | 已在真实工程/评审中反复观察到独立方法缺口 | **不可以**，通过准入 Gate 后才可晋级 |
| `TARGET_COVERAGE` | 为覆盖完整研发生命周期而列出的目标方法单元 | **不可以**；当前只是 coverage hypothesis |
| `CONDITIONAL_SPECIALIZATION` | 只有特定产品/技术栈需要的专业能力 | **不可以**；按产品线重复证据决定是否建立 |
| `EXTERNAL_BOUNDARY` | 属于 Hardware / Structure / 合规或其他责任域 | 不应伪装成 Embedded Skill |

当前目标覆盖 inventory 共 **75 项**：

- 23 `CURRENT_CANONICAL`
- 9 `OBSERVED_GAP`
- 33 `TARGET_COVERAGE`
- 10 `CONDITIONAL_SPECIALIZATION`

这 **75 项不是“未来必须建 75 个 SKILL.md”**。它们是评审和规划用的 coverage inventory；长期可能通过合并、复用、workflow composition 保持更少的 canonical Skill。

## 3. Coordination / Intake / Evidence

| Skill | 状态 | Owner | 目标覆盖 |
|---|---|---|---|
| `embedded-task-classifier` | CURRENT_CANONICAL | Edge Coordination | request → task/mode/route |
| `embedded-material-readiness` | CURRENT_CANONICAL | Edge Coordination | source/system/device/material readiness 与 BLOCK |
| `embedded-evidence-normalizer` | CURRENT_CANONICAL | Edge Coordination | evidence identity、claim/source normalization |

这一层只组织任务与证据，不替 Engineering Capability 产生专业事实。

## 4. Architecture / Requirements / System Design

| Skill | 状态 | Target Owner | 目标覆盖 |
|---|---|---|---|
| `architecture-impact-analysis` | CURRENT_CANONICAL | `embedded.architecture` | 变化对边界、资源、NFR、验证面的影响 |
| `interface-contract-review` | CURRENT_CANONICAL | `embedded.architecture` | API/ABI/IPC/protocol/lifecycle/error/version contract |
| `requirements-decomposition` | TARGET_COVERAGE | `embedded.architecture` | 产品需求/Acceptance → 技术约束、责任、验证条件 |
| `resource-timing-power-budget-analysis` | TARGET_COVERAGE | `embedded.architecture` | CPU/RAM/ROM/带宽/时延/周期/功耗预算与余量 |
| `lifecycle-fault-recovery-architecture` | TARGET_COVERAGE | `embedded.architecture` | Boot/Run/Sleep/Reset/Recovery/OTA/失败中间态 |
| `platform-version-portability-analysis` | TARGET_COVERAGE | `embedded.architecture` | SoC/MCU/SDK/组件版本差异、兼容与迁移边界 |

完整覆盖要求架构 Skill 能把“能实现”与“能验证、能恢复、能升级、能跨版本运行”同时纳入设计。

## 5. Linux / BSP / Kernel / RootFS

| Skill | 状态 | Target Owner | 目标覆盖 |
|---|---|---|---|
| `boot-chain-analysis` | CURRENT_CANONICAL | `embedded.linux-bsp` | BootROM/SPL/U-Boot/Kernel/rootfs/userspace 启动链 |
| `device-tree-review` | CURRENT_CANONICAL | `embedded.linux-bsp` | DT/resource/binding/clock/reset/pinctrl/regulator |
| `irq-dma-analysis` | CURRENT_CANONICAL | `embedded.linux-bsp` | IRQ/DMA/cache/ownership/address/completion |
| `storage-filesystem-analysis` | CURRENT_CANONICAL | `embedded.linux-bsp` | media/controller/MTD/UBI/filesystem/app write path |
| `kernel-config-diff-review` | OBSERVED_GAP | `embedded.linux-bsp` | Kconfig/defconfig/SDK migration 差异 |
| `flash-ecc-badblock-analysis` | OBSERVED_GAP | `embedded.linux-bsp` | NAND ECC/bad block/controller/read-write semantics |
| `linux-board-bringup-analysis` | TARGET_COVERAGE | `embedded.linux-bsp` | 新板/新 SoC 从 console 到关键外设的分阶段 Bring-up |
| `linux-platform-resource-analysis` | TARGET_COVERAGE | `embedded.linux-bsp` | clock/reset/pinctrl/regulator/reserved-memory/IOMMU/CMA 等平台资源 |
| `rootfs-userspace-integration-analysis` | TARGET_COVERAGE | `embedded.linux-bsp` | rootfs、init、service、mount、权限、启动依赖与恢复 |
| `linux-network-subsystem-analysis` | TARGET_COVERAGE | `embedded.linux-bsp` | Ethernet/Wi-Fi 网络栈、接口、路由、DNS/socket 与系统级网络故障 |

Linux/BSP 目标覆盖应从“内核能启动”一直追到目标板真实 userspace/device behavior。

## 6. MCU / Bare-metal / RTOS

| Skill | 状态 | Target Owner | 目标覆盖 |
|---|---|---|---|
| `mcu-startup-analysis` | CURRENT_CANONICAL | `embedded.mcu-rtos` | Reset/vector/clock/C runtime/HAL/scheduler startup |
| `linker-map-analysis` | CURRENT_CANONICAL | `embedded.mcu-rtos` | Linker/MAP/ELF/ROM/RAM 布局与溢出 |
| `rtos-concurrency-analysis` | CURRENT_CANONICAL | `embedded.mcu-rtos` | task/ISR/lock/queue/priority/worst-case blocking |
| `watchdog-reset-analysis` | OBSERVED_GAP | `embedded.mcu-rtos` | watchdog ownership、reset reason、故障快照与恢复 |
| `ota-bootloader-analysis` | OBSERVED_GAP | `embedded.mcu-rtos` / `embedded.architecture` 待最终裁决 | Boot/App contract、升级状态机、掉电恢复、rollback |
| `mcu-board-bringup-analysis` | TARGET_COVERAGE | `embedded.mcu-rtos` | clock/GPIO/console/timer/basic bus/peripheral 的分阶段 Bring-up |
| `mcu-peripheral-timing-analysis` | TARGET_COVERAGE | `embedded.mcu-rtos` | timer/PWM/ADC/IRQ/DMA/优先级/采样与控制时序 |
| `realtime-scheduling-timing-analysis` | TARGET_COVERAGE | `embedded.mcu-rtos` | deadline/WCET/jitter/latency/scheduling budget |
| `baremetal-firmware-architecture` | TARGET_COVERAGE | `embedded.mcu-rtos` | super-loop/state machine/ISR foreground-background/resource ownership |

## 7. Cross-platform Power / Lifecycle

| Skill | 状态 | Target Owner | 目标覆盖 |
|---|---|---|---|
| `power-state-analysis` | OBSERVED_GAP | `embedded.linux-bsp` / `embedded.mcu-rtos` 待最终裁决 | standby/suspend/deep sleep/wakeup/state save-restore/power race |

Power 是跨 Linux/MCU 的真实交叉面；如果后续证据显示方法无法由单一 owner 稳定承载，应先做责任裁决，而不是为了方便直接增加新 Expert。

## 8. Driver / Component / Protocol / Device Integration

| Skill | 状态 | Target Owner | 目标覆盖 |
|---|---|---|---|
| `driver-integration-review` | CURRENT_CANONICAL | `embedded.driver-component` | init/deinit/error/recovery/power/concurrency/API compatibility |
| `device-substitution-qualification` | OBSERVED_GAP | `embedded.driver-component` | Flash/Wi-Fi/Power/Sensor 等替代器件 compatibility matrix |
| `production-calibration-test-analysis` | OBSERVED_GAP | `embedded.driver-component` | IMU/电机/传感器校准、产测数据与工程约束 |
| `datasheet-register-contract-analysis` | TARGET_COVERAGE | `embedded.driver-component` | datasheet/TRM/register/timing/error semantics → driver contract |
| `bus-protocol-driver-development` | TARGET_COVERAGE | `embedded.driver-component` | I2C/SPI/UART/CAN/USB/SDIO 等总线与协议驱动方法 |
| `component-api-platform-adapter-design` | TARGET_COVERAGE | `embedded.driver-component` | stable API、platform adapter、lifetime/version/diagnostics |
| `device-firmware-nvm-calibration-analysis` | TARGET_COVERAGE | `embedded.driver-component` | device firmware/NVM/calibration/version/reset/recovery |

不是每一种 I2C/SPI/UART 设备都建立独立 Skill；只有方法、Evidence contract 或责任边界长期分叉才继续拆分。

## 9. Build / Toolchain / Configuration / Artifact

| Skill | 状态 | Target Owner | 目标覆盖 |
|---|---|---|---|
| `toolchain-build-system-analysis` | TARGET_COVERAGE | `embedded.architecture` + 目标平台 Capability | compiler/linker/Make/CMake/Kconfig/toolchain/cross-build 问题 |
| `configuration-variant-dependency-analysis` | TARGET_COVERAGE | `embedded.architecture` + 目标平台 Capability | SKU/board/config/feature/dependency/version variant 管理 |
| `reproducible-firmware-packaging-analysis` | TARGET_COVERAGE | `embedded.architecture` | source/config/toolchain → image/package/hash/manifest 的可复现链 |

这里是 Engineering 方法；Assurance 中的 `build-evidence-check` 仍独立判断“构建证据是否成立”，两者不能合并为自签。

## 10. Debug / Reliability / Performance / Field Incident

| Skill | 状态 | Target Owner | 目标覆盖 |
|---|---|---|---|
| `log-triage` | CURRENT_CANONICAL | `embedded.debug-reliability` | raw log → timeline / Observed-Inferred separation |
| `crash-hardfault-analysis` | CURRENT_CANONICAL | `embedded.debug-reliability` | Crash/HardFault context、symbol、hypothesis |
| `memory-corruption-analysis` | CURRENT_CANONICAL | `embedded.debug-reliability` | OOB/UAF/stack/heap/DMA/lifetime corruption |
| `performance-analysis` | CURRENT_CANONICAL | `embedded.debug-reliability` | baseline/measurement/bottleneck/before-after |
| `long-run-soak-analysis` | OBSERVED_GAP | `embedded.debug-reliability` | 7x24、资源增长、温升、累计退化 |
| `latency-jitter-analysis` | OBSERVED_GAP | `embedded.debug-reliability` / `embedded.mcu-rtos` 待最终裁决 | tail latency、deadline、jitter、实时性证据 |
| `deadlock-race-analysis` | TARGET_COVERAGE | `embedded.debug-reliability` | wait-for graph、lock order、race/lost wakeup/starvation |
| `resource-leak-exhaustion-analysis` | TARGET_COVERAGE | `embedded.debug-reliability` | memory/fd/socket/thread/handle/queue 资源泄漏与耗尽 |
| `field-incident-correlation` | TARGET_COVERAGE | `embedded.debug-reliability` | 多设备/多版本/时间窗/环境事件关联与现场 RCA 收敛 |

## 11. Verification / Test / HIL / Regression

| Skill | 状态 | Target Owner | 目标覆盖 |
|---|---|---|---|
| `verification-plan-builder` | CURRENT_CANONICAL | Verification | Acceptance → verification layer → direct evidence |
| `regression-scope-analysis` | CURRENT_CANONICAL | Verification | change impact → minimum sufficient regression |
| `build-evidence-check` | CURRENT_CANONICAL | Verification | exact source/config/toolchain/artifact build evidence |
| `device-evidence-check` | CURRENT_CANONICAL | Verification | exact board/firmware/procedure/raw device evidence |
| `hil-evidence-check` | CURRENT_CANONICAL | Verification | exact HIL case/fixture/target/run evidence |
| `embedded-test-design-automation` | TARGET_COVERAGE | Verification | unit/component/integration/device 自动化测试设计 |
| `fault-injection-stress-verification` | TARGET_COVERAGE | Verification | timeout/reset/bus-error/power-loss/stress/soak 负向验证 |
| `performance-timing-verification` | TARGET_COVERAGE | Verification | latency/jitter/throughput/resource/power 的可比测量与判定 |
| `ota-powercycle-recovery-verification` | TARGET_COVERAGE | Verification | OTA/rollback/异常掉电/反复重启/recovery 设备级验证 |

测试代码存在不等于 Verification PASS；Verification 必须独立绑定 exact target identity、procedure 和 raw evidence。

## 12. Independent Review / Release

| Skill | 状态 | Target Owner | 目标覆盖 |
|---|---|---|---|
| `release-readiness-check` | CURRENT_CANONICAL | Independent Review | release candidate provenance/Verification/rollback/risk |
| `embedded-code-change-review` | TARGET_COVERAGE | Independent Review | code/config/DTS/linker/build change 的 defect/risk/evidence review |

代码审查不执行工程修改，不替代 Device/HIL Verification，也不自动拥有 A7 发布权限。

## 13. Embedded Security（横切能力）

当前五个 Embedded Capability 中没有单独的 security capability。为了完整覆盖嵌入式开发，至少需要规划以下方法面；在有重复真实任务之前，**不通过文档直接创建第六个 Capability**。

| Skill | 状态 | 暂定责任边界 | 目标覆盖 |
|---|---|---|---|
| `embedded-threat-model` | TARGET_COVERAGE | `embedded.architecture` | asset/trust boundary/attack surface/threat/mitigation/verifiability |
| `secure-boot-update-analysis` | TARGET_COVERAGE | architecture + Linux/MCU | secure boot、image authenticity、anti-rollback、OTA trust chain |
| `key-credential-secure-storage-analysis` | TARGET_COVERAGE | architecture + target platform | key/credential/OTP/eFuse/TEE/secure storage/lifecycle |
| `embedded-attack-surface-review` | TARGET_COVERAGE | architecture + Independent Review | network/service/debug port/dependency/production exposure review |

若这些方法形成独立任务入口、独立生命周期、稳定交付物与大量 Skill，再通过 ADR 评估是否需要新的 Capability；不能先为了目录完整性新增组织层。

## 14. Production / Factory / Lifecycle

| Skill | 状态 | Target Owner | 目标覆盖 |
|---|---|---|---|
| `factory-flashing-provisioning-analysis` | TARGET_COVERAGE | `embedded.driver-component` + Verification | factory flashing、identity、key/config provisioning、失败恢复 |
| `manufacturing-test-calibration-traceability` | TARGET_COVERAGE | `embedded.driver-component` + Verification | 产测、校准、limit、fixture、结果追溯与版本绑定 |

已有 `production-calibration-test-analysis` 是 evidence-backed gap；这里进一步表示完整量产链还需覆盖烧录/Provisioning 与产测追溯，但只有重复真实证据后才决定是否拆成 canonical Skill。

## 15. Conditional Product Specializations

以下不是所有嵌入式项目的共同基线，只在产品真的包含对应技术栈、且通用 Skill 无法稳定覆盖时建立。

| Skill | 状态 | 建议责任 | 适用产品/问题 |
|---|---|---|---|
| `motor-control-foc-analysis` | CONDITIONAL_SPECIALIZATION | MCU/RTOS + Driver | BLDC/PMSM、FOC、PI、位置/速度/电流环、保护与制动 |
| `audio-aec-ns-beamforming-analysis` | CONDITIONAL_SPECIALIZATION | Driver/Component + Architecture | 双麦/AEC/NS/BF/audio pipeline、实时性与资源 |
| `camera-isp-video-pipeline-analysis` | CONDITIONAL_SPECIALIZATION | Linux/BSP + Driver | sensor/ISP/V4L2/codec/buffer/latency/image quality |
| `sensor-fusion-imu-analysis` | CONDITIONAL_SPECIALIZATION | MCU/RTOS + Driver | IMU calibration、姿态、融合、漂移、异常判定 |
| `edge-ai-runtime-integration` | CONDITIONAL_SPECIALIZATION | Architecture + Linux/MCU | model/runtime/NPU/DSP/memory/latency/quantization/deployment |
| `wireless-rf-connectivity-analysis` | CONDITIONAL_SPECIALIZATION | Driver/Component + Hardware collaboration | Wi-Fi/BLE/RF、roaming、power、throughput、coexistence |
| `battery-charging-power-path-analysis` | CONDITIONAL_SPECIALIZATION | Driver/Component + Hardware collaboration | battery/charger/fuel gauge/power path/thermal/protection |
| `robot-motion-navigation-control-analysis` | CONDITIONAL_SPECIALIZATION | Architecture + MCU/RTOS | differential drive、odometry、motion control、navigation interface |
| `functional-safety-analysis` | CONDITIONAL_SPECIALIZATION | Architecture + Verification + external compliance | hazard/safety mechanism/diagnostic coverage/safety evidence |
| `av-sync-latency-analysis` | CONDITIONAL_SPECIALIZATION | Architecture + Debug/Reliability | audio/video clock、buffer、sync、end-to-end latency/jitter |

专项 Skill 必须复用通用 Skill 的 Evidence、BLOCK、Action Policy 和 Assurance 机制，不能形成平行治理体系。

## 16. 生命周期覆盖矩阵

| 生命周期阶段 | 至少需要覆盖的 Skill 组 |
|---|---|
| 需求澄清 / Acceptance | Coordination + Requirements + Verification Plan |
| 架构设计 / Feasibility | Architecture + Interface + Resource/Timing/Power + Security |
| 新板 / 新平台 Bring-up | Linux/MCU Bring-up + Driver + Build Evidence + Device Evidence |
| BSP / Firmware 开发 | Linux/BSP + MCU/RTOS + Build/Configuration |
| Driver / Component 开发 | Driver/Protocol/API/Adapter + target platform Skill |
| 功能集成 | Interface + Component + Concurrency/Timing + Regression |
| Debug / RCA | Log/Crash/Memory/Deadlock/Leak + evidence-driven Capability expansion |
| 性能 / 实时性 | Performance + Latency/Jitter + Resource/Timing Verification |
| Power / Recovery / OTA | Power + Watchdog + OTA/Bootloader + Recovery Verification |
| Stability / Reliability | Long-run + Stress/Fault Injection + Device/HIL |
| Security | Threat Model + Secure Boot/Update + Key/Credential + Attack Surface |
| Release | Build/Device/HIL Verification + Release Readiness + human approval |
| Production | Flash/Provisioning + Calibration/Test + Traceability |
| Field / RMA | Incident Correlation + exact version/device evidence + regression/knowledge harvest |
| 产品专项 | 按需加载 Conditional Specialization，不默认全开 |

## 17. “完整覆盖”不等于“全部同时加载”

完整覆盖的正确目标是：

1. **能力空间没有明显永久盲区**；
2. 一个任务只加载最小必要 Skill；
3. 通用 Skill 优先，专项 Skill 只在方法确实分叉时建立；
4. Engineering / Verification / Review 不合并；
5. 平台/项目名不直接等于 Skill；
6. Runtime provider 不成为 Skill owner；
7. 缺 Evidence 时能稳定 BLOCK；
8. 能从 Skill output 追到 source / device / build / test identity。

例如一个 SPI-NAND UBIFS 只读问题，可能只需要：

```text
embedded-material-readiness
→ log-triage
→ storage-filesystem-analysis
→ flash-ecc-badblock-analysis（如果未来晋级且证据触发）
→ device-evidence-check
```

不应因为“系统具备 75 项 coverage inventory”而把全部 Skill 加载。

## 18. 从 coverage inventory 到 canonical Skill 的晋级

`TARGET_COVERAGE` 或 `CONDITIONAL_SPECIALIZATION` 只有同时出现以下证据，才先进入 `OBSERVED_GAP`，再考虑 canonical：

1. 多个真实任务重复出现；
2. 现有 Skill 无法清晰承载，持续造成遗漏、错误或过载；
3. Required Inputs / Method / Outputs 能形成稳定契约；
4. BLOCK 条件可定义；
5. owner 能落到当前 Role / Capability / Assurance，或有充分证据触发 ADR；
6. 至少可设计 positive + BLOCK evaluation；
7. 独立 Skill 能降低误加载或提高一致性；
8. 没有扩大 action authority；
9. 不制造第二份 Source of Truth。

`OBSERVED_GAP` 晋级为 canonical 后，仍只表示 **DEFINED**；后续必须继续走 EVALUATED → PILOTED → REPEATABLE → PORTABLE/GOVERNED 的 Evidence 链。

## 19. 当前规划结论

当前应同时保留两个事实：

> **事实 A：当前 canonical invocation surface 是 23 个 Skill，统一最低成熟度仍是 DEFINED。**

> **事实 B：如果目标是覆盖完整嵌入式系统开发，当前已识别的目标方法空间是 75 项 coverage inventory；其中 9 项已有 OBSERVED_GAP 证据，33 项属于通用生命周期 TARGET_COVERAGE，10 项属于按产品启用的专项能力。**

因此下一阶段不应该把剩余 52 项一次性批量建成 Skill。正确做法是：

```text
coverage inventory
→ 真实任务触发
→ observed gap
→ owner / boundary review
→ contract + positive/BLOCK evaluation
→ canonical DEFINED
→ evidence-bound maturity
```

这既保证“完整嵌入式开发需要什么”在核心参考里可见，又保持 canonical registry 小而稳定、证据驱动。
