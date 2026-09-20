# Runtime R2 — Local Terminal Execution

## Purpose

R2 proves a real Runtime/Provider substitution against one exact frozen task. It does not require the provider invocation itself to run inside GitHub Actions.

The canonical split is:

- GitHub / Digital Worker freezes identities, task inputs, and governance.
- Each runtime executes the frozen task in its own local terminal domain.
- The runtime emits a native execution receipt and an evidence bundle.
- Digital Worker projects that native receipt into the portable R2 receipt and later owns comparison / qualification.
- Runtime receipts never claim Verification PASS, Product Ready, Release Ready, or R2 qualification by themselves.

## Credential boundary

ADK_ADMIN_TOKEN is the only canonical GitHub administration / privileged cross-repository token. It may be used by git / gh when GitHub access requires it.

Provider authentication stays local to the runtime:

- Codex: local Codex CLI login state under the selected CODEX_HOME.
- Claude Code: local Claude Code login state under the selected HOME.

GitHub must not require or store CODEX_RUNTIME_CREDENTIAL or CLAUDE_RUNTIME_CREDENTIAL for R2 execution. A GitHub PAT must never be reused as OpenAI or Anthropic provider authentication.

The local R2 evidence bundle records authorization metadata and digests only. It must never archive authentication files, access tokens, API keys, cookies, or local credential stores.

## Why a new freeze is required after runtime changes

A frozen R2 plan binds the exact runtime repository commit. Therefore a new runtime-owned local adapter cannot execute an older frozen plan whose runtime binding points to a commit that predates that adapter.

Historical freeze receipts remain immutable audit evidence. Do not rewrite them.

After changing either runtime binding:

1. merge the runtime change;
2. update config/integrations/cross-repo-lock.json to the exact merged runtime commit;
3. validate Digital Worker;
4. run a fresh Runtime R2 Freeze Campaign;
5. execute only the runtime commits named by that new frozen plan.

## Freeze

The GitHub freeze workflow is deterministic and provider-credential-free:

    gh workflow run runtime-r2-freeze.yml \
      --repo jiying2007/digital-worker \
      --ref main \
      -f confirmation=FREEZE_REAL_R2 \
      -f target_repository=jiying2007/ota_download_test \
      -f target_base_commit=eeb926bd1fff75d2a5d5abb9f0ede9c8f582cc6d

Download the resulting artifact and retain both campaign.json and frozen-plan.json. GitHub authentication used to read the artifact is a GitHub trust-domain concern only.

## Prepare exact local checkouts

For every execution, the following identities must match frozen-plan.json exactly:

- Digital Worker commit;
- Codex or Claude runtime binding commit;
- target base commit;
- immutable ADK release / consumer contract identities;
- clean target worktree.

Do not reuse one runtime's modified target worktree for the other runtime. Use two independent clean target checkouts/worktrees from the same exact base commit.

## Codex execution

Run the adapter from the exact Codex binding checkout:

    bash scripts/runtime-r2-local.sh \
      --digital-worker-root /path/to/digital-worker-exact-freeze-commit \
      --target-root /path/to/codex-r2-target \
      --frozen-plan /path/to/frozen-plan.json \
      --out /path/to/evidence/codex

The adapter creates an isolated CODEX_HOME. If that isolated home is not authenticated, it exits without qualifying the run and prints the exact local login command. Authenticate that isolated home, restore/recreate the target as a clean exact-base checkout if necessary, and rerun.

Expected outputs include codex-native.json, codex-portable.json, codex.patch, result-tree.tar.gz, provider output/event evidence, the local evidence bundle, and its SHA-256.

## Claude Code execution

Run the adapter from the exact Claude binding checkout and supply exact ADK checkouts:

    bash control/scripts/runtime-r2-local.sh \
      --digital-worker-root /path/to/digital-worker-exact-freeze-commit \
      --target-root /path/to/claude-r2-target \
      --frozen-plan /path/to/frozen-plan.json \
      --adk-contract-root /path/to/agent-dev-kit-exact-contract-commit \
      --adk-release-root /path/to/agent-dev-kit-exact-release-commit \
      --out /path/to/evidence/claude

The adapter creates an isolated HOME. If that home is not authenticated, it exits without qualifying the run and prints how to open Claude Code with that isolated home and complete /login. Restore/recreate the target as a clean exact-base checkout before retrying if execution touched it.

Expected outputs include claude-native.json, claude-native-validated.json, claude-portable.json, claude.patch, result-tree.tar.gz, Claude execution evidence, the local evidence bundle, and its SHA-256.

## Import and qualification

The two runtime executions are independent provider receipts. They are not themselves R2 qualification.

Digital Worker must verify that both portable receipts:

- reference the same frozen_inputs_sha256;
- match the exact frozen runtime bindings;
- started from the same exact target base;
- preserve the same Digital Worker governance / acceptance semantics;
- contain no Verification / Release authority claim;
- provide replay-complete result evidence.

Only the Digital Worker R2 evaluator / review path may derive the Replaceability result.

## Repository closure versus R2 evidence

Repository-local code, CI, contract, release, and governance closure must not be blocked by missing OpenAI/Anthropic credentials in GitHub.

Cross-repository Replaceability terminal evidence remains pending until the real local Codex and Claude executions are completed, imported, and evaluated. Moving provider execution to a local terminal removes a credential/venue coupling; it does not weaken the real-provider R2 evidence requirement.
