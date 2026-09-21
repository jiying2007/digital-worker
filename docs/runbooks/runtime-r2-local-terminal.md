# Runtime R2 — Local Terminal Execution

## Purpose

R2 proves a real Runtime/Provider substitution against one exact frozen task. It does not require the provider invocation itself to run inside GitHub Actions.

The canonical split is:

- GitHub / Digital Worker freezes identities, task inputs, and governance.
- Each runtime executes the frozen task in its own local terminal domain.
- The runtime exports a `.git`-free replay result tree and must pass Digital Worker's replay postflight before it may emit evidence-ready native/portable receipts.
- The replay postflight validates the frozen descriptor schema, independently checks frozen artifact identity, and executes every declared host-verifier step from the exported result tree. It is runtime-local conformance evidence, not Domain Verification.
- Digital Worker consumes those local evidence directories, projects native receipts into portable receipts, independently host-verifies both replay-complete result trees, and emits a small verification receipt.
- Runtime receipts never claim Verification PASS, Product Ready, Release Ready, or R2 qualification by themselves.

## Credential boundary

ADK_ADMIN_TOKEN is the only canonical GitHub administration / privileged cross-repository token. It may be used by git / gh when GitHub access requires it.

Provider authentication stays local to the runtime and R2 reuses the normal shared user runtime home:

- Codex: reuse the caller's existing `CODEX_HOME`, or `~/.codex` when `CODEX_HOME` is unset.
- Claude Code: reuse the caller's existing user `HOME` and `~/.claude`.

The canonical R2 mode is `shared-user-home`. Do not create a runtime home under the evidence directory. Existing provider/network configuration and authentication remain local runtime state.

GitHub must not require or store CODEX_RUNTIME_CREDENTIAL or CLAUDE_RUNTIME_CREDENTIAL for R2 execution. A GitHub PAT must never be reused as OpenAI or Anthropic provider authentication.

The canonical Digital Worker intake reads only explicitly named evidence files from the local evidence directory. Authentication files, access tokens, API keys, cookies, shared runtime homes, caches, sessions, and local provider configuration are never intake evidence and must never be committed or uploaded. Runtime receipts must state `runtime_home_mode=shared-user-home` and `credential_state_in_evidence=false`.

The evidence output directory is evidence-only. It must never become `CODEX_HOME`, user `HOME`, or a credential store.

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

## Local prerequisites

Both runtime-owned local adapters require Python 3.11 or newer and `jsonschema` for the mandatory replay postflight. The canonical adapters resolve `PYTHON_BIN` with a default of `python3`.

Historical freezes that bind older adapters remain immutable audit evidence, but they are not the canonical execution path after this hard-cut. Do not modify a historical frozen checkout to simulate the new shared-home behavior; create a fresh freeze bound to the current runtime adapters instead.

The Codex local adapter also requires the Python packages used by its exact asset/evidence path, including PyYAML and jsonschema. Validate these before starting a long R2 execution.

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

The adapter reuses the caller's existing Codex runtime home. By default that is the existing `CODEX_HOME`, or `~/.codex` when `CODEX_HOME` is unset. The normal Codex CLI must already work in that environment.

Frozen managed assets are applied to the shared Codex home using the repository's existing protected-path and allowed-live-drift policy. Authentication/session/cache state and allowed local provider configuration such as `config.toml` are local runtime state and are excluded from the R2 evidence identity. The adapter refuses to use a runtime home inside the evidence directory.

After provider execution, the adapter exports `result-tree.tar.gz` without `.git` and invokes `scripts/runtime_r2_result_postflight.py`. Evidence-ready output is forbidden unless `.r2/host-verifier.json` validates against the frozen schema and every declared replay step passes. The native receipt binds the resulting replay-postflight digest.

Expected outputs include codex-native.json, codex-portable.json, codex.patch, result-tree.tar.gz, result-postflight.json plus bounded postflight logs, provider output/event evidence, the local evidence bundle, and its SHA-256. The shared `CODEX_HOME` itself is never bundled.

## Claude Code execution

Run the adapter from the exact Claude binding checkout and supply exact ADK checkouts:

    bash control/scripts/runtime-r2-local.sh \
      --digital-worker-root /path/to/digital-worker-exact-freeze-commit \
      --target-root /path/to/claude-r2-target \
      --frozen-plan /path/to/frozen-plan.json \
      --adk-contract-root /path/to/agent-dev-kit-exact-contract-commit \
      --adk-release-root /path/to/agent-dev-kit-exact-release-commit \
      --out /path/to/evidence/claude

