# Strategy Baselines

`docs/strategy/` 只保存**当前仍有效**的阶段策略基线。已经被替代的策略不保留活动副本，历史通过 Git 查看。

## 当前基线

- [AI R&D Target Operating Model](ai-rd-target-operating-model.md)：长期 Operating Model；定义 4 个稳定控制面 + N 个 Runtime Binding + Thin Session Bootstrap，以及能力演进链/任务执行链分离、L0/L1/L2、Knowledge 双模式和 exact-source-set 身份语义。
- [Cross-Repo Terminal Maturity Landing](cross-repo-terminal-maturity-landing.md)：跨 `digital-worker / knowledge-hub / agent-dev-kit / llm_agent / Runtime / Assurance` 的终态成熟落地基线；按 Architecture、Identity、Delivery、Assurance、Replaceability、Operations 六个成熟轴推进 Debug / Feature / Release / Evolution Pilot、替换演练与 Productionization。
- [R0 Trust Closure](r0-trust-closure.md)：真实 Pilot 的可信链基线；约束 source/evidence/runtime identity 和阶段化仓库治理。
- [Embedded Domain Closed Loop V1](embedded-domain-closed-loop-v1.md)：当前嵌入式落地策略；先证明 Task / Engineering / Quality / Knowledge / Capability 五个闭环。

长期跨仓语义边界以 `../adr/ADR-005-cross-repo-semantic-ownership-and-evidence-federation.md` 为准；Strategy 不重新定义第二套 repository authority 或 evidence semantics。

## 规则

1. Strategy 可以规定本阶段范围、顺序、退出条件和明确非目标；
2. 不得覆盖 ADR、机器 Contract、Action Policy、Verification / Review 独立性；
3. 需要改变稳定架构语义时进入 ADR / Contract 评审；
4. 实施中发现的信息断点先记录为真实 evidence，重复出现后再升级 Schema / Skill / Platform；
5. Runtime/Provider exact pin 是一次 Pilot/集成的身份固定，不等于冻结总体 Provider；
6. Runtime local gate 不得推导 digital-worker Domain Gate / Verification PASS；
7. Session Bootstrap 只负责装配，不拥有长期 Gate、Knowledge 或 Skill SSOT；
8. 当前 strategy 被替代后直接从活动目录删除，由 Git history 保存演进过程；
9. 跨仓落地优先完善现有 identity/source-set/evidence contract，不因文档设计提前创建无真实 consumer 的长期 schema。