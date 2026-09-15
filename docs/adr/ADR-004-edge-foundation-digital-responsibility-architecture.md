# ADR-004：端侧底座数字责任架构（Edge Foundation Digital Responsibility Architecture）

- Status: accepted
- Date: 2026-09-14
- Accepted: 2026-09-15
- Scope: 研发中心端侧底座数字员工的稳定责任模型、编排边界、执行与可信保障边界，以及 canonical target-only 运行约束
- Runtime state（运行时状态）: canonical-target-only
- Legacy compatibility（旧兼容层）: physically-retired
- Product readiness controls routing（产品成熟度控制路由）: false
- Supersedes: ADR-002 中将“嵌入式系统 1+7”作为目标组织结构的决策；ADR-002 的 Gate / Evidence / Verification / Review / Action Policy 等工程治理原则继续有效
- Related: `docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md`
- Source material: `docs/source-materials/端侧底座专家团创建.docx`
- Canonical machine contract: `domains/edge-foundation/domain.yaml`

## 1. 背景与问题

端侧底座需要同时覆盖结构、硬件、嵌入式软件，并允许未来的 Agent、模型、办公入口、工程 Runtime 与知识 Provider 持续变化。早期嵌入式 1+7 资产对内部专业责任拆分有价值，但如果直接作为端侧底座的长期组织结构，会产生三类问题：

1. **抽象层级错位**：结构、硬件、嵌入式属于同层专业责任域，而 Linux/BSP、MCU/RTOS、Driver、Debug 更适合作为嵌入式专家内部能力域；
2. **组织与 Agent 拓扑耦合**：如果每个能力都固化成 Agent，模型、运行时与上下文策略变化会迫使责任架构重构；
3. **顶层编排绑定具体产品**：WorkBuddy、Codex、ADK 或其它产品都可能变化，不应成为责任架构成立的前提。

因此，本 ADR 冻结**责任边界与可信治理 Contract**，而把具体 Runtime / Provider / Worker 拓扑保持为可替换实现。

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
     └─ 能力域（Capability）
         └─ 原子技能（Skill）
```

横向保留四类稳定平面：

- **责任平面（Responsibility Plane）**：定义谁对什么专业判断负责；
- **编排平面（Orchestration Plane）**：负责路由、状态、门禁、恢复、预算与上下文；
- **执行平面（Execution Plane）**：代码、构建、CI、设备、HIL、脚本、人工与 Agent Runtime；
- **可信保障平面（Assurance Plane）**：Evidence、Verification、Independent Review、Evaluation 与 Release Readiness。

知识与上下文遵循 **Source of Truth stays at source（权威事实保留在原始来源）**：知识系统可以索引、检索、关联和组装上下文，但不得复制出第二套未受控权威事实源。

**Canonical routing 已由 Edge Foundation target runtime 承担。旧 1+7 compatibility tree、静态身份 mapping、shadow routing 与迁移期 switch machinery 已物理退役。** Product readiness 与 routing authority 已解耦；产品三轨 evidence 不会切换、回滚或决定 canonical routing。

## 3. 规范术语：中文主称 + 英文括注

后续人类文档默认优先使用中文；机器 ID、Schema 字段、行业标准缩写可保留英文。

| 英文术语 | 规范中文说法 | 本仓语义 |
|---|---|---|
| Domain | 领域 / 责任域 | 完整业务或研发责任边界，例如“端侧底座领域” |
| Role | 角色 / 职责角色 | 流程责任，不天然等于专家或 Agent |
| Expert | 专家 / 专业责任主体 | 稳定专业责任接口，例如“嵌入式系统专家” |
| Capability | 能力域 / 专业能力簇 | 专家内部一组稳定专业能力 |
| Skill | 技能 / 原子技能 | 可复用、可调用、可校验的最小专业能力 |
| Orchestration | 编排 | 任务路由、状态、门禁、恢复、预算和上下文组织 |
| Control Plane | 控制平面 | 负责规则、状态和治理，不直接等同于执行者 |
| Responsibility Plane | 责任平面 | 定义谁对什么专业判断负责 |
| Execution Plane | 执行平面 | 实际修改、构建、测试、设备动作等 |
| Assurance Plane | 可信保障平面 | 通过证据、验证、审查和评测证明结果可信 |
| Runtime | 运行时 | 承载 Agent/模型/工具执行的具体环境 |
| Provider | 提供方 / 能力提供方 | WorkBuddy、Codex、知识平台等可替换产品或服务 |
| Adapter | 适配器 | 把具体 Provider 映射到稳定 Contract 的实现层 |
| Contract | 契约 | 稳定输入、输出、责任、权限和失败语义 |
| Workflow | 工作流 | 完成一类任务的阶段和状态路径 |
| Gate | 门禁 | 进入下一阶段前必须满足的约束 |
| Evidence | 证据 | 支持 Claim / Decision / Verification 的可追溯事实 |
| Claim | 主张 | 需要证据支持的技术陈述 |
| Hypothesis | 假设 | 待验证的可能解释 |
| Finding | 发现项 | 审查或分析中识别出的事实、缺陷或风险 |
| Decision | 决策 | 基于约束和证据形成的正式选择 |
| Verification | 验证 | 证明实现或结论达到哪一证据层级 |
| Review | 审查 / 独立审查 | 独立判断证据充分性、风险和放行条件 |
| Closure | 收口 / 闭环 | 任务、证据、决策、交付与知识沉淀完成闭合 |
| Pilot | 试点 | 用真实或受控任务验证体系能力 |
| Product readiness | 产品成熟度 / 产品就绪度 | 由真实产品 Pilot evidence 决定，不等于路由权威 |
| Productionization | 生产化 | 从试点能力转为稳定生产运行的治理过程 |
| Progressive Disclosure | 渐进式披露 / 按需加载 | 只加载当前任务需要的能力、Skill 和上下文 |
| Source of Truth | 权威事实源 | 事实的 canonical 来源；本仓遵循 stays-at-source |
| Fail-closed | 保守阻断 / 失败即阻断 | 缺关键前置条件时不得猜测性继续或错误 PASS |

## 4. 稳定抽象模型

整个 `digital-worker` 的专业责任统一使用：

```text
领域（Domain）
  ↓
