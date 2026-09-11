# ADR-002：嵌入式系统专家团架构与落地边界

- Status: proposed-for-acceptance
- Date: 2026-09-11
- Scope: 研发中心 AI 数字员工体系中的嵌入式软件研发专家团
- Related: `研发中心AI数字员工研发流程规划.md`
- Related: `docs/adr/ADR-001-workbuddy-codex-integration-boundary.md`
- Reference: `产品专家团-核心参考/`

## Context

`digital-worker` 已经形成研发中心数字员工总体流程提案：飞书承载工作项与人工流程，WorkBuddy 负责办公入口、需求整理与结果呈现，WeKnora 作为内网 AI 检索层，工程师在真实仓库中使用 Codex CLI 执行研发任务；一期通过 `task-brief` 与 `delivery-receipt` 契约松耦合，不由 WorkBuddy 直接控制个人开发机 Codex。

仓库同时保留了较成熟的产品专家团参考实现，已经验证 Team Lead、正式专家、Skill、Workflow、Task Mode、Gate、run-state、I/O Contract、Schema、证据与 Deliverable Manifest 的工程化专家团模式。

研发中心嵌入式软件工作横跨 Linux/BSP、MCU/RTOS、驱动与组件、系统架构、调试可靠性、验证、发布与现场问题。若仅以 Prompt 或单个万能 Agent 承载，会产生职责漂移、证据不足、错误 PASS、自我验证和无法恢复等问题。

此外，`agent-dev-kit`、`knowledge-hub`、`codex` 等仓库存在可借鉴资产，但本项目要求嵌入式系统专家团在 `digital-worker` 内正式落地。因此这些仓库不能成为专家团定义的权威事实源或强运行时依赖。

## Decision

### D1. digital-worker 是专家团唯一设计与治理主仓

嵌入式系统专家团的下列正式资产全部落在 `digital-worker`：

- Agent 定义；
- Skill 定义；
- Workflow / Task Mode；
- Gate / run-state；
- I/O Contract；
- Schema；
- Action Policy；
- Evaluation / Golden Case；
- 运行与交付治理文档。

其他仓库仅作为参考实现、方法来源或未来可选连接器，不作为专家团运行前置条件。

### D2. 专家团采用“1 + 7”核心组织模型

唯一入口为 `embedded-system-team-lead`，负责接诊、路由、编排、Gate、恢复、进度和收口，不替正式专家直接产出复杂专业结论。

首批正式专家：

1. `embedded-architecture-expert`：系统架构、资源与接口、平台抽象和技术可行性；
2. `linux-bsp-expert`：Boot/BSP/Kernel/DT/Clock/Reset/Pinctrl/IRQ/DMA/Storage；
3. `mcu-rtos-expert`：Bare-metal/RTOS/Startup/Linker/ISR/DMA/Watchdog/Low Power/MCU OTA；
4. `driver-component-expert`：驱动、外设、连接、存储、电源、音频、电机等组件工程；
5. `debug-reliability-expert`：Crash/HardFault/Panic/内存/并发/性能/长稳/现场问题；
6. `verification-expert`：Unit/SIL/HIL/Fault Injection/Regression/Stress/Endurance；
7. `embedded-review-governor`：独立架构、代码、证据和发布就绪审查。

实施者不得给自己的修改签最终验证 PASS。

### D3. Agent、Skill、Workflow、Knowledge 分层

- Agent：稳定的职业角色；
- Skill：高频、可复用、可组合的专业原子能力；
- Workflow：固定任务闭环；
- Knowledge：可追溯的规则、资料、事实与案例。

SPI-NAND、UBI/UBIFS、DMA cache、Wi-Fi、Audio/DSP、Motor/FOC 等专项能力优先实现为 Skill，而不是无限扩张正式专家数量。

### D4. 延续 ADR-001 的契约式松耦合

当前阶段专家团不直接遥控个人 Codex CLI。

主链为：

```text
飞书 / WorkBuddy
    -> task-brief
    -> Embedded System Expert Team
    -> engineering-task-package
    -> Engineer + Codex CLI
    -> delivery-receipt
    -> Embedded Verification / Review
    -> WorkBuddy / 飞书
```

未来可将 `Engineer + Codex CLI` 替换为受控 Runner/执行网关，但上下游契约必须保持稳定。

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

禁止默认所有任务从完整链路起跑。

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

关键资料缺失时只能 `BLOCKED` 或在显式人工确认后 `DEGRADED_WITH_APPROVAL`，不得由模型自行补全硬件事实。

### D7. Debug 工作流必须维护 Hypothesis Registry

诊断链强制区分：

- `Observed`：直接观察事实；
- `Inferred`：基于证据的推断；
- `Confirmed`：通过代码、文档、实验或硬件验证确认。

每个假设具有 `open / supported / rejected / confirmed` 状态，并绑定正反证据和验证实验，禁止首次看到日志即宣布根因。

### D8. Evidence 是一等数据对象

所有关键结论均应具备：

- `claim`；
- `evidence_refs[]`；
- `confidence`；
- `verification_status`。

证据类型覆盖源码、commit、日志、core/dump、datasheet/TRM、schematic、waveform、构建、CI、binary hash、device identity、HIL 和 measurement。

