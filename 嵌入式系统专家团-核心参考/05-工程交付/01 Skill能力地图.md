# Skill 能力地图

Skill 的 canonical ownership 与物理位置都以 `domains/edge-foundation/skills.yaml` 为唯一权威。本页只按 **Role / Capability / Assurance** 分组解释，不创建第二份 Skill Registry。

> 评审提示：本页回答“**现在有哪些 canonical Skill、归谁**”。  
> “为什么这样规划、还缺什么、如何新增/拆分/合并”请看 [Skill 规划清单与定义规范](04%20Skill规划清单与定义规范.md)；  
> “Skill 文件存在是否代表成熟、如何准入/退役”请看 [Skill 生命周期、成熟度与准入](05%20Skill生命周期成熟度与准入.md)。

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

当前 iterative Pilot 的 Independent Review unavailable policy 不改变 ownership；它只改变当前阶段 completion 的硬门条件。

## 9. 使用规则

1. Task 路由到 Domain Expert / Capability 后再加载必要 Skill；
2. Skill 数量不是架构，也不决定 Expert 数量；
3. Skill 可以被不同 Runtime 实现，但 owner contract 不随 Runtime 改变；
4. Skill 物理文件统一位于 `domains/edge-foundation/skills/<id>/SKILL.md`，frontmatter `owner_kind/owner` 必须与 registry 一致；
5. 新 Skill 必须由重复 real evidence 证明，而不是为了目录对称新增；
6. Verification / Review Skill 不得被 Engineering 实施结果自签；
7. 未注册 Skill 不得作为 canonical invocation surface；
8. Action ceiling 以 Skill contract 与 `runtime/action-policy.yaml` 共同约束，默认不因 Runtime 品牌扩大。

当前 registry 共 23 个 Skill。CI 会逐个校验 Skill 文件的 `id / owner_kind / owner / path / action ceiling` 与 `skills.yaml` 一致，并禁止旧组织 identity 重新进入 target Skill。

## 10. 评审时如何解读这张图

这 23 个 Skill 是当前 canonical invocation surface，但**不能从“已注册”直接推出“工程能力已成熟”**。

评审至少区分三件事：

| 问题 | 依据 |
|---|---|
| 这个 Skill 是否存在、归谁、文件在哪里？ | `skills.yaml` |
| 这个 Skill 应该怎样定义、何时使用、何时 BLOCK？ | 对应 `SKILL.md` + Skill 定义规范 |
| 这个 Skill 是否经过真实工程证明、能跨 Runtime 稳定复用？ | Golden Case + real Pilot + lifecycle maturity evidence |

因此后续优化的 P0 不是无条件增加 Skill 数量，而是把当前 23 个 Skill 的 **Use When / Do Not Use For / Required Inputs / Method / Output / Evidence / BLOCK / Handoff / Evaluation / Limits** 补到一致的最低定义质量，再由真实任务决定 candidate 是否晋级。