专家（Expert）
  ↓
能力域（Capability）
  ↓
技能（Skill）
```

横向存在：Role、Orchestration、Runtime、Assurance、Knowledge、Evidence、Identity 与 Audit。

### 4.1 Expert 不等于 Agent

`Expert` 是稳定专业责任契约，不规定运行时必须有一个同名 Agent。合法实现包括单会话、多 Worker、人工 + Agent 协同，或 Runtime 更换但 Expert Contract 不变。

### 4.2 Capability 默认不等于 Agent

Capability 定义“会什么、需要什么知识、有哪些 Skill、输出什么专业结果”，不规定必须启动独立 Agent。是否拆 Worker 由 Runtime 按复杂度、上下文、成本和并行性决定。

### 4.3 Coordinator 不等于第四个技术专家

端侧协调角色负责 Intake、Triage、路由、跨域综合、状态和 Closure；它是 Role，不是 Structure / Hardware / Embedded 之外的第四个 Domain Expert。

## 5. 端侧底座目标责任模型

当前稳定 Domain Expert 基线为三个：

1. **结构专家（Structure Expert）**：机构、装配、公差、结构热、防护、冲击/跌落、机械可靠性等；
2. **硬件专家（Hardware Expert）**：原理图、PCB、电源、器件、SI/PI、EMC、Bring-up 与硬件故障等；
3. **嵌入式系统专家（Embedded System Expert）**：系统架构、Linux/BSP、MCU/RTOS、驱动与组件、系统调试、OTA、功耗/性能等。

“三专家”是当前稳定基线，不是永久硬编码。只有当某个 Capability 长期具备独立入口、独立生命周期、独立交付物、独立知识体系、大量稳定 Skill 和明确跨 Expert 接口时，才通过新的 ADR 评估是否晋升 Expert。

## 6. 嵌入式系统专家内部能力模型

当前 canonical Capability 基线为：

- 嵌入式架构（Embedded Architecture）；
- Linux / BSP；
- MCU / 裸机 / RTOS；
- 驱动与组件（Driver / Component）；
- 调试与可靠性（Debug / Reliability）。

后续由真实任务证据驱动扩展 Boot/OTA/Recovery、Power/Performance、Connectivity、Motor Control、Audio、Security/Safety、Edge AI 等。默认先扩 Capability / Skill，不扩正式 Expert。

## 7. 四个逻辑平面

### 7.1 责任平面（Responsibility Plane）

回答“谁对什么专业判断负责”。核心结构是 Domain → Expert → Capability → Skill。

### 7.2 编排平面（Orchestration Plane）

回答“任务怎么走”。负责 Domain Routing、状态、Gate、Context、Budget、Retry、Resume、Escalation 与权限编排。顶层只依赖稳定 Contract，不绑定 WorkBuddy 或其它具体产品。

### 7.3 执行平面（Execution Plane）

回答“谁真正执行动作”。可由 Engineer、Codex、ADK、IDE Agent、脚本、CI、HIL、设备或未来其它 Runtime 承担。

### 7.4 可信保障平面（Assurance Plane）

回答“如何证明结果可信”。包括 Evidence、Verification、Independent Review、Policy、Evaluation 和 Release Readiness。Engineering、Verification、Review/Release authority 必须保持分离。

## 8. 端侧任务运行模式

冻结四种高层工作语义：

- `single_domain`：单领域任务；
- `multi_domain`：明确跨两个及以上 Domain Expert；
- `diagnostic`：根因未知，以 Hypothesis / Evidence 驱动动态扩展能力；
- `review`：设计/方案/发布就绪审查，不默认进入工程实施。

具体 workflow、Agent/Worker 数量、并行/串行拓扑继续由 Runtime 按任务决定；活动执行面必须服从 `domains/edge-foundation/runtime/**` 与 `domains/edge-foundation/routing.yaml`。

## 9. 跨专家协作：Claim / Evidence 驱动

跨 Structure / Hardware / Embedded 协同禁止依赖无边界的“多 Agent 会议”。共享工作对象优先采用：

```text
Claim → Hypothesis → Evidence → Finding → Decision → Verification → Closure
```

事实状态使用 Observed / Inferred / Confirmed；缺关键证据时 fail-closed。

## 10. Engineering / Verification / Review 分离

以下边界是 P0 不变量：

```text
专业判断 ≠ 工程实施
工程实施完成 ≠ Verification PASS
Verification PASS ≠ Review / Release 已批准
```

Verification 与 Review 可以由不同 Agent、CI/HIL、人工或混合方式实现，但 Contract、证据要求与责任独立性不能因为 Runtime 变化而消失。A6/A7 等高风险动作继续服从人工 Gate 与 Action Policy。

## 11. 旧 1+7 资产的终态

早期 1+7 模型中的成熟知识、专业方法和 Skill 已吸收到 Edge Foundation 的 Embedded System Expert / Capability / Skill 体系；迁移本身已经结束。

终态约束为：

- 旧 compatibility tree 不属于活动执行面；
- 静态身份 mapping、shadow routing 与迁移 switch machinery 不属于活动执行面；
- 活动 routing、Runtime、Skill ownership、Pilot 与 Knowledge Registry 均由 `domains/edge-foundation/**` 承担；
- CI 必须持续阻止旧活动路径和迁移期语义回归；
- 历史迁移过程由 Git history 和历史 ADR 上下文保留，不维护第二套可执行 rollback architecture；
- Product readiness 不得以任何方式把 routing authority 回退到旧模型。

如果 canonical runtime 出现缺陷，应修复当前 target contract/runtime 或通过正常代码版本回退处理，而不是恢复已退役的第二套责任架构。

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
- 当前核心 Domain Expert 为 Structure / Hardware / Embedded；
- Coordinator 是 Role，不是 Domain Expert；
- Expert 是责任 Contract，不等于 Agent；
- Capability 是专业能力簇，不默认等于 Agent；
- Skill 是原子能力；
- Orchestration 与具体 WorkBuddy / ADK / Codex 解耦；
- Runtime 与 Responsibility 解耦；
- Engineering / Verification / Review 责任独立；
- Source of Truth stays at source；
- Canonical routing authority 属于 Edge Foundation target runtime；
- Product readiness 不控制 routing authority；
- 旧 compatibility / shadow / migration switch 不再属于活动架构。

### 13.2 暂不冻结

- WorkBuddy 或其它产品是否作为顶层编排实现；
- Agent / Worker 数量；
- 并行或串行拓扑；
- 具体模型和 Runtime；
- 具体 Workflow / Gate 数量；
- Verification / Review 的具体 Agent 或平台实现；
- Memory backend、Context budget、Knowledge Provider 与其它 Provider 选择。

这些 `not_frozen` 项是可替换实现空间，不代表责任架构未闭环。

## 14. Acceptance Evidence（验收证据）

本 ADR 已满足并持续要求以下验收条件：

1. Edge Foundation Domain Contract、三 Expert 责任模型和 Embedded Capability 已进入机器可校验资产；
2. routing、Runtime、Skill、Gate、Golden Case、Assurance、Pilot、Schema、Knowledge Registry 已形成 canonical target assets；
3. 旧 compatibility、静态 mapping、shadow 与 switch machinery 已从活动执行面物理退役；
4. CI 同时验证 canonical architecture、canonical routing、target assets、zero-live legacy references 与 terminal semantic consistency；
5. Product readiness evaluator 只接收 canonical real Pilot evidence，synthetic evidence 不计入产品成熟度；
6. Product readiness 与 routing authority 机器级解耦；
7. 至少一条真实 Feature Pilot 已在 target-only runtime 重放并形成 eligible receipt；
8. Runtime / Provider 继续保持可替换，不反向污染稳定责任 Contract。

因此，本 ADR 的**架构验收已经完成**。Debug 与 Review/Release 的真实证据仍属于 Product readiness，不是本 ADR accepted 状态的前置条件。

## 15. 最终原则

> **领域定系统边界，专家承担专业责任，能力域组织专业能力，技能提供原子能力；编排负责怎么组织任务，运行时负责怎么执行，可信保障独立证明结果。**

任何具体 Agent 产品、模型、知识平台或工作入口都只能实现这些 Contract，不能反过来定义组织责任架构；Product readiness 也不能反向改变已经接受的 canonical routing authority。
