# docs 目录说明

`docs/` 保存跨团队的正式架构决策、阶段策略、治理规则、运行手册、原始输入和必要历史归档。嵌入式专家团的人类可读架构与评审资料统一放在 `嵌入式系统专家团-核心参考/`，机器资产放在 `expert-groups/embedded-system/`。

## 目录

- `adr/`：Architecture Decision Record；
- `strategy/`：当前阶段已经收敛、可指导实施的策略基线；
- `governance/`：跨仓治理规则；
- `runbooks/`：可直接执行的运行手册；
- `source-materials/`：原始 docx/外部输入，不是运行 SSOT；
- `archive/`：确有必要保留在工作区的历史材料。

## 文档分工

### ADR

记录长期稳定的架构决策、备选方案和原因。需要改变稳定架构语义时修改 ADR/Contract，而不是在普通说明文档中覆盖。

### Strategy

规定当前阶段要做什么、不做什么、顺序和退出条件。Strategy 可以被下一阶段替代，但不能覆盖机器 Contract、Action Policy 或 Verification/Review 独立性。

### Runbook

告诉执行人员具体怎么操作，包括命令、前置条件、失败处理和恢复方法。

### 核心参考

`../嵌入式系统专家团-核心参考/` 面向研发人员和评审人，解释架构、流程、职责、专业工作方法、关键产物、治理和典型案例。它不复制机器规则，也不承担第二套 SSOT。

## 当前嵌入式基线

当前阶段以 `strategy/embedded-domain-closed-loop-v1.md` 为实施基线：先用真实 Debug / Feature / Review-Release 任务证明工程闭环，再验证知识复用和多 Runtime 可替换性。

评审入口：

`../嵌入式系统专家团-核心参考/00-评审入口/01 评审说明与决策清单.md`

## 规则

1. 当前权威文档使用稳定路径，不维护 `_V2/_V3/_final` 活动副本；
2. 历史优先由 Git history 提供，已失效的 review/brainstorm/过渡 strategy 不留活动兼容副本；
3. 二进制原始输入统一放 `source-materials/`；
4. 原始材料规范化并核验来源后，才进入正式 Contract/ownership/decision；
5. Provider-specific 事实不得覆盖 Provider-neutral 上位原则；
6. Runtime-local PASS 不得推导 Domain Verification PASS；
7. 任务分支生命周期遵循 `governance/branch-lifecycle.md`。
