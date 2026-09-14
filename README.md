# digital-worker

研发中心 AI 数字员工主仓。这里维护稳定的责任、任务、工程交接、证据、验证、审查、权限和成熟度规则；不复制知识全文、通用 Agent 资产或具体 Coding Runtime。

## 当前阶段

仓库处于 **iterative-development**。端侧目标责任模型已经冻结为：

```text
Domain（领域）
  → Expert（专家）
    → Capability（能力域）
      → Skill（技能）
```

端侧底座领域（Edge Foundation Domain）当前由 **结构专家、硬件专家、嵌入式系统专家**三个 Domain Expert 组成；端侧协调是 Role（角色），不是第四个技术专家。Orchestration（编排）、Execution（执行）和 Assurance（可信保障）与具体 Provider / Runtime 解耦。

旧嵌入式 `1+7` 仍是当前 **legacy compatibility surface（旧版兼容表面）**，继续承载既有 Task / Gate / Skill owner / Golden Case / Pilot Contract 和 rollback；但它不再保存独立迁移 phase 状态，也不再作为目标组织结构扩张。8/8 身份桥接只保留在 `domains/edge-foundation/compatibility/embedded-1plus7-mapping.yaml`，晋级状态由真实 Pilot receipt + phase-3 readiness 计算。

`canonical_routing_switched=false` 仍是硬约束。Phase-3 只允许切换 canonical routing authority 和引入 selector entrypoint；禁止在同一动作中改写 compatibility mapping、废弃/删除旧身份、扩大 A0-A7、改变 Verification / Independent Review 独立性或绑定具体 Provider。旧身份 deprecation / removal 分别属于后续独立阶段。

## 真实 Pilot 进展

当前三轨不是“尚未开始”，而是处在不同真实证据阶段：

| Track | 当前状态 | 主要剩余项 |
|---|---|---|
| Debug | 已选定 SSC305 / SPI-NAND / UBI-UBIFS 并发写后只读问题 | 产品源码 exact SHA、原始 dmesg/UBI/UBIFS/MTD 日志、设备/Flash/Kernel/Test identity |
| Feature | PCR02 OTA artifact identity 组件已完成真实 Engineering 与可复跑 Verification | Independent Review + Pilot structured terminal bundle |
| Review / Release | PCR02 v1.1.21 artifact identity 与 HTTP/HTTPS distribution evidence 已完成 | 真实设备下载/安装/启动/回滚、独立 release review、人工 release gate |

Synthetic evidence 只验证工具链，永远不计入 phase-3 promotion。只有三轨都形成 eligible real receipt，才能得到 `ELIGIBLE_FOR_REVIEW`；这仍只允许发起独立 canonical-switch 评审，不自动切路由，也不自动声明 Production Ready。

当前目标仍是 **E2 Engineering Closed Loop，并为 E3 Knowledge Closed Loop 建基础**。

## 主要入口

- [研发中心 AI 数字员工研发流程规划](研发中心AI数字员工研发流程规划.md)：研发中心总体流程和 Provider-neutral 原则；
- [ADR-003：Provider-neutral AI R&D Target Architecture](docs/adr/ADR-003-provider-neutral-ai-rd-target-architecture.md)：总体 Provider-neutral 架构决策；
- [ADR-004：端侧底座数字责任架构](docs/adr/ADR-004-edge-foundation-digital-responsibility-architecture.md)：端侧责任模型与中英术语；
- [端侧底座机器责任模型](domains/edge-foundation/domain.yaml)：三 Domain Expert、协调角色、编排/执行/可信保障边界；
- [旧 1+7 身份桥接](domains/edge-foundation/compatibility/embedded-1plus7-mapping.yaml)：静态 8/8 mapping + removal gates，不保存 mutable phase 状态；
- [端侧 Shadow Routing](domains/edge-foundation/routing-shadow.yaml)：旧 Task 到目标责任语义的非 canonical 对照；
- `scripts/evaluate_edge_foundation_pilot_shadow.py`：真实 Pilot → Edge Foundation shadow receipt；
- `scripts/evaluate_edge_foundation_phase3_readiness.py`：聚合真实 receipt，判断 `ELIGIBLE_FOR_REVIEW`；
- [AI R&D Target Operating Model](docs/strategy/ai-rd-target-operating-model.md)；
- [Embedded Domain Closed Loop V1](docs/strategy/embedded-domain-closed-loop-v1.md)；
- [嵌入式兼容执行面](expert-groups/embedded-system/README.md)；
- [嵌入式核心参考](嵌入式系统专家团-核心参考/)；
- [真实 Pilot Runbook](docs/runbooks/embedded-pilot.md) 与 [Quickstart](docs/runbooks/embedded-closed-loop-quickstart.md)；
- [Contract Catalog](contracts/catalog.json)。

## 长期边界

稳定模型是 **责任/控制面稳定 + Runtime 可替换 + Thin Session Bootstrap**：

- `digital-worker`：Domain / Role / Expert / Capability / Skill、Work/Run、Gate、Action Policy、Engineering handoff、Identity/Evidence、Verification、Review、Pilot/Maturity；
- `knowledge-hub`：Knowledge Registry、authority、ACL、freshness、context/evidence 查询与知识生命周期；
- `agent-dev-kit`：通用 Agent/Skill、Asset Profile、immutable release、资产校验与回滚；
- `llm_agent`：外部实践 intake、采用/健康度观察、Runtime 对比；
- Runtime Binding：Codex、Claude Code、IDE/Internal Runtime、WorkBuddy 或未来其他实现；
- Thin Session Bootstrap：单次会话装配 project/mode/contract/skill/provider identity，不成为新的控制面。

稳定原则：**责任（Responsibility）不等于运行时（Runtime）；专家（Expert）不等于 Agent；能力域（Capability）不默认等于 Agent；知识索引不替代权威 Source。**

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

Debug 另外要求一份共享 Hypothesis Registry。Material Manifest 在 `planned/running/blocked` 可诚实保持 `BLOCKED`；进入 `complete` 前必须是 `READY` 或经明确批准的 `DEGRADED`。completed run 会重新校验终态材料和 frozen evidence bundle；禁止通过“文件存在”推导材料已充分。

## 仓库治理

当前 main server-side protection 仍延后到 Productionization；repository-local CI 必须持续通过。进入 Productionization 前运行：

```bash
python scripts/verify_repository_governance.py --strict
```

活动目录只保留当前 target、仍有实际执行/rollback 责任的 compatibility surface，以及机器可验证的迁移契约。历史方案由 Git history 与 ADR 保存，不再维护平行“最新版/最终版”入口。
