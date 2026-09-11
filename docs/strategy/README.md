# Strategy Baselines

`docs/strategy/` 保存已经完成本阶段讨论收敛、可用于指导实施，但不替代 ADR / Contract / Schema 权威的阶段策略基线。

## 当前基线

- [Embedded Domain Closed Loop V1](embedded-domain-closed-loop-v1.md)：当前阶段嵌入式研发域内闭环终版方案；目标是先让嵌入式独立形成 Task / Engineering / Quality / Knowledge / Capability 五个闭环，再通过 Adapter 向企业上下游扩展。
- [Four-Repo AI R&D Operating System](four-repo-ai-operating-system.md)：定义 `digital-worker + knowledge-hub + agent-dev-kit + llm_agent` 的职责边界、SSOT、跨仓 Identity、Provider pin 与 Knowledge/Agent/Runtime handoff。

## 规则

1. Strategy Baseline 可以规定当前阶段的实施顺序、范围、退出条件和明确非目标；
2. 不得覆盖 ADR、机器 Contract、Action Policy、Verification / Review 独立性；
3. 需要改变稳定架构语义时必须进入 ADR / Contract 评审；
4. 实施中发现的信息断点先记录为 Pilot evidence，重复出现后再升级 Schema / Skill / Platform；
5. Provider exact pin 只固定一次 Pilot/集成消费的接口身份，不等于冻结总体 Provider 选择；
6. Provider CI 未执行/失败、route 未登记或 identity 不完整时必须显式 BLOCKED/NOT_READY，不得写成 PASS；
7. Strategy 可被后续阶段 supersede，但历史通过 Git 保留。
