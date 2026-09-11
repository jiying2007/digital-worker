# 嵌入式系统专家团

- Architecture status: `frozen`
- Implementation status: `pilot-operations-ready`
- Version: `0.7.0`
- Architecture model: `provider-neutral`
- Date: 2026-09-11
- Owner domain: 研发中心 / 嵌入式系统（软件）
- Current stage strategy: `docs/strategy/embedded-domain-closed-loop-v1.md`

## 当前能力

当前已经具备从结构化接单到真实 Pilot 操作的完整基础设施：1+7 核心专家、23 个 P0 Skills、Gate/Action/Material 治理、Engineering Handoff、Product Cross-Team Contract、Golden Cases、Pilot Run/Result/Metrics，以及 fail-closed CI。

当前阶段不再继续扩 Agent/平台，而是推进 **Embedded Domain Closed Loop V1**：先让嵌入式自身形成 Task / Engineering / Quality / Knowledge / Capability 五个闭环，再通过 Adapter 向企业上下游扩展。

V1 最小执行集固定为：

```text
One Work Item / Run
+ Shared Material/System Context
+ One Hypothesis Registry for Debug
+ Exact Source / Artifact Identity
+ Acceptance -> Evidence
+ Knowledge Harvest
+ Embedded Knowledge Registry
```

## Provider-neutral 基线

v0.7.0 的关键变化不是扩 Agent/Skill，而是把专家团与具体 Provider 解耦：

- Expert identity 不绑定 Codex / Claude / 其他模型；
- `phase.execution` 统一为 `Engineer + Engineering Agent Runtime`；
- Runtime Provider 当前 `not-frozen`；
- Gate K 不绑定 WeKnora/飞书等具体 Knowledge Provider；
- Knowledge Source 遵循 `source_of_truth_stays_at_source`；
- Provider 切换不得改变 task taxonomy、Gate、Evidence、Verification 和 Review 语义。

## Engineering Runtime

允许候选包括：Codex、Claude Code、IDE Agent、Internal Agent 和未来受控 Runtime Gateway。

所有 Runtime 必须消费相同 `engineering-task-package`，输出 `delivery-receipt + evidence`，并继续经过独立 Verification / Review。Interaction / Work Item Provider 默认不得直接控制个人开发机和 A6/A7 高风险动作。

## Knowledge / Context

专家团当前只冻结原则，不冻结知识平台：

- 飞书/协作文档、NAS、Git、CI/HIL、Artifact Store 等按事实类型分别保留权威；
- WeKnora 或其他系统可以成为 Knowledge Provider，但不自动成为所有知识 SSOT；
- 关键上下文必须保留 source/version/ACL/provenance；
- 当前 Embedded Knowledge Registry：`knowledge/registry.yaml`；
- Registry 首版状态为 `internal-seed`，50 条均来自仓库内可核验 Source；
- NAS / 飞书 / CI-HIL / 历史 RCA 等真实外部 Source 继续由 #16 扩展；
- Registry 只做索引和 authority pointer，不复制原始权威形成第二 SSOT。

## 真实 Pilot 关键规则

- `real` run 必须绑定 `repo_root + exact base_commit`，不能只写漂移分支名；
- 所有运行期 artifact ref 必须位于当前 run directory 内，禁止路径逃逸；
- completed run 必须生成带 SHA256 的 `evidence-bundle.json`；
- 三条轨道都必须附加 `material_manifest`、`acceptance_evidence_matrix`、`knowledge_harvest`；
- `debug` 另外必须包含共享 Hypothesis Registry；
- `feature` 必须包含 engineering-task-package、delivery-receipt、verification、independent review 和 pilot-result；
- `review_release` 必须包含 verification/review/pilot-result；
- Knowledge Harvest 允许 `NO_KNOWLEDGE_DELTA`，禁止为了流程制造伪知识；
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
```

收口时除原有 track artifacts 外，至少附加：

```text
--extra material_manifest=<material-manifest.json>
--extra acceptance_evidence_matrix=<acceptance-evidence-matrix.md>
--extra knowledge_harvest=<knowledge-harvest.md>
```

Debug 再附加：

```text
--extra hypothesis_registry=<hypothesis-registry.json>
```

详细说明见 `docs/runbooks/embedded-pilot.md`。

## Pilot 生产化边界

真实 Pilot 仍要求 debug / feature / review_release 三轨各至少 1 个 completed run，`incorrect_pass_rate=0`、`unauthorized_actions=0`、`audit_trace_completeness=1.0`。

当前阶段只目标推进到 **E2 Engineering Closed Loop，并为 E3 Knowledge Closed Loop 建基础**。即使满足所有门槛，也只允许进入独立人工 productionization review，不自动成为 Production Ready，不自动扩大 A3-A7。
