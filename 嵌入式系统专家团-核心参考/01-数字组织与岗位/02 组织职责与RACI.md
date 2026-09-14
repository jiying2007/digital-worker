# 数字岗位协作与 RACI

> 本文只回答“**8 个数字岗位之间如何协作、谁对哪类判断负责**”。  
> 每个岗位自身的职责、输入输出、工作要求和数字任职资格，统一见 [《数字岗位与能力模型》](03%20数字岗位与能力模型.md)，本文不重复岗位说明书。

## 1. 协作原则

专家团保持 **1 名主理人 + 7 个专业角色 / 8 个数字岗位**，但不意味着每个任务都需要 8 个岗位参与。

```text
                       P01 技术负责人
                             │
             ┌───────────────┼────────────────┐
             ▼               ▼                ▼
         P02 架构        P03/P04/P05       P06 调试可靠性
        系统边界          平台与设备事实       根因闭环
             │               │                │
             └───────────────┼────────────────┘
                             ▼
                       Engineering
                             │
                             ▼
                      P07 Verification
                             │
                             ▼
                       P08 Independent Review
```

协作遵守四条规则：

1. **P01 管任务和收口，不替专业岗位下领域事实结论**；
2. **P02 管系统边界，P03-P05 对各自平台/设备事实负责，P06 管复杂 RCA 方法与根因收敛**；
3. **Engineering 实施与专家判断分开**；
4. **P07 Verification 与 P08 Independent Review 独立于实施，并彼此职责不同**。

---

## 2. 核心 RACI

R=Responsible，A=Accountable，C=Consulted，I=Informed。

|活动|P01 主理人|P02 架构|P03 BSP|P04 MCU|P05 驱动|P06 调试|P07 验证|P08 审查|
|---|---|---|---|---|---|---|---|---|
|任务分类 / Knowledge-Material-Intake 准备度|A/R|C|C|C|C|C|I|I|
|系统架构 / 接口 / NFR|A|R|C|C|C|C|C|I|
|Linux/BSP 平台事实|A|C|R|C|C|C|C|I|
|MCU/RTOS 平台事实|A|C|C|R|C|C|C|I|
|Driver / Component 设备与接口事实|A|C|C|C|R|C|C|I|
|复杂 Debug Hypothesis / Root Cause|A|C|C|C|C|R|C|I|
|Technical Decision / Engineering Package|A/R|C|C|C|C|C|C|I|
|代码 / 配置 / 构建 / 设备实施|I|I|I|I|I|I|I|I|
|Verification Plan / Report|I|C|C|C|C|C|A/R|I|
|Independent Review / Release Readiness|I|C|C|C|C|C|C|A/R|
|Closure / Knowledge Harvest|A/R|I|I|I|I|I|C|C|

工程实施由**工程师 + 受控 Engineering Runtime**负责，不自动归属于任何 Expert Position。岗位参与的最小集合由任务影响面决定。

---

## 3. 专业冲突怎么处理

### 3.1 两个专业岗位给出不同结论

先检查：

1. 是否使用同一 `System Context`；
2. source / firmware / board / device identity 是否一致；
3. 两个结论分别属于谁的事实责任边界；
4. 哪个新的区分实验能够消除冲突。

P01 负责推动收敛，但不能通过投票替代 Evidence。

### 3.2 架构假设与领域事实冲突

P02 负责系统边界和目标约束；P03-P05 负责证明具体平台和设备事实。如果架构假设与 TRM、代码或测量冲突，应更新 Technical Decision，而不是要求领域事实服从架构文档。

### 3.3 Debug RCA 跨多个领域

P06 维护**唯一 Hypothesis Registry 和 Root Cause 状态**；P03-P05 为假设提供各领域直接事实。不能让每个专业各自维护一份互相冲突的 RCA。

---

## 4. Verification、Review 与实施冲突

### Verification 与实现者

P07 对“现有 Evidence 能证明到哪一层”有独立判断权。实现者可以：

- 补充证据；
- 指出验证方法错误；
- 修复实现后重新提交验证。

但实现者不能自行把 FAIL/NOT_RUN 改成 PASS。

### Review 与项目进度

P08 的 Finding 不能因 deadline 被删除。业务需要承担残余风险时，应走明确 Risk Acceptance / `APPROVE_WITH_RISK`，保留 owner、期限、containment 和 rollback。

Verification 事实状态不会因为风险被接受而改变。

---

## 5. 简单任务如何缩编

组织模型稳定，任务参与岗位可以很小：

|任务|典型最小组合|
|---|---|
|单一 DTS/resource 问题|P01 + P03；按 required layer 引入 P07|
|明确 MCU Linker overflow|P01 + P04；需要系统资源权衡时加 P02|
|未知原因的现场偶发故障|P01 + P06 + 相关领域 Owner；之后 P07/P08|
|纯技术可行性评审|P01 + P02；不自动进入 Engineering|
|单纯 Code Review|P08 主责；需要领域事实时按需拉 P02-P06|
|Release / OTA Readiness|P07 + P08；P01 提供闭环材料，Release Owner 保留人工批准|

原则是：**只拉完成当前 Claim 所需的最小岗位集合**，不是“专家越多质量越高”。

---

## 6. 人、Agent 与 Runtime 的关系

数字岗位是稳定责任模型，Agent 是岗位实现，Runtime 是执行环境。三者不能混为一体：

- 人类组织保留授权、风险接受、设备写入和发布等高风险责任；
- Agent 可以承担稳定岗位的分析、判断和产物生成职责；
- Runtime 可以执行受控工程动作，但 Runtime success 不等于领域结论或 Verification PASS；
- 换 Runtime 不改变 Position、RACI、Gate 或 Evidence 规则；
- 独立性由责任主体和证据链体现，不以“换了一个模型”代替。

跨产品、项目、硬件、测试/HIL、Release、Knowledge、IT/Security 的组织关系见 [《跨团队 RACI》](04%20跨团队RACI.md)。
