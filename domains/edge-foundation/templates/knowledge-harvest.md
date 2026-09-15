# Knowledge Harvest

Work Item: `<work_item_id>`  
Run ID: `<run_id>`

Result: `<NO_KNOWLEDGE_DELTA|KNOWLEDGE_CANDIDATE>`

> V1 运行产物。Knowledge Harvest 不是“每个任务必须写文档”的 KPI；没有可复用增量时明确填写 `NO_KNOWLEDGE_DELTA` 即可。

## Candidate Types

- Root Cause / Known Issue
- Design Rule
- Compatibility Conclusion
- Checklist / Runbook
- Verification Case
- Skill / Tool Candidate
- Stale / Superseded Knowledge

## Candidates

| Type | Summary | Evidence Ref | Existing Knowledge Ref | Proposed Owner | Action |
|---|---|---|---|---|---|
| `<type>` | `<summary>` | `<evidence-ref>` | `<knowledge-id or none>` | `<owner>` | `<create|update|supersede|none>` |

## Review Rules

- Candidate 必须有 evidence；
- 不复制原始 Authority Source 作为第二份 SSOT；
- 只有可复用、影响未来任务的增量才进入正式 Knowledge；
- Skill / Tool 必须等待重复真实需求，不因单一案例立即升级。
