# Runtime R2 — Periodic Qualification

## Purpose

R2 is the periodic real-runtime qualification for the replaceability claim. It is not a repository-closure gate, product-release gate, or daily development gate.

The canonical authority is `manifests/runtime-r2-qualification-policy.json`.

R1 remains the mandatory runtime-binding conformance layer. R2 is run periodically and after material runtime changes to prove, with real providers, that the same frozen task can still be completed and replay-verified without changing Domain semantics.

## What R2 can and cannot decide

R2 may decide only whether the declared runtime portability / terminal replaceability claim is currently qualified.

R2 status must not automatically change:

- repository health or repository closure;
- Product Readiness or release authority;
- ADK release qualification;
- Knowledge Provider qualification;
- Domain Verification for an unrelated product run.

A failed or incomplete R2 campaign is valid evidence. Record it as `blocked`; do not repeatedly tune provider behavior until a PASS appears.

## Cadence

Run one fresh campaign:

- quarterly; and
- after a new Runtime Binding;
- after a runtime-adapter semantic change;
- after a provider/model major change;
- after an ADK/runtime-contract major change;
- when requalification is explicitly requested.

The recommended freshness window is 120 days. A stale qualification removes the current replaceability claim; it does not make the repository unhealthy.

## Simplified qualification chain

The long-term chain is intentionally small:

```text
freeze exact same task
        ↓
real Codex execution ──┐
                       ├─ replay postflight
real Claude execution ─┘
        ↓
independent Digital Worker verification
        ↓
one R2 qualification receipt
```

Each campaign therefore proves real provider execution under one frozen comparison boundary; it is not a synthetic smoke test.

The four invariants are:

1. both real runtimes execute the same frozen task independently;
2. runtime/provider state and credentials do not enter the result evidence;
3. each exported result tree replays without `.git`, runtime-home state, or provider credentials;
4. Digital Worker, not either runtime, decides qualification.

An additional human independent-review workflow and a second root certifier are not required for periodic R2 qualification.

## Credential boundary

GitHub and provider credentials remain separate trust domains.

- `ADK_ADMIN_TOKEN` may be used only for Git/GitHub administration when needed.
- Codex reuses the caller's existing `CODEX_HOME` or `~/.codex`.
- Claude Code reuses the caller's existing user `HOME` / `~/.claude`.
- GitHub must not store OpenAI/Anthropic provider credentials for R2.
- A GitHub PAT must never be reused as provider authentication.
- runtime homes, authentication files, caches, sessions, cookies, and tokens are never R2 evidence.

The evidence output directory must never be used as a runtime home.

## 1. Freeze one exact campaign

Freeze remains provider-credential-free:

```bash
gh workflow run runtime-r2-freeze.yml \
  --repo jiying2007/digital-worker \
  --ref main \
  -f confirmation=FREEZE_REAL_R2 \
  -f target_repository=jiying2007/ota_download_test \
  -f target_base_commit=<exact-40-hex>
```

Retain `campaign.json` and `frozen-plan.json`. Historical freezes are immutable.

A runtime-adapter or binding change requires a new freeze because the frozen plan binds exact runtime commits.

## 2. Prepare independent exact checkouts

For each runtime execution, match `frozen-plan.json` exactly:

- Digital Worker governance commit;
- runtime-binding commit;
- target base commit;
- immutable ADK release / consumer-contract identities;
- clean target worktree.

Codex and Claude must use separate clean target worktrees. Never reuse another runtime's modified worktree.

Both runtime-owned adapters require Python 3.11+ and `jsonschema`. ADK execution must use the same reviewed Python environment, for example by binding `ADK_PYTHON_BIN` to the selected R2 interpreter.

## 3. Execute Codex locally

From the exact Codex binding checkout:

```bash
bash scripts/runtime-r2-local.sh \
  --digital-worker-root /path/to/digital-worker-exact-freeze-commit \
  --target-root /path/to/codex-r2-target \
  --frozen-plan /path/to/frozen-plan.json \
  --out /path/to/evidence/codex
```

The adapter must fail closed unless the frozen identities match and replay postflight passes.

## 4. Execute Claude Code locally

From the exact Claude binding checkout:

```bash
bash control/scripts/runtime-r2-local.sh \
  --digital-worker-root /path/to/digital-worker-exact-freeze-commit \
  --target-root /path/to/claude-r2-target \
  --frozen-plan /path/to/frozen-plan.json \
  --adk-contract-root /path/to/agent-dev-kit-exact-contract-commit \
  --adk-release-root /path/to/agent-dev-kit-exact-release-commit \
  --out /path/to/evidence/claude
```

Use the adapter's bounded turn budget. A runtime process returning exit code zero is not sufficient; replay postflight must still pass.

If a real runtime repeatedly omits a frozen MUST requirement, asks for permission already granted by the adapter, or otherwise cannot produce replay-complete evidence, record the campaign as blocked and fix the runtime adapter before the next qualification campaign. Do not manually repair the runtime result tree and present it as native provider evidence.

## 5. Replay postflight

Each adapter exports a `.git`-free `result-tree.tar.gz` and runs Digital Worker's replay authority.

Replay postflight must independently verify:

- frozen artifact identity;
- machine-readable frozen identity binding;
- the frozen host-verifier descriptor schema;
- every declared host-verifier step;
- absence of Verification/Release/R2 authority claims by the runtime.

A runtime-local postflight is conformance evidence, not the final qualification decision.

## 6. Independent qualification

When both runtime evidence directories are replay-complete, run Digital Worker verification:

```bash
python3 scripts/runtime_r2_local_verify.py \
  --root /path/to/current-digital-worker \
  --freeze-dir /path/to/runtime-r2-freeze-<run-id> \
  --codex-evidence-dir /path/to/codex-evidence \
  --claude-evidence-dir /path/to/claude-evidence \
  --out /path/to/r2-verification \
  --verification-actor local-user:<user>@<host>
```

The verifier is the qualification authority. It checks both provider results against the same frozen inputs and independently replays the required target verification.

The current verifier emits `runtime-r2-domain-verification.json`. Until the receipt schema naturally evolves, that small verifier-owned document is the canonical R2 qualification receipt.

No runtime receipt may self-qualify R2.

## Long-lived evidence

Keep the repository-facing R2 surface small.

Long-lived tracked evidence should contain only:

- the frozen campaign identity needed to identify the exact comparison; and
- the small Digital Worker qualification receipt (or its future compatible replacement).

Provider execution output, result trees, replay logs, runtime-native/portable receipts, runtime homes, caches, and credentials remain local/audit evidence and are not normal long-lived repository assets.

## Failure semantics

Use these states:

- `qualified`: a current campaign proves the declared replaceability claim;
- `blocked`: current campaign evidence is incomplete or a runtime failed qualification;
- `stale`: prior qualification is outside the freshness window or a material change requires requalification;
- `not_run`: no current R2 claim may be made.

`blocked`, `stale`, and `not_run` do not invalidate repository closure or product release. They only prohibit claiming current R2 runtime replaceability.

## Repository closure versus R2

Repository-local code, CI, contracts, release mechanics, governance, and R1 runtime-binding conformance may reach closure independently of R2.

R2 remains a long-term periodic qualification asset so that Provider-neutral / replaceable-runtime claims can be demonstrated when needed without putting real-provider execution in the daily production hot path.
