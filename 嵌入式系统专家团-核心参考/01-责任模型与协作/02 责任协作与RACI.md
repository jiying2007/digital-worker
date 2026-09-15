# 责任协作与 RACI

RACI 在这里描述**目标责任单元之间的协作**，不再用旧数字岗位或旧 Expert identity 作为组织骨架。

## 1. 基本规则

- Edge Coordination 负责路由、Gate、交接和收口，不替专业 Expert 生成领域事实；
- Domain Expert 对本领域专业判断负责；
- Embedded System Expert 内部由 Capability 承担具体专业责任；
- Engineering 执行者负责实现与直接执行结果，不拥有 Domain Verification PASS；
- Verification 对证据覆盖和验证层级负责；
- Independent Review 负责额外独立风险判断，不拥有 A7 release authority；
- 高风险设备写和 Release 保留明确 human gate。

## 2. 目标 RACI

| 活动 | Edge Coordination | Embedded System Expert / Capability | Structure / Hardware Expert | Engineering | Verification | Independent Review | Human Gate |
|---|---|---|---|---|---|---|---|
| Task intake / scope | A/R | C | C | I | I | I | C |
| Material readiness | A/R | C | C | I | C | I | C |
| 专业技术分析 | C | A/R | A/R（命中其领域时） | C | C | I | I |
| Engineering Package | A | R/C | C | C | C | I | I |
| 代码/配置修改 | I | C | C | A/R | I | I | 按 Action level |
| Build / direct test | I | C | C | A/R | C | I | 按 Action level |
| Acceptance → Evidence | C | C | C | C | A/R | C | I |
| Verification verdict | I | C | C | C | A/R | I | I |
| Independent Review | I | C | C | I | C | A/R | I |
| Device write | C | C | C | R（获批后） | C | I | A |
| Release action | C | C | C | R（获批后） | C | C | A |
| Closure / Knowledge Harvest | A/R | C | C | C | C | C | I |

`A/R/C/I` 只表示责任关系，不自动授权工具动作。动作权限仍以 A0-A7 policy 为准。

## 3. Embedded Capability 之间如何协作

同一任务可以命中多个 Capability，但仍属于同一个 Embedded System Expert。例如 DMA stale 问题可能同时需要：

```text
embedded.debug-reliability
+ embedded.linux-bsp
+ embedded.driver-component
```

这不是“三个 Expert 协同”，而是**一个 Domain Expert 内部多 Capability 协作**。

只有出现真实跨域证据，例如板级电气状态不确定、原理图/电源时序冲突、信号完整性或器件电气契约问题，才升级到 Hardware Expert；不能因为任务复杂就默认多 Expert。

## 4. Verification / Review 的阶段边界

长期目标保持 Engineering、Verification、Review 分离。当前 iterative Pilot 为了不被 reviewer/tool 可用性阻断，允许 Independent Review unavailable 时使用 static checks + Hosted CI + traceable Verification evidence 完成 Pilot，但必须显式保留：

- 没有 Independent Review PASS；
- 没有跨层推导 Device/HIL/Release PASS；
- 没有扩大 Action authority；
- Release 仍由 A7 human decision 控制。

## 5. 冲突处理

出现责任冲突时按以下顺序处理：

1. 回到 `domain.yaml` 看 Domain / Expert / Capability ownership；
2. 回到 Material/System Context 核对事实身份；
3. 将争议拆成可证伪的问题并分配 Evidence owner；
4. 需要跨域时使用 evidence-triggered escalation；
5. 无法解决则 BLOCK，不允许通过增加一个临时“专家/Agent”掩盖责任不清。
