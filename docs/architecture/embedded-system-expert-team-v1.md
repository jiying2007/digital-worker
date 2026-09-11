# 嵌入式系统专家团当前阶段终版设计 V1

- 状态：`frozen-for-implementation`
- 日期：2026-09-11
- 适用范围：研发中心嵌入式系统（软件）研发数字员工改造
- 主仓：`jiying2007/digital-worker`
- 架构决策：`docs/adr/ADR-002-embedded-system-expert-team-architecture.md`
- 上游总流程：`研发中心AI数字员工研发流程规划_V2.md`
- 集成边界：`docs/adr/ADR-001-workbuddy-codex-integration-boundary.md`
- 主要参考：`产品专家团-核心参考/`

> 本文定义的是“当前阶段终版”：冻结后续实现必须遵循的组织、流程、契约、门禁和评测边界；它不是最终全部功能已经实现的声明。

---

## 1. 审查结论

### 1.1 当前仓库基础已经足够进入正式专家团建设

`digital-worker` 已经具备三类关键基础：

1. 研发中心数字员工总体流程 V2：定义飞书、WorkBuddy、WeKnora、Codex、Git/CI/HIL 的职责和事实源；
2. ADR-001：冻结一期 WorkBuddy 与 Codex 的契约式松耦合边界；
3. 产品专家团核心参考：提供成熟的 Team Lead、Agent、Skill、Workflow、Gate、run-state、I/O、Schema、deliverable packaging 和断点恢复范式。

因此嵌入式系统专家团不应再建设第二套“总平台”，而应作为 V2 中的正式专业技术决策与治理层落地。

### 1.2 之前最容易走偏的四个方向

审查后明确拒绝：

- 将外部仓库设为嵌入式专家团 SSOT；
- 用单个万能 Agent 覆盖完整嵌入式研发；
- 以大量 Prompt/Skill 数量代替 Workflow、Gate 和 Contract；
- 让实现 Agent 自己验证并宣布交付完成。

### 1.3 当前阶段最重要的成果不是 Skill 数量

当前阶段优先级为：

```text
组织边界 > 任务分类 > 工作流 > Gate > Contract > Evidence > Evaluation > Skill 扩充
```

若顺序反过来，后续会出现能力重复、职责冲突、上下文拼接混乱和无法自动回归的问题。

---

## 2. 总体定位

嵌入式系统专家团是研发中心 AI 数字员工体系中的“嵌入式软件专业技术组织”。

它负责把上游业务/产品任务转换为可执行、可验证、可审计的嵌入式研发任务，并对工程输出进行独立专业复核。

### 2.1 它负责什么

- 嵌入式技术接诊与任务分类；
- 系统架构与技术可行性；
- Linux/BSP/Boot/Kernel/Device Tree；
- MCU/RTOS/Bare-metal；
- 驱动与公共组件；
- 调试、性能与可靠性；
- 验证策略与 HIL；
- 代码/架构/证据独立审查；
- release/OTA 工程准备度；
- 现场问题 RCA；
- 专业知识候选沉淀。

### 2.2 它不负责什么

- 不替代产品专家团做市场、用户、PRD 和产品价值判断；
- 不替代飞书成为工作项状态主库；
- 不替代 Git 成为源码主库；
- 不替代 CI/HIL 成为验证事实源；
- 不直接控制个人开发机无限 Shell；
- 不自动执行 OTP/Fuse、生产密钥、生产 OTA、Release Promotion 等高风险动作；
- 不把未经审核的 AI 推断写成企业正式知识。

---

## 3. 在研发中心总体流程中的位置

```text
产品/项目/研发工作项
        │
        ▼
飞书 / WorkBuddy
        │
     task-brief
        │
        ▼
┌─────────────────────────────────────┐
│ Embedded System Expert Team         │
│                                     │
│  Team Lead                          │
│    ├ Architecture                   │
│    ├ Linux/BSP                      │
│    ├ MCU/RTOS                       │
│    ├ Driver/Component               │
│    ├ Debug/Reliability              │
│    ├ Verification                   │
│    └ Review Governor                │
│                                     │
│  Workflow / Gate / Contract / Eval  │
└───────────────┬─────────────────────┘
                │
     engineering-task-package
                │
                ▼
         Engineer + Codex CLI
                │
        delivery-receipt
                │
                ▼
  Verification + Independent Review
                │
                ▼
         WorkBuddy / 飞书
```

