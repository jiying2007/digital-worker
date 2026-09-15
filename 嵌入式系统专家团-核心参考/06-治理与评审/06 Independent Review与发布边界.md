# Independent Review与发布边界

Independent Review 属于 Assurance Plane，用于在需要时对 Evidence、Verification、Open Risk、Rollback、Provenance 与错误放行风险做额外独立判断。它不是 Embedded Capability，也不拥有 Release authority。

## 1. 长期责任

Independent Review 关注：

- Work Item / Run / Context identity 是否一致；
- Evidence 是否支持声明的结论；
- 是否存在 unsupported claim 或 incorrect PASS；
- P0/P1 finding 是否关闭或有明确 human risk acceptance；
- rollback / provenance / open risk 是否完整；
- Verification 是否发生跨层推导；
- Review 是否被实施者自签或被同一自动化路径隐式绕过。

## 2. 当前 iterative Pilot 的阶段策略

Independent Review **优先使用，但 reviewer/tool 不可用时不是硬 completion gate**。

允许替代组合：

```text
static checks
+ Hosted CI
+ traceable Verification evidence
```

使用替代路径时必须明确：

- `review_report_ref` 可以为空；
- 不得声称 Independent Review PASS；
- 不得因此推导 Device/HIL/Release PASS；
- 不得扩大 A0-A7 action authority；
- Audit trace 必须能解释为何走替代路径。

Feature real Pilot `FEATURE-PCR02-OTA-001` 已证明这条路径可以形成 real completed + phase3 eligible receipt，同时保持 device/release scope 明确未验证。

## 3. Release authority

Review verdict 不是 A7 授权。Release action 必须保留 human decision，至少确认：

- release candidate exact identity；
- required Device/HIL/rollback evidence；
- known risks / waivers；
- deployment scope；
- 回退条件；
- 明确批准者与时间。

没有 A7 human decision，不允许把 review/CI 状态解释为“已发布授权”。

## 4. Review 与 Verification 的关系

Verification 回答“证据证明到哪一层”；Independent Review 回答“基于这些证据和风险，是否存在额外错误放行问题”。Review 不应重复执行全部测试，也不能把缺失 Verification 通过评论补成 PASS。

## 5. canonical switch / productionization

当前 Pilot completion waiver 不自动等价于后续 productionization 或 canonical-routing governance 的 waiver。进入更高成熟度阶段时，可以重新要求更严格的 Independent Review / approvals / repository protection；这些要求必须由对应阶段 Contract 明确，而不是把当前试点临时约束写死成永久组织结构。

## 6. BLOCK 条件

Review 可用且发现未处理的重大风险、Evidence/Verification identity 断链、错误 PASS、隐藏未验证项或 Release authority 被自动化绕过时必须 BLOCK。Review 不可用时则按当前 Pilot policy 走显式替代，而不是伪造 reviewer 或 review verdict。
