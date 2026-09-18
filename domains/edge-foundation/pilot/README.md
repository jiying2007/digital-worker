# 嵌入式系统专家团 Pilot Operations

当前状态：`pilot-operations-ready`。真实 Pilot 的契约、操作 CLI、证据打包、指标聚合和安全门禁已具备。

**Product Readiness 的实时完成度不在本 README 复制维护。** 唯一权威状态来自：

- `scripts/evaluate_edge_foundation_product_readiness.py` 的机器结果；
- #26 `Embedded Domain Closed Loop V1 rollout tracker` 的真实 evidence ledger。

这样避免 README 与真实三轨进度发生状态漂移。

## 目录与 SSOT

- `pilot-plan.yaml`：三轨 Pilot 与 promotion gate；
- `artifact-requirements.yaml`：各 track completed run 的最小 artifact 集；
- `runs/`：本地/受控运行目录，默认 Git ignore；
- `../../../../scripts/embedded_pilot.py`：init/status/complete/bundle/validate/summary；
- `../../../../scripts/evaluate_embedded_pilot.py`：Pilot 指标聚合；
- `../../../../scripts/evaluate_edge_foundation_product_readiness.py`：Product Readiness 当前机器真值；
- GitHub #26：三轨真实 evidence rollout 唯一人工可读 ledger。

## 运行生命周期

```text
Issue / task-brief
  -> init(planned)
  -> status running
  -> Expert Team / Engineering Handoff
  -> complete(structured artifacts)
  -> evidence-bundle(SHA256)
  -> pilot-result
  -> evaluator / metrics
```

`complete` 是 fail-closed：缺 track 必需产物时不会进入 completed。

## 证据存储原则

`digital-worker` 保存契约、结构化 Pilot 记录与证据哈希/引用。大体积或敏感原始日志、core、dump、固件、客户材料仍保存在其权威受控系统；不要因为 Pilot 将其直接提交到本仓。

## 三条真实轨道与唯一 rollout ledger

- #6 Debug
- #7 Feature
- #8 Review/Release
- #26 rollout tracker / Product Readiness ledger

各 track 是否已完成、是否可计入 Product Readiness，必须由真实 canonical receipt + evaluator/#26 判定；README、synthetic fixture、示例或历史 Issue 状态均不能替代。

#9 是已关闭的历史 rollout tracker，已由 #26 supersede，不再作为活动控制面。
