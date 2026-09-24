# 小团队按需采用与资产保留

Decision date: 2026-09-24
Status: accepted adoption direction; runtime evidence remains independently evaluated

## 决策与适用范围

小团队直接使用 Codex CLI + ADK 导出资源。Digital Worker 不是日常开发、ADK 资产安装、项目 Git/CI 验收或 Knowledge Hub 使用的必要组件。本仓保留为按需采用的领域责任与正式证据参考实现，而不是要求每个成员安装的生产前置系统。

本决策收紧的是采用范围，不改写已有正式 Run 的合同。ADR-003/004/005、Edge Foundation、Work/Run、Verification、receipt 与 Product readiness 继续适用于显式选择本仓集成的任务；不得据此要求未采用本仓的普通项目建立平行 Work/Run 台账。

engineering-platform 是独立方案，不并入、不绑定、不迁移到本仓。没有实际消费者需求，不新增控制面、中央调度器、代理 RPC 网络、适配器或跨仓状态同步层。

## 小团队主线

维护与分发：`llm_agent -> agent-dev-kit -> Codex 资源发行 -> CLI`。

日常研发：需求/Issue -> 工程师直接使用 CLI -> 项目源码与构建/测试 -> 审查和责任人接受 -> 可复用经验进入 Knowledge Hub。

WorkBuddy 可以产生需求和协作材料，不因发起任务而获得工程验收或发布权限。Claude 等替代运行时按任务使用；未完成对应真实验证时，不宣称等价替代资格。

ADK 负责可复用能力与资产发布，不接管具体项目运行状态。项目 Git/CI/HIL/设备是工程事实来源；项目负责人的接受结论不由 ADK Release、Runtime receipt、知识检索或本仓文档代替。Knowledge Hub 保留自己的来源、权限、复核与知识提升边界。

## Codex 集成

Codex 的 Session Bootstrap contract 1.3 在 `jiying2007/codex` PR #28 落地：L0/L1 不读取 Digital Worker checkout 或集成配置，L1 仍保留 ADK source identity 与 Knowledge Provider 要求。普通 runtime identity 从既有 ADK lock 派生，不新增一份跨仓身份源。

L2 仍是显式选用的 Digital Worker 正式证据路径。缺少 ETP、exact governance、Knowledge pin 或其它正式材料时必须阻断，不得为完成日常任务而伪造这些材料，也不得将 L2 失败静默降级成 L1。

L0/L1 ready 只表示装配条件，不表示项目测试、审查、设备验证或发布已经通过。未采用 L2 的项目照常执行自己的正式发布要求；不需要为此先部署 Digital Worker。

## 已有资产的处理

- 已验证的通用方法：先与 ADK 去重、验证复用收益，再通过独立 ADK 变更吸收；不整包合并本仓代码和模型。
- 项目特定验收、设备验证、发布条件：保留于项目的原始权威系统；本仓只保留被采用的合同与引用。
- 排障经验、设计理由、参考材料：进入 Knowledge Hub 的候选/复核生命周期，保留来源和适用条件；不自动提升 active。
- 已有 Pilot、R2、产品证据：保留原始 ID、commit、digest 和语义。采用范围改变不会把旧证据重标成新项目、新资源版本或新 Runtime 的证明。
- 未证明有收益的职责模型和资格扩展：停止因“多仓终态闭环”而扩建；有具名消费者及实际缺口时再评估。

不删除本仓，不自动归档仓库，不修改访问权限，也不关闭尚未完成的产品验证问题来制造完成状态。

## R2 与产品资格

继续遵循现有 periodic R2 policy：R2 blocked/stale/not-run 不阻断无关日常开发；只有声称当前 Runtime Portability / Terminal Replaceability 时，才要求新鲜真实证据。llm_agent 只观察，不建立第二个 R2 certifier。

Product readiness、Runtime qualification、组件 Release 和长期运营分别判定。本次采用范围调整不把任何 BLOCKED 项改成 PASS，不取消已采用本仓任务的 Verification、Review 或授权边界。

## 验收

代码级证据归属于 Codex PR #28 及对应精确 head CI：无 Digital Worker 时 L0/L1 可装配，L2 缺材料仍阻断，原有正式身份与升级重新冻结回归保留。

团队采用仍需在真实环境验证资源安装/发现、项目交付、中断恢复、升级回退和跨任务知识复用。仓库合同、文档、synthetic fixture 与 CI 不能代替成员 live、设备或长期运营证据。
