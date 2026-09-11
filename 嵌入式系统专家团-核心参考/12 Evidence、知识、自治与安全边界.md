# 12 Evidence、知识、自治与安全边界

> 同步基线：`v0.7.0 / provider-neutral`

## 1. Evidence-first

关键结论使用：`claim + evidence_refs + fact_state + confidence + verification_status`。

典型 evidence：source/commit、log/dump/register、datasheet/TRM、schematic、waveform/measurement、build/CI、artifact hash、device identity、HIL/test report。

Confidence 不能替代 Verification。

## 2. Knowledge：统一访问，不强制统一存储

当前原则是 **Source of Truth stays at source**。

可能的权威 Source：

- 飞书/协作文档：人工协作知识；
- NAS：Datasheet/TRM/SDK Guide/供应商资料/历史归档；
- Git：源码、ADR、Runbook、配置；
- CI/HIL：构建和验证事实；
- Artifact Store：发布制品与 hash；
- Issue/RCA：历史问题与决策证据。

Knowledge Provider（如 WeKnora 或其他 RAG/Search 实现）负责索引、检索、引用和评测，不自动取得原始 Source 的权威身份。

## 3. Knowledge Registry / Gateway / Context Broker

建议逐步形成：

- Registry：记录 knowledge_id、source、owner、revision、ACL、freshness、authority；
- Gateway：统一 search/get/cite/resolve-authority 接口；
- Context Broker：按 task/user/project/repo/permission 组装最小必要上下文。

Context Broker 当前是候选能力，不等于必须立即建设平台。

## 4. NAS 治理

- 静态参考资料可登记后索引；
- Firmware/BSP/build/config 等强版本敏感资产按 exact path/hash/revision 使用；
- 不默认“整个 NAS 全量向量化”；
- ACL、敏感级别、owner、freshness 是 PoC 必测项。

## 5. A0-A7

A0 Read / A1 Analyze / A2 Generate 默认允许；A3 Worktree / A4 Build Test 受控；A5 Device Read 授权后；A6 Device Write、A7 Release 需人工审批。

**动作权限与 Provider 名称解耦。** Codex、Claude、WorkBuddy 或任何其他 Agent 都不能因品牌/入口不同获得额外 Action Level。

## 6. 永不默认自动

OTP/Fuse、生产签名密钥、Production OTA、不可逆 Boot 配置、破坏性生产数据动作。

## 7. Evidence Bundle

真实 Pilot 用结构化 Evidence Bundle 保存 kind/ref/hash/required；原始日志/core/firmware 默认留在受控源系统，`digital-worker` 只保存 Contract 和可审计引用。

## 8. Fail-closed

包括：未注册 Skill、review_only 隐式执行、real Pilot 非 exact base、artifact 路径逃逸、缺 required artifact、incorrect PASS、unauthorized action、unresolved ownership、Provider-specific machine residue 等均阻断。

## 9. Secret / Sensitive Data

需要明确 log/core 脱敏、客户资料 ACL、HIL 串口上下文边界、firmware retention、生产 key/签名服务隔离。AI 不拥有生产 Secret 管理权。

## 10. 当前评审问题

- Knowledge Source Inventory 的 owner 是谁；
- 默认 Knowledge Provider 是否需要主备；
- `knowledge_refs` 是否升级为 source/revision/ACL/provenance 对象；
- Context Broker 的收益是否足以覆盖建设复杂度；
- Evidence Bundle 是否应接入统一 Evidence/Artifact Store；
- main protection 何时开启。
