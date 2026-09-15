# 嵌入式系统专家团 Pilot Operations

当前状态：`pilot-operations-ready`。真实 Pilot 的契约、操作 CLI、证据打包、指标聚合和安全门禁已具备；**三条真实 Pilot 尚未完成**。

## 目录与 SSOT

- `pilot-plan.yaml`：三轨 Pilot 与 promotion gate；
- `artifact-requirements.yaml`：各 track completed run 的最小 artifact 集；
- `runs/`：本地/受控运行目录，默认 Git ignore；
- `../../../../scripts/embedded_pilot.py`：init/status/complete/bundle/validate/summary；
- `../../../../scripts/evaluate_embedded_pilot.py`：指标聚合，直接读取 Pilot Plan。

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

## 当前真实轨道

- #6 Debug
- #7 Feature
- #8 Review/Release
- #9 rollout tracker

以上 Issue 仍需绑定实际 work item/repo/base 后才能运行，synthetic fixture 不可用于关闭。
