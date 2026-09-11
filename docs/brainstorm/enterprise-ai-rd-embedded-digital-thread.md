# 企业—研发—嵌入式 AI Digital Thread 头脑风暴

- Status: brainstorm / non-normative
- Date: 2026-09-11
- Scope: 企业经营、产品研发、嵌入式系统上下游、AI 协作与知识学习闭环
- Related: `研发中心AI数字员工研发流程规划.md`
- Related: `docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md`

> 本文只归档当前阶段有价值的思路、候选模型和待验证方向，不代表已经拍板。正式决策仍需进入 ADR / Contract / Schema / Governance。

## 1. 核心观察

AI 不应被设计成企业现有工具链之外的独立聊天层。更有价值的方向是：

> 把企业经营目标、产品需求、工程实现、验证、发布、生产、现场问题与知识学习串成一条可追溯数字线程，AI 作为跨阶段协作、检索、推理、执行和审查能力嵌入其中。

因此长期重点可能不是“统一使用哪个 AI 产品”，而是建立稳定的：

- 对象身份；
- Contract；
- Evidence；
- Authority；
- Permission；
- Approval；
- Audit；
- Evaluation。

Provider 可以替换，但数字线程上的语义和责任不能漂移。

---

## 2. 一条 Enterprise Engineering Digital Thread

候选主线：

```text
企业战略 / 经营目标
        ↓
市场 / 用户 / 客诉
        ↓
产品规划 / 产品定义
        ↓
系统需求 / 技术可行性
        ↓
硬件 / 嵌入式 / App / Cloud / 算法
        ↓
集成 / 验证 / HIL
        ↓
Release / 量产 / MES
        ↓
设备运行 / OTA / 售后
        ↓
质量问题 / RCA / 数据
        └──────────────→ 回到产品、验证和经营
```

关键不是所有系统合并，而是同一业务对象在不同阶段拥有稳定 identity，并且关系可追溯。

### 2.1 候选核心对象

```text
product_id
requirement_id
work_item_id
technical_decision_id
hardware_revision
repo / commit
build_id
artifact_hash
firmware_version
device_id / serial_number
test_run_id / hil_run_id
release_id
production_batch_id
field_incident_id
rca_id
knowledge_id
```

### 2.2 候选关系图

```text
requirement → implemented_by → commit
commit → built_as → artifact
artifact → deployed_to → device
device → verified_by → hil_run
artifact → released_as → release
device → produced_in → production_batch
incident → affects → device / release / batch
incident → resolved_by → commit
rca → creates → knowledge / rule / golden_case
```

如果这些关系长期可追溯，AI 可以从“读文档回答问题”升级为“基于真实企业状态进行影响分析、追溯和决策辅助”。

---

## 3. 三个闭环

### 3.1 Business Loop：为什么做

```text
经营目标
 → 市场机会
 → 用户反馈
 → 产品需求
 → Priority
 → Investment
```

AI 候选能力：

- 市场/用户/客诉聚合；
- 需求主题聚类；
- 产品需求草稿；
- Roadmap 冲突分析；
- 风险/依赖汇总；
- 经营目标与项目状态关联。

边界：AI 可以组织证据和候选判断，但“做不做、何时做、投入多少”仍是人类经营/产品责任。

### 3.2 Engineering Loop：怎么做、怎么证明

```text
Product Requirement
       ↓
System Requirement
       ↓
Technical Review
       ↓
Architecture
       ↓
Engineering Task
       ↓
Implementation
       ↓
Verification
       ↓
Release
```

现有可复用基础：

- `task-brief`
- `technical-review-request`
- `embedded-feasibility-review`
- `engineering-task-package`
- `delivery-receipt`
- `verification-report`
- `review-report`
- Evidence / Gate / Action Policy

这套模型未来可能扩展到硬件、App、Cloud、算法等团队。

### 3.3 Learning Loop：公司是否越来越聪明

```text
项目
 ↓
实施
 ↓
测试
 ↓
失败
 ↓
现场问题
 ↓
RCA
 ↓
方法 / 规则 / Case / Checklist
 ↓
下一个项目
```

一个更强的能力成长链可能是：

```text
Evidence
  ↓
RCA
  ↓
Reusable Skill
  ↓
Golden Case
  ↓
Design Rule
  ↓
Verification Rule
```

