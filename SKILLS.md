# SKILLS — Digital Worker Skill Architecture, Plan & Review Index

> **用途：正式评审 / Skill 规划 / 生命周期治理的人类第一入口**  
> **机器权威：[`domains/edge-foundation/skills.yaml`](domains/edge-foundation/skills.yaml)**  
> **当前阶段：`iterative-development`**
>
> 本文件是 reviewer-facing index，不是第二份 Skill Registry。  
> Skill 是否 canonical、归谁、物理路径在哪里，只由 `domains/edge-foundation/skills.yaml` 裁决。

## 1. Skill 在 digital-worker 中是什么

稳定架构是：

```text
Domain
  → Expert
    → Capability
      → Skill
```

Skill 是**可被任务编排按需加载、具有稳定 owner、明确输入输出、可重复方法、可验证结果和 Action ceiling 的最小工程方法单元**。

Skill 不是：

- Expert / Capability 的别名；
- 一个 Agent、Session、Worker 或 Runtime；
- 一条 prompt；
- 一个工具 wrapper；
- 一篇知识文档；
- “模型会不会做某事”的泛化能力声明；
- 为了目录对称而新增的分类项。

稳定边界：

- **Responsibility ≠ Runtime**
- **Expert ≠ Agent**
- **Capability ≠ Agent**
- **Skill definition ≠ Skill maturity**
- **Skill invocation ≠ Skill evaluation**
- **Skill EVALUATED ≠ real PILOTED**
- **Skill maturity ≠ Product readiness**
- **Runtime capability ≠ Action authority**

## 2. Authority Map

| 问题 | Human View | Machine / Decision Authority |
|---|---|---|
| 当前有哪些 canonical Skill | 本文件 / [Skill 能力地图](嵌入式系统专家团-核心参考/05-工程交付/01%20Skill能力地图.md) | [`skills.yaml`](domains/edge-foundation/skills.yaml) |
| Skill 为什么存在、怎么规划 | [Skill 规划清单与定义规范](嵌入式系统专家团-核心参考/05-工程交付/04%20Skill规划清单与定义规范.md) | real evidence + review decision |
| 单个 Skill 怎么执行 | 各 `SKILL.md` | 各 canonical `SKILL.md` + Runtime contract |
| 当前仓库静态事实快照 | [当前机器状态快照](嵌入式系统专家团-核心参考/00-评审导览/03%20当前机器状态快照.md) | derived snapshot JSON，非 authority |
| Skill 当前成熟到哪 | [Skill 评审成熟度台账](嵌入式系统专家团-核心参考/05-工程交付/06%20Skill评审成熟度台账.md) | frozen evaluation / Pilot receipts |
| 如何从 DEFINED → EVALUATED | [Skill 评测与证据闭环](嵌入式系统专家团-核心参考/05-工程交付/07%20Skill评测与证据闭环.md) | evaluation plan + receipts + evaluators |
| 任务怎么选 Skill 上层责任 | Task/routing docs | [`routing.yaml`](domains/edge-foundation/routing.yaml) |
| Skill 能做多大动作 | Skill frontmatter | [Action Policy](domains/edge-foundation/runtime/action-policy.yaml) + Skill ceiling |
| Skill 是否让产品可发布 | 不直接决定 | Product readiness / Verification / Review / A7 human decision |

## 3. 当前 canonical 23 Skills

当前 registry 固定 **23 个 canonical Skill**。数量不是架构 KPI；新增必须由重复真实证据触发。

### 3.1 Edge Coordination Role

| Skill | Owner | 主要用途 | Contract |
|---|---|---|---|
| `embedded-task-classifier` | `edge-coordination` | Task type / route / mode 前置分类，选择最小责任路径 | [SKILL.md](domains/edge-foundation/skills/embedded-task-classifier/SKILL.md) |
| `embedded-material-readiness` | `edge-coordination` | Source / device / evidence / test material 准备度与 BLOCK 判断 | [SKILL.md](domains/edge-foundation/skills/embedded-material-readiness/SKILL.md) |
| `embedded-evidence-normalizer` | `edge-coordination` | Evidence provenance / identity / claim normalization | [SKILL.md](domains/edge-foundation/skills/embedded-evidence-normalizer/SKILL.md) |

Coordination Skill 组织任务，不替 Embedded Capability 产生专业事实。

### 3.2 `embedded.architecture`

