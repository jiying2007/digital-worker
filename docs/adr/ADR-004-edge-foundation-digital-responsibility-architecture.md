# ADR-004：端侧底座数字责任架构（Edge Foundation Digital Responsibility Architecture）

- Status: proposed-for-acceptance
- Date: 2026-09-14
- Scope: 研发中心端侧底座数字员工的稳定责任模型、编排边界、嵌入式 1+7 兼容迁移与治理原则
- Supersedes: ADR-002 中将“嵌入式系统 1+7”作为目标组织结构的决策；ADR-002 的 Gate / Evidence / Verification / Review / Action Policy 等工程治理原则继续有效
- Related: `docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md`
- Source material: `docs/source-materials/端侧底座专家团创建.docx`

## 1. 背景与问题

当前 `expert-groups/embedded-system/` 已经形成较完整的 1 名主理人 + 7 个专业角色、23 个 P0 Skill、Gate、Evidence、Verification、Review、Pilot 与工程交接契约。这些资产对嵌入式软件内部专业责任拆分很有价值，但把它们直接提升为“端侧底座”的目标组织结构会产生三类问题：

1. **抽象层级错位**：结构、硬件、嵌入式属于同一层专业责任域，而 Linux/BSP、MCU/RTOS、Driver、Debug 更适合作为嵌入式专家内部能力域；
2. **组织与 Agent 拓扑耦合**：若把每个专业能力都固化成 Agent，模型、运行时和上下文策略变化会迫使组织架构重构；
3. **顶层编排绑定具体产品**：WorkBuddy、Codex、ADK 或其他编排/执行产品都可能变化，不应成为责任架构成立的前提。

因此需要把稳定的**责任边界**与可演进的**运行实现**分离。

## 2. 决策摘要

端侧底座采用以下稳定责任模型：

```text
端侧底座领域（Edge Foundation Domain）
│
├─ 端侧协调角色（Edge Coordination Role）
│
├─ 结构专家（Structure Expert）
├─ 硬件专家（Hardware Expert）
└─ 嵌入式系统专家（Embedded System Expert）
     └─ 能力域（Capabilities）
         └─ 原子技能（Skills）
```

同时横向保留：

- 编排平面（Orchestration Plane）：路由、状态、门禁、恢复、预算、上下文；
- 执行平面（Execution Plane）：代码、构建、CI、设备、HIL、脚本、人工和 Agent Runtime；
- 可信保障平面（Assurance Plane）：证据、验证、独立审查、策略、评测和发布就绪；
- 知识与上下文能力：Source of Truth stays at source，知识系统负责索引、检索、关联与上下文组装，不复制第二套权威事实源。

## 3. 规范术语：中文主称 + 英文括注

后续人类文档默认优先使用中文；机器 ID、Schema 字段、行业标准缩写可保留英文。

|英文术语|规范中文说法|本仓语义|
|---|---|---|
|Domain|领域 / 责任域|完整业务或研发责任边界，例如“端侧底座领域”|
|Role|角色 / 职责角色|流程责任，不天然等于专家或 Agent，例如“协调角色”|
|Expert|专家 / 专业责任主体|稳定专业责任接口，例如“嵌入式系统专家”|
|Capability|能力域 / 专业能力簇|专家内部一组稳定专业能力，例如“Linux/BSP 能力域”|
|Skill|技能 / 原子技能|可复用、可调用、可校验的最小专业能力|
|Orchestration|编排|任务路由、状态、门禁、恢复、预算和上下文组织|
|Control Plane|控制平面|负责规则、状态和治理，不直接等同于执行者|
|Responsibility Plane|责任平面|定义谁对什么专业判断负责|
|Execution Plane|执行平面|实际修改、构建、测试、设备动作等|
|Assurance Plane|可信保障平面|通过证据、验证、审查和评测证明结果可信|
|Runtime|运行时|承载 Agent/模型/工具执行的具体环境|
|Provider|提供方 / 能力提供方|WorkBuddy、Codex、知识平台等可替换产品或服务|
|Adapter|适配器|把具体提供方映射到稳定 Contract 的兼容层|
|Contract|契约|稳定输入、输出、责任、权限和失败语义|
|Workflow|工作流|完成一类任务的阶段和状态路径|
|Gate|门禁|进入下一阶段前必须满足的约束|
|Evidence|证据|支持 Claim / Decision / Verification 的可追溯事实|
|Claim|主张|需要证据支持的技术陈述|
|Hypothesis|假设|待验证的可能解释|
|Finding|发现项|审查或分析中识别出的事实、缺陷或风险|
|Decision|决策|基于约束和证据形成的正式选择|
|Verification|验证|证明实现或结论达到哪一证据层级|
|Review|审查 / 独立审查|独立判断证据充分性、风险和放行条件|
|Closure|收口 / 闭环|任务、证据、决策、交付与知识沉淀完成闭合|
|Pilot|试点|用真实或受控任务验证体系能力|
|Productionization|生产化|从试点能力转为稳定生产运行的治理过程|
|Progressive Disclosure|渐进式披露 / 按需加载|只加载当前任务需要的能力、Skill 和上下文|
|Source of Truth|权威事实源|事实的 canonical 来源；本仓遵循 stays-at-source|
|Fail-closed|保守阻断 / 失败即阻断|缺关键前置条件时不得猜测性继续或错误 PASS|

