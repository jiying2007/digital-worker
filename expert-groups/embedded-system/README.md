# 嵌入式系统专家团

- Architecture status: `frozen`
- Implementation status: `pilot-operations-ready`
- Version: `0.7.0`
- Architecture model: `provider-neutral`
- Date: 2026-09-11
- Owner domain: 研发中心 / 嵌入式系统（软件）

## 当前能力

当前已经具备从结构化接单到真实 Pilot 操作的完整基础设施：1+7 核心专家、23 个 P0 Skills、Gate/Action/Material 治理、Engineering Handoff、Product Cross-Team Contract、12 个 Golden Cases、Pilot Run/Result/Metrics，以及 fail-closed CI。

v0.7.0 的关键变化不是扩 Agent/Skill，而是把专家团与具体 Provider 解耦：

- Expert identity 不绑定 Codex / Claude / 其他模型；
- `phase.execution` 统一为 `Engineer + Engineering Agent Runtime`；
- Runtime Provider 当前 `not-frozen`；
- Gate K 不绑定 WeKnora/飞书等具体 Knowledge Provider；
- Knowledge Source 遵循 `source_of_truth_stays_at_source`；
- Provider 切换不得改变 task taxonomy、Gate、Evidence、Verification 和 Review 语义。

## Engineering Runtime

允许候选包括：

- Codex；
- Claude Code；
- IDE Agent；
- Internal Agent；
- 未来受控 Agent Runtime Gateway。

所有 Runtime 必须消费相同 `engineering-task-package`，输出 `delivery-receipt + evidence`，并继续经过独立 Verification / Review。

Interaction / Work Item Provider 默认不得直接控制个人开发机和 A6/A7 高风险动作。

## Knowledge / Context

专家团当前只冻结原则，不冻结知识平台：

- 飞书/协作文档、NAS、Git、CI/HIL、Artifact Store 等按事实类型分别保留权威；
- WeKnora 或其他系统可以成为 Knowledge Provider，但不自动成为所有知识 SSOT；
- 后续通过 Knowledge Registry / Gateway / Context Broker PoC 评估统一访问；
- 关键上下文必须保留 source/version/ACL/provenance。

## 真实 Pilot 关键规则

- `real` run 必须绑定 `repo_root + exact base_commit`，不能只写漂移分支名；
- 所有运行期 artifact ref 必须位于当前 run directory 内，禁止路径逃逸；
- completed run 必须生成带 SHA256 的 `evidence-bundle.json`；
- `debug` 必须包含 Hypothesis Registry；
- `feature` 必须包含 engineering-task-package、delivery-receipt、verification、independent review 和 pilot-result；
- `review_release` 必须包含 verification/review/pilot-result；
- 原始现场日志、core、固件等默认不提交到本仓，保留受控系统中的权威引用。

## 操作示例

```bash
python scripts/embedded_pilot.py init \
  --run-id PILOT-DEBUG-001 \
  --track debug --source-type real \
  --task-type defect_debugging --workflow-mode diagnostic_chain \
  --human-owner <owner> --task-brief <task-brief.json> \
  --repo-root <repo-root> --base-commit <exact-sha>

python scripts/embedded_pilot.py status expert-groups/embedded-system/pilot/runs/PILOT-DEBUG-001 running
python scripts/embedded_pilot.py validate expert-groups/embedded-system/pilot/runs/PILOT-DEBUG-001
```

收口时使用 `complete` 附加对应 track 的结构化产物；工具自动生成 Evidence Bundle 并做 fail-closed 验证。

## Pilot 生产化边界

真实 Pilot 仍要求 debug / feature / review_release 三轨各至少 1 个 completed run，`incorrect_pass_rate=0`、`unauthorized_actions=0`、`audit_trace_completeness=1.0`。

新增总体架构要求：至少用同一工程 Contract 对比两个 Engineering Agent Runtime，证明 Provider 可替换不会破坏 Evidence/Verification 语义。

即使满足所有门槛，也只允许进入独立人工 productionization review，不自动成为 Production Ready。
