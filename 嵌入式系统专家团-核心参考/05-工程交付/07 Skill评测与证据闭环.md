# Skill 评测与证据闭环

> 本页解释一个 canonical Skill 如何从“定义完整”走到“可以被评审地声明 EVALUATED”，以及为什么 CI fixture、单次调用、真实 Pilot、跨 Runtime 是四类不同证据。

## 1. 完整证据链

```text
skills.yaml + SKILL.md
      │
      │ canonical identity / owner / action ceiling / contract hash
      ▼
skill-evaluation-plan.yaml
      │
      ├─ positive case
      └─ BLOCK negative case
              │
              ▼
      Skill invocation receipt
      - skill contract SHA-256
      - runtime identity
      - input evidence refs
      - output refs + hashes
      - actual action level
      - COMPLETED / BLOCKED / FAILED
      - runtime/evaluation attestation
              │
              ▼
      Skill evaluation receipt
      - case identity
      - expected vs observed status
      - contract verdict
      - independent semantic evaluator
      - semantic evidence ref + SHA-256
              │
              ├──────── positive case evidence
              └──────── BLOCK case evidence
                         │
                         ▼
              Skill evaluation summary
              - same Skill contract
              - same Runtime implementation
              - same source type
              - both case evidence eligible
                         │
                         ▼
                    EVALUATED
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
 real Work/Run receipt           second Runtime pair
          │                             │
          ▼                             ▼
       PILOTED                    portability evidence
```

任何箭头都不能靠文字推断跳过。

## 2. 为什么必须有 positive + BLOCK 两类 case

只验证“材料齐全时能给出结果”会鼓励错误放行。对工程 Skill，更关键的是知道什么时候**不应该继续**。

因此 23 个 canonical Skill 都必须至少具备：

- **positive**：材料充分、对象身份明确时，按 contract 输出可交接结果；
- **BLOCK**：关键 identity/evidence/authority 不足时，正确拒绝高置信结论或越权动作。

当前 `domains/edge-foundation/evaluation/skill-evaluation-plan.yaml` 固定为：

- 23 个 Skill；
- 每个 Skill 1 positive；
- 每个 Skill 1 BLOCK；
- 总计 46 个 case。

case 定义只说明“应该评什么”，不说明“已经通过”。

## 3. Skill Invocation Receipt 证明什么

`schemas/skill-invocation-receipt.v1.schema.json` 冻结一次调用的 provenance：

| 字段 | 评审意义 |
|---|---|
| `skill_id` | 调用哪个 canonical Skill |
| contract version/path/SHA | 调用的到底是哪一版方法 |
| owner/action ceiling | 责任和权限边界是否漂移 |
| Runtime provider/id/execution identity | 谁真正执行 |
| input refs | 输入 Evidence/材料是什么 |
| output refs + SHA | 输出对象是什么且是否可防漂移 |
| actual action level | 实际动作是否超过 Skill ceiling |
| result | COMPLETED / BLOCKED / FAILED |
| attestation | 谁对执行 provenance 负责 |

真实 receipt 必须由 `runtime-binding` attestation 提供；Digital Worker 只校验和冻结，不应伪造 Runtime 已执行。

该 receipt 只能证明“发生过一次符合 provenance contract 的调用”，不能证明输出技术内容正确。

## 4. Skill Evaluation Receipt 证明什么

`schemas/skill-evaluation-receipt.v1.schema.json` 把一次 invocation 对照一个 evaluation case。

自动检查部分：

- receipt 本身是否 canonical-valid；
- `skill_id` 是否匹配 case；
- positive 是否观察到 COMPLETED；
- BLOCK case 是否观察到 BLOCKED；
- plan hash 是否可追踪。

但“输出分析是否技术正确”“BLOCK reason 是否真正符合场景”属于**语义质量**，不能由结构检查冒充。

所以 semantic evaluation 默认是：

```text
NOT_EVALUATED
```

要成为可计入成熟度的 case evidence，必须额外具备：

- `human-review` 或 `independent-evaluator`；
- evaluator identity；
- semantic evidence ref；
- semantic evidence SHA-256；
- semantic status = PASS。

只有这时 `case_evidence_eligible=true`。

## 5. 为什么单张 case PASS 仍不等于 EVALUATED

一个 Skill 可能会“正常材料时答得很好”，但在关键材料缺失时仍然编造结论。