专家团属于专业决策与工程治理层，不承担办公入口和源码执行环境的职责。

---

## 4. 组织模型：1 + 7

## 4.1 主理人：embedded-system-team-lead

唯一对外入口，负责：

- 任务接诊；
- `task_type` 判断；
- workflow mode 选择；
- 材料完整性检查组织；
- 风险分类；
- 专家路由；
- Gate 推进；
- run-state 与恢复；
- 工程交接；
- 交付收口；
- 跨专家团协调。

主理人不代替正式专家直接完成复杂专业分析，也不作为最终产品验收人。

## 4.2 系统架构专家：embedded-architecture-expert

负责：

- 系统分层与模块边界；
- Linux/MCU/RTOS 功能划分；
- IPC / threading / scheduling；
- memory/resource budget；
- boot / fault containment；
- platform abstraction；
- API / ABI；
- portability；
- architecture impact；
- technical feasibility。

## 4.3 Linux/BSP 专家：linux-bsp-expert

负责：

- BootROM / SPL / U-Boot；
- Linux kernel；
- Device Tree；
- Kconfig；
- pinctrl / clock / reset；
- IRQ / DMA；
- storage / filesystem；
- BSP porting / board bring-up；
- kernel/platform issue。

## 4.4 MCU/RTOS 专家：mcu-rtos-expert

负责：

- bare-metal / RTOS；
- startup；
- linker / memory layout；
- ISR / DMA / timer；
- task / queue / semaphore / lock；
- watchdog；
- low power；
- flash；
- MCU bootloader / OTA。

## 4.5 驱动与组件专家：driver-component-expert

负责：

- GPIO / I2C / SPI / UART / USB；
- Wi-Fi / BLE；
- Flash / storage device；
- sensor / camera / audio；
- motor / power IC；
- middleware / reusable component；
- component API / portability。

## 4.6 调试与可靠性专家：debug-reliability-expert

负责：

- kernel panic / crash / hardfault；
- memory corruption / leak；
- race / deadlock；
- stack / heap；
- CPU / memory / latency；
- startup / IRQ latency；
- thermal / long-run；
- intermittent field issue；
- RCA。

## 4.7 验证专家：verification-expert

负责：

- unit / component test；
- static analysis；
- SIL / simulation；
- HIL；
- fault injection；
- regression；
- stress / endurance；
- verification plan；
- evidence completeness。

## 4.8 独立审查专家：embedded-review-governor

负责：

- architecture review；
- code review；
- concurrency / memory safety；
- security / regression impact；
- evidence review；
- release readiness review。

约束：实现者不能独立批准自己的最终验证和发布准备度。

---

## 5. Agent / Skill / Workflow / Knowledge 分层规则

### Agent

只有当能力对应长期稳定的职业角色，并拥有独立责任边界和判断职责时才创建 Agent。

### Skill

专项技术能力默认 Skill 化。例如：

- `spi-nand-diagnosis`
- `ubi-ubifs-diagnosis`
- `device-tree-review`
- `dma-cache-coherency-analysis`
- `linker-map-analysis`
- `hardfault-analysis`
- `wifi-connectivity-diagnosis`
- `audio-aec-analysis`
- `motor-foc-analysis`
- `ota-failure-analysis`

### Workflow

固定业务闭环定义 Workflow，不通过临时 prompt 拼流程。

### Knowledge

知识必须具备来源、版本、适用平台和证据级别；硬件事实不能由语言模型常识替代。

---

## 6. Task Taxonomy

首批冻结 14 类任务：

