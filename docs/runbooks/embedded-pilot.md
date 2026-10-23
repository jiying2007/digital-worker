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

材料校验从 task type 的 `material-requirements.yaml` 和 Task Brief 验证要求重新推导必需项，至少保留 repo、base_commit 和 test_environment；要求 Device/HIL/Release 验证时还必须具备 device_identity。删除项目或把 `required` 改成 false 不会降低门槛。历史清单中已 available 的材料可继续使用，无须改写冻结证据。

终态材料验证还必须绑定 `--pilot-run <run-dir>/pilot-run.json`，比较 run_id、仓库来源与 base_commit；Pilot CLI 自动传入该上下文。独立结构检查未提供 Run 时会返回 `identity_validated=false`、`terminal_acceptable=false`；请求 `--require-terminal-ready` 而缺 Run 则阻断。仓库标识接受等价 GitHub HTTPS URL（可带 `.git` 或尾斜杠），提交比较忽略十六进制大小写。`repo.version` 可描述结果提交，不要求它等于 base commit；身份冲突不能通过 DEGRADED 放行。

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

工具在 Verification 的 `review_substitute` 中检查 `unavailable_reason`，以及
`static_checks` / `hosted_ci` 的 `{ "status": "pass", "evidence_ref": "https://..." }`。
两项引用必须同时列入 `evidence_refs`，使用无凭据 URI 或完整 `sha256:<64hex>`，
禁止只写“CI 成功”等文字。该声明随 Verification 一起冻结；缺失时 completion、终态 validate
和 receipt 重算均拒绝。历史 Verification 不自动迁移；新增的
`verification-report.review-policy-v2.json` 仅结构化已有证据，不代表重新执行历史 CI。
新增 `review_substitute` 字段需要新版 Verification schema，旧版读取器会拒绝该字段。
迁移时保留原报告，以新增报告重建 Run；已有独立 Review 且使用旧字段集的文档继续可读。
回退时只回退本轮代码/schema，并重新生成对应版本的派生回执，不改写既有终态证据。

completed Run 的 Verification 和已提供的 Review 均须填写非空 `implementation_owner`，
以及独立的 `verifier` / `reviewer`；仍须 `independence_confirmed=true`。
校验会去除身份两端空白，拒绝验证者、审查者或已提供的 `decision_actor_identity_ref`
等于实现者。不同身份字符串只是本地声明，不能替代主体认证或独立审查事实。
缺少主体的历史报告可在非终态检查材料；终态验证和资格重算会阻断。
应由实际责任人补齐真实报告并创建 superseding Run，不改写历史终态证据、不代填主体。

终态 required 且 available 的 `device_identity`、`test_environment` 必须提供非空
`source` 和 `evidence_ref`。planned/running 可继续使用 missing/null 表达未知信息。
Run 内的派生报告不得覆盖 `pilot-run.json` 或任何冻结引用，输出路径不得穿过符号链接；
写入遵守 Run 写锁并采用原子替换。

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

`complete` 会校验结构化 Contract、Material terminal readiness 和 required artifacts，将附件和 `evidence-bundle.json` 写入独立 generation，并最后原子切换 Run 引用。消费者通过 `pilot-run.json` 的 `evidence_bundle_ref` 定位 bundle，不固定读取根目录文件；历史平铺 Run 继续可读。Completed run 是 terminal；修订历史证据必须创建 superseding run，禁止改写旧 run。写锁、错误码和只读恢复见[本地工具操作](tool-quality.md)。

完成操作先在临时候选目录运行全部终态校验，通过后发布附件和 bundle，最后原子替换 Run 状态。校验失败保留原目录及可重试状态；发布过程中若发生 I/O 故障，Run 的终态标记尚未发布时可修正后重试。

```bash
python scripts/edge_pilot.py validate <run-dir>
```

任何 Material、artifact set 或 SHA 漂移都必须 fail-closed。

