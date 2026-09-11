# 嵌入式系统专家团权威来源顺序

出现冲突时，先判断是**总体架构问题**还是**专家团内部运行问题**。

## 1. 上位总体架构

以下文件优先定义 Provider、知识、Runtime 与组织级边界：

1. `研发中心AI数字员工研发流程规划.md`：当前总体提案；
2. `docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md`：Provider-neutral 总体架构原则；
3. `docs/adr/ADR-001-workbuddy-codex-integration-boundary.md`：特定 Provider 场景的历史/局部决策，已 `superseded-in-part`；
4. `docs/adr/ADR-002-embedded-system-expert-team-architecture.md`：嵌入式专家团在总体架构中的正式边界。

总体架构明确：Provider 可替换，Contract 稳定；Knowledge Source / Provider 分离；Expert 与 Engineering Agent Runtime 解耦。

## 2. 嵌入式专家团内部权威顺序

1. `expert-group.yaml`：专家团身份、成员、顶层边界、Runtime/Knowledge Provider 状态；
2. `config/workflow.yaml`：阶段、Gate、transition 与 recovery；
3. `config/task-modes.yaml`：任务类型和默认路由；
4. `config/action-policy.yaml`：动作权限和人工审批边界；
5. `config/gate-policy.yaml` / `config/material-requirements.yaml`：Gate 与材料规则；
6. `contracts/experts/*.io.yaml`、`contracts/engineering-handoff.yaml` 与跨团队 Contract：输入输出和 handoff；
7. `schemas/*.schema.json`：Artifact 字段、状态与机器校验；
8. `agents/*.md`：角色执行纪律；
9. `skills/*/SKILL.md`：原子能力实现方法；
10. `嵌入式系统专家团-核心参考/`：人工可读解释层与内部评审材料；
11. `docs/source-materials/`、`docs/archive/`：原始输入与历史草案，仅供证据追溯。

## 3. Provider-specific 规则

- WorkBuddy、飞书、WeKnora、Codex、Claude 等不能通过局部配置反向覆盖 ADR-003；
- Provider Adapter 可以定义连接方式，但不得改变 task/evidence/verification/action 语义；
- 某 Provider 暂不可用时，可以更换 Provider 或进入 BLOCKED，不得通过弱化 Gate 解决；
- Gate K 判断“知识/证据是否足够可信”，不是判断某个特定 RAG 服务是否在线；
- `phase.execution` 的正式角色是 `engineer-plus-engineering-agent`，具体 Runtime 可选择。

## 4. 解释层规则

- 核心参考文档用于讨论、评审和培训，不是第二套 SSOT；
- 原始 docx 只有在被规范化、引用并完成来源核验后，才可作为具体职责/ownership 的证据；
- 历史草案不参与当前运行时裁决；
- Git history 用于版本追溯，不通过在活动目录复制 `_V2/_V3/_legacy` 文件维持兼容。

任何下层文件不得绕过总体 ADR、Action Policy、Verification 或 Independent Review 边界。
