# ADR-002：嵌入式系统专家团架构与落地边界

- Status: proposed-for-acceptance
- Date: 2026-09-11
- Scope: 研发中心 AI 数字员工体系中的嵌入式软件研发专家团
- Related: `研发中心AI数字员工研发流程规划.md`
- Related: `docs/adr/ADR-001-workbuddy-codex-integration-boundary.md`
- Related: `docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md`
- Reference: `产品专家团-核心参考/`

## Context

研发中心已经确认需要把 AI 引入嵌入式软件研发闭环，但总体平台、知识平台和 Engineering Agent Runtime 尚未冻结。飞书、WorkBuddy、WeKnora、Codex、Claude Code 等均是候选 Provider；NAS、Git、CI/HIL、Artifact Store 等也承载不可替代的工程事实。

在这种情况下，嵌入式系统专家团必须是**Provider-neutral 的专业组织与治理层**，不能绑定某个办公入口、知识平台或模型 Runtime。

研发中心嵌入式软件工作横跨 Linux/BSP、MCU/RTOS、驱动与组件、系统架构、调试可靠性、验证、发布与现场问题。若仅用 Prompt 或万能 Agent 承载，会产生职责漂移、证据不足、错误 PASS、自我验证和恢复困难等问题。

`digital-worker` 因此作为专家团设计、Contract、Gate、Evidence、Evaluation 与 Pilot 的正式治理主仓。

## Decision

### D1. digital-worker 是专家团唯一设计与治理主仓

以下正式资产全部落在 `digital-worker`：

- Agent 定义；
- Skill 定义；
- Workflow / Task Mode；
- Gate / run-state；
- I/O Contract；
- Schema；
- Action Policy；
- Evaluation / Golden Case；
- Pilot / Productionization 治理；
- Cross-team Contract。

外部仓库、办公平台、知识平台和模型 Runtime 均是参考或 Provider，不成为专家团定义的权威事实源。

### D2. 专家团采用“1 + 7”核心组织模型

唯一编排入口：`embedded-system-team-lead`。

正式专家：

1. `embedded-architecture-expert`：系统架构、资源与接口、平台影响、技术可行性；
2. `linux-bsp-expert`：Boot/BSP/Kernel/DT/Clock/Reset/Pinctrl/IRQ/DMA/Storage；
3. `mcu-rtos-expert`：Bare-metal/RTOS/Startup/Linker/ISR/DMA/Watchdog/Low Power/MCU OTA；
4. `driver-component-expert`：驱动、外设、连接、存储、电源、音频、电机等组件工程；
5. `debug-reliability-expert`：Crash/HardFault/Panic/内存/并发/性能/长稳/现场问题；
6. `verification-expert`：Unit/SIL/HIL/Fault Injection/Regression/Stress/Endurance；
7. `embedded-review-governor`：独立架构、代码、证据和发布就绪审查。

实施者不得给自己的修改签最终 Verification / Review PASS。

### D3. Expert、Skill、Workflow、Knowledge、Runtime 分层

- Expert：稳定职业角色；
- Skill：高频可复用专业原子能力；
- Workflow：固定任务闭环；
- Knowledge：可追溯规则、资料、事实和案例；
- Agent Runtime：执行 Expert/Workflow 任务的模型或工具实现，可替换。

SPI-NAND、UBI/UBIFS、DMA cache、Wi-Fi、Audio/DSP、Motor/FOC 等专项优先实现为 Skill，而不是无限扩张正式专家数量。

### D4. Engineering Handoff 必须 Provider-neutral

主链：

```text
Work Item / Interaction Provider
    -> task-brief
    -> Embedded System Expert Team
    -> engineering-task-package
    -> Engineer + Engineering Agent Runtime
    -> delivery-receipt
    -> Verification / Independent Review
    -> Work Item / Collaboration Provider
```

`Engineering Agent Runtime` 可以是 Codex、Claude Code、IDE Agent、内部 Agent、受控 Runner 或未来其他实现。

办公入口/协作 Provider 默认不得直接控制个人开发机、设备写或 Release。

### D5. 任务必须先分类，再选择链路

首批 `task_type`：

- `feature_development`
- `defect_debugging`
- `architecture_design`
- `technical_feasibility_review`
- `platform_bringup`
- `bsp_porting`
- `driver_development`
- `component_development`
- `mcu_firmware_development`
- `performance_optimization`
- `stability_reliability`
- `code_review`
- `release_ota`
- `field_incident`

首批 `workflow_mode`：

- `full_chain`
- `short_chain`
- `diagnostic_chain`
- `bringup_chain`
- `review_only`
- `release_chain`
- `single_expert`

禁止默认 full chain；任何 mode 扩展必须有 Team Lead 决策。

### D6. Gate 与状态机是主控制机制

核心 Gate：

- `gate.k`：Knowledge Readiness；
- `gate.m`：Engineering Material Readiness；
- `gate.0`：Intake Clarity；
- `gate.t`：Technical Decision；
- `gate.e`：Engineering Handoff；
- `gate.v`：Verification；
- `gate.r`：Independent Review；
- `gate.c`：Closure。

关键资料缺失时只能 `BLOCKED`，或在显式人工确认后 `DEGRADED_WITH_APPROVAL`。

### D7. Debug 必须维护 Hypothesis Registry

事实状态：

- `Observed`；
- `Inferred`；
- `Confirmed`。

Hypothesis 状态：

- `open`；
- `supported`；
- `rejected`；
- `confirmed`。

禁止首次看到日志就宣布根因。

### D8. Evidence 是一等对象

关键结论应具备：

