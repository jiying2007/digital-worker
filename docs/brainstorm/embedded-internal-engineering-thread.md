# 嵌入式系统内部 Engineering Thread 头脑风暴

- Status: `brainstorm / non-normative`
- Date: 2026-09-11
- Related: `expert-groups/embedded-system/`
- Related: `docs/adr/ADR-002-embedded-system-expert-team-architecture.md`
- Related: `docs/brainstorm/enterprise-ai-rd-embedded-digital-thread.md`

> 本文讨论“嵌入式系统专家团内部到底怎么串起来”。它不是对现有 1+7 / Workflow / Contract 的替代决策，而是尝试把现有专家角色进一步放到同一条工程数字线程上。后续只有被真实 Pilot 证明有价值的部分，才应提升为正式 Contract / Schema。

## 1. 核心判断

嵌入式内部不能靠“Architecture 专家答完 → BSP 专家再答 → Driver 专家再答”的文本串行方式连接。

更合理的候选模型是：

> **所有专家围绕同一个 Work Item、同一个 System Context、同一份 Decision/Evidence Ledger、同一条 Artifact Lineage 和同一张 Verification Matrix 协作。**

专家是共享工程对象上的不同责任角色，而不是彼此独立的聊天机器人。

## 2. 内部真正需要串起来的不是 Agent，而是 5 条主线

### 2.1 System Context 主线

回答“我们到底在讨论哪一个系统”。

候选最小字段：

```text
product / project
board revision
SoC / MCU
repo set + exact SHA
SDK / kernel / RTOS / toolchain
firmware / image identity
hardware interfaces
active feature flags / config
reference device / test environment
```

Architecture、BSP、MCU、Driver、Debug 都消费同一个 Context Snapshot。

### 2.2 Task / Decision 主线

回答“为什么改、决定了什么、还有什么没决定”。

```text
work_item
 → task-charter
 → routing
 → technical-analysis
 → decision
 → engineering-task-package
 → change
 → verification
 → review
```

每个关键 Decision 应记录：owner、evidence、impact、assumption、unresolved item。

### 2.3 Evidence 主线

回答“这个结论凭什么”。

现有 Evidence-first / Observed-Inferred-Confirmed / Hypothesis Registry 可以继续作为骨架。

建议整个任务只维护一份共享 Evidence Graph，而不是每个专家复制一套证据摘要。

### 2.4 Artifact Lineage 主线

回答“这次修改到底变成了哪个可运行对象”。

```text
repo SHA
 → build/config/toolchain
 → binary hash
 → firmware/image
 → device identity
 → HIL/Test run
 → release candidate
```

这条线连接工程执行、验证和 Release。

### 2.5 Verification Matrix 主线

回答“哪些要求在哪一层被证明”。

```text
acceptance criterion
    ↕
verification layer
    ↕
evidence
    ↕
status / owner
```

避免每个专家说“我这里验证过了”，最后没人知道总体还缺什么。

## 3. 候选四个共享对象

可以把内部串联理解成四个共享对象加现有 Gate。

### A. System Context Snapshot

一个任务开始时冻结关键工程身份，变更后显式更新。

### B. Decision / Evidence Ledger

统一保存 claim、fact state、decision、assumption、evidence、open question。

### C. Change / Artifact Lineage

把 source change、build、binary、device、test 串成可追溯链。

### D. Verification Matrix

把 acceptance criterion 映射到 Host / Cross-build / SIL / Device / HIL / Release。

这四个对象可以先作为 Brainstorm 概念，不建议立即新增四套复杂 Schema；先利用现有 task-charter、technical-analysis、engineering-task-package、delivery-receipt、verification-report 验证是否真的存在信息丢失，再决定升级。

## 4. 1+7 在共享对象上的责任

### Team Lead

不是转发专家答案，而是维护：

- active System Context；
- task graph / stage；
- owner；
- Gate status；
- unresolved dependencies；
- reflow / stop condition。

### Architecture Expert

主要写入：

- system boundary；
- subsystem ownership；
- interface impact；
- resource / timing / dependency；
- architectural decisions。

