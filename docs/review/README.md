# Architecture Review Readiness Pack

> 状态：`review-candidate`
>
> 输入基线：`main@9fe79cd52633d62c39e460b45f5e78369db0ab30`
>
> 用途：正式 Architecture Review 前的决策包。本文档集不替代 ADR、Contract、Schema 或专家团机器资产。

## 评审目标

本轮只评“架构原则是否足以进入真实 PoC/Pilot”，不评 Production Ready。

评审后必须明确：

1. 哪些原则 `ACCEPT`；
2. 哪些原则 `REVISE`；
3. 哪些问题 `DEFER` 到 PoC/Pilot；
4. 哪些工作必须有 Owner / due date / follow-up Issue；
5. 是否允许启动 #6/#7/#8、#16/#18；
6. ADR-003 是 `accepted`、`revise` 还是继续 `proposed-for-review`。

## 阅读顺序

1. [Pre-read](architecture-review-pre-read.md)
2. [Decision Matrix](architecture-review-decision-matrix.md)
3. [Evidence / Assumption Gaps](architecture-review-evidence-gaps.md)
4. [RACI](architecture-review-raci.md)
5. [End-to-End Walkthroughs](architecture-review-walkthroughs.md)
6. 深入资料：`研发中心AI数字员工研发流程规划.md`、ADR-003、`嵌入式系统专家团-核心参考/`

## 明确非目标

本轮不决定：最终 WorkBuddy/飞书/WeKnora/Codex/Claude 选型、Context Broker 是否建设、MES/Field 全量接入、A5-A7 扩权、Production Ready。

## 评审退出条件

会议结束必须形成可追踪的 Decision List；任何 `REVISE/DEFER` 都必须绑定 Owner、证据缺口和下一步 Issue。没有证据的 Provider 能力不得填 PASS。
