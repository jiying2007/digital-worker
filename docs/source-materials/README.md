# 原始输入材料

本目录保存研发中心数字员工方案与专家团设计过程中使用的原始输入。它们可以作为来源证据，但**不是当前运行时 SSOT，也不能直接覆盖 ADR / Contract / Schema / Workflow**。

当前材料：

- `研发中心AI数字员工办公体系改造方案（预案）.docx`
- `端侧底座专家团创建.docx`
- `硬件电路/硬件电路开发模块（举例）.docx`

## 使用规则

1. 二进制材料先规范化为可 diff 的 Markdown/结构化摘要，再进入正式评审；
2. 任何职责、ownership、接口或安全边界的 resolved 决策必须附 evidence ref；
3. 原始文件保持只读，不在本仓复制多个“最新版/最终版/兼容版”；
4. 敏感现场日志、core、binary、固件和客户材料不因 Pilot 自动归档到这里；
5. 对端侧底座专家团的 capability ownership，在 `端侧底座专家团创建.docx` 完成规范化前保持 fail-closed / unresolved。
