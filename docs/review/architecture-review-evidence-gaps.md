# Architecture Review Evidence / Assumption Gap Register

> 目的：明确“我们现在不知道什么”，避免把未知误写成架构结论。

|ID|Assumption / Gap|Current status|Risk if assumed true|Evidence needed|Owner|Follow-up|
|---|---|---|---|---|---|---|
|A001|飞书能否稳定承载 Work Item identity / approval / notification|UNVERIFIED|入口与状态漂移|真实 API/权限/审计 PoC|TBD|#17|
|A002|WeKnora ACL / revoke / freshness 能否满足企业知识治理|UNVERIFIED|越权或陈旧知识|ACL 负向测试、更新/删除传播|TBD|#16|
|A003|NAS 资料是否有稳定 metadata / version / ACL|UNASSESSED|错误版本进入 AI 上下文|Source Inventory 样本|TBD|#16|
|A004|Codex / Claude 等 Runtime 能否消费同一 Contract 与 Context|UNVERIFIED|Runtime-neutral 只停留在设计|同任务双 Runtime Pilot|TBD|#18|
|A005|当前 `knowledge_refs` 是否需要 source/version/ACL/provenance|UNPROVEN|Schema 过轻或过度设计|#16/#18 真实字段需求|TBD|#16/#18|
|A006|`executor_identity` 是否需要 runtime/provider/model/version 拆分|UNPROVEN|执行身份追踪不足|Multi-runtime Pilot evidence|TBD|#18|
|A007|端侧底座与嵌入式能力 ownership|BLOCKED|重复 Agent/Skill/平台建设|规范化原文 + ownership map|TBD|#11|
|A008|main required check / branch protection|NOT_ENABLED|红 CI 可被绕过|管理员启用 + 红/绿 PR 验证|TBD|#12|
|A009|已合并任务分支是否完成 GC|NOT_DONE|基线噪音、误用历史分支|物理删除 + branch list|TBD|#19|
|A010|3 条 real Pilot 是否能证明基本工程闭环|NO_EVIDENCE|架构可行但无法证明真实价值|Debug/Feature/Review real runs|TBD|#6/#7/#8|
|A011|Integration Reconciliation 是否需要独立 Skill/Role|UNPROVEN|跨域冲突晚发现|real Pilot 记录 interface conflict|TBD|#6/#7 observations|
|A012|Acceptance → Evidence 是否需要独立 Verification Matrix Schema|UNPROVEN|验收与验证证据映射弱|real Pilot 观察追踪成本|TBD|#7/#8 observations|

## 使用规则

1. `UNVERIFIED/UNPROVEN/UNASSESSED` 不等于失败，只表示不能作为已证实前提。
2. 能用现有 Contract 表达的，不提前新增 Schema。
3. Gap 关闭时必须保留 evidence ref，不以会议口头结论关闭。
4. Provider 产品宣传、Demo、个人使用体验不能替代企业 ACL / identity / audit / recovery 证据。
