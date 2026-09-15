# 嵌入式真实 Pilot 执行说明

Pilot 用于验证 Embedded Domain Closed Loop 和真实产品工程成熟度，不用于证明 AI 永远正确，也不直接授予 Production Ready / Release Ready。

当前 **Edge Foundation 已是 canonical execution authority**。Product readiness 与 routing authority 解耦：Feature 已有 1 条 eligible real receipt；Debug 与 Review/Release 仍等待真实外部/设备 Evidence，因此 Product readiness 保持 BLOCKED。

机器入口：

- Domain：`domains/edge-foundation/domain.yaml`
- Routing：`domains/edge-foundation/routing.yaml`
- Runtime policy：`domains/edge-foundation/runtime/`
- Pilot plan：`domains/edge-foundation/pilot/pilot-plan.yaml`
- Artifact requirements：`domains/edge-foundation/pilot/artifact-requirements.yaml`
- Schemas：`domains/edge-foundation/schemas/`
- Knowledge Registry：`domains/edge-foundation/knowledge/registry.yaml`

策略基线：`docs/strategy/embedded-domain-closed-loop-v1.md`。快速入口：`docs/runbooks/embedded-closed-loop-quickstart.md`。

## 1. 绑定真实任务

真实 Pilot 必须形成稳定 Task Brief，并至少绑定：human owner、repo root、**full 40-hex exact Git base SHA**、Acceptance Criteria、required verification。`main/dev`、短 SHA、口头版本号都不能替代 immutable source identity。

同一 Run 的参与 Role / Expert / Capability / Assurance 共享同一个 Work Item / Run Identity 和 Material/System Context，不各自重建版本事实。

## 2. 初始化与 Scaffold

```bash
python scripts/edge_pilot.py init \
  --run-id <run-id> \
  --track <debug|feature|review_release> \
  --source-type real \
  --task-type <task-type> \
  --workflow-mode <mode> \
  --human-owner <owner> \
  --task-brief <task-brief.json> \
  --repo-root <repo-root> \
  --base-commit <full-40-hex-sha>

python scripts/edge_pilot_scaffold.py \
  domains/edge-foundation/pilot/runs/<run-id>
```

`embedded_pilot.py` / `embedded_pilot_scaffold.py` 保留为命令兼容入口，但数据和 Contract authority 与 `edge_*` 入口完全相同，均来自 Edge Foundation target tree。

Scaffold 不猜未知事实。源码、日志、设备、测试环境未确认时，Material Manifest 必须保持 `missing / BLOCKED`。

Material terminal rule：

- `planned / running / blocked` 可保持 `readiness=BLOCKED`；
- `complete` 前必须重新计算材料门槛；
- `BLOCKED` 不得进入 completed evidence bundle；
- `DEGRADED` 必须有明确 `degradation_approved_by`；
- completed run 的后续 `validate` 会再次重算材料门槛和 frozen bundle；
- Debug 采用 **reproduction OR authoritative log**；
- Material readiness 不替代 Verification 或 Review。

## 3. Canonical Routing 与责任模型

Task Type 先由 `domains/edge-foundation/routing.yaml` 映射到：

```text
target mode
→ Domain Expert
→ Embedded Capability
→ Assurance
```

Runtime mode 由 `runtime/task-modes.yaml` 约束。Runtime mode 只描述执行步骤，不改变责任归属。

跨域升级必须 Evidence-triggered。比如 Bring-up/Driver 出现板级电气状态、原理图、电源时序、信号/供电证据时，才允许升级到 Hardware Expert；没有 Evidence 不预加载跨域 Expert。

## 4. Knowledge Context

本地 Registry 是 bootstrap/catalog，不复制权威原文：

```bash
python scripts/edge_knowledge.py verify
python scripts/edge_knowledge.py query --text "<task terms>" --limit 10
```

长期 Context / Evidence lifecycle 由 Knowledge Hub 提供。`KNOWLEDGE_HUB_ROOT` 必须指向 `config/integrations/cross-repo-lock.json` 固定的 exact provider commit；Adapter 同时检查 Git HEAD 与 canonical contract digest，漂移即 BLOCK。

```bash
export KNOWLEDGE_HUB_ROOT=/path/to/exact-pinned/knowledge-hub
python scripts/edge_knowledge.py adapter-status
python scripts/edge_knowledge.py context \
  --cwd "$PWD" --query "<platform symptom subsystem>" \
  --task-type general --context-budget small --limit 3
python scripts/edge_knowledge.py evidence-pack \
  --query "<platform symptom subsystem>" \
  --scope-ref repository:<repo-id>
```

查询命中只是候选，仍必须核对 authority / version / ACL / provenance。

## 5. Session Bootstrap / Runtime Binding

Runtime Binding 可替换，但必须保留 frozen identity spine。以 Codex 为例，L2 formal session 应绑定 exact base、Engineering Task Package、digital-worker、Knowledge Hub、ADK release/source-set、Runtime distribution、sandbox/approval 与 Execution Receipt。

Runtime-local success 只证明执行事实，不得包含或推导：

```text
verification_pass
release_ready
domain_gate_pass
```

ADK Asset Profile 与 Runtime Profile 是不同身份；digital-worker 不硬编码 Runtime 私有 profile。

## 6. Engineering 执行

默认责任链：

```text
Technical Decision
→ Engineering Task Package
→ Engineer + Engineering Agent Runtime
→ Delivery Receipt
→ Verification
→ Review when required/available by current-stage policy
→ Closure
```