### Linux/BSP Expert

主要写入：

- boot/kernel/DT/platform dependencies；
- Linux-side resource / driver integration impact；
- platform verification requirements。

### MCU/RTOS Expert

主要写入：

- firmware/startup/interrupt/RTOS/timing/resource impact；
- MCU-side interface assumptions；
- firmware artifact identity / device constraints。

### Driver/Component Expert

主要写入：

- device interface contract；
- component behavior；
- platform abstraction；
- integration changes / compatibility risks。

### Debug/Reliability Expert

主要维护：

- hypothesis registry；
- failure evidence；
- causal chain；
- stress/reliability risk；
- root-cause confidence。

### Verification Expert

主要维护 Verification Matrix：

- criterion；
- layer；
- environment；
- artifact / device identity；
- result / evidence；
- missing coverage。

### Review Governor

不是重新分析一遍全部技术，而是独立检查：

- decision 是否被 evidence 支撑；
- context / artifact identity 是否一致；
- Verification 是否覆盖 acceptance；
- blocker/unverified 是否被隐藏；
- release claim 是否越级。

## 5. 内部协作不应全是串行链，而应是 DAG

很多任务天然并行。

例如 Feature：

```text
             Architecture
             /          \
          BSP          MCU
             \          /
            Driver/Component
                   ↓
              Integration
                   ↓
             Verification
                   ↓
                Review
```

例如 Debug：

```text
Observed Evidence
      ↓
Hypothesis Registry
   ↙      ↓       ↘
BSP      MCU     Driver
   \      ↓       /
    experiments/results
           ↓
       Root Cause
           ↓
          Fix
           ↓
 Verification/Regression
```

Team Lead 管 DAG、依赖和收口，不要求每个角色都完整串行执行。

## 6. “Handoff” 应该传递结构化增量，而不是重新讲背景

当前容易出现的低效模式：

```text
专家 A 分析 2 页
  → 专家 B 重新理解背景
  → 专家 C 再重复一次
```

候选改进：下游默认继承统一 Context，只传递 Delta：

```text
新增事实
新增决定
接口变化
风险变化
需要对方回答的问题
新增 evidence
```

可以降低 context rebuild、遗漏和不同专家对版本理解不一致的问题。

## 7. 内部最重要的 Identity Spine

建议整个工作项至少始终保持三类身份明确。

### Target Identity

```text
product / board / SoC / MCU / device / environment
```

### Source & Artifact Identity

```text
repo SHA / build config / binary hash / firmware / image
```

### Run Identity

```text
work_item / expert-team run / execution / verification / HIL run
```

如果其中一条断掉，后续“通过/失败”都可能失真。

## 8. Feature 场景候选内部主链

```text
Task Brief
 ↓
System Context Freeze
 ↓
Architecture Impact
 ↓
BSP / MCU / Driver 并行影响分析
 ↓
Interface & Dependency Reconciliation
 ↓
Technical Decision
 ↓
Engineering Task Package
 ↓
Engineering Agent Runtime / Engineer
 ↓
Delivery Receipt + Artifact Lineage
 ↓
Verification Matrix Execution
 ↓
Independent Review
 ↓
Knowledge Candidate / Closure
```

其中 Interface & Dependency Reconciliation 可能是目前 1+7 中值得强化的动作，不一定需要新增 Expert，可以先由 Team Lead + Architecture Expert 共同完成。

## 9. Debug 场景候选内部主链

```text
Incident / Reproduction
 ↓
System Context Freeze
 ↓
Evidence Normalization
 ↓
Hypothesis Registry
 ↓
按假设路由 BSP / MCU / Driver / Architecture
 ↓
Experiment Plan
 ↓
Observed Result 回写共享 Evidence
 ↓
Hypothesis supported/rejected/confirmed
 ↓
Root Cause
 ↓
Fix Package
 ↓
Regression / Stress / HIL
 ↓
Review
 ↓
RCA → Knowledge / Golden Case / Skill Candidate
```

Debug 的关键不是专家更多，而是所有人维护同一棵 Hypothesis/Evidence Tree。

