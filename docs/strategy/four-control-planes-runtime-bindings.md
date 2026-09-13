# 4 个稳定控制面 + N 个可替换 Runtime Binding

- Status: `superseded`
- Superseded by: [`AI R&D Target Operating Model — Final Baseline`](ai-rd-target-operating-model.md)
- Historical scope: 4 control planes + replaceable Runtime Bindings transition design

本文是 2026-09-12 建立 4+N 架构时的阶段策略记录，保留用于追踪设计演进。

核心原则仍然有效：

- `digital-worker` / `knowledge-hub` / `agent-dev-kit` / `llm_agent` 是四个稳定控制面；
- Codex / Claude / Other 通过可替换 Runtime Binding 接入；
- Asset Profile 与 Runtime Profile 分离；
- Runtime local gate 不得推导 digital-worker Domain Gate / Verification PASS；
- Knowledge Provider 通过公共 Contract 消费，不依赖内部目录；
- Runtime Binding 不是第五个控制面。

但本文原版本中的以下过渡语义已被后续 ADK/Codex 合同和终态审查 supersede：

```text
provider-produced monolithic Codex bundle
asset_bundle_hash as required cross-plane identity
BLOCKED_ASSET_BUNDLE_IDENTITY as terminal readiness model
```

终态采用：

```text
immutable ADK release
+ exact-source-set handoff
+ Runtime consumer assembly
+ exact Runtime Binding / Execution Receipt
```

同时，最终 Operating Model 进一步冻结：

- 能力演进链与任务执行链分离；
- Runtime Binding 内允许一个极薄 Session Bootstrap / Task Router；
- L0 Quick Assist / L1 Governed Engineering / L2 Formal Evidence 三种运行等级；
- Knowledge 日常 current-provider 与 Formal exact-pinned 双模式；
- `llm_agent` 退出日常执行热链；
- 不新增第五控制面、中央 Runtime Gateway、Context Broker Service 或大一统 Knowledge 平台，除非后续真实重复证据证明必要。

所有新的架构实施与跨仓合同迁移均以 [`ai-rd-target-operating-model.md`](ai-rd-target-operating-model.md) 为 Strategy Baseline。历史具体内容可通过 Git 查看本文件在被 supersede 前的版本。