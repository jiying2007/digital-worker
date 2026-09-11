# Architecture Review Decision Matrix

> 现场直接填写 `Decision / Owner / Due / Follow-up`。建议只允许 `ACCEPT / REVISE / DEFER` 三种状态。

|ID|Decision|Recommendation|Current evidence|If rejected / deferred|Owner|Status|Due|Follow-up|
|---|---|---|---|---|---|---|---|---|
|D01|1+7 是否作为当前正式组织模型|ACCEPT|机器配置、Golden Cases、核心参考已一致|重新拆组织会扩大变更面|TBD|TBD|TBD|—|
|D02|14 task types + 7 workflow modes|ACCEPT baseline|路由/Workflow/CI 已落地|需重做 routing/golden baseline|TBD|TBD|TBD|Pilot 后复审|
|D03|Verification 与 Independent Review 职责独立|ACCEPT|Schema/Workflow 已强制 independence|错误放行风险上升|TBD|TBD|TBD|—|
|D04|P0 Skill 最大 A2|ACCEPT Pilot 阶段|Action Policy + Skills 已约束|需要新增执行安全证据|TBD|TBD|TBD|Pilot 后复审|
|D05|Provider-neutral Engineering Handoff|ACCEPT|ADR-003、machine contracts、CI 已同步|重新绑定单一 Runtime|TBD|TBD|TBD|#18|
|D06|Exact-base + Evidence-first + Verification layering|ACCEPT|Contract/Schema/Pilot 已实现|可追溯性和错误 PASS 风险显著增加|TBD|TBD|TBD|—|
|D07|Source of Truth stays at source|ACCEPT|ADR-003 + Knowledge policy|需要重新证明全量集中迁移收益|TBD|TBD|TBD|#16|
|D08|Knowledge 先 Inventory + PoC 再选型|ACCEPT|当前 Provider not-frozen|提前锁定平台存在 ACL/freshness 风险|TBD|TBD|TBD|#16|
|D09|允许多个 Engineering Agent Runtime|ACCEPT with evidence|Contract 已 neutral，尚缺真实对比|默认 Runtime 暂不决定|TBD|TBD|TBD|#18|
|D10|Provider 采用 Capability Matrix + fallback|ACCEPT|#17 已定义评估框架|容易由偏好/采购现状替代能力证明|TBD|TBD|TBD|#17|
|D11|端侧底座 ownership / main protection / branch GC 必须有 Owner|ACCEPT|#11/#12/#19 均为显式 blocker|治理噪音持续存在|TBD|TBD|TBD|#11/#12/#19|
|D12|Productionization 必须单独人工评审|ACCEPT|Pilot Safety Gate 已禁止 auto-production-ready|架构评审可能被误当上线批准|TBD|TBD|TBD|#9|

## 会议规则

- 没有 evidence 的能力不得填 `ACCEPT`；可以 `DEFER`。
- `REVISE` 必须写明具体修改对象，不接受“再优化一下”这种不可执行结论。
- `DEFER` 必须绑定 PoC/Pilot/Issue 与退出条件。
- Provider 选型不得反向改变已经接受的稳定 Contract 原则，除非重新开 ADR。
