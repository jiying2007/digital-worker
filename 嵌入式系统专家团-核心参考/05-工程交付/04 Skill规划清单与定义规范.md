# Skill 规划清单与定义规范

> `domains/edge-foundation/skills.yaml` 是 **canonical Skill Registry**。  
> 本页是 **planning + reviewer view**，用于解释“为什么有这些 Skill、还缺什么、什么条件下才能新增/拆分/合并”，不构成第二份可执行 Registry。

## 1. Skill 的定义

一个 Skill 是 **可被任务编排按需加载、具有稳定 owner、明确输入输出、可重复方法、可验证结果和 Action ceiling 的最小工程方法单元**。

Skill 不是：

- Expert 的别名；
- Capability 的别名；
- 一个 Agent/Session/Worker；
- 一条 prompt；
- 一个 CLI/tool wrapper；
- 一篇知识文章；
- 为了目录对称而创建的分类项；
- “模型会不会做某件事”的能力声明。

判断某内容是否值得成为 Skill，至少要同时满足：

1. 在多个真实任务中重复出现；
2. 方法边界相对稳定；
3. 输入和输出可以定义；
4. owner 可明确落到 Role / Capability / Assurance；
5. 缺材料时能给出一致 BLOCK；
6. 结果可以由 Evidence 或 Golden Case 评价；
7. 独立加载能降低执行噪声或提高一致性。

## 2. 当前 canonical 23 Skill

### 2.1 Coordination

| Skill | Owner | 解决的问题 | 关键输出 |
|---|---|---|---|
| `embedded-task-classifier` | Edge Coordination | request → task/mode/route 前置分类 | routing decision |
| `embedded-material-readiness` | Edge Coordination | source/system/material 是否足以开始 | readiness / missing-material |
| `embedded-evidence-normalizer` | Edge Coordination | evidence identity、claim/source 规范化 | normalized evidence metadata |

### 2.2 Architecture

| Skill | Owner | 解决的问题 | 关键输出 |
|---|---|---|---|
| `architecture-impact-analysis` | `embedded.architecture` | 变化对边界、资源、NFR、验证面的影响 | impact analysis |
| `interface-contract-review` | `embedded.architecture` | API/ABI/protocol/lifecycle/error/version contract | interface findings |

### 2.3 Linux / BSP

| Skill | Owner | 解决的问题 | 关键输出 |
|---|---|---|---|
| `boot-chain-analysis` | `embedded.linux-bsp` | reset → bootloader → kernel → rootfs 启动链 | last-confirmed-stage / next observation |
| `device-tree-review` | `embedded.linux-bsp` | DT、resource、binding、clock/reset/pinctrl | DT/resource findings |
| `irq-dma-analysis` | `embedded.linux-bsp` | IRQ/DMA/cache/ownership/platform contract | concurrency/data-path analysis |
| `storage-filesystem-analysis` | `embedded.linux-bsp` | MTD/flash/UBI/UBIFS/filesystem 层级问题 | storage layer analysis |

### 2.4 MCU / RTOS

| Skill | Owner | 解决的问题 | 关键输出 |
|---|---|---|---|
| `mcu-startup-analysis` | `embedded.mcu-rtos` | reset/vector/startup/init 链 | startup analysis |
| `linker-map-analysis` | `embedded.mcu-rtos` | ELF/MAP/linker/ROM/RAM 布局与溢出 | memory layout evidence |
| `rtos-concurrency-analysis` | `embedded.mcu-rtos` | task/ISR/lock/queue/scheduling 并发 | concurrency/timing findings |

### 2.5 Driver / Component

| Skill | Owner | 解决的问题 | 关键输出 |
|---|---|---|---|
| `driver-integration-review` | `embedded.driver-component` | 设备接入、lifecycle、error/recovery、compatibility | integration analysis / compatibility matrix |

### 2.6 Debug / Reliability

| Skill | Owner | 解决的问题 | 关键输出 |
|---|---|---|---|
| `log-triage` | `embedded.debug-reliability` | 原始日志时间线、Observed/Inferred 分离 | timeline / evidence gaps |
| `crash-hardfault-analysis` | `embedded.debug-reliability` | Crash/HardFault fault context 与 root-cause hypothesis | fault analysis |
| `memory-corruption-analysis` | `embedded.debug-reliability` | 越界/UAF/stack/heap/lifetime corruption | corruption hypotheses |
| `performance-analysis` | `embedded.debug-reliability` | baseline、测量、瓶颈、回归 | bottleneck / delta evidence |