因此 `scripts/evaluate_skill_maturity.py` 必须同时拿到：

- positive evaluation receipt + 对应 invocation；
- BLOCK evaluation receipt + 对应 invocation。

并检查：

1. 两张 receipt 都是当前 evaluation plan；
2. case IDs 正确；
3. Skill identity 正确；
4. 两张 `case_evidence_eligible=true`；
5. 两边 frozen Skill contract SHA 一致；
6. 两边 Runtime provider/runtime_id 一致；
7. 两边 source type 一致；
8. evaluation→invocation hashes 没漂移。

全部成立才输出：

```text
status = EVALUATED
```

否则输出：

```text
status = DEFINED
blockers = [...]
```

## 6. EVALUATED 仍然不代表什么

`EVALUATED` **不自动表示**：

- 真实产品已经用过；
- Skill 已经 PILOTED；
- 多个真实任务可重复；
- 第二 Runtime 同样有效；
- Product readiness PASS；
- Release Ready；
- action authority 可以扩大。

Skill evaluation summary 固定保持：

```text
portability_proven = false
product_readiness_inherited = false
```

直到对应独立证据存在。

## 7. 与真实 Pilot 的关系

真实 Pilot 的 Skill maturity 使用 `skill-invocation-receipt.v1`，但要求更严格：

- source_type = real；
- runtime-binding attestation；
- runtime execution identity；
- exact Work/Run / source / device / artifact context；
- receipt 被 Pilot evidence bundle 冻结；
- downstream Verification 不能由 Skill 自签。

所以：

```text
synthetic evaluation receipt
    ≠ real Pilot receipt

EVALUATED
    ≠ PILOTED
```

现有历史 Feature Pilot 在 Skill receipt contract 建立之前已经冻结；为了证据真实性，不做事后伪造回填。

## 8. 与第二 Runtime 的关系

Portability 需要同一 frozen Skill Contract 在至少第二个 Runtime 上形成可比证据。

至少比较：

- 相同或等价 input/source set；
- Skill contract SHA；
- positive 与 BLOCK behavior；
- unsupported claim；
- correct block；
- output/evidence traceability；
- action ceiling；
- semantic evaluation。

第二 Runtime 证据不能由“Provider 名字不同”替代。

## 9. CI 能证明什么

当前 CI 可以证明：

- 23 个 Skill 都有 review-grade contract；
- 46 个 evaluation case 完整且与 registry 同步；
- invocation receipt schema/validator fail-closed；
- evaluation receipt 的结构/semantic evidence boundary fail-closed；
- positive+BLOCK 聚合规则不会从单 case 或 mixed Runtime 错升 EVALUATED；
- Pilot 可向后兼容地冻结 Skill invocation evidence。

CI fixture **不能证明**：

- 某个真实 Runtime 已经具备该 Skill 的工程质量；
- 某个 Skill 当前真实处于 EVALUATED；
- 当前真实产品使用过该 Skill；
- 第二 Runtime portability 已成立。

这些必须有持久化真实/独立 evaluation evidence。

## 10. 评审时最小追问

对任何“这个 Skill 已成熟”的说法，至少追问：

1. canonical `SKILL.md` SHA 是什么？
2. positive case ID 和 BLOCK case ID 是什么？
3. 两次 invocation 分别由哪个 Runtime 执行？
4. input/output Evidence refs 和 hashes 在哪里？
5. 谁做 semantic evaluation？
6. semantic evidence hash 是什么？
7. positive + BLOCK 是否使用同一 frozen contract / Runtime？
8. evaluation summary 是否真的为 EVALUATED？
9. 是否存在 real Pilot invocation receipt？
10. 是否存在第二 Runtime 对照？

只要缺任一对应成熟阶段的证据，就保持较低状态，而不是用“模型看起来会做”填空。

## 11. 当前状态

当前仓库已经具备完整的 **Skill 定义、usage provenance、evaluation plan、case receipt、positive+BLOCK aggregation** 基础设施。

但是目前还没有把 23 个 Skill 的 46 个 case 全部执行成持久化、独立 semantic PASS evidence；也没有存量真实 Pilot 的 Skill-level provenance 回填。

因此正式评审仍应写：

> **23 个 canonical Skill 的定义与评测机制已闭环；当前 Skill 工程成熟度统一保持 DEFINED，逐 Skill EVALUATED / PILOTED / REPEATABLE / portability 需由后续真实证据推进。**
