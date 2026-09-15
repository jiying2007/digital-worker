# Independent Review与发布边界

Independent Review 属于 Assurance Plane，负责从 implementation 与 domain decision 之外检查 Evidence、Risk、错误放行和 Release Readiness。它可以接受明确残余风险，但不能改写 Verification 的事实状态，也不能替代 A7 Release Owner。

## 1. 典型任务

Code Review、关键技术方案审查、Release/OTA Readiness、correctness/safety finding、Risk Acceptance 边界、rollback/provenance 检查和错误 PASS 拦截。

## 2. 必要输入

- exact source / artifact / candidate identity；
- Technical Decision / Engineering Package；
- Delivery Receipt；
- Verification Report；
- Acceptance → Evidence Matrix；
- open blocker / risk / waiver；
- rollback / provenance；
- required human approval。

## 3. 审查顺序

1. **Identity**：确认评审对象就是实施与验证对象；
2. **Acceptance/Evidence**：确认 required Verification 没有缺层或跨层推导；
3. **Hidden Gap**：检查 unverified item、blocker、waiver 是否被隐藏；
4. **High-risk Surfaces**：接口、lifetime、并发、资源、安全、Power、OTA/rollback；
5. **Authority**：检查 A0–A7 与 required human approval；
6. **Decision**：最后才给 Review Decision。

## 4. Code Review

Code Review 默认 review-only：只评审，不隐式修改。需要领域事实时拉对应 Expert/Capability；需要修复时返回 Engineering；修改后的 diff 必须重新建立评审对象 identity。

重点包括 correctness、memory/lifetime、concurrency、error path、resource cleanup、security boundary、compatibility、observability、test adequacy 和 rollback impact。

## 5. Release / OTA Review

至少核：

- exact source/artifact/manifest/provenance；
- 产品/board/device/firmware baseline；
- download/package integrity；
- install/upgrade/downgrade；
- reboot/boot/resulting version；
- rollback/power-loss/failure path；
- required Device/HIL/soak；
- open risk / containment；
- Release Owner 与 A7 approval。

单个 hosted CI、package SHA 或单个 HIL case 不能扩写成“Release 已验证”。

## 6. Finding 与 Risk Acceptance

每个 Finding 必须指向具体 Evidence、规则或缺口，并标明 severity、affected scope、owner、required rework 或接受条件。

`APPROVE_WITH_RISK` 至少保留：risk、impact、evidence、mitigation/containment、owner、acceptor、expiry/target fix、rollback 和对客户/Release 的影响。

Review 可以接受 residual risk，但不能把 Verification 的 NOT_RUN/FAIL 改成 PASS。

## 7. 当前 iterative Pilot 的阶段性策略

Independent Review 优先使用，但 reviewer/tool 不可用时，static checks + Hosted CI + traceable Verification 可以满足当前 iterative Pilot completion。必须记录不可用事实；该替代：

- 不等于 Independent Review PASS；
- 不提高 action authority；
- 不替代 Device/HIL；
- 不形成 Release Approval；
- 不取消 A7 human gate。

正式发布、关键高风险变更或后续 productionization 可以重新把 Independent Review 设为强制条件，而无需改变责任模型。

## 8. 输出 Contract

Review Report、Findings、Decision、Residual Risk、Unverified Items、Required Rework、Responsible Stage、Release Readiness、Authority Check。

## 9. 常见错误

- 因 deadline 删除 Finding；
- 用“以前版本没问题”替代当前 Evidence；
- 只看 CI summary，不看 required Device/HIL；
- Risk waiver 无 owner/期限；
- review-only 中偷偷修代码导致评审对象变化；
- 把 Readiness Decision 写成已执行 Release；
- Review 把 Verification FAIL/NOT_RUN 解释成 PASS；
- 独立 reviewer 不可用却伪造 review receipt。

## 10. BLOCK 条件

source/artifact identity 不一致、required Verification 缺失、关键 correctness/safety Finding 未处理、rollback/provenance 属于 required evidence 但缺失、Risk Acceptance 无责任人/期限、A6/A7 人工 Gate 未满足时，应 BLOCK / REQUEST_CHANGES。

## 11. Knowledge Harvest 与质量指标

可沉淀 review checklist、finding pattern、risk template、release-readiness checklist、rollback/provenance rule。主要指标：incorrect-pass interception、finding recurrence、risk expiry compliance、review evidence traceability、release escape rate。