长期价值可能不只来自“多写代码”，而来自减少重复踩坑和重复分析。

---

## 4. 嵌入式系统在企业研发中的位置

嵌入式不应被视为孤立软件团队，更像系统集成中枢之一。

```text
            Product
               ↓
        System Requirement
               ↓
       System Architecture
          ↙          ↘
     Hardware      Embedded
       ↕              ↕
 Mechanical        Algorithm
       ↘              ↙
          Integration
```

因此嵌入式专家团除了 Linux / MCU / Driver 专业能力，还需要稳定的跨团队 Contract。

---

## 5. Product → Embedded

产品侧不应只给“实现这个功能”，更合理的是结构化技术评审输入：

```text
目标用户 / 场景
产品行为
性能目标
成本目标
功耗目标
安全目标
发布时间
已知约束
验收意图
```

嵌入式返回：

```text
可行性
平台影响
CPU / RAM / Flash
功耗
实时性
启动时间
接口影响
驱动影响
风险
验证策略
硬件依赖
开放问题
```

现有 `technical-review-request → embedded-feasibility-review` 可以视为第一版跨团队数字线程节点。

---

## 6. Hardware ↔ Embedded

这一条可能是后续高价值方向。

候选机器可读对象：

```text
board-manifest
hardware-interface-contract
schematic-reference
pin-resource-map
power-domain-map
clock-resource-map
device-bom-capability
hardware-change-notice
measurement-evidence
```

例如 Wi-Fi 芯片替换，不应只停留在聊天通知，而应自动触发 Impact Analysis：

```text
Hardware Change
  ↓
GPIO 是否变化
Power sequence 是否变化
Driver 是否变化
Firmware 是否变化
RF / Certification 是否变化
Factory Test 是否变化
OTA / compatibility 是否变化
```

AI 很适合辅助这种跨域影响分析，但具体硬件事实必须来自权威设计/测量来源。

---

## 7. Embedded 内部协作链

```text
Embedded Architecture
        ↓
 ┌──────┼────────┐
Linux   MCU     Components
/BSP   /RTOS    /Driver
 └──────┼────────┘
        ↓
Integration
        ↓
Debug / Reliability
        ↓
Verification
        ↓
Review / Release
```

候选稳定原则：

- 同一个 task；
- 同一个 system context；
- 同一个 evidence graph；
- 同一个 gate ledger；
- 专业专家不各自独立“答题”；
- Team Lead 负责上下文和 Gate 编排，不代替专业结论。

现有 1+7 专家团可以继续作为这一层的实现基础。

---

## 8. Embedded → Verification → Release

“代码 merge”不应等于嵌入式交付完成。

候选链：

```text
Source
 ↓
Build
 ↓
Binary
 ↓
Firmware identity
 ↓
Device deployment
 ↓
HIL
 ↓
Release
```

应该持续保留 identity：

```text
Git SHA
→ Build ID
→ Binary SHA256
→ Firmware Version
→ Device SN
→ HIL Run ID
→ Release ID
```

这类 identity 是 AI 做可信追溯的基础。

---

## 9. Embedded → Manufacturing / MES

未来可以考虑把生产事实纳入同一条数字线程：

```text
生产烧录版本
Bootloader version
Calibration version
Factory config
Device SN / MAC
Hardware revision
供应商批次
产测结果
```

现场问题后可以沿链追溯：

```text
Field Device
 ↓
SN
 ↓
Production Batch
 ↓
HW Revision
 ↓
Component Vendor / Lot
 ↓
Firmware
 ↓
Calibration
 ↓
Factory Test / HIL baseline
```

这可能对批次问题、供应商问题、固件问题区分非常有价值。

---

## 10. Field / After-sales → Embedded

下游应该反向进入研发：

```text
Telemetry / Customer Ticket / RMA / Crash / OTA Failure
                    ↓
              Incident Triage
                    ↓
                   RCA
                    ↓
        Affected Version / HW / Batch
                    ↓
                   Fix
                    ↓
                Regression
                    ↓
                Knowledge
```

再反馈到：

- Product；
- Design Rule；
- Supplier；
- Manufacturing；
- Verification；
- Skill / Golden Case。

这是真正的企业学习闭环。

---

## 11. AI Operating Layer 的候选形态

不建议建设单一“超级 Agent”。可以拆成不同 AI 能力域：