Debug 强制 Observed / Inferred / Confirmed，并维护一份共享 Hypothesis Registry。多仓 Feature 优先 `One Run → Multiple Engineering Packages`，每个 Package 独立 exact base / scope / delivery identity，Run 层统一收口。

## 7. 必需运行产物

所有真实 Pilot 收口至少包含：

1. `material_manifest`：共享 Material/System Context；
2. `acceptance_evidence_matrix`：Acceptance → Verification layer → Evidence；
3. `knowledge_harvest`：`NO_KNOWLEDGE_DELTA` 或 evidence-backed candidate；
4. track-specific structured artifacts；
5. `pilot-result`；
6. frozen `evidence-bundle.json`。

Debug 额外要求 `hypothesis_registry`。Feature 要求 Engineering Task Package + Delivery Receipt。Verification 在当前阶段仍为 completion 硬要求。

## 8. Current-stage Review Policy

Independent Review 是 Assurance 能力，但 iterative Pilot 阶段 **preferred, not hard-required when unavailable**。

Review unavailable 时，completion substitute 必须至少包含：

- traceable Verification report；
- static checks；
- Hosted CI evidence；
- reviewer/tool unavailable 的记录。

替代只解除当前 Pilot completion blocker，不等于 Independent Review PASS，不降低 Device/HIL/Release Evidence，不替代 A7 human release decision。

## 9. Complete 与冻结 Evidence

Feature 示例：

```bash
python scripts/edge_pilot.py complete <run-dir> \
  --engineering-task-package <engineering-task-package.json> \
  --delivery-receipt <delivery-receipt.json> \
  --verification-report <verification.json> \
  --pilot-result <pilot-result.json> \
  --extra material_manifest=<run-dir>/working/material-manifest.json \
  --extra acceptance_evidence_matrix=<run-dir>/working/acceptance-evidence-matrix.md \
  --extra knowledge_harvest=<run-dir>/working/knowledge-harvest.md
```

有 Review 时可额外传 `--review-report`。Debug 再增加：

```text
--extra hypothesis_registry=<run-dir>/working/hypothesis-registry.json
```

`complete` 会校验结构化 Contract、Material terminal readiness 和 required artifacts，生成 `evidence-bundle.json` 与 SHA-256。Completed run 是 terminal；修订历史证据必须创建 superseding run，禁止改写旧 run。

```bash
python scripts/edge_pilot.py validate <run-dir>
```

任何 Material、artifact set 或 SHA 漂移都必须 fail-closed。

## 10. Canonical Pilot Receipt

Completed Pilot 通过 terminal integrity 后生成 canonical receipt：

```bash
python scripts/edge_pilot.py receipt <run-dir>
```

默认输出：

```text
<run-dir>/edge-foundation-pilot-receipt.json
```

Receipt 明确绑定：

```text
routing_authority = edge-foundation
canonical_routing = true
task_type / workflow_mode
target_mode / target_experts / target_capabilities / assurance
eligibility_checks
product_readiness_eligible
```

只有 `source_real + completed + result_provided + outcome_pass + zero unauthorized actions + audit trace complete` 全部满足，receipt 才能计入 Product readiness。

## 11. Product Readiness

三轨聚合：

```bash
python scripts/edge_pilot.py product-readiness \
  domains/edge-foundation/pilot/runs \
  --output edge-foundation-product-readiness.json \
  --require-ready
```

当前门槛：Debug / Feature / Review-Release 各至少 1 个 eligible real receipt，总计至少 3；同时 `incorrect_pass_rate=0`、`unauthorized_actions=0`、`audit_trace_completeness=1.0`。

当前真实状态：Feature=1，Debug=0，Review/Release=0，所以 Product readiness 正确返回 BLOCKED。**该状态不控制或回退 canonical routing。** 全部满足后也只进入 Productionization Review，不自动声明 Release Ready / Production Ready。

## 12. Pilot Metrics

```bash
python scripts/evaluate_edge_pilot.py \
  <pilot-result...> \
  --output pilot-metrics.json \
  --markdown-output pilot-metrics.md
```

门槛来自 `domains/edge-foundation/pilot/pilot-plan.yaml`。Synthetic 只验证工具链，不计入真实 Product readiness。

## 13. Knowledge Harvest

`NO_KNOWLEDGE_DELTA` 是合法结果。对 evidence-backed `KNOWLEDGE_CANDIDATE`，使用跨仓 handoff contract 路由到 Knowledge Hub 生命周期，不在 digital-worker 复制第二份知识原文。

```bash
python scripts/edge_knowledge.py proposal-route --proposal <PROPOSAL_JSON>
```

## 14. Closure Gate

接受真实 completed run 前至少要求：

- materially used provider/binding exact identity 已核验；
- Acceptance Criteria 均映射具体 Evidence；
- source/artifact/device/test identity exact 或明确 unresolved；
- Execution Receipt 保留；
- Verification 真实且不跨层推导；
- Review policy 已解析；
- `incorrect_pass=0` 且无 unauthorized action；
- Knowledge Harvest finalized；
- 新 Schema/Skill/Capability 只由重复真实缺口触发。

仓库仍处于 `iterative-development`，server-side protection 暂不是 real Pilot completion gate；进入 Productionization 前运行：

```bash
python scripts/verify_repository_governance.py --strict
```

## 15. 当前实施边界

不要因为单次 Pilot 成功就新增统一 Knowledge Platform、Vector DB、Context Broker、Knowledge Graph、Integration Expert、central Runtime Gateway 或 Runtime-specific control plane。稳定模型保持 **责任/Contract 稳定 + replaceable Runtime + thin Session Bootstrap + independent Assurance + Evidence-driven evolution**。
