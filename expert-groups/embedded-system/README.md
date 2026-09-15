# 嵌入式兼容执行面（Embedded Legacy Compatibility Surface）

- Machine version: `0.7.0`
- Semantic lifecycle: `legacy-compatibility-surface`
- Target responsibility model: `../../domains/edge-foundation/domain.yaml`
- Compatibility mapping: `../../domains/edge-foundation/compatibility/embedded-1plus7-mapping.yaml`
- Canonical routing: **not switched**

## 1. 目录职责

本目录只保存 canonical switch 前仍被实际执行链、rollback 或历史 Contract 消费的 compatibility assets。它**不再定义目标组织、Skill ownership、Gate ownership 或 Golden Case authority**，也不得新增 legacy Expert identity。

目标责任模型由 `domains/edge-foundation/**` 定义：

```text
Edge Foundation Domain
├─ Edge Coordination Role
├─ Structure Expert
├─ Hardware Expert
└─ Embedded System Expert
   └─ Capability → Skill

Assurance
├─ Verification
└─ Independent Review
```

## 2. 当前仍保留的 compatibility surface

- 8 个 legacy execution identities 与其 I/O adapter；
- 14 类 Task 的当前 execution routing / workflow modes；
- 23 个 Skill 的现有物理实现文件；
- Gate / Action / Material / Evidence compatibility contracts；
- Engineering Handoff / Pilot operational assets；
- Knowledge bootstrap registry；
- fail-closed schemas / fixtures / CI 所需兼容入口。

其中 target ownership 已迁移：

- Skill ownership → `../../domains/edge-foundation/skills.yaml`；
- Gate ownership → `../../domains/edge-foundation/gate-policy.yaml`；
- Golden Case authority → `../../domains/edge-foundation/evaluation/golden-cases.yaml`。

`tests/golden-cases.yaml` 现在仅是 retirement pointer，不再包含第二份 case dataset。

## 3. Provider / Runtime 边界

- Expert responsibility 不绑定 Codex、Claude、WorkBuddy 或其他 Runtime；
- Engineering execution = Engineer + replaceable Engineering Agent Runtime；
- Runtime-local PASS 不等于 Domain Verification PASS；
- Source of Truth stays at source；
- Provider 切换不得改变 Task/Gate/Evidence/A0-A7 语义。

## 4. Pilot 当前状态

| Track | 状态 | 剩余真实 blocker |
|---|---|---|
| Feature | **DONE / phase3 eligible** | `FEATURE-PCR02-OTA-001` 已 terminalized |
| Debug | OPEN | SSC305/UBIFS exact source + raw log/reproduction + device identity |
| Review / Release | OPEN | PCR02 device install/boot/rollback + required Verification + applicable A7 decision |

当前 iterative Pilot 阶段若 Independent Review unavailable，可由 static checks + Hosted CI + traceable Verification evidence 完成 Pilot；这不表示 Independent Review PASS，也不能跨层推导 Device/HIL/Release PASS。

## 5. 迁移边界

当前必须保持：

```text
canonical_routing_switched = false
```

因此当前 execution adapters 不能被整体物理删除。但任何已经 target-owned、且不再被执行依赖的数据副本应先收敛为单一 authority；Golden Cases 即按此原则完成去重。

达到三轨 eligible real receipt 后，phase3-readiness 才可能进入 `ELIGIBLE_FOR_REVIEW`。Canonical switch、legacy deprecation、legacy physical removal 分别是后续独立阶段，不能提前合并为一次大爆炸迁移。