### D9. 验证状态分层，禁止单一 PASS 覆盖全部交付状态

至少区分：

- `implemented`；
- `host_verified`；
- `cross_build_verified`；
- `sil_verified`；
- `device_verified`；
- `hil_verified`；
- `release_verified`。

Host 或交叉构建通过不得推导 Board/HIL 或 Release 通过。

### D10. 高风险动作保持人工门禁

自治等级：

- A0 READ
- A1 ANALYZE
- A2 GENERATE
- A3 MODIFY_WORKTREE
- A4 BUILD_TEST
- A5 DEVICE_READ
- A6 DEVICE_WRITE
- A7 RELEASE

当前阶段默认自动开放 A0-A2；A3-A4 在工程师/Codex 受控环境执行；A5 需授权；A6 必须人工批准；A7 必须人工批准。OTP/Fuse、生产密钥、生产 OTA、不可逆启动配置等不得自动执行。

### D11. 产品专家团与嵌入式专家团通过 Contract 协作

产品专家团负责 What / Why，嵌入式系统专家团负责 How / Feasibility / Evidence。

跨团接口采用机器可读 handoff，而不是 Agent 自由聊天：

```text
Product Expert Team
    -> technical-review-request
Embedded System Expert Team
    -> embedded-feasibility-review
Product Expert Team
```

### D12. 与端侧底座专家团按 Capability Ownership 消除重叠

对于端侧底座专家团已拥有或未来正式化的能力，双方使用统一映射：

- `OWN`
- `SHARED`
- `CONSUME`
- `PROVIDE`
- `OUT_OF_SCOPE`

同一能力不得复制两套权威 Agent/Skill。若职责冲突，先更新 ownership map，再调整实现。

### D13. 知识主库沿用研发流程总纲，不另建第二套企业知识系统

正式协作知识继续以飞书原文为人工主库、WeKnora 为 AI 检索层。专家团本地 `knowledge/` 仅保存方法、清单、模板、术语、可信源目录和静态工程规则，不复制企业知识正文。

### D14. 先冻结架构契约，再扩 Skill

当前阶段只冻结：

- 组织模型；
- task taxonomy；
- workflow / Gate；
- I/O contract；
- evidence model；
- autonomy policy；
- cross-team boundary；
- evaluation contract。

架构冻结后已建设首批 23 个 P0 Skill 与运行脚本；后续 P1 Skill 必须由真实 Pilot 中重复出现的能力缺口驱动，禁止无证据扩张。

## Consequences

### 正向影响

- 与现有研发流程总纲和 ADR-001 一致，不引入第二套总流程；
- 复用产品专家团成熟的工程化组织方法，而非复制其产品领域内容；
- `digital-worker` 内形成真正可治理、可版本化、可评测的专家团；
- 后续可替换模型、Codex 运行方式或设备执行层，而不破坏业务契约；
- 明确独立验证和证据门禁，降低 AI 错误宣称完成的风险。

### 成本与债务

- 需要维护 Schema、Gate 和 run-state，而不仅是 Prompt；
- 需要真实历史案例建设 Golden Case；
- 需要后续补齐端侧底座专家团 capability ownership 的逐项映射；
- 二进制参考文档不利于代码审查和差异追踪，后续应增加受控 Markdown 镜像或提取版。

## Rejected Options

### 方案 A：把 agent-dev-kit 作为 Agent/Skill SSOT

拒绝。它可参考，但会造成 `digital-worker` 无法独立治理专家团，并形成跨仓版本耦合。

### 方案 B：建立万能嵌入式 Agent

拒绝。职责、上下文、验证和风险范围过大，无法独立审查，也不利于精准路由。

### 方案 C：一开始建设几十个专项专家

拒绝。专项能力优先 Skill 化，正式 Agent 保持稳定角色边界。

### 方案 D：WorkBuddy 直接控制个人 Codex 和设备

拒绝。延续 ADR-001，一期只通过结构化输入输出契约协作。

### 方案 E：AI 自己实现、自己验证、自己宣布完成

拒绝。正式交付必须保留 Verification 和 Review 独立角色及证据门禁。

## Acceptance Criteria

本 ADR 可转 `accepted` 的最低条件：

1. `嵌入式系统专家团-核心参考/` 完成内部评审并转为 `reviewed-baseline`；
2. `expert-group.yaml`、`task-modes.yaml`、`workflow.yaml` 与文档一致；
3. 至少建立 10 个真实嵌入式 Golden Case；
4. P0 核心专家职责没有重叠冲突；
5. 与产品专家团 handoff contract 有最小可用 Schema；
6. 与端侧底座专家团完成第一版 ownership map；
7. 不存在未授权设备写、发布和不可逆动作的默认路径。

## Rollback / Revisit Triggers

出现以下任一情况需重新评审本 ADR：

- 产品专家团正式运行框架发生不兼容的组织级变化；
- WorkBuddy/Codex 集成策略推翻 ADR-001；
- 端侧底座专家团正式职责与本方案大面积冲突；
- 真实试点证明 1+7 组织模型导致高比例错误路由或严重上下文损耗；
- 受控执行网关进入生产，需要重新划分 A3-A7 权限。