### 2.7 Assurance / Verification

| Skill | Owner | 解决的问题 | 关键输出 |
|---|---|---|---|
| `verification-plan-builder` | Verification | Acceptance → layer → evidence 计划 | verification plan |
| `regression-scope-analysis` | Verification | 改动影响的回归边界 | regression scope |
| `build-evidence-check` | Verification | Build/cross-build 证据是否直接有效 | build evidence result |
| `device-evidence-check` | Verification | target device identity/result 是否有效 | device evidence result |
| `hil-evidence-check` | Verification | HIL 对象/场景/结果是否满足 contract | HIL evidence result |

### 2.8 Assurance / Review

| Skill | Owner | 解决的问题 | 关键输出 |
|---|---|---|---|
| `release-readiness-check` | Independent Review | release candidate provenance/evidence/risk/rollback | review report |

**重要：上表只说明当前注册事实，不说明 23 个 Skill 均已达到相同成熟度。**

## 3. 当前最重要的规划不是“继续加 Skill”

近期 P0 是把所有 canonical Skill 补到同一最低定义质量。每个 `SKILL.md` 应逐步具备以下 13 段：

1. **Identity**：id / version / owner / action ceiling；
2. **Purpose**：解决什么问题；
3. **Use When**：什么任务/触发条件下加载；
4. **Do Not Use For**：明确非目标；
5. **Required Inputs**：缺一不可的材料；
6. **Optional Inputs**：增强但非硬门；
7. **Method**：可重复步骤；
8. **Outputs**：结构、状态与 handoff；
9. **Evidence Rules**：什么能支持 Observed / Inferred / Confirmed；
10. **BLOCK Conditions**：何时必须停止或降级；
11. **Verification / Review Handoff**：谁证明、谁不能自签；
12. **Evaluation**：Golden Case / real Pilot / failure case；
13. **Known Limits / Change Notes**：边界、已知不覆盖项、版本变化。

这 13 段是“定义完整性”标准，不意味着实际工程成熟度已经 PASS。

## 4. Evidence-backed Candidate Skill 规划池

以下仅是已经观察到重复工程信号的 **候选缺口**，状态统一为 `OBSERVED_GAP`，不进入 canonical Registry。只有重复 real evidence 证明独立方法价值后才晋级。

> 这 9 项 **不是完整嵌入式研发所需 Skill 的全集**。完整生命周期的目标覆盖清单见 [嵌入式系统开发 Skill 全景与目标覆盖](08%20嵌入式系统开发Skill全景与目标覆盖.md)。该全景进一步区分 `CURRENT_CANONICAL / OBSERVED_GAP / TARGET_COVERAGE / CONDITIONAL_SPECIALIZATION`，避免把“未来可能需要覆盖”误写成“当前候选已成立”。

| Candidate | 候选 Owner | 触发来源 | 与现有 Skill 的关系 | 晋级所需证据 |
|---|---|---|---|---|
| `power-state-analysis` | linux-bsp / mcu-rtos，待裁决 | suspend/resume/standby/deep sleep/wakeup | 当前分散在 BSP/MCU 指南 | ≥2 类真实 power issue，方法稳定且跨任务复用 |
| `ota-bootloader-analysis` | mcu-rtos / architecture，待裁决 | bootloader/OTA/version/rollback | 当前 release check 偏 Assurance，工程分析缺独立单元 | ≥2 个真实 OTA 工程任务证明独立 engineering method |
| `watchdog-reset-analysis` | mcu-rtos | watchdog/reset-reason/recovery | 与 crash 分析相邻但对象不同 | 多次 reset incident，能形成稳定 reset evidence contract |
| `device-substitution-qualification` | driver-component | Flash/WiFi/Power/传感器国产替代 | 当前由 driver-integration-review 覆盖 | compatibility matrix 复杂度和复用频率持续上升 |
| `production-calibration-test-analysis` | driver-component | IMU/电机/传感器生产校准、产测 | 当前未形成独立 Skill | 多产品存在稳定 calibration/test data contract |
| `long-run-soak-analysis` | debug-reliability | 7x24、内存泄漏、温升、长期退化 | performance/log 可部分覆盖 | 多个 soak 场景出现统一指标、采样、判定方法 |
| `latency-jitter-analysis` | debug-reliability / mcu-rtos，待裁决 | 实时性、调度、音视频/控制时延 | performance + RTOS concurrency 有重叠 | 证明需要独立 timing model 和 evidence contract |
| `kernel-config-diff-review` | linux-bsp | Kconfig/defconfig/BSP migration | 可嵌入 architecture/BSP review | 多平台 porting 中高频重复且独立产生缺陷发现 |
| `flash-ecc-badblock-analysis` | linux-bsp | NAND ECC/bad block/FSP/BDMA | storage-filesystem-analysis 子域 | storage Skill 过宽导致方法/证据长期分叉时再拆分 |

