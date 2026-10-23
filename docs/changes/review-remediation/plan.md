# 全面审查整改计划

目标：关闭 2026-10-23 全面审查的六项发现，定位全量签名测试错误；保留已有 dirty 与终态历史证据，不提交或推送。

Primary skill：adk-planning-execution-loop。原始请求：按建议全部优化落地。

## 阶段与验收

1. F1/F2 契约与资格门禁（主代理，串行）：Verification 增加结构化 Review 替代声明，明确不可用原因及 static/Hosted CI 的可追溯引用；终态 required+available 设备/环境材料要求身份来源和证据引用。completion、validate、receipt、readiness 使用同一规则。缺项反例拒绝、合法路径通过。
2. F3 派生输出（主代理）：拒绝链接和 marker/冻结引用碰撞；Run 内输出使用同锁和原子替换，检查 summary/readiness 输出。失败不改变原证据。
3. F4/F5 子进程（独立实现任务）：清理不可被重复取消中断，Provider 调用显式使用预算；专属临时进程组测试结束回收。
4. F6 CI 与测试稳定性（CI 主代理；签名独立任务）：补触发路径和定向覆盖，捕获签名失败诊断并修复真实原因，禁止绕过信任验证。
5. 集成验收：定向回归、完整 unit、机械合同校验、真实 Feature 材料重放、性能对照、独立全生命周期复审。新源码摘要绑定新证据；旧报告仅作历史记录。

## 最小契约决策

- Review 替代信息放入已冻结的 Verification，包含 unavailable_reason、static_checks/hosted_ci 的 pass 状态与 evidence_ref。引用必须出现在 Verification.evidence_refs 且具有 URI 或 SHA256 形式。声明不等于独立 Review PASS 或 release approval。
- 终态必需且 available 的 device_identity/test_environment 必须有非空 source 与 evidence_ref；未知材料在非终态仍可 missing/null。已有冻结历史材料不自动补写身份或替代声明；不满足新规则的历史输入明确拒绝，新回放使用可审查的补充材料。
- 验证共享输出串行；独立任务仅写指定模块及新测试文件，不互相覆盖。

## 执行约束

work_item_kind=implementation；implementation_permission=用户本轮明确授权；exit_gate=六项回归及独立复审；handoff_target=主代理集成；retention=仓库计划/脱敏验证报告，原始诊断仅 /tmp。
retry_budget=每类故障两次无信息增量后重审假设；staleness_threshold=源码摘要变化即证据过期；heartbeat=每里程碑更新；stop_condition=pass/replan/blocked。
excluded_context=用户职责文档、真实设备/生产写入、commit/push/merge、未验证的 Provider 权威事实。

状态：完成。verifier=独立自动技术复审与使用验收；open_items=[]（本轮本地工具范围）；completion_claim=六项发现及签名错误落地、定向/全量/性能与独立验收通过。

## 里程碑 1

六项修复与反例已落地。独立使用验收首轮25条CLI通过。
独立复审发现F3同类遗漏：nearest owner可被嵌套标记遮蔽；已改为全部祖先Run保护、稳定顺序锁及禁止生成嵌套marker，并增加对应反例。contract_change_decision=明确所有祖先所有权；new_finding_class_count=0；review_round=2待复验。
全量首次集成265项暴露两项问题：GPG实际报agent IPC不可达（公钥已导入），以及旧reader不能读取新可选schema字段。
GPG修复禁止公钥操作自动启动agent，不忽略非零；旧reader测试明确限定generation路径兼容，使用带Review且符合旧schema的文档，新substitute字段须新schema。
下一步：最终定向回归→新源码冻结→阶段验收/独立复审；共享报告串行生成，历史报告保留。

## 里程碑 2

最终224文件源码摘要a250994bf9e714b9924b4cca0414add31c8f0748e350e7dcf85a2a1b83ade16c。
5项阶段验收、268项单测、17条检查、35项行为回归、4类旅程全部通过；独立全生命周期Spec/Quality=PASS/PASS、32条独立CLI验收符合预期。
attestation_readback=源码摘要和7份阶段报告绑定一致；stop_condition=pass；logical_task_open=false；session_handoff_required=false；consecutive_clean_reviews=1；review_round=2；new_finding_class_count=0。
无commit/push/merge；无live配置或权限变化。Provider活动记录dry-run失败且未持久化，不推导为知识已归档。
