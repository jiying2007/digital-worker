# Four-Repo AI R&D Operating System — superseded

- Status: `superseded`
- Superseded by: [`four-control-planes-runtime-bindings.md`](four-control-planes-runtime-bindings.md)

原“四仓”方案已经完成第一轮职责收敛，但 `jiying2007/codex` 的实际实现证明 Runtime 需要独立的 Distribution / Host Integration 边界，而不应成为第五个控制面。

当前阶段正式采用：

> **4 个稳定控制面 + N 个可替换 Runtime Binding**

稳定控制面继续是：

- `digital-worker` — R&D Operating Model
- `knowledge-hub` — Knowledge Control Plane
- `agent-dev-kit` — Agent Asset Control Plane
- `llm_agent` — Practice & Runtime Evaluation Lab

Runtime Binding 作为可替换实现层：

- `jiying2007/codex` — 第一套 Codex Runtime Distribution & Host Integration；
- Claude Code / IDE Agent / Internal Agent 后续复用同一 Runtime Binding Contract。

本文件仅保留历史路径兼容，不再作为当前 Strategy Baseline。
