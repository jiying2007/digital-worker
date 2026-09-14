# docs 目录说明

`docs/` 保存跨团队的正式架构决策、阶段策略、治理规则、运行手册、原始输入和必要历史归档。端侧目标责任架构以 ADR + `domains/edge-foundation/` 机器 Contract 为准；`嵌入式系统专家团-核心参考/` 是迁移期的人类专业参考，`expert-groups/embedded-system/` 是当前仍承担执行/rollback 的 legacy compatibility surface（旧版兼容表面），两者都不是第二套目标架构 SSOT。

## 目录

- `adr/`：Architecture Decision Record（架构决策记录）；
- `strategy/`：当前阶段已经收敛、可指导实施的策略基线；
- `governance/`：跨仓治理规则；
- `runbooks/`：可直接执行的运行手册；
- `source-materials/`：原始 docx/外部输入，不是运行 SSOT；
- `archive/`：确有必要保留在工作区的历史材料。

## 文档分工

### ADR

记录长期稳定的架构决策、备选方案和原因。改变稳定架构语义必须修改 ADR / Contract，不在普通说明文档中覆盖。

### Strategy

规定当前阶段做什么、不做什么、顺序和退出条件。Strategy 可以被下一阶段替代，但不能覆盖机器 Contract、Action Policy 或 Verification / Independent Review 独立性。

### Runbook

告诉执行人员具体怎么操作，包括命令、前置条件、失败处理和恢复方法。可执行流程语义应尽量归并到 Runbook，不为同一门禁另建平行策略小页。

### 核心参考

`../嵌入式系统专家团-核心参考/` 面向研发人员和评审人，解释职责、流程、专业工作方法、关键产物、治理和典型案例。它服务于 Embedded Expert 的专业能力沉淀，不重新定义端侧组织层级，也不复制机器规则形成第二 SSOT。

## 当前端侧 / 嵌入式基线

- 目标责任模型：`../docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md` + `../domains/edge-foundation/domain.yaml`；
- 当前工程闭环策略：`strategy/embedded-domain-closed-loop-v1.md`；
- 真实 Pilot 唯一操作说明：`runbooks/embedded-pilot.md`；
- 旧 `1+7`：仅作为当前 canonical execution / rollback 的兼容执行面，8/8 身份桥接由 `../domains/edge-foundation/compatibility/embedded-1plus7-mapping.yaml` 维护，不保存 mutable phase 状态。

评审入口：

`../嵌入式系统专家团-核心参考/00-评审入口/01 评审说明与决策清单.md`

## 规则

1. 当前权威文档使用稳定路径，不维护 `_V2/_V3/_final` 活动副本；
2. 历史优先由 Git history / ADR 提供，已失效 review/brainstorm/过渡 strategy 不留活动兼容副本；
3. 二进制原始输入统一放 `source-materials/`；
4. 原始材料规范化并核验来源后，才进入正式 Contract / ownership / decision；
5. Provider-specific 事实不得覆盖 Provider-neutral 上位原则；
6. Runtime-local PASS 不得推导 Domain Verification PASS；
7. 任务分支生命周期遵循 `governance/branch-lifecycle.md`；
8. 迁移 readiness 由真实 receipt / evaluator 计算，不把可变 phase 状态复制到多个 YAML / Markdown。