## 4. 稳定抽象模型

整个 `digital-worker` 的专业责任建议统一使用：

```text
领域（Domain）
  ↓
专家（Expert）
  ↓
能力域（Capability）
  ↓
技能（Skill）
```

横向存在：

```text
角色（Role）
编排（Orchestration）
运行时（Runtime）
可信保障（Assurance）
知识 / 证据 / 身份 / 审计
```

### 4.1 Expert 不等于 Agent

`Expert` 是稳定专业责任契约，不规定运行时必须有一个同名 Agent。

合法实现包括：

- 一个 Expert 由一个模型会话承担；
- 一个 Expert 动态拉起多个临时 Worker，再统一综合；
- 一个 Expert 由人工 + Agent 协同承担；
- Runtime 变化但 Expert Contract 不变。

### 4.2 Capability 默认不等于 Agent

Capability 定义“会什么、需要什么知识、有哪些 Skill、输出什么专业结果”，不规定必须启动独立 Agent。是否拆 Worker 由运行时按复杂度、上下文、成本和并行性决定。

### 4.3 Coordinator 不等于第四个技术专家

端侧协调角色负责 Intake、Triage、路由、跨域综合、状态和 Closure；它是 Role，不是 Structure / Hardware / Embedded 之外的第四个 Domain Expert。

## 5. 端侧底座目标责任模型

当前稳定 Domain Expert 基线为三个：

1. **结构专家（Structure Expert）**：机构、装配、公差、结构热、防护、冲击/跌落、机械可靠性等；
2. **硬件专家（Hardware Expert）**：原理图、PCB、电源、器件、SI/PI、EMC、Bring-up 与硬件故障等；
3. **嵌入式系统专家（Embedded System Expert）**：系统架构、Linux/BSP、MCU/RTOS、驱动与组件、系统调试、OTA、功耗/性能等。

“三专家”是当前基线，不是永久硬编码。当一个 Capability 长期具备独立入口、独立生命周期、独立交付物、独立知识体系、大量 Skills 和明确跨 Expert 接口时，可通过 ADR 晋升为新的 Domain Expert。

## 6. 嵌入式专家内部能力模型

第一阶段将现有 1+7 中成熟专业角色重新解释为 Embedded Expert 的能力资产：

- 嵌入式架构（Embedded Architecture）；
- Linux / BSP；
- MCU / 裸机 / RTOS；
- 驱动与组件（Driver / Component）；
- 调试与可靠性（Debug / Reliability）。

后续由真实 Pilot 驱动扩展：Boot/OTA/Recovery、Power/Performance、Connectivity、Motor Control、Audio、Security/Safety、Edge AI 等。默认先扩 Capability / Skill，不扩正式 Expert。

## 7. 四个逻辑平面

### 7.1 责任平面（Responsibility Plane）

回答“谁对什么专业判断负责”。核心结构是 Domain → Expert → Capability → Skill。

### 7.2 编排平面（Orchestration Plane）

回答“任务怎么走”。负责 Domain Routing、状态、Gate、Context、Budget、Retry、Resume、Escalation 与权限编排。顶层只依赖稳定 Contract，不绑定 WorkBuddy 或其他具体产品。

### 7.3 执行平面（Execution Plane）

回答“谁真正执行动作”。可由 Engineer、Codex、ADK、IDE Agent、脚本、CI、HIL、设备或其他 Runtime 承担。

### 7.4 可信保障平面（Assurance Plane）

回答“如何证明结果可信”。包括 Evidence、Verification、Independent Review、Policy、Evaluation 和 Release Readiness。它必须与工程实施责任保持独立。

## 8. 端侧任务基本运行模式

第一阶段只冻结四种高层语义，避免过早把工作流数量写死：

- `single_domain`：单领域任务；
- `multi_domain`：明确跨两个及以上 Domain Expert；
- `diagnostic`：根因未知，以 Hypothesis / Evidence 驱动动态拉专家；
- `review`：只做设计/方案/发布就绪审查，不默认进入工程实施。

