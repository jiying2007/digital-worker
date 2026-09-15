# docs 目录说明

`docs/` 保存跨团队的正式架构决策、阶段策略、治理规则、运行手册、原始输入和必要历史归档。端侧底座的正式责任与运行边界以 ADR + `domains/edge-foundation/` 机器 Contract 为准；`嵌入式系统专家团-核心参考/` 是面向研发与评审人员的专业参考，不是第二套运行 SSOT。

**Canonical routing 已由 Edge Foundation target runtime 承担。旧嵌入式 1+7 compatibility tree、静态身份 mapping、shadow routing 与迁移期 switch machinery 已物理退役。** 当前活动执行面只读取 `domains/edge-foundation/**`；历史迁移方案只由 Git history / ADR / archive 保留，不再作为活动 Runbook、rollback surface 或第二套兼容架构。

## 目录

- `adr/`：Architecture Decision Record（架构决策记录）；
- `strategy/`：当前阶段已经收敛、可指导实施的策略基线；
- `governance/`：跨仓治理规则；
- `runbooks/`：当前仍可直接执行的运行手册；
- `source-materials/`：原始 docx/外部输入，不是运行 SSOT；
- `archive/`：确有必要保留在工作区、但不参与活动执行的历史材料；
- `brainstorm/`：非规范性探索记录，不得覆盖 ADR / Contract / Governance。

## 文档分工

### ADR

记录长期稳定的架构决策、备选方案和原因。改变稳定架构语义必须修改 ADR / Contract，不在普通说明文档中覆盖。

### Strategy

规定当前阶段做什么、不做什么、顺序和退出条件。Strategy 可以被下一阶段替代，但不能覆盖机器 Contract、Action Policy 或 Verification / Independent Review 独立性。

### Runbook

告诉执行人员具体怎么操作，包括命令、前置条件、失败处理和恢复方法。`runbooks/` 只保留当前可执行流程；已经完成的迁移/切换步骤不得继续作为活动 Runbook。

### 核心参考

`../嵌入式系统专家团-核心参考/` 面向研发人员和评审人，解释职责、流程、专业工作方法、关键产物、治理和典型案例。它服务于 Embedded System Expert 的专业能力沉淀，不重新定义端侧组织层级，也不复制机器规则形成第二 SSOT。

## 当前端侧 / 嵌入式基线

- 总体 Provider-neutral 架构：`adr/ADR-003-provider-neutral-ai-rd-target-architecture.md`；
- 跨仓语义所有权、Authority 与证据联邦：`adr/ADR-005-cross-repo-semantic-ownership-and-evidence-federation.md`；
- 长期 Operating Model：`strategy/ai-rd-target-operating-model.md`；
- 跨仓终态成熟落地：`strategy/cross-repo-terminal-maturity-landing.md`；
- 责任模型：`adr/ADR-004-edge-foundation-digital-responsibility-architecture.md` + `../domains/edge-foundation/domain.yaml`；
- Canonical routing：`../domains/edge-foundation/routing.yaml`；
- Canonical runtime：`../domains/edge-foundation/runtime/`；
- Canonical Skill：`../domains/edge-foundation/skills.yaml` + `../domains/edge-foundation/skills/`；
- 当前工程闭环策略：`strategy/embedded-domain-closed-loop-v1.md`；
- 真实 Pilot 操作说明：`runbooks/embedded-pilot.md`；
- Product readiness evaluator：`../scripts/evaluate_edge_foundation_product_readiness.py`；
- Knowledge Registry：`../domains/edge-foundation/knowledge/registry.yaml`；
- 核心专业评审入口：`../嵌入式系统专家团-核心参考/06-治理与评审/01 评审说明与决策清单.md`。

当前 Product readiness 与 routing authority 已解耦。Debug / Feature / Review-Release 三轨真实 evidence 只决定 Product readiness，不会切换、回退或重新打开 canonical routing。

## 规则

1. 当前权威文档使用稳定路径，不维护 `_V2/_V3/_final` 活动副本；
2. 历史优先由 Git history / ADR 提供，已失效 review/迁移 runbook/过渡 strategy 不留活动兼容副本；
3. 二进制原始输入统一放 `source-materials/`；
4. 原始材料规范化并核验来源后，才进入正式 Contract / ownership / decision；
5. Provider-specific 事实不得覆盖 Provider-neutral 上位原则；
6. Runtime-local PASS 不得推导 digital-worker Domain Verification PASS；
7. 任务分支生命周期遵循 `governance/branch-lifecycle.md`；
8. Product readiness 由真实 canonical Pilot receipt / evaluator 计算，synthetic evidence 不计入产品成熟度；
9. 活动文档与机器 Contract 不得引用已物理退役的 1+7、compatibility、shadow routing 或迁移 switch machinery；
10. Productionization 前必须启用并验证 server-side repository governance，不能用 repository-local CI 替代；
11. 跨仓协同优先使用 refs-first identity、exact Source Set、Receipt/Evidence，不复制其它仓的 canonical SSOT；
12. Contract Authority、Fact Authority 与 Decision Authority 不得通过本地实现或 Provider PASS 混为一体。