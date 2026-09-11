# 嵌入式系统专家团真实 Pilot 执行说明

Pilot 的目标是验证 Expert Team Operating Model，而不是证明 AI 永远正确。当前基础设施状态为 `pilot-operations-ready`，真实三轨证据仍待执行。

## 1. 绑定真实任务

先形成 `task-brief v1`。真实 Pilot 必须有 human owner、repo root、**exact Git base SHA**、验收和所需验证层级。只提供 `main/dev` 等分支名时不得开始 real run。

## 2. 初始化

```bash
python scripts/embedded_pilot.py init \
  --run-id <run-id> \
  --track <debug|feature|review_release> \
  --source-type real \
  --task-type <task-type> \
  --workflow-mode <mode> \
  --human-owner <owner> \
  --task-brief <task-brief.json> \
  --repo-root <repo-root> \
  --base-commit <exact-sha>
```

然后用 `status ... running` 开始记录。

## 3. 执行

Expert Team 默认 A0-A2。代码修改/构建经 Engineering Handoff -> Engineer + Codex；设备写和 Release 保留人工 Gate。Debug 强制 Observed/Inferred/Confirmed + Hypothesis Registry。

## 4. 收口

使用 `complete` 附加 track 所需结构化产物。工具会校验 work_item、run_id、repo/base、独立 verification/review，并生成 `evidence-bundle.json`，对所有结构化 artifact 计算 SHA256。

```bash
python scripts/embedded_pilot.py complete <run-dir> \
  --verification-report <verification.json> \
  --review-report <review.json> \
  --pilot-result <pilot-result.json> \
  ...
```

Feature 还必须提供 engineering-task-package 与 delivery-receipt；Debug 还必须通过 `--extra hypothesis_registry=<file>` 提供 Hypothesis Registry。

## 5. 汇总与评分

```bash
python scripts/embedded_pilot.py summary expert-groups/embedded-system/pilot/runs --output pilot-status.json
python scripts/evaluate_embedded_pilot.py <pilot-result...> --output pilot-metrics.json --markdown-output pilot-metrics.md
```

评分门槛从 `pilot-plan.yaml` 读取。Synthetic 只验证工具链，不计入真实 Pilot。

## 6. 生产化门禁

三轨真实 completed run 和安全指标满足后，也仅能提交 productionization 人工评审；仓库不会自动扩大 A3-A7，也不会自动标记 Production Ready。