| task_type | 典型场景 | 默认模式 |
|---|---|---|
| feature_development | 新功能实现 | short_chain/full_chain |
| defect_debugging | 缺陷定位修复 | diagnostic_chain |
| architecture_design | 架构设计/重构 | short_chain |
| technical_feasibility_review | 技术可行性评审 | review_only |
| platform_bringup | 新板/新 SoC Bring-up | bringup_chain |
| bsp_porting | BSP/Kernel 移植 | bringup_chain |
| driver_development | 新驱动/驱动改造 | short_chain |
| component_development | 公共组件建设 | short_chain |
| mcu_firmware_development | MCU/RTOS 功能 | short_chain |
| performance_optimization | CPU/RAM/ROM/Latency | short_chain |
| stability_reliability | 长稳/可靠性 | diagnostic_chain |
| code_review | 代码审核 | review_only |
| release_ota | Release/OTA | release_chain |
| field_incident | 现场事故/RCA | diagnostic_chain |

Task Taxonomy 是机器可读路由规则，不以自然语言习惯长期隐式维护。

---

## 7. Workflow Modes

### 7.1 full_chain

用于跨多专业、需求到验证完整闭环的新能力。

```text
Intake -> Material -> Architecture -> Domain Analysis
-> Engineering Handoff -> Execution -> Verification
-> Independent Review -> Closure
```

### 7.2 short_chain

用于已有产品上的常规功能、驱动、组件或优化。

### 7.3 diagnostic_chain

用于 Bug、长稳、现场问题。

```text
Intake
-> Evidence Freeze
-> Observation
-> Hypothesis Registry
-> Diagnostic Experiments
-> Root Cause
-> Fix Plan
-> Execution
-> Regression
-> Review
-> RCA / Closure
```

### 7.4 bringup_chain

用于新平台/BSP/板卡：

```text
Material Readiness
-> Boot/BSP Analysis
-> Platform Plan
-> Build
-> Flash/Deploy
-> UART/JTAG/Device Evidence
-> HIL
-> Review
```

### 7.5 review_only

只做技术评审、PR Review 或可行性评审，不自动扩展为实施任务。

### 7.6 release_chain

```text
Candidate Identity
-> Clean Source / Provenance
-> Build / Artifact Identity
-> Regression
-> Device/HIL
-> OTA / Rollback
-> Independent Review
-> Human Release Gate
```

### 7.7 single_expert

仅用于边界清晰、无需跨专家判断的专项分析。

---

## 8. Gate 体系

## Gate K：Knowledge Readiness

检查任务需要的：

- datasheet；
- TRM；
- SDK/BSP；
- known issues；
- engineering rule；
- historical RCA。

输出：`PASS / BLOCKED / DEGRADED_WITH_APPROVAL`。

## Gate M：Engineering Material Readiness

至少检查：

- repo；
- branch/base SHA；
- dirty baseline；
- board revision；
- SoC/MCU；
- SDK/kernel/toolchain；
- schematic revision；
- firmware/version；
- logs/reproduction；
- device identity。

涉及硬件判断但缺 datasheet/schematic/version 时不得生成高置信度结论。

## Gate 0：Intake Clarity

五维：

- 目标；
- 范围；
- 边界；
- 约束；
- 验收。

## Gate T：Technical Decision

检查：

- 方案；
- architecture impact；
- dependencies；
- risk；
- validation plan；
- rollback；
- unresolved items。

## Gate E：Engineering Handoff

确保 `engineering-task-package` 可供工程师/Codex 执行。

## Gate V：Verification

按验证层级判定，禁止跨层推导。

## Gate R：Independent Review

由独立审查角色判断是否存在设计、实现、证据或回归风险。

## Gate C：Closure

检查 deliverable manifest、open risks、knowledge candidate、execution log 完整性。

---

## 9. 状态与恢复

专家团必须维护 `team-run-state` 和 `gate-ledger`。

推荐状态：

```text
draft
needs_information
ready_for_analysis
in_analysis
ready_for_engineering
in_engineering
ready_for_verification
in_verification
ready_for_review
blocked
needs_rework
completed
cancelled
```

恢复原则：

- 从 failed stage/step 继续；
- 不因单点失败整链重跑；
- 每个 blocker 必须附 `resume_instructions`；
- 降级运行必须记录 approval 和影响范围；
- 下游发现上游证据不足时允许一次精确回流，禁止无限循环。

---

## 10. 三层 I/O Contract

直接沿用产品专家团已经验证的三层契约思想。

### L1：Expert Contract

定义专家：

- consume 什么上下文；
- 做什么职责判断；
- 产出什么 artifact；
- 交给谁。

不细写字段。