| Skill | Owner | 主要用途 | Contract |
|---|---|---|---|
| `architecture-impact-analysis` | `embedded.architecture` | 系统边界、接口、资源、NFR、生命周期、验证影响 | [SKILL.md](domains/edge-foundation/skills/architecture-impact-analysis/SKILL.md) |
| `interface-contract-review` | `embedded.architecture` | API/ABI/IPC/protocol/timing/ownership/version/error contract | [SKILL.md](domains/edge-foundation/skills/interface-contract-review/SKILL.md) |

### 3.3 `embedded.linux-bsp`

| Skill | Owner | 主要用途 | Contract |
|---|---|---|---|
| `boot-chain-analysis` | `embedded.linux-bsp` | Reset → bootloader → kernel → rootfs/userspace 启动链 | [SKILL.md](domains/edge-foundation/skills/boot-chain-analysis/SKILL.md) |
| `device-tree-review` | `embedded.linux-bsp` | DT/resource/driver binding 与 exact board revision | [SKILL.md](domains/edge-foundation/skills/device-tree-review/SKILL.md) |
| `irq-dma-analysis` | `embedded.linux-bsp` | IRQ/DMA mapping、ownership、cache、ordering、completion | [SKILL.md](domains/edge-foundation/skills/irq-dma-analysis/SKILL.md) |
| `storage-filesystem-analysis` | `embedded.linux-bsp` | media/ECC/controller/MTD/UBI/filesystem 分层分析 | [SKILL.md](domains/edge-foundation/skills/storage-filesystem-analysis/SKILL.md) |

### 3.4 `embedded.mcu-rtos`

| Skill | Owner | 主要用途 | Contract |
|---|---|---|---|
| `mcu-startup-analysis` | `embedded.mcu-rtos` | Reset/vector/clock/C runtime/HAL/scheduler startup | [SKILL.md](domains/edge-foundation/skills/mcu-startup-analysis/SKILL.md) |
| `linker-map-analysis` | `embedded.mcu-rtos` | Linker/MAP/ELF/ROM/RAM 精确量化 | [SKILL.md](domains/edge-foundation/skills/linker-map-analysis/SKILL.md) |
| `rtos-concurrency-analysis` | `embedded.mcu-rtos` | task/ISR/lock/queue/priority/worst-case timing | [SKILL.md](domains/edge-foundation/skills/rtos-concurrency-analysis/SKILL.md) |

### 3.5 `embedded.driver-component`

| Skill | Owner | 主要用途 | Contract |
|---|---|---|---|
| `driver-integration-review` | `embedded.driver-component` | device integration、lifecycle、recovery、power、compatibility | [SKILL.md](domains/edge-foundation/skills/driver-integration-review/SKILL.md) |

### 3.6 `embedded.debug-reliability`

| Skill | Owner | 主要用途 | Contract |
|---|---|---|---|
| `log-triage` | `embedded.debug-reliability` | raw log → timeline，Observed/Inferred/Confirmed 分离 | [SKILL.md](domains/edge-foundation/skills/log-triage/SKILL.md) |
| `crash-hardfault-analysis` | `embedded.debug-reliability` | Crash/HardFault context → falsifiable hypotheses | [SKILL.md](domains/edge-foundation/skills/crash-hardfault-analysis/SKILL.md) |
| `memory-corruption-analysis` | `embedded.debug-reliability` | OOB/UAF/stack/heap/DMA/lifetime corruption | [SKILL.md](domains/edge-foundation/skills/memory-corruption-analysis/SKILL.md) |
| `performance-analysis` | `embedded.debug-reliability` | baseline/measurement/bottleneck/before-after/regression | [SKILL.md](domains/edge-foundation/skills/performance-analysis/SKILL.md) |

### 3.7 Assurance — Verification

| Skill | Owner | 主要用途 | Contract |
|---|---|---|---|
| `verification-plan-builder` | `verification` | Acceptance → verification layer → direct evidence | [SKILL.md](domains/edge-foundation/skills/verification-plan-builder/SKILL.md) |
| `regression-scope-analysis` | `verification` | change impact → minimum sufficient regression | [SKILL.md](domains/edge-foundation/skills/regression-scope-analysis/SKILL.md) |
| `build-evidence-check` | `verification` | exact source/config/toolchain/artifact build evidence | [SKILL.md](domains/edge-foundation/skills/build-evidence-check/SKILL.md) |
| `device-evidence-check` | `verification` | exact board/firmware/procedure/raw device evidence | [SKILL.md](domains/edge-foundation/skills/device-evidence-check/SKILL.md) |
| `hil-evidence-check` | `verification` | exact HIL case/fixture/target/run evidence | [SKILL.md](domains/edge-foundation/skills/hil-evidence-check/SKILL.md) |

