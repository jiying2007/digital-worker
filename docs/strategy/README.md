# Strategy Baselines

`docs/strategy/` 保存已经完成本阶段讨论收敛、可用于指导实施，但不替代 ADR / Contract / Schema 权威的阶段策略基线。

## 当前基线

- [Embedded Domain Closed Loop V1](embedded-domain-closed-loop-v1.md)：当前阶段嵌入式研发域内闭环终版方案；目标是先让嵌入式独立形成 Task / Engineering / Quality / Knowledge / Capability 五个闭环，再通过 Adapter 向企业上下游扩展。
- [4 个稳定控制面 + N 个可替换 Runtime Binding](four-control-planes-runtime-bindings.md)：当前跨仓实施基线；四个稳定控制面保持 Provider-neutral，`jiying2007/codex` 作为第一套 Runtime Binding，后续 Runtime 必须复用同一身份、receipt 和验证边界。

## 已 supersede

- [Four-Repo AI R&D Operating System](four-repo-ai-operating-system.md)：已被 4+N 模型 supersede；仅保留历史路径和设计演进记录。

## 规则

1. Strategy Baseline 可以规定当前阶段的实施顺序、范围、退出条件和明确非目标；
2. 不得覆盖 ADR、机器 Contract、Action Policy、Verification / Review 独立性；
3. 需要改变稳定架构语义时必须进入 ADR / Contract 评审；
4. 实施中发现的信息断点先记录为 Pilot evidence，重复出现后再升级 Schema / Skill / Platform；
5. Provider / Runtime Binding exact pin 只固定一次 Pilot/集成消费的接口身份，不等于冻结总体 Provider 选择；
6. Contract CI success 与 Operational Readiness 分开；Provider CI 未执行/失败、route 未登记、asset bundle identity 缺失或 runtime identity 不完整时必须显式 BLOCKED/NOT_READY；
7. Runtime local gate 不得推导 digital-worker Domain Gate / Verification PASS；
8. Strategy 可被后续阶段 supersede，但历史通过 Git 保留。
