# Embedded Knowledge Registry

当前 Registry：`registry.yaml`。

## 定位

Registry 是嵌入式域的知识**索引与权威指针**，不是第二份知识主库，也不是 RAG/向量库。

当前状态：`internal-seed`。

首版只登记 `digital-worker` 仓库内可核验对象，用于验证：

- knowledge_id 是否稳定；
- source_ref 是否可追溯；
- authority / owner / domain / tags 是否足以支撑任务上下文；
- Knowledge Harvest 是否能引用/更新已有知识对象。

NAS、飞书、供应商 Datasheet/TRM/SDK、CI/HIL、历史 RCA 等真实外部 Source 尚未在此宣称完成接入，继续由 Issue #16 做 Source Inventory / PoC。

## 原则

1. `Source of Truth stays at source`；
2. Registry 只保存 metadata 和 source ref，不复制强版本事实形成第二 SSOT；
3. Provider binding 保持 `not_frozen`；
4. Source ACL 不因被 Registry 索引而放宽；
5. stale / conflicting / unknown authority 必须显式处理；
6. Knowledge Candidate 必须来自真实 evidence；
7. 单一案例不自动升级 P1 Skill / Tool。

## V1 目标

当前 50 条 internal seed 只是起点。31~60 天阶段目标是通过 #16 把 Registry 扩展到 50~100 个**高价值且真实使用**的对象，并至少覆盖三类实际 Source；成功标准不是条目数量，而是 Knowledge 在后续真实任务中被正确引用和复用。
