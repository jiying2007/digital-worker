# Pilot Material Manifest 终态门禁

本页记录嵌入式真实 Pilot 的 Material Manifest（材料清单）终态语义，避免运行说明与机器实现再次漂移。

- `planned / running / blocked` 阶段允许 Material Manifest 保持 `BLOCKED`，用于诚实表达源码、日志、设备、测试环境等材料仍不完整。
- `complete` 进入终态前必须重新校验 Material Manifest；`BLOCKED` 不得进入 completed evidence bundle。
- completed run 后续执行 `validate` 时必须再次重算同一终态门槛，防止完成后材料被篡改、失效或 readiness 漂移。
- `DEGRADED` 只有在存在明确 `degradation_approved_by` 时才可作为终态材料状态。
- Debug 轨道采用“复现步骤（reproduction）或权威日志（log）至少一个可用”的 OR 语义；现场问题无法稳定复现但存在可追溯原始日志时，不应被错误阻断。
- Material Manifest 只证明材料是否足以进入终态，不替代 Verification（验证）或 Independent Review（独立审查）。

权威实现：

- `scripts/validate_material_manifest.py`
- `scripts/embedded_pilot.py`
- `expert-groups/embedded-system/schemas/material-manifest.schema.json`

这道门禁不改变 Task routing、A0-A7 权限、Pilot promotion threshold、Verification / Review 独立性或 Edge Foundation phase-3 迁移规则。
