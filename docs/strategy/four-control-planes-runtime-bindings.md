# 4 个稳定控制面 + N 个可替换 Runtime Binding

- Status: `current-stage-baseline`
- Provider selection: `not_frozen`
- Scope: digital-worker / knowledge-hub / agent-dev-kit / llm_agent + replaceable engineering Runtime Bindings

## 1. 目标

把研发 AI 体系稳定为四个长期控制面，同时允许 Codex、Claude Code、IDE Agent、内部 Agent 等 Runtime 独立演进和替换。

```text
                    digital-worker
                 R&D Operating Model
        Work / Expert / Gate / Evidence / Review
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
 knowledge-hub    agent-dev-kit     llm_agent
 Knowledge CP     Agent Asset CP    Practice/Eval Lab
        │              │              │
        └──────────────┼──────────────┘
                       ▼
             Runtime Target Contract
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
   Codex Binding   Claude Binding   Other Binding
         │
         ▼
      Codex CLI
         │
         ▼
 Git / Build / Test / Device / HIL
         │
         ▼
 Runtime Execution Receipt
         │
   ┌─────┴────────┐
   ▼              ▼
digital-worker   llm_agent
Verification     Comparison
```

## 2. 四个稳定控制面

### digital-worker

拥有 Work Item/Run、Expert identity/routing、Domain Workflow/Gate、Action Policy、Technical Decision、Engineering Handoff、工程身份链、Verification、Independent Review 和 Pilot/Maturity。

不得拥有 Runtime-specific exporter、Runtime Host 配置、Knowledge lifecycle 或跨 Runtime 评价实现。

### knowledge-hub

拥有 Knowledge Registry、Context/Evidence Pack、ACL/authority/freshness、生命周期、Owner Review/Promotion 和 Compatibility Intelligence。Runtime 只能通过公共 Provider Contract 消费，不得依赖 `.tmp`、内部 receipt 目录或缓存路径。

### agent-dev-kit

拥有 reusable Agent/Skill、Asset Profile、Workflow Asset、target export contract、资产验证与 release/rollback。`embedded-fullstack` 是 Asset Profile，不是 Codex Runtime Profile。

### llm_agent

拥有外部实践 intake/adoption、Runtime health、cross-runtime comparison 和 Loop Readiness。它不执行生产 Runtime，也不拥有 digital-worker Verification PASS。

## 3. N 个 Runtime Binding

Runtime Binding 是可替换的 Host/Distribution Adapter，不是第五个控制面。

第一套实现：

```text
jiying2007/codex
role = Codex Runtime Distribution & Host Integration
runtime_target = codex-cli
```

它可以拥有：

- Codex Runtime Profile（`token-lean` / `team-collab` 等）；
- Codex config render；
- MCP/sandbox/approval 绑定；
- source → build → plan → dry-run → apply → rollback；
- live drift/conformance；
- Runtime Execution Receipt。

它不得拥有：

- digital-worker Domain Gate / Verification PASS；
- Knowledge lifecycle；
- reusable Agent/Skill SSOT；
- cross-runtime effectiveness evaluation。

未来 Claude Code、IDE Agent、Internal Agent 必须复用同一 Runtime Binding Contract，而不是重新定义研发流程语义。

## 4. 三类身份必须分开

```text
ADK Asset Profile
  example: embedded-fullstack

Runtime Profile
  example: codex/token-lean

Runtime Target / Host
  example: codex-cli / developer-workstation
```

Asset Profile 决定“带哪些可复用能力”；Runtime Profile 决定“如何在具体 Runtime 上披露/并行/加载这些能力”。二者不得合并为一个 `profile` 字段。

## 5. Runtime Execution Receipt

Runtime Binding 每次执行必须提供可追踪 receipt，至少关联：

- work_item_id / run_id；
- Runtime Binding repository + exact commit；
- runtime target/profile/host；
- ADK provider commit/version/Asset Profile/asset bundle hash；
- runtime/model/MCP/sandbox/approval identity；
- target repo base/result SHA；
- runtime-local gate evidence；
- evidence refs。

Receipt **禁止**包含或推导：

```text
verification_pass
release_ready
domain_gate_pass
```

这些仍由 digital-worker 独立裁决。

## 6. 当前 Codex readiness

Codex Runtime Binding contract 与独立 CI 已建立并通过 PR contract CI，但 ADK 尚未提供经过证明的 `embedded-fullstack -> codex-cli` `asset_bundle_hash`。

因此当前必须保持：

```text
BLOCKED_ASSET_BUNDLE_IDENTITY
```

不得拿 Codex `manifests/lock.json`、Git blob SHA、短 SHA 或 tag 替代 provider-produced bundle identity。

## 7. Knowledge Provider 边界

Codex 通过 Runtime-local Adapter 调用 Knowledge Provider 的公共操作：context、evidence-pack、action-check、proposal-route、activity-capture。

成功判定只消费公开 status/result/receipt semantics，不检查 Knowledge Hub 内部目录布局。Provider unavailable、route unresolved、ACL/authority 不清楚时必须 BLOCKED/NEEDS_REVIEW。

## 8. Runtime 对照实验

#18 的统一实验结构：

- digital-worker 冻结任务、Context、Acceptance、Action、Verification；
- ADK 冻结 Asset Profile / bundle identity；
- 每个 Runtime Binding 提供独立 Runtime Profile 与 Execution Receipt；
- llm_agent 比较 runtime health、correctness、evidence、recovery、cost/context 等；
- digital-worker 使用同一 Verification/Review 标准作最终工程判断。

前一个 Runtime 的最终 patch/答案不得泄漏给后一个 Runtime。

## 9. 当前不做

- 不把 Codex 变成第五个控制面；
- 不把 digital-worker 变成 Runtime Gateway；
- 不让 ADK 直接写真实 `~/.codex`；
- 不把 Knowledge Hub 内部路径当 API；
- 不重写历史 Codex vendor provenance 冒充新来源；
- 不在没有真实 bundle identity 时宣称 Runtime Binding READY；
- 不因 Runtime local gate 成功宣称 Engineering/Release PASS。

## 10. 下一阶段退出条件

Runtime Binding 从 candidate 进入 real Pilot 至少需要：

1. provider-produced ADK Codex target bundle + SHA-256；
2. Codex consumer 验证同一 bundle identity；
3. Runtime Execution Receipt 可真实生成并绑定 #6/#7/#8 Work Item；
4. Knowledge Hub public Provider Contract/route 可用或明确使用 bootstrap candidate fallback；
5. Codex Binding exact SHA、ADK exact SHA、llm_agent exact SHA 被 digital-worker lock；
6. real run 中 Runtime receipt 与 digital-worker Verification 明确分层；
7. #18 第二个 Runtime Binding 使用同一 Contract 完成对照。