### L2：Skill Contract

定义字段级：

- inputs；
- outputs；
- schema；
- constraints；
- failure conditions。

### L3：Stage Artifact Contract

阶段产物必须声明：

- `consumed_refs`；
- `downstream_contract`。

用于机器检查是否真的消费了上游数据、是否存在 orphan output 或伪闭环。

---

## 11. 核心数据契约

首批需要正式 Schema 化：

### 11.1 task-brief

复用 V2，对专家团增加：

- embedded task type；
- target board/platform；
- hardware/software boundary；
- verification level；
- allowed/forbidden actions。

### 11.2 engineering-material-manifest

统一记录硬件、软件、版本、资料和设备基线。

### 11.3 technical-analysis

承载架构/专业分析结论、风险和 evidence refs。

### 11.4 hypothesis-registry

```yaml
hypothesis_id:
statement:
evidence_for: []
evidence_against: []
confidence:
experiment:
status: open | supported | rejected | confirmed
```

### 11.5 engineering-task-package

专家团交给 Engineer/Codex 的正式执行契约。

### 11.6 delivery-receipt

复用 V2，作为真实工程执行回执。

### 11.7 verification-report

分别记录：

- host；
- cross build；
- SIL；
- device；
- HIL；
- release。

### 11.8 evidence-ref

证据统一对象。

### 11.9 expert-handoff

跨专家/跨专家团机器可读交接。

### 11.10 deliverable-manifest

正式闭环必须存在，否则不可宣称完成。

---

## 12. Evidence 与 Confidence

### 12.1 Evidence Type

- source code；
- commit / diff；
- build output；
- CI；
- log；
- core/dump；
- datasheet/TRM；
- schematic；
- waveform；
- measurement；
- binary hash；
- device identity；
- HIL report。

### 12.2 Claim Contract

重要结论必须具备：

```yaml
claim:
evidence_refs: []
confidence:
verification_status:
```

### 12.3 推荐证据置信等级

- C0：未知/无证据；
- C1：模型推断；
- C2：经验或历史案例支持；
- C3：源码/配置验证；
- C4：正式文档验证；
- C5：实验/设备验证；
- C6：量产/现场长期验证。

置信等级不是正确率数字，只用于表达证据强度。

---

## 13. Debug 专用纪律

Debug 是嵌入式专家团需要重点工程化的任务。

强制区分：

### Observed

直接来自日志、寄存器、dump、代码、测量或复现的事实。

### Inferred

基于事实的推断，但尚未被实验确认。

### Confirmed

通过代码路径、文档或实验闭环证明。

禁止：

- 看到单条日志直接宣称 root cause；
- 用相似历史问题覆盖当前设备证据；
- 缺板卡/SDK/版本信息时假装精确；
- 只证明“修改后不复现”就宣称机理根因已确认。

---

## 14. Verification 分层

验证状态必须独立保存：

```text
implemented
host_verified
cross_build_verified
sil_verified
device_verified
hil_verified
release_verified
```

例如：

- `host_verified=true` 不代表 ARM/MCU 交叉构建通过；
- `cross_build_verified=true` 不代表 binary 已运行在目标设备；
- `device_verified=true` 不代表完整 HIL 场景通过；
- `hil_verified=true` 不代表 Release/OTA/rollback 已验证。

这是专家团的硬门禁之一。

---

## 15. Autonomy / Action Policy

### A0 READ

读取仓库、资料、日志。

### A1 ANALYZE

技术分析、检索、比较、设计。

### A2 GENERATE

生成报告、方案、patch 建议、测试计划。

### A3 MODIFY_WORKTREE

真实代码修改。当前由工程师/Codex 受控执行。

### A4 BUILD_TEST

Host、静态检查、交叉构建、允许范围内的自动测试。

### A5 DEVICE_READ

UART、ADB/SSH 只读诊断、设备状态读取；必须受权。

### A6 DEVICE_WRITE

烧录、配置写入、重启、设备状态改变；必须人工批准并具备恢复方案。

### A7 RELEASE

发布、量产 OTA、Release Promotion；必须人工批准。

永久禁止默认自动化：

- OTP/Fuse；
- 生产签名密钥；
- 删除生产数据；
- 不可逆 boot 配置；
- 无回退策略的生产 OTA。

