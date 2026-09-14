# R0 Trust Closure — Real Pilot 信任基线

- Status: `current-stage-trust-baseline`
- Date: 2026-09-14
- Applies before: acceptance of real Debug / Feature / Review-Release Pilot evidence
- Current repository stage: `iterative-development`
- Architecture: unchanged — 4 stable control planes + N replaceable Runtime Bindings + thin Session Bootstrap inside each Runtime Binding

## Why R0 exists

`digital-worker` 的 Contract/Tooling 成熟度已经高于真实运行证据成熟度。R0 先闭合 evidence integrity、跨仓 exact identity、Knowledge identity 与 Runtime identity，避免真实 Pilot 开始后再返工可信链。

当前阶段以快速迭代和真实证据积累为优先。**GitHub main server-side enforcement 不再作为 real Pilot acceptance 的当前前置条件**；它保留为 Productionization / 多人受保护协作前的治理 Gate。仓库内 CI、Evidence、Verification/Review、Action Policy 与 fail-closed identity 仍然必须执行。

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
- stage-aware live repository governance report。

Branch GC 保留独立最小 write permission，并 pin Action SHA。

## R0.7 GitHub server governance — deferred for current stage

Repository-local CI 不能替代 GitHub server-side enforcement；但是否立即启用 server-side protection 是**阶段策略**，不是架构真理。

当前 `iterative-development` 阶段：

- `main` 可以保持 unprotected；
- 缺少 ruleset **不阻塞** #6/#7/#8 real Pilot acceptance；
- `Repository Governance Audit` 默认以 advisory 模式运行，未保护时返回 `DEFERRED_CURRENT_STAGE` 而非失败；
- repo-local Contract CI、cross-repo identity、Pilot evidence integrity、Verification/Review 和 Action Policy 仍然是硬门禁。

进入 `productionization`、多人长期协作或正式受保护发布阶段前，必须切换 strict audit，并满足：

- Require PR；
- Require `Embedded Expert Contracts / validate`；
- block force push / non-fast-forward；
- block main deletion；
- bounded bypass；
- required approval 按团队规模提升。

验证命令：

```bash
# 当前迭代阶段：advisory
python scripts/verify_repository_governance.py

# Productionization 前：hard gate
python scripts/verify_repository_governance.py --strict
```

`.github/repository-governance-contract.json` 保存当前 stage policy 与未来 strict target，避免把“暂不保护 main”误写成“永久不需要治理”。

## R0 Exit Gate — current iterative stage

当前阶段接受 real completed Pilot 需要：

- Trust regression CI PASS；
- exact cross-repo verification PASS；
- Knowledge adapter identity fail-closed PASS；
- ADK immutable release / Runtime source-set / Session Bootstrap identity PASS；
- Contract Catalog PASS；
- Runtime Binding 执行任务时保留 Runtime distribution identity + Execution Receipt；
- Runtime-local PASS 不越权成为 Domain Verification PASS；
- Acceptance -> Evidence、Independent Verification/Review 与 terminal evidence integrity PASS。

**当前不要求 main server governance audit PASS。** Repository Governance strict PASS 被移动到 Productionization Gate，不再阻塞真实 Pilot 的迭代落地。

R0 代码侧 trust/source-set migration 已闭合。后续证据顺序：#6 Debug → #7 Feature → #8 Review/Release → #16 Knowledge reuse → #18 multi-runtime → Productionization Review / strict governance。