Assurance Skill 独立于 Engineering，不允许 implementation self-approval。

### 3.8 Assurance — Independent Review

| Skill | Owner | 主要用途 | Contract |
|---|---|---|---|
| `release-readiness-check` | `review` | exact release candidate provenance/Verification/rollback/risk readiness | [SKILL.md](domains/edge-foundation/skills/release-readiness-check/SKILL.md) |

Release readiness 不等于 A7 release approval。

## 4. 每个 canonical Skill 的统一定义标准

23 个 `SKILL.md` 当前均被 CI 强制具备：

1. Purpose
2. Use When
3. Do Not Use For
4. Required Inputs
5. Optional Inputs
6. Method
7. Outputs
8. Evidence Rules
9. BLOCK Conditions
10. Verification / Review Handoff
11. Evaluation
12. Known Limits / Change Notes

Frontmatter 同时冻结：

- `id`
- `version`
- `owner_kind`
- `owner`
- `max_action_level`
- `inputs`
- `outputs`

定义完整只表示 **DEFINED**，不等于工程成熟。

## 5. 当前成熟度快照

截至当前基线：

| 维度 | 当前状态 |
|---|---|
| Canonical registry | 23/23 |
| Review-grade Skill contract | 23/23 |
| Positive evaluation case plan | 23/23 |
| BLOCK negative case plan | 23/23 |
| Total Skill evaluation cases | 46 |
| Invocation receipt contract | READY |
| Pilot receipt freezing | READY |
| Case evaluation receipt | READY |
| Positive + BLOCK maturity aggregation | READY |
| 持久化、独立 semantic PASS 的完整 Skill case pair | **尚无 canonical evidence** |
| Canonical Skill 可诚实声明的统一最低阶段 | **DEFINED** |
| Real Skill-level Pilot attribution | EVIDENCE_PENDING |
| Cross-Runtime portability | EVIDENCE_PENDING |

关键原则：

> CI 能证明评测机制和 fail-closed 规则正确，不能凭 CI fixture 自动把某个 canonical Skill 升为 EVALUATED。

逐 Skill 状态见 [Skill 评审成熟度台账](嵌入式系统专家团-核心参考/05-工程交付/06%20Skill评审成熟度台账.md)。

## 6. DEFINED → EVALUATED 的证据 Gate

评测规划：[`skill-evaluation-plan.yaml`](domains/edge-foundation/evaluation/skill-evaluation-plan.yaml)。

一个 Skill 只有同时满足下面条件，才可形成 bounded `EVALUATED` evidence：

1. positive case 已执行；
2. BLOCK case 已执行；
3. 两次 invocation 都绑定 canonical Skill contract SHA-256；
4. 两次 invocation 使用同一 Skill contract；
5. 两次 invocation 使用同一 Runtime provider/runtime_id；
6. 两次 invocation source type 一致；
7. expected vs observed result 一致；
8. 两个 case contract verdict 均 PASS；
9. 两个 case 均经过 human-review 或 independent-evaluator semantic PASS；
10. semantic evidence 都有 ref + SHA-256；
11. 两张 `case_evidence_eligible=true`；
12. [`evaluate_skill_maturity.py`](scripts/evaluate_skill_maturity.py) 聚合后 status = `EVALUATED`。

即使 EVALUATED：

```text
portability_proven = false
product_readiness_inherited = false
```

完整说明见 [Skill 评测与证据闭环](嵌入式系统专家团-核心参考/05-工程交付/07%20Skill评测与证据闭环.md)。

## 7. EVALUATED → PILOTED → REPEATABLE → PORTABLE

### PILOTED

至少需要：

- real Work/Run；
- exact source/system/device/artifact identity；
- Runtime-owned attested [Skill Invocation Receipt](schemas/skill-invocation-receipt.v1.schema.json)；
- receipt 被 Pilot immutable evidence bundle 冻结；
- downstream Verification 独立于 Skill execution。

历史 Pilot 不做无 attestation 的事后伪回填。

