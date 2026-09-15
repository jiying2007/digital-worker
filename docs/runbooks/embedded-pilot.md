# 嵌入式真实 Pilot 执行说明

Pilot 用于验证 Embedded Domain Closed Loop 和 Edge Foundation 目标责任模型能否在真实工程中形成可追溯闭环；它不自动授予 Production Ready，也不自动扩大 A0-A7 权限。

当前机器状态：`pilot-operations-ready`。

当前三轨：

| Track | 当前状态 | 剩余项 |
|---|---|---|
| Debug | 已选 SSC305 / SPI-NAND / UBI-UBIFS 只读问题 | 产品 exact repo/SHA + 原始日志/复现 + device/flash/kernel/test identity |
| Feature | `FEATURE-PCR02-OTA-001` 已 completed，`phase3_evidence_eligible=true` | 已闭环 |
| Review / Release | PCR02 v1.1.21 artifact identity + hosted distribution 已完成 | 实机 download/install/boot/rollback + required Verification + A7 human decision |

权威机器规则：

- `expert-groups/embedded-system/pilot/pilot-plan.yaml`
- `expert-groups/embedded-system/pilot/artifact-requirements.yaml`
- `scripts/embedded_pilot.py`
- `scripts/validate_material_manifest.py`

本文只解释如何使用这些机器 Contract，不建立第二套规则。

## 1. 当前阶段 Review 策略

当前阶段为 `iterative-pilot`。

Independent Review（独立审查）仍是 Assurance 能力，**优先使用，但 reviewer/tool 不可用时不是 Pilot completion 的硬门**。

允许的当前阶段替代证据：

- static checks；
- Hosted CI；
- traceable Verification Report。

替代时必须保持：

- 明确记录 Review 不可用；
- 不声称 `Independent Review PASS`；
- 不把 Hosted CI / Runtime-local PASS 当成 Device / HIL / Release PASS；
- 不因此扩大 A0-A7；
- Release action 仍受 A7 human gate 约束。

因此当前 Debug / Feature 可以在没有 `review_report_ref` 时完成；`verification_report_ref` 仍是所有三轨的硬要求。

Review / Release 轨即使没有 Independent Review，也**不能**跳过真实 device/release evidence 与适用的 A7 human decision。

## 2. 绑定真实任务

真实 Pilot 必须先形成 `task-brief v1`，至少具有：

- stable `work_item_id`；
- human owner；
- repo root；
- **full 40-hex exact Git base SHA**；
- Acceptance Criteria；
- required Verification；
- A0-A7 边界。

分支名、短 SHA、placeholder repo、synthetic 日志不能作为 real-run source identity。

初始化：

```bash
python scripts/embedded_pilot.py init \
  --run-id <RUN_ID> \
  --track <debug|feature|review_release> \
  --source-type real \
  --task-type <TASK_TYPE> \
  --workflow-mode <MODE> \
  --human-owner <OWNER> \
  --task-brief <TASK_BRIEF_JSON> \
  --repo-root <REPO_ROOT> \
  --base-commit <FULL_40_HEX_SHA>
```

可生成工作材料骨架：

```bash
python scripts/embedded_pilot_scaffold.py \
  expert-groups/embedded-system/pilot/runs/<RUN_ID>
```

## 3. Material Manifest（材料清单）

Scaffold 不猜测未知事实。材料不足时应诚实保持 `BLOCKED`。

终态规则：

- `planned / running / blocked` 可保持 `readiness=BLOCKED`；
- `complete` 前必须重新计算材料门槛；
- `BLOCKED` 不得进入 completed bundle；
- `DEGRADED` 必须有明确 `degradation_approved_by`；
- completed run 的 `validate` 会再次重算材料语义并核 frozen bundle；
- Debug 采用 **reproduction OR authoritative log**；
- Material readiness 不替代 Verification。

## 4. Engineering / Analysis

稳定责任模型：

```text
Edge Coordination Role
  → Domain Expert / Capability
  → Engineering execution
  → Verification
  → optional Independent Review when available
  → Closure
```

当前 Embedded System Expert 的专业能力：

- `embedded.architecture`
- `embedded.linux-bsp`
- `embedded.mcu-rtos`
- `embedded.driver-component`
- `embedded.debug-reliability`

Runtime Provider 可替换，不能拥有 Domain Verification / Release authority。

Debug 使用一份共享 `hypothesis_registry`，并持续区分：

`Observed / Inferred / Confirmed`。

## 5. 当前必须保留的闭环产物

所有真实 Pilot 至少保留：

1. Task Brief；
2. Verification Report；
3. Pilot Result；
4. `material_manifest`；
5. `acceptance_evidence_matrix`；
6. `knowledge_harvest`；
7. frozen `evidence-bundle.json`。

Feature 另外要求：

- Engineering Task Package；
- Delivery Receipt。