## 10. Bring-up 场景候选内部主链

Bring-up 更像依赖图：

```text
Power/Clock/Reset
 ↓
Boot Chain
 ↓
Memory/Storage
 ↓
Kernel/RTOS baseline
 ↓
Core peripherals
 ↓
Driver/components
 ↓
Connectivity/feature
 ↓
Stress/HIL
```

每一步的 output 同时成为下一步 prerequisite 和 Evidence；不是一次性“Bring-up 专家报告”。

## 11. Release 场景候选内部主链

```text
Source baseline
 ↓
Build identity
 ↓
Artifact hash
 ↓
Verification coverage
 ↓
Known risks / waivers
 ↓
Target device / rollout scope
 ↓
Rollback evidence
 ↓
Independent readiness review
```

Release Expert/Review 不应重新发明测试，而是检查前面 Artifact/Evidence Thread 是否闭合。

## 12. 内部可能需要的未来 Contract（仅候选）

以下对象可在 real Pilot 证明有重复需求后再正式化：

1. `system-context-manifest`
2. `interface-impact-map`
3. `decision-ledger`
4. `artifact-lineage`
5. `verification-matrix`
6. `integration-readiness`

不要一次性全部 Schema 化。

## 13. Integration 是当前值得重点思考的空白

现有专家角色覆盖 Architecture、BSP、MCU、Driver、Debug、Verification、Review，但“多子系统分析完成以后，谁负责把接口/依赖重新对齐”值得真实 Pilot 观察。

候选方案：

- 方案 A：Team Lead 负责 integration reconciliation；
- 方案 B：Architecture Expert 承担 system integration；
- 方案 C：未来形成 `system-integration` Skill；
- 方案 D：真实工作量足够大时才新增 Integration Expert。

当前不建议立即增加第 8 个正式专家。

## 14. AI Runtime 如何进入内部链

Engineering Agent Runtime 不应该拿到“所有专家长文”，而应该拿到最小 Context Package：

```text
work item
system context
technical decision
implementation scope
interface constraints
acceptance criteria
allowed/forbidden actions
required verification
relevant evidence refs
```

这样 Codex / Claude / 其他 Runtime 可以替换，而不会承担 Expert Team 的全部推理上下文。

## 15. Knowledge 如何进入内部链

Knowledge 不是单独的“搜索步骤”，而应在 Gate K 与各 stage 按需解析。

候选方式：

- Team Lead 明确 required source class；
- Expert 按任务请求最小知识上下文；
- claim 引用 source/version；
- source 冲突写入 Ledger；
- stale/unknown authority 不能静默升级为事实。

## 16. 内部串联效果应该怎么量化

值得关注的指标不是 Agent 调用次数，而是：

- context rebuild count；
- handoff information loss；
- duplicate analysis；
- stale context incidents；
- interface mismatch discovered late；
- rework caused by cross-domain dependency；
- artifact identity gaps；
- verification coverage gaps；
- incorrect cross-layer PASS；
- root cause lead time。

这些指标能判断“专家团是否真的串起来”，而不是只判断单个专家回答质量。

## 17. 最小可落地版本

不新增平台，先在 3 个 real Pilot 中要求：

1. 每个任务固定一份 System Context；
2. 所有专家引用同一 work_item / run_id；
3. Debug 共用同一 Hypothesis Registry；
4. Execution 必须产生 exact source/artifact identity；
5. Verification 对 acceptance criterion 建一张简单矩阵；
6. Review 检查 Context/Evidence/Artifact/Verification 四条线是否一致；
7. 记录 handoff 重复、信息丢失和 rework。

如果这 7 项明显降低返工，再考虑增加正式 Schema / UI / Context Broker。

## 18. 当前推演结论（非正式）

目前最可能有效的内部骨架不是“更多 Agent”，而是：

```text
One Work Item
+ One System Context
+ One Decision/Evidence Ledger
+ One Artifact Lineage
+ One Verification Matrix
+ Role-based Expert DAG
```

这可能是 1+7 从“专家集合”升级为“数字研发团队”的关键。