### REPEATABLE

至少需要多个真实任务证明：

- correct block rate；
- unsupported claim rate；
- evidence traceability；
- failure/recovery consistency；
- recurrence/regression；
- Skill 不是只在单一项目/单一提示下成立。

### PORTABLE

至少需要第二 Runtime 在同一 frozen Contract 下形成可比 evidence：

- input/source set 等价；
- positive + BLOCK behavior 可比；
- action ceiling 不扩大；
- output/evidence traceability 可比；
- semantic evaluation 独立；
- 不以 Provider 名字不同替代真实对照。

## 8. Evidence-backed Candidate Skill 规划池（非 canonical）

以下 9 项均为 **OBSERVED_GAP / planning candidate**，不允许被 canonical routing 直接调用。它们是已有重复工程信号的候选，不是完整嵌入式研发方法空间的全集。

完整目标覆盖请看 [嵌入式系统开发 Skill 全景与目标覆盖](嵌入式系统专家团-核心参考/05-工程交付/08%20嵌入式系统开发Skill全景与目标覆盖.md)：当前规划视图为 23 `CURRENT_CANONICAL` + 9 `OBSERVED_GAP` + 33 `TARGET_COVERAGE` + 10 `CONDITIONAL_SPECIALIZATION`，总计 75 项 coverage inventory；其中非 canonical 项均不得被当前 routing 直接调用。

当前 evidence-backed candidate：

| Candidate | 候选责任 | 为什么观察到 | 晋级前至少需要 |
|---|---|---|---|
| `power-state-analysis` | linux-bsp / mcu-rtos，待裁决 | suspend/resume/standby/deep sleep/wakeup | ≥2 类真实 power issue，方法边界稳定 |
| `ota-bootloader-analysis` | mcu-rtos / architecture，待裁决 | bootloader/OTA/version/rollback engineering | ≥2 个真实 OTA 工程任务证明独立方法价值 |
| `watchdog-reset-analysis` | mcu-rtos | watchdog/reset-reason/recovery | 多次 reset incident + 稳定 evidence contract |
| `device-substitution-qualification` | driver-component | Flash/WiFi/Power/传感器替代 | compatibility matrix 复杂度/复用频率持续上升 |
| `production-calibration-test-analysis` | driver-component | IMU/电机/传感器校准与产测 | 多产品稳定 calibration/test contract |
| `long-run-soak-analysis` | debug-reliability | 7x24、泄漏、温升、长期退化 | 多个 soak 场景形成统一方法 |
| `latency-jitter-analysis` | debug-reliability / mcu-rtos，待裁决 | 实时性与尾延迟 | 证明独立 timing model 与 evidence contract |
| `kernel-config-diff-review` | linux-bsp | Kconfig/defconfig/BSP migration | 多平台 porting 高频重复且有独立缺陷发现价值 |
| `flash-ecc-badblock-analysis` | linux-bsp | NAND ECC/bad block/controller | storage Skill 长期方法/证据分叉时再拆 |

候选规则：

- Candidate 不得进入 canonical invocation surface；
- Candidate 不得写成“团队已具备成熟能力”；
- owner 有歧义时先裁决责任；
- 能被现有 Skill 清楚覆盖就不新增；
- 单个案例不触发 canonical 新增。

## 9. 新增 Skill 的准入 Gate

新 Skill 进入 `skills.yaml` 前，至少通过：

### G1 — Responsibility
- owner 落到已有 Role / Capability / Assurance；
- 不因想运行独立 Agent 而新增 owner；
- 与相邻 Skill 的边界能用正反例解释。

### G2 — Repetition
- 多个真实任务重复出现；
- 不是一次性项目技巧；
- 能证明不独立建 Skill 会持续制造问题。

### G3 — Contract
- inputs / outputs / BLOCK / action ceiling 明确；
- 缺材料时不会靠猜测继续；
- output 可被后续 Gate / Assurance 消费。

### G4 — Evaluation
- positive case；
- BLOCK negative case；
- semantic evidence boundary；
- forbidden overclaim 可检查。

### G5 — Integration
- registry / physical path / owner frontmatter 同步；
- 必要 routing/capability 引用更新；
- Engineering / Verification / Review 分离不被破坏。

### G6 — Change Safety
- 不隐式扩大 action authority；
- 有兼容/迁移/rollback；
- 不制造第二份 Source of Truth。