Debug 另外要求：

- shared Hypothesis Registry。

Independent Review 可用时可附加 `review_report`；当前阶段不可用时不再硬阻断 completion。

## 6. 收口与冻结证据

Feature 当前示例：

```bash
python scripts/embedded_pilot.py complete <RUN_DIR> \
  --engineering-task-package <engineering-task-package.json> \
  --delivery-receipt <delivery-receipt.json> \
  --verification-report <verification.json> \
  --pilot-result <pilot-result.json> \
  --extra material_manifest=<material-manifest.json> \
  --extra acceptance_evidence_matrix=<acceptance-evidence-matrix.md> \
  --extra knowledge_harvest=<knowledge-harvest.md>
```

Independent Review 已取得时，可额外传入：

```text
--review-report <review.json>
```

Debug 另外增加：

```text
--extra hypothesis_registry=<hypothesis-registry.json>
```

`complete` 会校验 Contract、Material readiness 和 required artifacts，随后生成 frozen evidence bundle。

Completed run 是 terminal。修正必须创建 superseding run，不能改写旧 evidence。

终态复核：

```bash
python scripts/embedded_pilot.py validate <RUN_DIR>
```

任何 artifact set / SHA / material readiness 漂移必须 fail-closed。

## 7. Verification 边界

Verification 仍是必需项，并且不得用以下内容替代：

- Runtime-local PASS；
- 单纯“代码能编译”；
- 不对应 exact source/artifact identity 的旧日志；
- Hosted CI 对 Device/HIL/Release 的跨层推断。

Verification Report 必须保留实际验证层与 `unverified_items`。

当前 Review waiver 只取消“独立 reviewer/tool 不可用时的流程阻塞”，不取消 Verification。

## 8. Review / Release 特殊边界

对于 `review_release`：

- artifact / distribution PASS 不等于 Device PASS；
- Device PASS 不自动等于 Release Approval；
- 如本次动作包含 release，A7 必须有 human decision；
- device identity、install、boot、result version、rollback/failure evidence 按实际 scope 保留；
- Independent Review 可用时继续作为附加 Assurance evidence。

## 9. Knowledge Harvest

`NO_KNOWLEDGE_DELTA` 合法。

有真实复用价值时记录 evidence-backed knowledge candidate；权威原文继续留在 Source，本仓只保 identity / provenance / evidence refs，不复制形成第二 SSOT。

## 10. Edge Foundation shadow receipt

真实 completed Pilot 通过 terminal integrity 后：

```bash
python scripts/embedded_pilot.py edge-shadow <RUN_DIR>
```

得到：

```text
<RUN_DIR>/edge-foundation-shadow-receipt.json
```

当前 `phase3_evidence_eligible=true` 需要：

- real source；
- run completed；
- Pilot Result present；
- outcome PASS；
- unauthorized actions = 0；
- audit trace complete。

Review Report 是否存在**不再是当前阶段 eligibility 条件**。

## 11. Phase-3 readiness

聚合三轨：

```bash
python scripts/embedded_pilot.py phase3-readiness \
  <RUNS_ROOT> \
  --output edge-foundation-phase3-readiness.json \
  --require-ready
```

门槛：

- Debug >= 1 eligible real receipt；
- Feature >= 1 eligible real receipt；
- Review/Release >= 1 eligible real receipt；
- total real completed >= 3；
- `incorrect_pass_rate = 0`；
- `unauthorized_actions = 0`；
- `audit_trace_completeness = 1.0`。

当前 Feature 已满足 1 条：`FEATURE-PCR02-OTA-001`。

因此当前仍是：

```text
Feature       1/1
Debug         0/1
ReviewRelease 0/1
phase3        BLOCKED
```

`canonical_routing_switched` 必须继续为 `false`。

## 12. Canonical switch 与旧 1+7

`ELIGIBLE_FOR_REVIEW` 只允许进入 canonical-switch 评审，不自动切换。

Phase-3 只允许变更：

1. canonical routing authority；
2. canonical routing selector entrypoint。

禁止顺手：

- 删除/改写 compatibility mapping；
- 删除旧 identity；
- 重写 Skill owner；
- 扩大 A0-A7；
- 改变 Verification/Review Assurance 语义；
- 绑定具体 Provider。

Canonical switch 稳定后才进入：

```text
Phase 4: deprecate legacy invocation
→ soak / rollback window
→ zero live-reference proof
→ Phase 5: physical removal
```

## 13. 当前下一动作

1. #6：补 SSC305/UBIFS exact source/log/device identity，形成 Debug real receipt；
2. #8：补 PCR02 实机 OTA/download/install/boot/rollback + Verification + A7 evidence，形成 Review/Release real receipt；
3. 达到 3/3 eligible 后运行 phase3-readiness 并进入 canonical-switch review。
