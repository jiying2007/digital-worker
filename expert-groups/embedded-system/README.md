# 嵌入式系统专家团

- Architecture status: `frozen`
- Implementation status: `pilot-operations-ready`
- Version: `0.6.0`
- Date: 2026-09-11
- Owner domain: 研发中心 / 嵌入式系统（软件）

## 当前能力

当前已经具备从结构化接单到真实 Pilot 操作的完整基础设施：1+7 核心专家、23 个 P0 Skills、Gate/Action/Material 治理、Engineering Handoff、Product Cross-Team Contract、12 个 Golden Cases、Pilot Run/Result/Metrics，以及 fail-closed CI。

本阶段新增 `scripts/embedded_pilot.py`，统一真实 Pilot 的 `init -> running/blocked -> complete -> evidence bundle -> validate -> summary`。完成态不再依赖人工拼 JSON；每条轨道必须满足 `pilot/artifact-requirements.yaml`。

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

真实 Pilot 仍要求 debug / feature / review_release 三轨各至少 1 个 completed run，`incorrect_pass_rate=0`、`unauthorized_actions=0`、`audit_trace_completeness=1.0`。评分器现在直接读取 `pilot-plan.yaml`，避免配置与代码门槛漂移。

即使满足所有门槛，也只允许进入独立人工 productionization review，不自动成为 Production Ready。