---

## 16. Product Expert Team Handoff

产品专家团主要回答：

- 为什么做；
- 为谁做；
- 做什么；
- 业务与产品验收是什么。

嵌入式系统专家团主要回答：

- 技术上怎么做；
- 是否可行；
- 架构/资源/平台影响；
- 风险在哪里；
- 如何验证；
- 有什么证据。

接口：

```text
technical-review-request
    ↓
Embedded System Expert Team
    ↓
embedded-feasibility-review
```

输出至少包含：

- feasibility；
- architecture impact；
- platform impact；
- resource budget；
- software/hardware dependency；
- implementation constraints；
- risks；
- verification strategy；
- open questions；
- evidence / confidence。

---

## 17. 与端侧底座专家团的边界原则

本阶段不通过名称猜测双方职责，而使用 Capability Ownership Map 管理。

每一项能力标记：

- OWN：本专家团唯一权威；
- SHARED：共同参与但指定最终 owner；
- CONSUME：消费对方能力；
- PROVIDE：向对方提供能力；
- OUT_OF_SCOPE：不承担。

嵌入式系统专家团默认承担的核心域：

- Boot/BSP；
- Linux/Kernel；
- MCU/RTOS/Bare-metal；
- Driver/Embedded Component；
- Product integration；
- Debug/Reliability；
- Embedded Verification；
- OTA/Release engineering；
- Field RCA。

正式实施前必须生成第一版 ownership map，并由相关负责人确认。

---

## 18. Knowledge Strategy

沿用 V2：

```text
飞书知识库 = 人工正式知识主库
WeKnora = AI 检索与引用层
```

专家团本地可保存：

- methodology；
- checklists；
- templates；
- terminology；
- source registry；
- static engineering rules；
- evaluation fixtures。

不允许在 `digital-worker` 和飞书中长期人工双写同一正式知识正文。

每个真实任务结束可生成 `knowledge-candidate`，由人工审核后进入正式知识流程。

---

## 19. P0 Skill 建设范围

当前阶段只冻结类别，下一阶段实现。

### Team Governance

- embedded-task-classifier
- embedded-material-readiness
- embedded-risk-classifier
- embedded-evidence-normalizer
- embedded-quality-gate
- embedded-consistency-checker
- embedded-execution-logger
- embedded-deliverable-packager

### Architecture

- system-impact-analysis
- interface-contract-review
- thread-task-model-review
- memory-budget-analysis
- power-state-analysis

### Linux/BSP

- boot-chain-analysis
- bsp-structure-analysis
- device-tree-review
- clock-reset-pinctrl-analysis
- irq-dma-analysis
- storage-filesystem-analysis

### MCU/RTOS

- mcu-startup-analysis
- linker-map-analysis
- isr-dma-analysis
- rtos-concurrency-analysis
- watchdog-analysis
- mcu-ota-analysis

### Debug/Reliability

- log-triage
- crash-analysis
- hardfault-analysis
- memory-corruption-analysis
- deadlock-race-analysis
- performance-analysis
- longrun-analysis

### Verification

- verification-plan-builder
- regression-scope-analysis
- build-evidence-check
- device-evidence-check
- hil-evidence-check
- release-readiness-check

专项 Flash/Wi-Fi/Audio/FOC 等作为后续 P1/P2。

---

## 20. Evaluation Contract

专家团从第一版开始就需要 Golden Cases。

### 首批案例建议

- boot failure；
- kernel panic；
- MCU hardfault；
- SPI-NAND ECC；
- UBI/UBIFS；
- DMA cache coherency；
- Wi-Fi connectivity；
- memory leak；
- deadlock；
- CPU high；
- motor low-speed issue；
- audio AEC/noise issue；
- OTA failure；
- long-run failure；
- embedded PR review。

### 每个 Case 至少包含

```yaml
task_type:
expected_route:
required_evidence: []
forbidden_claims: []
expected_gate:
expected_expert:
acceptable_conclusion:
```

### 核心指标

- Routing Accuracy；
- Evidence Coverage；
- Unsupported Claim Rate；
- Correct Block Rate；
- Incorrect PASS Rate；
- Root Cause Accuracy；
- Verification Completeness；
- Human Correction Rate。

