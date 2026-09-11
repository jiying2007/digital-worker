# 嵌入式系统专家团权威来源顺序

出现冲突时按以下顺序裁决：

1. `expert-group.yaml`：专家团身份、成员、顶层边界；
2. `config/workflow.yaml`：阶段、Gate、transition 与 recovery；
3. `config/task-modes.yaml`：任务类型和默认路由；
4. `config/action-policy.yaml`：动作权限和人工审批边界；
5. `config/gate-policy.yaml` / `config/material-requirements.yaml`：Gate 与材料规则；
6. `contracts/experts/*.io.yaml` 与跨团队/工程交接 Contract：专家输入输出和 handoff；
7. `schemas/*.schema.json`：Artifact 字段、状态与机器校验；
8. `agents/*.md`：角色执行纪律；
9. `skills/*/SKILL.md`：原子能力实现方法；
10. `嵌入式系统专家团-核心参考/`：人工可读解释层与内部评审材料；
11. `docs/source-materials/`、`docs/archive/`：原始输入与历史草案，仅供证据追溯，不直接覆盖现行设计。

上位组织约束仍受以下文件控制：

- `研发中心AI数字员工研发流程规划.md`；
- `docs/adr/ADR-001-workbuddy-codex-integration-boundary.md`；
- `docs/adr/ADR-002-embedded-system-expert-team-architecture.md`。

## 解释层规则

- 核心参考文档用于讨论、评审和培训，不是第二套 SSOT；
- 原始 docx 只有在被规范化、引用并完成来源核验后，才可作为具体职责/ownership 的证据；
- 历史草案不参与当前运行时裁决；
- Git history 用于版本追溯，不通过在活动目录复制 `_V2/_V3/_legacy` 文件维持兼容。

任何下层文件不得绕过 ADR 与研发中心总体流程的安全边界。