## 10. Canonical Pilot Receipt

Completed Pilot 通过 terminal integrity 后生成 canonical receipt：

```bash
python scripts/edge_pilot.py pilot-receipt <run-dir>
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

真实 completed Run 必须重新通过完整 Run、材料及 frozen bundle 校验，提供与 bundle 一致的 Pilot result。只有来源真实、完成、结果 PASS、零未授权动作、审计完整、没有错误 PASS、必需验证完成、证据满足且无 unsupported claims，receipt 才能计入 Product readiness。

`complete` 拒绝 Run 内的文件、目录和悬空符号链接，先验证独立临时副本，失败保留原 Run，成功最后发布 Run 状态。已提供的 Review 必须为 `APPROVE` 或 `APPROVE_WITH_RISK`；`BLOCKED` / `REQUEST_CHANGES` 会使 `review_acceptable=false`。Review 不可用时继续执行当前阶段的替代策略。

新 receipt 的 `evidence` 保存相对于 receipt 的 Run 引用和 Run SHA-256。Product readiness 聚合时会重新加载原 Run、核验冻结附件并重算 receipt；仅有布尔资格字段或旧的无来源 real receipt 不再足以计数，必须从原始冻结 Run 重新生成。搬移证据时保留 Run 及其附件的相对目录关系。

## 11. Product Readiness

三轨聚合：

```bash
python scripts/edge_pilot.py product-readiness \
  domains/edge-foundation/pilot/runs \
  --output edge-foundation-product-readiness.json \
  --require-ready
```

当前门槛：Debug / Feature / Review-Release 各至少 1 个 eligible real receipt，总计至少 3；同时 `incorrect_pass_rate=0`、`unauthorized_actions=0`、`audit_trace_completeness=1.0`。

安全门槛检查本次显式输入集合中的全部 real completed Run，不能通过跳过不合格 receipt 隐藏违规。三轨数量满足但集合中存在错误 PASS、未授权动作或审计缺项时仍返回 BLOCKED；synthetic 与未完成 Run 不计入真实覆盖。

当前真实状态：Feature=1，Debug=0，Review/Release=0，所以 Product readiness 正确返回 BLOCKED。**该状态不控制或回退 canonical routing。** 全部满足后也只进入 Productionization Review，不自动声明 Release Ready / Production Ready。

## 12. Pilot Metrics

```bash
python scripts/evaluate_edge_pilot.py \
  <pilot-result...> \
  --output pilot-metrics.json \
  --markdown-output pilot-metrics.md
```

门槛来自 `domains/edge-foundation/pilot/pilot-plan.yaml`。Synthetic 只验证工具链，不计入真实 Product readiness。

该结果入口仅输出描述性统计：重复 run_id 被拒绝，BLOCKED 不计入通过数量。兼容字段 `real_completed_runs` 和 `track_coverage` 只统计自报的 real PASS 结果，不证明 Run 已完成；`promotion_eligible` 固定为 false，并包含 `canonical-receipt-evaluation-required`。产品资格使用上节 canonical receipt 聚合入口。

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

跨仓 checkout verifier 的 `--fetch` 只接受全新目标目录，已有目录或符号链接一律保留并拒绝；先在临时目录获取 exact commit，确认 HEAD 后发布。重复验证已有 checkout 时不传 `--fetch`；需要重新获取时选择新目录。

仓库仍处于 `iterative-development`，server-side protection 暂不是 real Pilot completion gate；进入 Productionization 前运行：

```bash
python scripts/verify_repository_governance.py --strict
```

## 15. 当前实施边界

不要因为单次 Pilot 成功就新增统一 Knowledge Platform、Vector DB、Context Broker、Knowledge Graph、Integration Expert、central Runtime Gateway 或 Runtime-specific control plane。稳定模型保持 **责任/Contract 稳定 + replaceable Runtime + thin Session Bootstrap + independent Assurance + Evidence-driven evolution**。
