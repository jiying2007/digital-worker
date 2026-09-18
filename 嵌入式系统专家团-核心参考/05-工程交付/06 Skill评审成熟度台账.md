# Skill 评审成熟度台账

> 本台账回答“23 个 canonical Skill **现在到底成熟到哪一步**”。  
> 它是 reviewer-facing maturity ledger，不是第二份 Skill Registry；Skill 是否存在、归谁、路径在哪里，仍只由 `domains/edge-foundation/skills.yaml` 裁决。

## 1. 当前总判断

截至当前 main：

- 23/23 canonical Skill 已完成统一 review-grade contract hardening；
- registry / owner / action ceiling / physical path 已由 CI fail-closed 校验；
- 12 个 canonical Golden Case 仍主要验证 **task / routing / capability / assurance**，并没有显式记录“本 case 调用了哪些 Skill”；
- 新的 `skill-invocation-receipt.v1` contract 与 Pilot 冻结入口已经建立，可校验 Skill contract hash/owner/version/action ceiling、Runtime binding、input/output refs 与 attestation；
- **但现有已冻结真实 Pilot evidence 尚未补录这些 receipt**，因此历史/当前真实使用仍不能自动归因到具体 Skill；
- 因此不能从“Golden Case PASS”或“真实 Pilot completed”直接推导任一 Skill 已达到 `EVALUATED`、`PILOTED` 或 `REPEATABLE`；
- 当前可诚实声明的统一最低状态是：**23 个 Skill 均达到 DEFINED；更高成熟度必须逐个补 Skill-level evaluation / usage evidence。**

换句话说：**定义闭环与 Skill usage receipt 基础设施已建立；Skill evaluation 与真实历史使用证据闭环仍未完成。**

## 2. 状态语义

本台账只使用以下状态，避免含糊的“成熟/基本成熟”：

| 状态 | 含义 |
|---|---|
| `DEFINED` | Skill contract 已具备 Purpose、适用/禁用边界、输入、方法、输出、Evidence、BLOCK、Handoff、Evaluation、Limits |
| `DIRECT_CASE_PENDING` | 有接近的 Golden Case，但 case 尚未显式绑定 Skill invocation/output，所以不能算 Skill evaluation |
| `NO_DIRECT_CASE` | 当前 Golden Case 没有足够接近的 Skill-specific case |
| `REAL_USAGE_NOT_ATTRIBUTED` | 可能参与真实任务，但 frozen Pilot evidence 没记录 Skill invocation/output，不能计为 Skill-level Pilot |
| `PORTABILITY_NOT_PROVEN` | 没有同一 frozen Skill Contract 在第二 Runtime 下的可比执行证据 |
| `GOVERNED_DEFINITION` | owner/path/action/contract structure 已被 CI 治理，但不代表工程效果成熟 |

## 3. 23 个 canonical Skill 当前台账

> “Closest Golden Case” 只表示最接近的现有 case，**不表示该 Skill 已通过评测**。