### 4.1 候选池的硬规则

- Candidate **不得**被 routing 当作 canonical Skill 调用；
- Candidate **不得**在评审材料中写成“已具备能力”；
- 候选 owner 尚有歧义时必须先做责任裁决；
- 能由现有 Skill 清楚覆盖的，不新增；
- 一个真实案例不足以触发 canonical 新增；
- 新 Skill 必须同时补 registry、`SKILL.md`、evaluation、必要的 routing/capability 引用和 CI。

## 5. Skill Contract 模板

新建或重构 Skill 时建议使用：

```markdown
---
id: <stable-id>
version: <semver>
owner_kind: role|capability|assurance
owner: <canonical-owner>
max_action_level: <A0-A7>
inputs: [...]
outputs: [...]
---

# <Skill Name>

## Purpose
## Use When
## Do Not Use For
## Required Inputs
## Optional Inputs
## Method
## Outputs
## Evidence Rules
## BLOCK Conditions
## Verification / Review Handoff
## Evaluation
## Known Limits / Change Notes
```

Frontmatter 只保留机器需要的稳定字段；大段规划、成熟度描述不要塞入 registry，避免把人类规划状态误变成运行时权威。

## 6. Skill 组合规则

1. 一个任务通常加载 **最小必要集合**，不是把整个 Capability 的 Skill 全部加载；
2. Diagnostic 任务先由 evidence 驱动扩展，不预先“专家团全开”；
3. Engineering Skill 可以产生工程结论，但不能给自己的 Verification PASS；
4. Review Skill 不得隐式修改工程对象；
5. Skill 之间出现稳定前后依赖时，优先在 workflow/contract 表达，不把 Skill 合并成巨型流程；
6. 同一事实只保留一个 authoritative evidence identity，不因多 Skill 使用而复制事实。

## 7. Definition of Done：一个 Skill 何时算“定义完成”

至少满足：

- owner 与 registry 一致；
- Use When / Do Not Use For 清楚；
- required inputs 可判断 READY/BLOCKED；
- Method 可由不同 Runtime 重复执行；
- output 能被后续 Gate/Assurance 消费；
- evidence claim 强度规则明确；
- action ceiling 明确且不过权；
- 至少 1 个 positive case + 1 个 failure/block case；
- 没有用“模型聪明程度”作为唯一成功条件；
- 文档、registry、test/evaluation 不冲突。

## 8. 规划优先级

### P0 — Definition Hardening
统一补强现有 23 Skill 的 contract 完整性，并建立自动检查。

### P1 — Evidence-backed Gaps
从真实 Pilot / incident 中统计重复方法缺口，候选池按证据晋级，而不是一次性全建。

### P2 — Composition Quality
评估不同 task 的 Skill 组合是否过载、遗漏或产生重复 reasoning。

### P3 — Runtime Portability
同一 frozen Skill Contract 在不同 Runtime 下执行，比较结果质量、BLOCK correctness 和 Evidence traceability。

### P4 — Lifecycle Governance
建立 deprecation/merge/retire 流程，避免 Skill 只增不减。

Skill 体系的终态指标不是“数量越来越多”，而是：**以更少、更稳定、可组合的 Skill 覆盖更多真实工程任务，并且结果更可验证。**
