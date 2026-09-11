# Acceptance → Evidence Matrix

Work Item: `<work_item_id>`  
Run ID: `<run_id>`

> V1 运行产物。用于把验收条目显式映射到 Verification layer 与 Evidence；当前不作为正式 Schema。

| Acceptance Criterion | Verification Layer | Artifact / Device / Test Identity | Evidence Ref | Status | Notes |
|---|---|---|---|---|---|
| `<criterion>` | `<host|cross_build|sil|device|hil|release>` | `<identity>` | `<evidence-ref>` | `<PASS|FAIL|BLOCKED|NOT_RUN>` | `<notes>` |

## Rules

- 每个必须验收的 criterion 至少一行；
- PASS 必须有 Evidence Ref；
- 未运行不得写 PASS；
- 不同 Verification layer 不得互相推导；
- identity 无法确认时使用 BLOCKED，而不是推测。
