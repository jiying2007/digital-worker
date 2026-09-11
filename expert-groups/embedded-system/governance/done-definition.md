# 嵌入式系统专家团 Done Definition

## 架构/分析类任务

只有在以下条件满足时才能宣称本轮分析闭环：

- task-charter 明确目标、范围、非目标和验收；
- 关键 claim 绑定 evidence 或明确标记 inference；
- blocker、risk、unverified item 未被摘要隐藏；
- 对需要实施的任务形成 engineering-task-package；
- Gate T/E 的状态可追溯。

## Debug 类任务

除上述条件外，还必须：

- 建立 Hypothesis Registry；
- Observed / Inferred / Confirmed 明确区分；
- confirmed root cause 有可复核证据或实验；
- 修复后给出 regression scope。

## 工程交付类任务

不能仅凭“代码已改”宣称完成。至少需要：

- delivery receipt 对应正确 repo/base/变更；
- required verification 每层有明确状态；
- Verification Expert 独立核验；
- Review Governor 完成 Gate R；
- Gate C 生成 deliverable manifest 并保留开放风险。

## 禁止的完成声明

以下任一情况不得宣称“已完成/可发布/生产就绪”：

- required verification 为 not_run / blocked 且未显式降级；
- 缺制品或设备身份却声称 HIL 有效；
- implementation owner 自签最终 verification；
- P0/P1 finding 未关闭或未经责任人显式接受；
- 发布/生产 OTA 缺 release owner 人工批准；
- 仍存在未记录的关键 blocker。
