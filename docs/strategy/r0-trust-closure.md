# R0 Trust Closure — Real Pilot 前置信任闭环

- Status: `current-stage-gate`
- Date: 2026-09-13
- Applies before: acceptance of the first real Debug / Feature / Review-Release Pilot
- Architecture: unchanged — 4 stable control planes + N replaceable Runtime Bindings + thin Session Bootstrap inside each Runtime Binding

## Why R0 exists

`digital-worker` 的 Contract/Tooling 成熟度已经高于真实运行证据成熟度。进入 real Pilot 前先补齐证据完整性、跨仓身份和 GitHub server governance，避免第一个真实 run 完成后再返工可信链。

R0 不扩 Expert、Skill、Provider、Context Broker 或 Knowledge Platform；只把已经声明的 fail-closed 语义变成可验证事实。

## R0.1 Pilot evidence integrity

Required:

- real `base_commit` = full 40-hex Git SHA；
- engineering-task-package / delivery-receipt 使用同样的 full SHA contract；
- completed/cancelled 为 CLI terminal state；
- completed 后禁止重新 bundle 或回退 running；
- completed validate 每次重新计算 artifact SHA-256；
- evidence artifact set 必须与当前 run refs 精确一致；
- 修订通过 superseding run，而不是改写 completed history。

这提供 fail-closed integrity 与操作不可变语义；如果未来需要抵抗有意重写本地文件，再由真实需求决定是否加入签名/远端 WORM evidence store。

## R0.2 Cross-repo verified lock

`config/integrations/cross-repo-lock.json` v4 同时 pin：

- repository；
- exact provider/runtime commit；
- contract path/version；
- canonical JSON SHA-256；
- ADK immutable v5.1 release identity；
- ADK Runtime Binding contract digest；
- Codex Runtime Binding v2 digest；
- Codex Session Bootstrap contract digest；
- Runtime source identity mode / readiness。

`verify_cross_repo_checkouts.py` 必须对 Knowledge Hub / ADK / llm_agent / Codex：

1. checkout lock 中 exact SHA；
2. 验证 HEAD；
3. 读取该 SHA 上真实 contract；
4. 验证 version；
5. 验证 canonical digest；
6. 对 ADK 额外验证 immutable release tree / manifest blob / tag peel；
7. 对 Codex 额外验证 Session Bootstrap L0/L1/L2 contract；
8. 生成 cross-repo verification receipt。

**Pin 落后于 provider main 是允许的。** Latest 不等于 compatible；promotion 必须经过 consumer verification。

## R0.3 Knowledge runtime identity

`embedded_knowledge.py` 不再仅凭目录存在判 READY。`KNOWLEDGE_HUB_ROOT` 必须匹配锁定 Knowledge Hub commit + public integration contract digest，否则：

```text
BLOCKED_PROVIDER_IDENTITY_MISMATCH
```

Codex L2 Session Bootstrap 也必须执行同一 exact-pinned Knowledge identity 检查。L0/L1 可使用 current reviewed provider，但不得把该模式冒充 Formal reproducibility。

## R0.4 Agent / Runtime identity

正式 Runtime execution 不再依赖 monolithic `asset_bundle_hash`。R0 要求：

```text
ADK immutable release identity
+ Asset Profile
+ Runtime Binding exact commit
+ exact source-set identity
+ runtime distribution identity when executed
+ Session Bootstrap identity
+ Runtime Execution Receipt
```

当前第一套 Codex Binding 的 source identity 已收敛为 `exact-release-source-blobs`，Runtime Binding readiness 为 `SOURCE_SET_BOUND`。这只证明 Runtime source/distribution 身份可追踪，不代表 digital-worker Verification PASS 或 Product Release Ready。

## R0.5 Contract authority

`contracts/catalog.json` 是本仓 Contract Catalog。它只登记 digital-worker 自己拥有的 authoritative contracts，不镜像 Knowledge Hub/ADK/Runtime 的 contract body。

Catalog 解决：authority、owner、producer、consumer、status、compatibility；外部 contract 继续由 cross-repo lock 引用。

## R0.6 CI hardening

Permanent contract CI requires:

- GitHub Actions full-SHA pins；
- exact top-level Python validator dependencies；
- minimal `contents: read`；
- timeout/concurrency；
- unit trust regressions；
- real cross-repo exact-SHA fetch + digest verification；
- immutable ADK release / Codex Session Bootstrap verification；
- verification receipt artifact；
- live repository governance report。

Branch GC 保留独立最小 write permission，并 pin Action SHA。

## R0.7 GitHub server governance

Repository-local CI 不能替代 GitHub server-side enforcement。

`.github/repository-governance-contract.json` 定义最低目标：

- Require PR；
- Require `Embedded Expert Contracts / validate`；
- block force push；
- block main deletion；
- bounded bypass；
- 当前单 owner 阶段 required approval 可为 0，多 contributor productionization 前提升。

`verify_repository_governance.py` 和 `Repository Governance Audit` 验证 live state。

当前 ChatGPT GitHub connector 没有 repository ruleset/branch-protection mutation surface，所以这一个动作必须由具有 GitHub repository administration 权限的主体设置；在 live audit PASS 前，状态是 **external governance blocker**，不得伪造完成。

## R0 Exit Gate

R0 只有在以下条件全部满足后才允许“接受”第一个 real completed Pilot：

- Trust regression CI PASS；
- exact cross-repo verification PASS；
- Knowledge adapter identity fail-closed PASS；
- ADK immutable release / Runtime source-set / Session Bootstrap identity PASS；
- Contract Catalog PASS；
- main server governance audit PASS；
- Runtime Binding 执行任务时保留 Runtime distribution identity + Execution Receipt；
- Runtime-local PASS 不越权成为 Domain Verification PASS。

代码侧 R0 trust/source-set migration 已可闭合；在 live server governance PASS 之前，**real completed Pilot 仍不得被正式接受**。

R0 后续证据顺序保持：#6 Debug → #7 Feature → #8 Review/Release → #16 Knowledge reuse → #18 multi-runtime。