The adapter reuses the caller's existing user `HOME` for local authentication/provider state, but controlled R2 execution must not inherit user-level behavioral instructions or settings. The canonical invocation uses `--setting-sources project,local`, so the shared home supplies login/network/provider state while user-scope Claude behavior remains outside the frozen execution context.

Materialized frozen runtime assets are installed into the shared runtime home. The provider authorization receipt must record `execution_context_mode=frozen-project-local`, `user_setting_source_loaded=false`, `runtime_home_mode=shared-user-home`, and `credential_state_in_evidence=false`. The normal Claude Code CLI must already work in the shared environment.

The adapter permits the minimal workspace scaffolding required by this task, including `Bash(mkdir *)`, while keeping the rest of the Bash allowlist bounded. Its turn budget is explicit and bounded: default 32 turns, configurable with `--max-turns N` or `CLAUDE_R2_MAX_TURNS`, and constrained to 1–64. A fixed 20-turn ceiling is retired because the real R2 campaign reached the limit while still in legitimate tool-use.

The adapter refuses to use a runtime home inside the evidence directory. After provider execution, it exports `result-tree.tar.gz` without `.git` and invokes the same Digital Worker replay postflight authority. A Claude CLI exit code of zero is insufficient for evidence-ready output: descriptor schema validation and all declared replay steps must also pass.

Expected outputs include claude-native.json, claude-native-validated.json, claude-portable.json, claude.patch, result-tree.tar.gz, result-postflight.json plus bounded postflight logs, Claude execution evidence, the local evidence bundle, and its SHA-256. The shared user home is never bundled.

## Local intake and Domain Verification

The two runtime executions are independent provider receipts. They are not themselves R2 qualification.

Run Digital Worker verification from a current Digital Worker checkout. The verifier records its own implementation commit separately from the older frozen governance commit, so a historical freeze remains valid while verification tooling evolves:

    python3 scripts/runtime_r2_local_verify.py \
      --root /path/to/current-digital-worker \
      --freeze-dir /path/to/runtime-r2-freeze-<run-id> \
      --codex-evidence-dir /path/to/codex-evidence \
      --claude-evidence-dir /path/to/claude-evidence \
      --out /path/to/r2-verification \
      --verification-actor local-user:<user>@<host>

The verifier fail-closes unless both runtime results:

- reference the same frozen_inputs_sha256;
- match the exact frozen runtime binding commits;
- preserve the exact frozen target base and Digital Worker governance identity;
- contain no Verification / Release authority claim;
- record local-terminal execution using `shared-user-home`;
- explicitly state that credential state did not enter evidence;
- for Claude, prove the controlled execution context excluded user-level behavioral settings (`execution_context_mode=frozen-project-local`, `user_setting_source_loaded=false`);
- record no GitHub provider credential;
- provide replay-complete result-tree evidence whose digest matches the native receipt;
- bind exactly one replay-postflight digest produced from the exported `.git`-free result tree;
- preserve the authority boundary that replay postflight is required before evidence-ready but is not Domain Verification;
- independently pass the target host unit tests and OTA manifest verifier.

Expected output:

    runtime-r2-domain-verification.json
    codex-domain-host-tests.log
    codex-domain-ota-verify.log
    claude-domain-host-tests.log
    claude-domain-ota-verify.log

Only the small verification receipt and bounded log digests belong in long-lived repository review evidence. Runtime homes, provider credentials, caches, full local sessions, and other private runtime state do not.

## Independent Review

Copy the verification receipt into the canonical tracked path:

    reports/runtime-r2/verification/R2-FEATURE-PCR02-OTA-001/runtime-r2-domain-verification.json

Commit that small receipt through normal repository review, then run the manual Runtime R2 Independent Review workflow against that tracked path. The reviewer must be distinct from both provider execution actors and the local verification actor.

The independent review remains non-terminal and only makes the evidence eligible for the root runtime-portability certifier. Neither runtime execution nor local verification may self-qualify R2.

## Repository closure versus R2 evidence

Repository-local code, CI, contract, release, and governance closure must not be blocked by missing OpenAI/Anthropic credentials in GitHub.

Cross-repository Replaceability terminal evidence remains pending until the real local Codex and Claude executions are completed, imported, and evaluated. Moving provider execution to a local terminal removes a credential/venue coupling; it does not weaken the real-provider R2 evidence requirement.