现有嵌入式 14 Task / 7 Mode 在兼容期继续运行；是否收敛到以上四种高层语义，由真实 Pilot 和迁移 Evaluation 决定，不做大爆炸替换。

## 9. 跨专家协作：Claim / Evidence 驱动

跨 Structure / Hardware / Embedded 协同禁止依赖无边界的“多 Agent 会议”。共享工作对象优先采用：

```text
Claim → Hypothesis → Evidence → Finding → Decision → Verification → Closure
```

事实状态继续沿用：Observed / Inferred / Confirmed；缺关键证据时 fail-closed。

## 10. Engineering / Verification / Review 分离

以下责任边界继续作为 P0 约束：

```text
专业判断 ≠ 工程实施
工程实施完成 ≠ Verification PASS
Verification PASS ≠ Review / Release 已批准
```

Verification 与 Review 可由不同 Agent、CI/HIL、人工或混合方式实现，但 Contract 与独立性不能因为 Runtime 变化而消失。

## 11. 旧 1+7 兼容迁移

当前 `expert-groups/embedded-system/` 在迁移期间保留为 **legacy compatibility surface（旧版兼容表面）**，不再代表目标组织层级。

语义映射：

- `embedded-system-team-lead` → 端侧协调职责 + 嵌入式能力路由职责；
- `embedded-architecture-expert` → `embedded.architecture` Capability；
- `linux-bsp-expert` → `embedded.linux-bsp` Capability；
- `mcu-rtos-expert` → `embedded.mcu-rtos` Capability；
- `driver-component-expert` → `embedded.driver-component` Capability；
- `debug-reliability-expert` → `embedded.debug-reliability` Capability；
- `verification-expert` → Assurance / Verification responsibility + embedded verification methods；
- `embedded-review-governor` → Assurance / Review responsibility + embedded review criteria。

迁移顺序固定为：

```text
新责任模型
→ compatibility mapping
→ 双轨 validation / evaluation
→ canonical routing 切换
→ 旧身份 deprecated
→ 真实 Pilot 通过后再删除旧身份
```

禁止直接删除 1+7 造成现有 Pilot、Skill owner、Task routing、Schema 或 Golden Case 大面积失效。

## 12. Capability 晋升 Expert 的门槛

Capability 只有长期同时满足大部分以下条件，才进入晋升评审：

1. 独立责任边界；
2. 独立任务入口；
3. 独立生命周期；
4. 独立核心交付物；
5. 独立知识体系；
6. 大量稳定 Skills；
7. 长期被直接路由；
8. 与其他 Expert 有明确 I/O Contract。

## 13. 冻结项与继续实验项

### 13.1 本 ADR 冻结

- Edge Foundation 是 Domain；
- 当前核心 Domain Experts 为 Structure / Hardware / Embedded；
- Coordinator 是 Role，不是 Domain Expert；
- Expert 是责任 Contract，不等于 Agent；
- Capability 是专业能力簇，不默认等于 Agent；
- Skill 是原子能力；
- Orchestration 与具体 WorkBuddy / ADK / Codex 解耦；
- Runtime 与 Responsibility 解耦；
- Engineering / Verification / Review 责任独立；
- Source of Truth stays at source；
- 上层 Contract 不暴露全部底层 Skills。

### 13.2 暂不冻结

- WorkBuddy 是否作为顶层编排实现；
- Agent / Worker 数量；
- 并行或串行拓扑；
- 具体模型和 Runtime；
- 具体 Workflow / Gate 数量；
- Verification / Review 的具体 Agent 或平台实现；
- Memory backend、Context budget 和 Provider 选择。

## 14. Acceptance Criteria

本 ADR 转 `accepted` 至少需要：

1. 端侧底座 Domain Contract 和三 Expert 责任模型进入机器可校验资产；
2. 旧 1+7 完成 8/8 显式兼容映射，无孤儿身份；
3. 新 validator 能 fail-closed 检查 Coordinator ≠ Expert、三 Expert 基线、Runtime 不冻结、Assurance 独立；
4. 现有 `validate_embedded_assets.py` 继续 PASS，证明迁移首阶段未破坏旧机器契约；
5. CI 同时执行旧嵌入式 validator 和新端侧架构 validator；
6. 至少一个真实或受控 Pilot 证明新责任语义可以承接旧嵌入式任务；
7. canonical routing 切换必须另行评审，不在本 ADR 首阶段直接完成。

## 15. 最终原则

> **领域定系统边界，专家承担专业责任，能力域组织专业能力，技能提供原子能力；编排负责怎么组织任务，运行时负责怎么执行，可信保障独立证明结果。**

任何具体 Agent 产品、模型或工作入口都只能实现这些 Contract，不能反过来定义组织责任架构。
