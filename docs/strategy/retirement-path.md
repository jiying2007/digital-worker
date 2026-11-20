# digital-worker 日常退出与最终退役边界

日期：2026-11-18
基线：`7decf126ee8a83cfc609401c12ebd85153205cea`
状态（2026-11-20 复核）：**公开主线活跃消费者已大幅解除；历史消费仍需保全，私有主机未核验，暂不永久删除**。

## 决策

个人和小团队的实际工程任务由项目的 Git/CI + 已授权 Codex CLI/ADK 执行；远程飞书服务由现有 `jiying2007/codex` 维护。`engineering-platform/tool/eng` 也已进入退出主线。本仓不是任何日常任务、CLI 登录、构建、验收或 Knowledge Hub 的依赖。停止建设第二套日常执行器、中心台账、专家协调服务和额外安装系统。

这不是否定原始嵌入式参考资料或改变已冻结的 Formal Pilot 结论。已有证明缺口（包括 Debug、Review/Release、Skill 评测和 R2）保持未完成，不为“仓库退役”批量关闭 Issue，也不把 BLOCKED 改为 PASS。

## 当前保留对象（不能当作无价值残留删除）

| 类别 | 检查边界 | 处置 |
|---|---|---|
| 日常三类 Markdown 模板 | `docs/templates/{debug-fix,feature-change,review-release}.md` | 已在 `engineering-platform` [PR #308](https://github.com/jiying2007/engineering-platform/pull/308) 合并，准确复制到发行包并由实际 PR 安装烟测核验 |
| 领域方法 | `domains/edge-foundation/skills/` 的 23 个 canonical 定义 | 当前最低成熟度仅 DEFINED；与 ADK 逐项去重，不能直接作为成熟 Skills 批量导入 |
| 唯一参考资料 | `嵌入式系统专家团-核心参考/`、`产品专家团-核心参考/` | 需要保留的事实/方法按实际用途迁至项目或 Knowledge Hub 的受复核资料；不凭目录数量创建新的 Skill |
| 冻结的 Pilot/产品/R2 证据 | `domains/edge-foundation/pilot/evidence/`、`reports/runtime-r2/` 等 | 原 SHA、Work/Run、来源、合同、结果及 UNKNOWN/BLOCKED 语义保留，不重写为另一仓库的新证明 |
| 研发开源合同与迁移历史 | `contracts/`、`docs/adr/`、`schemas/`、`docs/archive/` | 可归档只读，确保明确采用的消费者有确定性的读取路径 |

截至此基线，本仓有 9 个未关闭 Issue（#6、#8、#12、#16、#17、#18、#26、#131、#132）。关闭/迁移要按真实任务所有权和证据完成情况处理，不能因为退役而假装问题解决。

## 2026-11-20 已核对的消费者状态

1. **Agent Dev Kit**：当前 \`main\` Tree 已不含此前的 \`manifests/integrations/digital-worker.json\`、\`.github/contracts/digital_worker_contract.py\`、\`.github/workflows/digital-worker-contract.yml\`；存在对应旧消费者退役变更记录。历史提交与 evidence 仍然可追溯；不能仅由当前文件缺席推断所有私有外部消费者已退出。
2. **Codex**：当前 \`manifests/session_bootstrap.json\` 与 \`docs/session-bootstrap.md\` 仅保留 L0/L1；L2 参数被显式拒绝，旧 Runtime Receipt v2 schema 仅用于历史验证。日常链路不再依赖 Digital Worker。
3. **llm_agent**：\`manifests/digital_worker_runtime_pilot.json\` 为 \`retired-historical-only\`、\`report-only\`，保留旧资格合同断言作为证据审计，不再有活跃 R2 资格权威；旧链接不应当作新的启动要求。
4. **engineering-platform**：历史三模板曾经合入，但 \`eng\` 执行器也不再是建议的新日常入口。参见其 Final 1.5 决策 PR #312。
5. **未知领域**：尚未在实际主机、非公开 GitLab/局域网仓库、自动化、设备和工作区内完成搜索/停机核验。这是退出前的明确阻塞，不能称为“全部消费者为零”。

详细逐项映射见 [absorption-map-20261120.md](absorption-map-20261120.md)。历史冻结 R2/L2/产品资格决策不改写为 PASS。

## 明确的退出门槛

| 阶段 | 完成条件 | 当前 |
|---|---|---|
| A. 日常独立 | 三个模板随 `eng` 包发行；日常文档不再指向本仓；真实无模型安装通过 | **源码/PR 安装烟测完成**（#308，`f1724353`）；真实开发机任务采用另属阶段 D |
| B. 正式消费者退场 | ADK 专属合同和 Codex L2 活动入口切断，llm_agent 保留只读历史，其他实际消费主机待核对 | **公开当前代码路径已收敛；全环境未完成** |
| C. 历史证据保全 | 不可变的 Git 历史、完整有价值材料、证据/Issue 映射以及可恢复副本经过核对 | 未完成 |
| D. 使用主机切换 | 实际检查、备份及退出仍运行的旧进程/计划；必要时完成真实项目试用 | 未执行 |
| E. 仓库归档 | A—D 核验后使用 GitHub Archive 设为只读，保留历史 URL 与 commit 身份 | 未执行 |

**优先使用归档，不优先永久删除。** GitHub Archive 能停止活跃维护，同时保留检索、证据回读与追责所需的不可变提交引用。若确需永久删除，应额外取得 Git bundle/离线可恢复完整备份并验证恢复，确保所有活跃消费者和外部永久 URL 已迁移；删除是独立高风险管理动作，不纳入模板和执行器的普通 PR。

## 不做的事

不创建巡检任务、不引入额外控制面、不修改原有正式 evidence、不把 23 个 DEFINED Skill 批量晋升、不为兼容旧路径编写长期 shim、不消耗模型额度。最后的“全面移除”只以**没有运行时依赖、没有悬空消费者、历史可追溯、旧主机确实退出**为判断依据。
