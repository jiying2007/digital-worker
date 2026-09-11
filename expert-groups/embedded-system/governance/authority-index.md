# 嵌入式系统专家团权威来源顺序

出现冲突时按以下顺序裁决：

1. `expert-group.yaml`：专家团身份、成员、顶层边界；
2. `config/workflow.yaml`：阶段、Gate、transition 与 recovery；
3. `config/task-modes.yaml`：任务类型和默认路由；
4. `config/action-policy.yaml`：动作权限和人工审批边界；
5. `config/gate-policy.yaml` / `config/material-requirements.yaml`：Gate 与材料规则；
6. `contracts/experts/*.io.yaml`：L1 专家 I/O；
7. `schemas/*.schema.json`：Artifact 字段与状态；
8. `agents/*.md`：角色执行纪律；
9. 后续 `skills/*/SKILL.md`：原子能力实现方法；
10. `references/`、历史说明和示例。

上位组织约束仍受以下文件控制：

- `研发中心AI数字员工研发流程规划_V2.md`；
- `docs/adr/ADR-001-workbuddy-codex-integration-boundary.md`；
- `docs/adr/ADR-002-embedded-system-expert-team-architecture.md`。

任何下层文件不得绕过 ADR 与研发中心总体流程的安全边界。
