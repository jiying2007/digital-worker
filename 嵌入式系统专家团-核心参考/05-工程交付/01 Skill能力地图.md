# Skill能力地图

Skill 的 target ownership 以 `domains/edge-foundation/skills.yaml` 为唯一权威。本页只按 **Role / Capability / Assurance** 分组解释，不再按旧执行身份分组。Skill 物理文件当前仍可能位于 `expert-groups/embedded-system/skills/`，但**文件位置不定义 owner**。

## 1. Edge Coordination Role（`edge-coordination`）

| Skill | 用途 |
|---|---|
| `embedded-task-classifier` | Task type / route / mode 前置分类 |
| `embedded-material-readiness` | Material/System Context 准备度与 BLOCK 判断 |
| `embedded-evidence-normalizer` | Evidence identity / source / claim 规范化 |

Coordination Skill 负责组织任务，不产生 Embedded 专业事实。

## 2. `embedded.architecture`

| Skill | 用途 |
|---|---|
| `architecture-impact-analysis` | 系统边界、变化面、资源/NFR/验证影响 |
| `interface-contract-review` | 接口、异常、版本、生命周期契约审查 |

## 3. `embedded.linux-bsp`

| Skill | 用途 |
|---|---|
| `boot-chain-analysis` | Bootloader → Kernel → rootfs 阶段定位 |
| `device-tree-review` | DT/resource/driver binding 审查 |
| `irq-dma-analysis` | IRQ/DMA/cache ownership 与 platform contract |
| `storage-filesystem-analysis` | MTD/UBI/UBIFS/storage 层级分析 |

## 4. `embedded.mcu-rtos`

| Skill | 用途 |
|---|---|
| `mcu-startup-analysis` | Reset/startup/init 链分析 |
| `linker-map-analysis` | Linker/MAP/ELF/ROM/RAM 量化 |
| `rtos-concurrency-analysis` | task/ISR/lock/queue/worst-case 并发分析 |

## 5. `embedded.driver-component`

| Skill | 用途 |
|---|---|
| `driver-integration-review` | 设备接入、错误恢复、Adapter/API/兼容性审查 |

## 6. `embedded.debug-reliability`

| Skill | 用途 |
|---|---|
| `log-triage` | Timeline 与原始日志分层 |
| `crash-hardfault-analysis` | Crash/HardFault 上下文与 hypothesis |
| `memory-corruption-analysis` | 内存越界/踩踏/生命周期分析 |
| `performance-analysis` | baseline / measurement / bottleneck / regression |

## 7. Assurance / Verification（`verification`）

| Skill | 用途 |
|---|---|
| `verification-plan-builder` | Acceptance → required layer → Evidence 计划 |
| `regression-scope-analysis` | 受影响范围与回归边界 |
| `build-evidence-check` | Build/Cross-build 直接证据检查 |
| `device-evidence-check` | target device 证据与 identity 检查 |
| `hil-evidence-check` | HIL 对象、场景和结果证据检查 |

这些 Skill 属于 Assurance，不是 Embedded Capability。

## 8. Assurance / Review（`review`）

| Skill | 用途 |
|---|---|
| `release-readiness-check` | Release candidate、provenance、rollback、risk readiness |

当前 iterative Pilot 的 Independent Review unavailable waiver 不改变这个 ownership；它只改变试点 completion 的阶段性硬门条件。

## 9. 使用规则

1. Task 路由到 Domain Expert / Capability 后再加载必要 Skill；
2. Skill 数量不是架构，也不决定 Expert 数量；
3. Skill 可以被不同 Runtime 实现，但 owner contract 不随 Runtime 改变；
4. Legacy Skill frontmatter/路径只承担当前执行兼容，不能反向覆盖 target ownership；
5. 新 Skill 必须由重复 real evidence 证明，而不是为了目录对称新增；
6. Verification / Review Skill 不得被工程实施结果自签。

当前 registry 共 23 个 Skill；核心参考只展示 target ownership，一旦机器 registry 增删，CI 会要求本页同步。
