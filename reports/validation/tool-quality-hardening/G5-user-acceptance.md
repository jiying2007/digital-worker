# 使用验收边界

自动重放见 G5-user-journeys.json：

1. 保留Feature证据初始化、冻结、验证与receipt生成；单Feature仍不能提升三轨产品资格。
2. Debug材料不足时blocked，补充上下文后允许重试，缺终态证据仍不授予资格。
3. Review材料不足时blocked，不计入产品资格，允许继续准备证据。
4. 中断后只读恢复预览、保留未引用generation并成功重试。

续行用户明确“授权自动审查验收”，本地G5改为独立自动使用流程验收，由/root/independent_acceptance承担。第二轮按冻结源码65b8b54b00f1135f1d72aff9030ea269d9f012499f051cb8224f3c907669caa5实跑17类场景，verdict=PASS；详细期望/实际/退出码见independent-round-2.json。

人类可用性研究与人类owner签收未执行，不属于本次用户授权的自动本地G5通过结论。自动验收不提升任何设备、Runtime或产品资格。

验收入口：docs/runbooks/tool-quality.md 的六个主要命令。独立使用者需按入口完成一个真实但可回滚的本地任务，检查错误可理解性、参数可发现性、BLOCKED原因与恢复提示；记录期望、观察、证据和接受结论。不要求真实设备部署，不由该流程授予产品资格。
