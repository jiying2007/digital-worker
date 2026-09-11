# Strategy Baselines

`docs/strategy/` 保存已经完成本阶段讨论收敛、可用于指导实施，但不替代 ADR / Contract / Schema 权威的阶段策略基线。

## 当前基线

- [Embedded Domain Closed Loop V1](embedded-domain-closed-loop-v1.md)：当前阶段嵌入式研发域内闭环终版方案；目标是先让嵌入式独立形成 Task / Engineering / Quality / Knowledge / Capability 五个闭环，再通过 Adapter 向企业上下游扩展。

## 规则

1. Strategy Baseline 可以规定当前阶段的实施顺序、范围、退出条件和明确非目标；
2. 不得覆盖 ADR、机器 Contract、Action Policy、Verification / Review 独立性；
3. 需要改变稳定架构语义时必须进入 ADR / Contract 评审；
4. 实施中发现的信息断点先记录为 Pilot evidence，重复出现后再升级 Schema / Skill / Platform；
5. Strategy 可被后续阶段 supersede，但历史通过 Git 保留。