| Skill | Owner | Definition | Closest Golden Case | Skill-level real usage | Portability | 当前可声明阶段 | 下一晋级条件 |
|---|---|---|---|---|---|---|---|
| `embedded-task-classifier` | edge-coordination | DEFINED | all routing cases（间接） | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED | Golden Case 显式冻结 classification input/output + route correctness |
| `embedded-material-readiness` | edge-coordination | DEFINED | 多个 Gate M case（间接） | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED | 至少 1 READY + 1 BLOCKED case 显式绑定 material manifest |
| `embedded-evidence-normalizer` | edge-coordination | DEFINED | all evidence-bearing cases（间接） | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED | 正例 + provenance/identity 缺失负例，冻结 normalized evidence refs |
| `architecture-impact-analysis` | embedded.architecture | DEFINED | GC-DRIVER-001 / GC-BRINGUP-001（接近） | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED | 增加 architecture change case，显式冻结 impact output |
| `interface-contract-review` | embedded.architecture | DEFINED | GC-DRIVER-001（接近） | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED | API/ABI/version/error contract 正负例各 1 |
| `boot-chain-analysis` | embedded.linux-bsp | DEFINED | GC-BOOT-001 | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED / DIRECT_CASE_PENDING | GC-BOOT 显式声明 Skill + frozen technical-analysis |
| `device-tree-review` | embedded.linux-bsp | DEFINED | GC-BRINGUP-001 / GC-DRIVER-001（接近） | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED | 增加 exact board revision + DT mismatch 负例 |
| `irq-dma-analysis` | embedded.linux-bsp | DEFINED | GC-DMA-001 | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED / DIRECT_CASE_PENDING | GC-DMA 显式绑定 Skill invocation/output |
| `storage-filesystem-analysis` | embedded.linux-bsp | DEFINED | GC-NAND-001 / GC-UBIFS-001 | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED / DIRECT_CASE_PENDING | 两个 case 冻结 storage-layer output + BLOCK behavior |
| `mcu-startup-analysis` | embedded.mcu-rtos | DEFINED | GC-BRINGUP-001（接近） | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED | 增加 reset/vector/startup 专门正负例 |
| `linker-map-analysis` | embedded.mcu-rtos | DEFINED | GC-LINKER-001 | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED / DIRECT_CASE_PENDING | GC-LINKER 显式冻结 exact MAP/ELF Skill output |
| `rtos-concurrency-analysis` | embedded.mcu-rtos | DEFINED | GC-RTOS-001 / GC-REVIEW-001 | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED / DIRECT_CASE_PENDING | deadlock 正例 + insufficient trace BLOCK 负例 |
| `driver-integration-review` | embedded.driver-component | DEFINED | GC-DRIVER-001 / GC-BRINGUP-001 | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED / DIRECT_CASE_PENDING | frozen compatibility/lifecycle analysis + error/power negative path |
| `log-triage` | embedded.debug-reliability | DEFINED | 多个 diagnostic case（间接） | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED | 原始 log → timeline 正例 + identity mismatch BLOCK 负例 |
| `crash-hardfault-analysis` | embedded.debug-reliability | DEFINED | GC-HARDFAULT-001 / GC-KPANIC-001 | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED / DIRECT_CASE_PENDING | 显式 Skill output hypothesis registry + symbol mismatch 负例 |
| `memory-corruption-analysis` | embedded.debug-reliability | DEFINED | GC-KPANIC-001（接近） | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED | 增加 earliest-corruption/candidate-writer 正负例 |
| `performance-analysis` | embedded.debug-reliability | DEFINED | NO_DIRECT_CASE | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED | baseline/measurement comparable 正例 + incomparable baseline 负例 |
| `verification-plan-builder` | verification | DEFINED | all verification cases（间接） | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED | Acceptance→layer 显式 output + layer-downgrade 负例 |
| `regression-scope-analysis` | verification | DEFINED | 多个 change cases（间接） | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED | interface/lifecycle indirect impact case + over/under scope 负例 |
| `build-evidence-check` | verification | DEFINED | GC-DRIVER-001 / GC-BRINGUP-001 / GC-OTA-001（接近） | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED | exact build/artifact 正例 + skipped build / build→device overclaim 负例 |
| `device-evidence-check` | verification | DEFINED | GC-HARDFAULT-001 / GC-BRINGUP-001（接近） | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED | exact device/firmware 正例 + wrong-board/wrong-version 负例 |
| `hil-evidence-check` | verification | DEFINED | GC-DRIVER-001 提及 HIL hooks，但非 HIL case | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED | 新增真实 HIL case + fixture/target/run identity 负例 |
| `release-readiness-check` | review | DEFINED | GC-OTA-001 | REAL_USAGE_NOT_ATTRIBUTED | PORTABILITY_NOT_PROVEN | DEFINED / DIRECT_CASE_PENDING | GC-OTA 冻结 review output + missing rollback/Verification BLOCK 负例 |

## 4. 为什么不能把当前 Golden Case 直接算成 Skill EVALUATED

当前 `evaluation/golden-cases.yaml` 明确记录：