其中 `Incorrect PASS Rate` 是最关键的安全质量指标之一，目标应接近 0。

---

## 21. Repo 落地结构

在现有仓库上增量建设：

```text
digital-worker/
├── README.md
├── 研发中心AI数字员工研发流程规划_V2.md
├── docs/
│   ├── adr/
│   │   ├── ADR-001-workbuddy-codex-integration-boundary.md
│   │   └── ADR-002-embedded-system-expert-team-architecture.md
│   └── architecture/
│       └── embedded-system-expert-team-v1.md
├── expert-groups/
│   └── embedded-system/
│       ├── README.md
│       ├── expert-group.yaml
│       ├── agents/
│       ├── config/
│       │   ├── workflow.yaml
│       │   ├── task-modes.yaml
│       │   ├── material-requirements.yaml
│       │   ├── action-policy.yaml
│       │   └── output-config.yaml
│       ├── contracts/
│       ├── schemas/
│       ├── skills/
│       ├── references/
│       ├── knowledge/
│       ├── scripts/
│       └── tests/
└── 产品专家团-核心参考/
```

注意：产品专家团当前目录仍标记为“核心参考”；后续若转正式运行资产，应单独做迁移决策，不与本次嵌入式专家团创建混在一起。

---

## 22. 权威顺序

嵌入式系统专家团内部发生文档冲突时，建议权威顺序：

1. `expert-group.yaml`：专家团身份、成员和顶层能力；
2. `config/workflow.yaml`：阶段、Gate、Transition；
3. `config/task-modes.yaml`：任务分类和路由；
4. `contracts/` + `schemas/`：数据契约；
5. `agents/*.md`：角色行为；
6. `skills/*/SKILL.md`：原子能力；
7. `references/`：方法论说明；
8. 说明性文档。

ADR 负责约束架构决策，不能被普通说明文档静默覆盖。

---

## 23. 当前阶段 Done-When

本设计阶段完成标准：

- ADR-002 已归档；
- 本终版设计已归档；
- 专家团目录和机器可读顶层 manifest 已建立；
- task taxonomy 和 workflow skeleton 与本文一致；
- 根 README 能导航到本设计；
- 通过分支 diff 自检，无对现有 V2/ADR-001 的冲突性修改。

达到这些条件，只代表“架构设计阶段冻结”，不代表专家团已经完成生产实现。

---

## 24. 下一阶段实施顺序

### M1：Governance Skeleton

- expert-group manifest；
- task modes；
- workflow；
- Gate/run-state schema；
- evidence schema；
- action policy。

### M2：Core Experts

落实 1+7 Agent 职责与 L1 contract。

### M3：P0 Skills

优先治理、架构、BSP、MCU、Debug、Verification。

### M4：Engineering Handoff

打通：

```text
task-brief
-> expert team
-> engineering-task-package
-> Codex/Engineer
-> delivery-receipt
-> verify/review
```

### M5：Cross-Team Contract

建立 Product Expert Team 技术评审 handoff 和端侧底座 ownership map。

### M6：Golden Cases / Pilot

使用真实历史问题做回归，并选择真实产品/平台试点。

---

## 25. 当前阶段最终决策摘要

1. `digital-worker` 是嵌入式专家团正式主仓和 SSOT；
2. 外部仓库只参考，不成为强依赖；
3. 采用 1+7 核心组织；
4. 专项能力优先 Skill 化；
5. 复用产品专家团 Team Lead / Gate / run-state / Contract / Schema 范式；
6. 延续 ADR-001，不直接遥控个人 Codex；
7. Debug 强制 Hypothesis Registry；
8. Evidence-first，关键结论必须可追溯；
9. Verification 与 Review 独立；
10. Host/Cross Build/Device/HIL/Release 分层状态；
11. 高风险设备与发布动作保留人工 Gate；
12. 与其他专家团通过机器可读 Contract 协作；
13. 当前先冻结架构契约，下一阶段再批量实现 Skill；
14. Evaluation 与实现同步建设，尤其控制 Incorrect PASS。

此版本作为后续嵌入式系统专家团实现工作的当前阶段设计基线。