## 10. 拆分、合并、退役

### 拆分信号
只有当多个信号长期同时出现时才拆分：

- Required Inputs 明显分成两套；
- Method 长期分叉；
- Evidence contract 不同；
- owner 形成真实责任边界；
- Golden/evaluation cases 很难共用；
- 拆分能降低误加载，而不是只让文件更短。

### 合并信号

- 两个 Skill 总是一起加载；
- inputs/outputs 大量重复；
- owner 相同；
- 很难设计独立 BLOCK case；
- 编排成本高于独立价值。

### Deprecated / Retired

退役需要：

- replacement 明确；
- registry/routing 不再引用；
- evaluation case 迁移；
- Git history 保留；
- 活动面不维护 shadow compatibility。

## 11. Skill 组合原则

1. Task 先路由到 Role / Expert / Capability，再选最小必要 Skill；
2. Diagnostic 模式按 Evidence 扩展，不默认“专家团全开”；
3. 一个 Capability 可以组合多个 Skill，但 Skill 数量不是 Expert 数量；
4. Engineering Skill 不自签 Verification；
5. Review Skill 不隐式执行工程修改；
6. Skill 之间的稳定前后依赖优先放 workflow/contract，不合成巨型 Skill；
7. 同一事实只保留一个 authoritative evidence identity；
8. Runtime 可替换，但 owner/action/evidence contract 不随 Runtime 品牌变化。

## 12. Reviewer Checklist

正式评审至少追问：

- 这个 Skill 为什么需要独立存在？
- owner 为什么属于这个 Capability / Assurance？
- Use When / Do Not Use For 是否无歧义？
- 缺什么必须 BLOCK？
- Evidence Rules 能否防止 inference 被写成 Confirmed？
- output 谁消费？
- Engineering / Verification / Review 是否分离？
- action ceiling 是否最小？
- positive + BLOCK case 是否都有？
- semantic evidence 是否独立且有 hash？
- 当前到底是 DEFINED、EVALUATED、PILOTED 还是更高？
- 是否有第二 Runtime portability evidence？
- 是否有人把 Skill maturity 偷换成 Product readiness？

## 13. 主要相关入口

- [当前机器 Review Snapshot](嵌入式系统专家团-核心参考/00-评审导览/03%20当前机器状态快照.md)
- [Canonical Skill Registry](domains/edge-foundation/skills.yaml)
- [Skill 能力地图](嵌入式系统专家团-核心参考/05-工程交付/01%20Skill能力地图.md)
- [Skill 规划清单与定义规范](嵌入式系统专家团-核心参考/05-工程交付/04%20Skill规划清单与定义规范.md)
- [Skill 生命周期、成熟度与准入](嵌入式系统专家团-核心参考/05-工程交付/05%20Skill生命周期成熟度与准入.md)
- [Skill 评审成熟度台账](嵌入式系统专家团-核心参考/05-工程交付/06%20Skill评审成熟度台账.md)
- [Skill 评测与证据闭环](嵌入式系统专家团-核心参考/05-工程交付/07%20Skill评测与证据闭环.md)
- [嵌入式系统开发 Skill 全景与目标覆盖](嵌入式系统专家团-核心参考/05-工程交付/08%20嵌入式系统开发Skill全景与目标覆盖.md)
- [Skill Evaluation Plan](domains/edge-foundation/evaluation/skill-evaluation-plan.yaml)
- [Skill Invocation Receipt Schema](schemas/skill-invocation-receipt.v1.schema.json)
- [Skill Evaluation Receipt Schema](schemas/skill-evaluation-receipt.v1.schema.json)
- [Skill Evaluation Summary Schema](schemas/skill-evaluation-summary.v1.schema.json)
- [End-to-End Review Checklist](嵌入式系统专家团-核心参考/06-治理与评审/07%20端到端评审检查表.md)

## 14. 当前结论

当前可以正式声明：

> **digital-worker 已建立 23 个 canonical Skill 的统一定义、规划、评测计划、invocation provenance、positive+BLOCK evaluation 和成熟度聚合机制；但目前没有以持久化独立 semantic PASS evidence 完成任一 canonical Skill 的正式晋级，因此 Skill 工程成熟度仍统一保持 DEFINED。**

这是一条有意保持保守的评审结论：**评测基础设施完成，不等于 Skill 本身已经成熟。**