- task type；
- target mode；
- expected Expert / Capability；
- required Assurance；
- required evidence；
- Gate behavior；
- forbidden claims；
- success signals。

但它**没有**记录：

- selected Skill IDs；
- Skill Contract version；
- Skill input identity；
- Skill output artifact identity/hash；
- Runtime binding；
- evaluation verdict per Skill；
- negative/BLOCK case 是否由目标 Skill 正确触发。

所以当前 Golden Case 能证明 routing/capability/assurance 行为，却不能证明某个具体 Skill 在某个 Runtime 上按其 contract 被正确执行。

## 5. 当前真实 Pilot 也缺 Skill-level attribution

当前真实 Pilot 资产已经能冻结 source/artifact/device/Verification 等重要 identity，但仓库搜索不到稳定的 Skill invocation / Skill output receipt 字段。

因此即便某个真实任务“事实上用了”某 Skill，只要 frozen evidence 没有记录：

```text
skill_id
skill_contract_version
owner
runtime_binding
input evidence refs
output artifact/ref
action level
started/finished identity
result / blocked reason
```

就不能把它计入 Skill maturity。

这些字段现在已有正式 contract；剩余缺口是让真实 Runtime binding 在后续 Run 中实际产生 attested receipt，并为 Golden Case 增加 Skill-specific evaluation verdict。

## 6. Skill 成熟度晋级规则

### DEFINED → EVALUATED

至少需要：

1. case 明确声明目标 `skill_id`；
2. contract version 固定；
3. input/output 结构可检查；
4. 1 个 positive case；
5. 1 个 negative/BLOCK case；
6. forbidden claim 能被检测；
7. verdict 只评价 Skill contract，不偷带 Product readiness。

### EVALUATED → PILOTED

至少需要：

1. real Work/Run；
2. exact source/system identity；
3. frozen Skill invocation receipt；
4. output artifact/evidence 可追溯；
5. downstream Verification 不依赖“Skill 自己说自己成功”。

### PILOTED → REPEATABLE

至少需要：

- 多个真实任务；
- 不同输入/故障形态；
- correct block rate 可观察；
- unsupported claim rate 可观察；
- recurrence/regression 结果可追踪；
- 同一 Skill 不是只在单个项目/单个专家提示下成立。

### REPEATABLE → PORTABLE/GOVERNED

至少需要：

- 第二 Runtime 执行同一 frozen Contract；
- input/source set 一致；
- 输出质量/阻断行为可比较；
- action authority 不因 Runtime 更换扩大；
- version/deprecation/rollback 有治理。

## 7. 评审时应如何使用本台账

评审人员看到一个 Skill 时，应按下面顺序追：

1. `skills.yaml`：它是否 canonical、归谁；
2. `SKILL.md`：定义是否完整；
3. 本台账：当前成熟度证据到哪一步；
4. Golden Case：有没有 Skill-specific evaluation；
5. real Pilot：有没有 Skill invocation receipt；
6. 第二 Runtime：Portability 是否证明；
7. metrics：是否有 correct block / unsupported claim / regression 数据。

只要第 4–6 步没有证据，就不能把 `DEFINED` 写成“成熟能力”。

## 8. 当前最优先的下一步

P0 不是继续扩 Skill 数量，而是让已经建立的 usage receipt 真正产生证据，并补齐 **Skill evaluation evidence**：

- Golden Case 增加显式 Skill target / contract version；
- Runtime binding 在真实执行后输出 attested Skill invocation receipt，Digital Worker 只校验/冻结；
- 正例与 BLOCK 负例都要形成 Skill-specific evaluation receipt/verdict；
- evaluator 聚合 Skill-level usage/evaluation，而不是从 Capability case 反推；
- 后续第二 Runtime 使用同一 frozen Contract 形成 portability 对照；
- maturity ledger 最终从“人工状态说明”迁移为“receipt 驱动”。

在这之前，当前 23 个 Skill 的正确结论是：

> **定义、治理与 Skill invocation receipt 基础设施已建立；存量真实使用仍未归因，Skill-level evaluation 与跨 Runtime portability 仍是 EVIDENCE_PENDING。**
