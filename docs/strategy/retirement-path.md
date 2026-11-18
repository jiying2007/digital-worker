# digital-worker 日常退出与最终退役边界

日期：2026-11-18
基线：`7decf126ee8a83cfc609401c12ebd85153205cea`
状态：**日常使用可退出；正式证据消费者未完全解除；不能永久删除**。

## 决策

个人和小团队的实际工程任务由项目的 Git/CI + 已授权 Runtime/ADK 执行，也可使用独立的 `engineering-platform/tool/eng`。本仓不是任何日常任务、CLI 登录、构建、验收或 Knowledge Hub 的依赖。停止建设第二套日常执行器、中心台账、专家协调服务和额外安装系统。

这不是否定原始嵌入式参考资料或改变已冻结的 Formal Pilot 结论。已有证明缺口（包括 Debug、Review/Release、Skill 评测和 R2）保持未完成，不为“仓库退役”批量关闭 Issue，也不把 BLOCKED 改为 PASS。

## 当前保留对象（不能当作无价值残留删除）

| 类别 | 检查边界 | 处置 |
|---|---|---|
| 日常三类 Markdown 模板 | `docs/templates/{debug-fix,feature-change,review-release}.md` | `engineering-platform` [PR #308](https://github.com/jiying2007/engineering-platform/pull/308) 复制到发行包；以 PR 合并和真实包烟测为完成条件 |
| 领域方法 | `domains/edge-foundation/skills/` 的 23 个 canonical 定义 | 当前最低成熟度仅 DEFINED；与 ADK 逐项去重，不能直接作为成熟 Skills 批量导入 |
| 唯一参考资料 | `嵌入式系统专家团-核心参考/`、`产品专家团-核心参考/` | 需要保留的事实/方法按实际用途迁至项目或 Knowledge Hub 的受复核资料；不凭目录数量创建新的 Skill |
| 冻结的 Pilot/产品/R2 证据 | `domains/edge-foundation/pilot/evidence/`、`reports/runtime-r2/` 等 | 原 SHA、Work/Run、来源、合同、结果及 UNKNOWN/BLOCKED 语义保留，不重写为另一仓库的新证明 |
| 研发开源合同与迁移历史 | `contracts/`、`docs/adr/`、`schemas/`、`docs/archive/` | 可归档只读，确保明确采用的消费者有确定性的读取路径 |

截至此基线，本仓有 9 个未关闭 Issue（#6、#8、#12、#16、#17、#18、#26、#131、#132）。关闭/迁移要按真实任务所有权和证据完成情况处理，不能因为退役而假装问题解决。

## 已查到的显式消费者与替换条件

1. **Agent Dev Kit**：`jiying2007/agent-dev-kit/manifests/integrations/digital-worker.json` 目前仍为 `status: active`，`.github/contracts/digital_worker_contract.py` 和 `.github/workflows/digital-worker-contract.yml` 有专门校验。若本消费方完全退役，需在 ADK 独立 PR 中同步调整/移除现行合同、CI 触发与文档，保持 ADK 对其他 consumer 的独立可用；不能简单删除 JSON 再声称旧 CI 绿色。
2. **Codex Runtime Binding**：`jiying2007/codex/manifests/integrations/digital-worker-runtime-binding.json` 仍为 active；`scripts/validate-runtime-binding.py` 和 `docs/session-bootstrap.md` 定义了显式 L2 Formal Evidence 路径。L0/L1 已不要求本仓，但 L2 需要精确的 Digital Worker Governance Identity/ETP。必须先决定停止提供 L2 还是由独立的保全证据入口接续，并在 Codex 独立 PR 验证“不再引用本仓”的新行为；不能静默降级 L2 到 L1。
3. **engineering-platform**：主线 `eng` 没有本仓 Runtime 依赖；但日常文档曾引用本仓三类模板。PR #308 将文件直接放入 `eng` 发行包，使用其实际安装包烟测验证，无须启动模型或设备。该项未合并前不得标为完成。

未检索到的本机/私有仓库消费者不能仅凭以上公开仓库检查假定不存在。永久删除前，应在正在使用的工作主机和项目上核查引用、安装脚本、定时任务及当前执行者。

## 明确的退出门槛

| 阶段 | 完成条件 | 当前 |
|---|---|---|
| A. 日常独立 | 三个模板随 `eng` 包发行；日常文档不再指向本仓；真实无模型安装通过 | PR #308 推进中 |
| B. 正式消费者退场 | ADK active consumer 合同和 Codex L2 的实际调用/准入路径已独立调整并验证；不伪造原 Formal 事实 | 未完成 |
| C. 历史证据保全 | 不可变的 Git 历史、完整有价值材料、证据/Issue 映射以及可恢复副本经过核对 | 未完成 |
| D. 使用主机切换 | 实际检查、备份及退出仍运行的旧进程/计划；必要时完成真实项目试用 | 未执行 |
| E. 仓库归档 | A—D 核验后使用 GitHub Archive 设为只读，保留历史 URL 与 commit 身份 | 未执行 |

**优先使用归档，不优先永久删除。** GitHub Archive 能停止活跃维护，同时保留检索、证据回读与追责所需的不可变提交引用。若确需永久删除，应额外取得 Git bundle/离线可恢复完整备份并验证恢复，确保所有活跃消费者和外部永久 URL 已迁移；删除是独立高风险管理动作，不纳入模板和执行器的普通 PR。

## 不做的事

不创建巡检任务、不引入额外控制面、不修改原有正式 evidence、不把 23 个 DEFINED Skill 批量晋升、不为兼容旧路径编写长期 shim、不消耗模型额度。最后的“全面移除”只以**没有运行时依赖、没有悬空消费者、历史可追溯、旧主机确实退出**为判断依据。
