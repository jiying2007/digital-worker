# 跨团队 RACI

专家团内部 RACI 解决“专业判断由谁负责”；本表解决真实研发组织中“产品、项目、工程、硬件、测试、发布、知识和安全”如何共同完成闭环。

R=Responsible，A=Accountable，C=Consulted，I=Informed。实际组织可以由同一人兼任多个角色，但关键批准和独立验证不能因此被省略。

## 1. 角色

- 产品负责人：产品目标、优先级、产品范围和验收意图；
- 项目负责人：计划、跨团队依赖、资源和业务风险协调；
- 嵌入式主理人：领域流程、技术路由、Gate、工程交接和收口；
- 开发工程师：代码/配置实施和工程事实确认；
- 硬件工程师：原理图、板卡、电气/时序测量等硬件事实；
- 测试/HIL Owner：测试环境、fixture、case 执行和原始测试证据；
- Verification：独立判断证据覆盖和 required layer 状态；
- Review Governor：独立判断风险和是否足以放行；
- Release Owner：发布窗口、目标范围、最终 A7 人工批准；
- Knowledge Owner：知识 authority、freshness、ACL 和正式提升；
- IT/Security：身份、Secret、网络、设备/系统权限和数据边界政策。

## 2. 主流程 RACI

|活动|产品|项目|主理人|开发|硬件|测试/HIL|Verification|Review|Release|Knowledge|IT/Sec|
|---|---|---|---|---|---|---|---|---|---|---|---|
|目标/产品验收意图|A/R|C|C|I|I|C|C|I|I|I|I|
|Task Brief / 技术入口澄清|C|C|A/R|C|C|C|I|I|I|I|I|
|工程材料/版本身份确认|I|C|A|R|R(硬件)|C|C|I|I|C|I|
|技术分析/方案|C|C|A|R/C|C|C|C|I|I|I|I|
|代码/配置实施|I|I|C|A/R|C|I|I|I|I|I|C(权限)|
|设备写入 A6 批准|I|C|C|R|C|C|I|I|I|I|A/C(组织政策)|
|测试/HIL 执行|I|C|C|C|C|A/R|C|I|I|I|I|
|Verification Plan/Report|I|I|I|C|C|C|A/R|I|I|I|I|
|Independent Review|I|I|I|C|C|C|C|A/R|I|I|I|
|Risk Acceptance|C|A(项目风险)|C|I|I|C|C|C|A(发布相关)|I|C(安全相关)|
|A7 Release 批准|I|C|I|I|I|C|C|C|A/R|I|C|
|Knowledge Harvest|I|I|A/R|C|C|C|C|C|I|C|I|
|知识正式提升/撤权|I|I|C|C|C|C|I|I|I|A/R|C|

## 3. Acceptance 谁负责

Acceptance 分两层：

- **产品验收意图**：产品负责人说明用户/产品层“什么算完成”；
- **工程可验证条件**：嵌入式主理人 + Verification 把意图转换成可执行、可取证的 criterion。

产品负责人不负责决定某条 HIL evidence 是否有效；Verification 也不负责替产品定义业务价值。

## 4. 硬件事实怎么进入软件任务

硬件团队对以下事实具有直接责任：

- schematic / board revision；
- 电源、时钟、信号完整性和测量结果；
- 料号/器件 revision；
- 硬件变更通知。

软件日志可以提出硬件假设，但不能替代示波器/仪器或正式硬件资料。硬件事实变化后，主理人负责判断哪些软件分析需要失效或重跑。

## 5. 测试/HIL 与 Verification 的边界

测试/HIL Owner 负责“正确地执行 case 并保存原始结果”；Verification 负责“这些结果能证明什么”。两者不能合并成“测试平台显示绿，所以 Verification PASS”。

## 6. Risk Acceptance

风险接受至少有两个维度：

- 项目/业务风险：项目负责人承担；
- Release 风险：Release Owner 承担。

涉及安全、权限、客户数据或生产环境时，IT/Security 必须参与。Verification 的事实状态不因为风险被接受而改变。

## 7. Knowledge Owner

Knowledge Owner 不负责重写所有原文，而负责：

- 哪个 Source 是 authority；
- 哪些版本仍有效；
- 谁能访问；
- 何时过期/复审；
- 是否正式提升、撤回或 supersede。

领域专家提供内容和证据，Knowledge Owner 负责生命周期治理。