```text
                 AI R&D Operating Layer

Business AI        Engineering AI       Knowledge AI
    │                    │                   │
市场/产品          Expert Teams          Knowledge Gateway
规划/项目          Engineering Agents    Context Broker
经营分析           Review / Debug        RCA / Case Mining
    │                    │                   │
    └────────────────────┼───────────────────┘
                         │
                  Enterprise Contracts
                         │
       Work Item / Evidence / Identity / Audit
```

Provider-neutral 原则仍适用：具体 Runtime / Provider 可以变化，但 Contract / Evidence / Permission / Audit 尽量稳定。

---

## 12. digital-worker 的长期定位候选

当前可继续讨论是否将 `digital-worker` 从“数字员工项目”逐步理解成：

> **Enterprise AI Operating Model / 企业 AI 协作与研发操作模型**

它治理的不只是 Agent，而是：

```text
人
+
AI
+
流程
+
知识
+
工具
+
证据
+
权限
+
责任
```

这只是方向性命名，不是当前正式结论。

---

## 13. 嵌入式上下游可优先考虑的 6 类 Contract

1. **Product → Embedded**
   - Technical feasibility / product requirement handoff

2. **Hardware → Embedded**
   - Board / schematic / interface / hardware change

3. **Embedded → Verification**
   - Build / firmware / required verification

4. **Embedded → Manufacturing**
   - Release / factory image / calibration / production config

5. **Field → Embedded**
   - Incident / device identity / logs / reproduction

6. **Embedded → Enterprise Knowledge**
   - RCA / reusable rule / case / runbook / skill candidate

这 6 类 Contract 是否都需要机器 Schema，应该由真实跨团队流程和 Pilot 逐步证明，不宜一次全部实现。

---

## 14. 候选最小 Enterprise Engineering Object Graph

如果未来要进一步推进 Digital Thread，可以先从最小对象图开始：

```text
Product
Requirement
Work Item
Technical Decision
Hardware Revision
Repo / Commit
Build
Artifact
Device
Verification Run
Release
Production Batch
Field Incident
RCA
Knowledge
```

先定义对象 identity、owner、authority 和关系，再讨论具体存储图数据库、搜索平台或 Agent 平台。

避免反过来先选“企业知识图谱产品”再强行映射业务。

---

## 15. 与当前已确定架构的关系

与 ADR-003 一致的思路：

- Provider 可替换，Contract 稳定；
- Source of Truth stays at source；
- Expert 与 Engineering Agent Runtime 解耦；
- Knowledge Source 与 Knowledge Provider 分离；
- Action / Evidence / Audit 不依赖单一 Agent 品牌。

本文新增但尚未正式决定的重点主要是：

- Enterprise Engineering Digital Thread；
- Business / Engineering / Learning 三闭环；
- 企业对象图；
- Hardware / Manufacturing / Field 的更完整上下游 Contract；
- `digital-worker` 是否长期演进成 Enterprise AI Operating Model。

---

## 16. 值得后续验证的问题

- 企业是否已有稳定的 product / requirement / work item / release ID，可以复用而非重建？
- 硬件 revision、BOM、生产批次、固件 identity 目前分别保存在哪里？
- MES / HIL / Artifact Store / 售后系统是否提供稳定 API？
- 哪些跨部门交接目前最依赖口头、聊天或 Excel？
- 哪些重复 RCA 最适合先形成 Golden Case / Design Rule？
- AI 是否应该直接访问 MES / 生产数据，还是通过只读 Evidence Gateway？
- Hardware Change Notice 是否值得成为第一批新 Contract？
- Field Incident 是否可以成为真实 Digital Thread PoC 的入口？
- 是否需要统一 enterprise object ID registry，还是只做跨系统映射表？
- 什么时候值得建设 Context Broker / Knowledge Graph / Digital Thread service？

---

## 17. 建议的推进顺序（仅供参考）

1. 先做跨系统 Source / Object Inventory；
2. 找一个真实产品建立最小对象追溯图；
3. 优先打通 Product → Embedded、Embedded → Verification；
4. 再选一个 Hardware Change 或 Field Incident 做跨团队 Pilot；
5. 从真实 Pilot 中决定是否需要新的 Contract / Schema；
6. 最后再判断是否值得建设统一 Digital Thread service / graph / Context Broker。

不要因为本文提出了完整愿景，就立即建设一个“大而全企业 AI 平台”。
