# Architecture Review Pre-read

## 1. 本轮要解决什么

研发中心已经形成 Provider-neutral 的 AI R&D Operating Model 候选：稳定 Contract / Evidence / Gate / Verification，不提前绑定 WorkBuddy、飞书、WeKnora、Codex、Claude 等具体 Provider。

本轮评审目标不是“选产品”，而是判断：

- 这套稳定层是否合理；
- 哪些部分可以直接进入真实 Pilot；
- 哪些结论必须继续用 PoC/Pilot 取证；
- 哪些边界当前必须保持 fail-closed。

## 2. 当前稳定层

- Task / Handoff Contract；
- Expert Team / Workflow / Gate；
- Evidence-first；
- Verification / Independent Review；
- A0-A7 Action Policy；
- Pilot / Evaluation / Productionization Gate；
- Source of Truth stays at source；
- Expert identity 与 Engineering Agent Runtime 解耦。

## 3. 当前未冻结层

- Interaction / Work Item Provider；
- Knowledge Provider；
- 默认 Engineering Agent Runtime；
- Context Broker / Runtime Gateway / Action Gateway；
- 端侧底座 ownership 具体域；
- 更高自动化权限。

## 4. 本轮明确不评

- WorkBuddy 是否最终采用；
- 飞书是否唯一 Work Item Provider；
- WeKnora 是否最终 Knowledge Provider；
- Codex vs Claude 最终默认 Runtime；
- Context Broker 是否现在建设；
- MES / Field 全量接入；
- A5-A7 自动化扩权；
- Production Ready。

## 5. 已有证据

- 1+7、14 task types、7 workflow modes、Gate、A0-A7、23 个 P0 Skill 已机器化；
- Engineering Handoff、Verification、Independent Review、Pilot CLI/validator/evaluator 已落地；
- provider-neutral architecture / core-reference synchronization / incorrect-PASS / Pilot CLI smoke 已纳入 CI；
- 当前核心参考为 `v0.7.0 / provider-neutral / review-ready`。

## 6. 当前主要证据缺口

- #6/#7/#8 尚无真实 Pilot completed evidence；
- #16 Knowledge Source Inventory/PoC 未完成；
- #18 Multi-runtime 对比未完成；
- #11 端侧底座 ownership 未完成；
- #12 main protection 未启用；
- #19 merged branch GC 未物理完成。

## 7. 建议本轮评审结论

推荐优先接受“稳定原则”，把 Provider 选型和复杂平台化能力继续 `DEFER` 到 PoC/Pilot；不要因为缺真实数据而否定已经成熟的 Contract/Governance，也不要因为架构合理而提前宣布 Production Ready。
