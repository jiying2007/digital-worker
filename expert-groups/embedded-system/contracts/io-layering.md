# 嵌入式系统专家团 I/O 契约分层

## 1. 三层契约

### L1：专家级契约

位置：`contracts/experts/*.io.yaml`。

描述专家职责级输入、输出、不得做什么、交给谁，不展开具体字段定义。

### L2：Skill 级契约

后续位置：`skills/*/SKILL.md` 的 `io` 元数据。

描述原子能力的字段级输入输出。Skill 不重新定义专家职责，也不得绕过 Gate。

### L3：Artifact / Stage 契约

位置：`schemas/*.schema.json`。

定义阶段产物的字段、状态和证据引用。关键产物必须显式记录：

- `consumed_refs`：本产物实际消费的上游 artifact/evidence；
- `downstream_contract`：允许下游依赖的稳定输出；
- `evidence_refs`：支撑关键 claim 的证据；
- `unverified_items`：未验证项，不允许在摘要中被省略。

## 2. 铁律

1. L1 不替代 L3 字段定义；
2. L2 不扩大 Agent 权限；
3. L3 不以自然语言 PASS 替代结构化验证层级；
4. 所有跨专家、跨阶段交接必须可追踪到 artifact ID；
5. Debug 的推断必须落在 Hypothesis Registry，不得直接升级为 confirmed；
6. 实施者不得生成自己的最终独立 review PASS；
7. 缺必需证据时返回 BLOCKED / DEGRADED，而不是补写虚构事实。

## 3. 当前核心 Artifact

- `task-charter`
- `material-manifest`
- `evidence-ref`
- `hypothesis-registry`
- `engineering-task-package`
- `verification-report`
- `review-report`
- `team-run-state`
- `gate-ledger`

当前阶段先冻结治理契约；P0 Skill 的字段级契约在下一阶段增加。
