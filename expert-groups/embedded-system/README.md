# 嵌入式兼容执行面（Embedded Legacy Compatibility Surface）

- Machine version: `0.7.0`
- Implementation status: `pilot-operations-ready`
- Semantic lifecycle: `legacy-compatibility-surface`
- Target responsibility model: `../../domains/edge-foundation/domain.yaml`
- Target ADR: `../../docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md`
- Current stage strategy: `../../docs/strategy/embedded-domain-closed-loop-v1.md`

## 这是什么

本目录保存当前仍在运行的嵌入式 `1+7` Task / Gate / Skill / Contract / Golden Case / Pilot 机器资产。它继续承担 **canonical execution 与 rollback**，但不再代表端侧目标组织结构，也不再扩展新的 legacy Expert identity。

目标责任模型是：

```text
Edge Foundation Domain
├─ Structure Expert
├─ Hardware Expert
└─ Embedded System Expert
    └─ Capability → Skill
```

旧 8 个身份到目标模型的唯一桥接表：

`../../domains/edge-foundation/compatibility/embedded-1plus7-mapping.yaml`

该 mapping 只保存静态 8/8 identity binding、removal gate 和 migration invariants，**不保存 mutable phase/readiness 状态**。真实晋级状态由 Pilot receipt + `evaluate_edge_foundation_phase3_readiness.py` 计算。

## 当前仍保留的能力资产

现有兼容面仍包含：

- 8 个 legacy digital identities；
- 23 个 P0 Skills；
- 14 类 Task 与现有 Workflow Mode；
- Gate / Action / Material / Evidence 治理；
- Engineering Handoff；
- Golden Cases；
- Pilot Run / Result / Metrics / Evidence Bundle；
- Verification / Independent Review 独立性；
- Knowledge Registry；
- fail-closed CI。

这些资产会按证据逐步迁移为 Embedded Expert 的 Capability / Skill 或 Assurance contract，而不是一次性删除。

## Provider-neutral 与 Runtime 边界

- Expert identity 不绑定 Codex / Claude / WorkBuddy / 其他模型；
- Engineering execution 是 `Engineer + Engineering Agent Runtime`；
- Runtime Provider 为 `not-frozen`；
- Knowledge Provider 不自动成为所有知识 SSOT；
- Source 遵循 `source_of_truth_stays_at_source`；
- Provider 切换不得改变 Task taxonomy、Gate、Evidence、Verification、Review 或 A0-A7 语义。

所有 Runtime 消费 `engineering-task-package`，输出 `delivery-receipt + evidence`，并继续经过独立 Verification / Review。

## 真实 Pilot 当前进度

| Track | 状态 | 剩余项 |
|---|---|---|
| Debug | 已选 SSC305 / SPI-NAND / UBI-UBIFS 只读问题 | 产品 repo exact SHA、原始日志、device/flash/kernel/test identity |
| Feature | PCR02 OTA artifact identity 已完成真实 Engineering + repeatable Verification | Independent Review + structured terminal bundle |
| Review / Release | PCR02 v1.1.21 artifact identity + HTTP/HTTPS distribution evidence 已完成 | device download/install/boot/rollback、Independent Review、human release gate |

Synthetic 只验证工具链，不计入 productionization / phase-3 promotion。

## 真实 Run 最小闭环

```text
One Work Item / Run
+ Shared Material/System Context
+ Exact Source / Artifact Identity
+ Acceptance → Evidence
+ Engineering Delivery
+ Verification
+ Independent Review
+ Knowledge Harvest
```

Debug 另外要求共享 `hypothesis_registry`。

Material Manifest 规则：

- planned/running/blocked 可诚实保持 `BLOCKED`；
- `complete` 前必须 `READY` 或明确批准的 `DEGRADED`；
- Debug 接受 `reproduction OR authoritative log`；
- completed run 会重新校验 Material Manifest 和 frozen evidence bundle；
- Material readiness 不替代 Verification / Independent Review。

唯一详细操作说明：`../../docs/runbooks/embedded-pilot.md`。

## Knowledge / Context

- 当前 Registry：`knowledge/registry.yaml`；
- Registry 只做索引和 authority pointer，不复制权威原文；
- 外部 Source 必须保留 source/version/ACL/provenance；
- 原始现场日志、core、固件等默认保留在受控权威系统，本仓只引用 identity/evidence。

## Canonical routing 迁移边界

当前仍保持：

```text
canonical_routing_switched = false
```

Phase-3 只有三轨 eligible real evidence + 独立评审后才能发起，并且只允许：

1. 切换 canonical routing authority；
2. 引入 `canonical-routing.yaml` selector entrypoint。

Phase-3 禁止改写 compatibility mapping、废弃/删除旧 identity、重写 Skill owner、扩大 A0-A7、改变 Verification / Review 独立性或绑定 Provider。

旧 identity deprecation 与 removal 必须分别进入后续独立阶段；在此之前本目录仍是合法执行/rollback surface，不能直接删除。

## 成熟度边界

当前只目标推进到 **E2 Engineering Closed Loop，并为 E3 Knowledge Closed Loop 建基础**。即使三轨门槛全部满足，也只进入独立 productionization / canonical-routing review；不自动成为 Production Ready，不自动扩大 A3-A7。