- claim；
- evidence_refs；
- confidence；
- verification_status。

证据可以来自源码/commit、日志、core/dump、datasheet/TRM、schematic、waveform、构建/CI、binary hash、device identity、HIL、measurement 等。

证据保留在适合的 Source of Truth；专家团消费的是受控 `evidence-ref`，而不是要求把所有原始证据复制进知识平台。

### D9. 验证状态分层

至少区分：

- `implemented`；
- `host_verified`；
- `cross_build_verified`；
- `sil_verified`；
- `device_verified`；
- `hil_verified`；
- `release_verified`。

禁止跨层推导 PASS。

### D10. 高风险动作与 Provider 无关，统一受 Action Policy 控制

自治等级：

- A0 READ
- A1 ANALYZE
- A2 GENERATE
- A3 MODIFY_WORKTREE
- A4 BUILD_TEST
- A5 DEVICE_READ
- A6 DEVICE_WRITE
- A7 RELEASE

当前默认：

- A0-A2 可自动；
- A3-A4 只在受控工程执行环境；
- A5 需授权；
- A6 / A7 需人工批准；
- OTP/Fuse、生产密钥、生产 OTA、不可逆启动配置不得默认自动执行。

无论 Runtime 是 Codex、Claude 还是其他 Agent，都不能绕过这一策略。

### D11. 产品专家团与嵌入式专家团通过 Contract 协作

```text
Product Expert Team
    -> technical-review-request
Embedded System Expert Team
    -> embedded-feasibility-review
Product Expert Team
```

产品专家团负责 What / Why / 优先级 / 产品边界；嵌入式专家团负责 How / Feasibility / Architecture Impact / Evidence / Verification Strategy。

### D12. 与端侧底座专家团通过 Capability Ownership 消除重叠

统一 ownership：

- `OWN`
- `SHARED`
- `CONSUME`
- `PROVIDE`
- `OUT_OF_SCOPE`

同一能力不得复制两套权威 Agent/Skill。当前 ownership 仍保持 evidence-needed。

### D13. 专家团不冻结企业知识平台

专家团只冻结以下知识原则：

1. Source of Truth stays at source；
2. 知识/证据访问必须保留 source/version/ACL/provenance；
3. local `knowledge/` 只保存方法、清单、模板、术语、可信源导航和静态规则；
4. 不复制企业知识正文形成第二套 SSOT；
5. Knowledge Provider（如 WeKnora）和 Source（如飞书/NAS/Git）解耦；
6. Gate K 判断“能否获得足够可信上下文”，而不是判断“某个特定知识平台是否在线”。

### D14. 首批 P0 Skill 已冻结，P1 由真实 Pilot 驱动

当前已经建设 23 个 P0 Skill。后续 P1 Skill 必须来自真实 Pilot 中重复出现、可稳定复用的能力缺口。

### D15. Provider 切换不能改变专家团语义

以下情况均不应改变 task taxonomy、Gate、Evidence、Verification 和 Review：

- Codex → Claude；
- Claude → IDE Agent；
- 飞书 → 其他 Work Item Provider；
- WeKnora → 其他 Knowledge Provider；
- WorkBuddy → 其他 Interaction Provider。

如果 Provider 切换需要修改核心 Workflow 语义，说明 Adapter 边界设计失败，需要先评审架构。

## Consequences

### 正向

- 专家团与具体模型/平台生命周期解耦；
- 同一专家能力可运行在不同 Engineering Agent Runtime；
- NAS、Git、CI/HIL 等工程事实保留原始权威；
- 可以独立 PoC Knowledge Provider 和 Runtime；
- 安全边界基于 action/evidence，而不是品牌。

### 成本

- 需要 Provider Adapter / Capability Matrix；
- Knowledge Gateway / Context Broker 需要进一步 PoC；
- 身份、ACL、source provenance 跨系统映射更复杂；
- 初期存在多入口、多 Runtime 的治理成本。

## Rejected Options

### A. 把某个 Coding Agent 作为专家团本体

拒绝。模型/CLI 是 Runtime，不是 Expert identity。

### B. 建立万能嵌入式 Agent

拒绝。职责、上下文和验证范围过大。

### C. 一开始建设几十个专项专家

拒绝。专项能力优先 Skill 化。

### D. 办公 Agent 直接控制个人开发机和设备

拒绝。沿用 ADR-001 的 Contract 松耦合原则。

### E. 统一把飞书/NAS/Git/HIL 内容搬进单一知识库

拒绝作为默认架构。统一访问可以，统一存储必须由 PoC 证明必要性。

### F. AI 自己实现、自己验证、自己宣布完成

拒绝。Verification 和 Independent Review 保持独立。

## Acceptance Criteria

本 ADR 可转 `accepted` 的最低条件：

1. 1+7 / task taxonomy / workflow mode 通过内部评审；
2. Machine Contract 中工程执行角色已 Provider-neutral；
3. 至少 10 个 Golden Case 保持可运行；
4. 产品专家团 handoff contract 可用；
5. 端侧底座 ownership 至少完成第一版；
6. 用同一工程 Contract 至少验证两个 Runtime；
7. 不存在 Provider-specific 绕过 A6/A7 的路径；
8. Knowledge Source / Provider 分离原则通过总体架构评审。

## Revisit Triggers

- ADR-003 被推翻；
- 端侧底座职责与本专家团大面积冲突；
- 真实 Pilot 证明 1+7 导致严重错误路由；
- 建设统一 Agent Runtime Gateway / Action Gateway；
- 企业确定强约束唯一 Provider 且 Provider 能力成为不可替代组织基础设施。
