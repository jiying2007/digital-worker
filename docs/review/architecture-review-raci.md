# Architecture Review RACI

> 本表先定义“需要哪些责任角色”，具体人名由评审会填写。若一个人兼任多个角色，责任仍按角色分开记录。

|工作项|Business/Process Owner|Embedded Engineering Owner|AI/Platform Owner|Knowledge Owner|Verification/HIL Owner|IT/Security|Release Owner|Architecture Review Board|
|---|---|---|---|---|---|---|---|---|
|批准 ADR-003 架构原则|C|R|C|C|C|C|C|A|
|选择首批 #6/#7/#8 Pilot|C|A/R|C|C|C|I|I|I|
|Knowledge Source Inventory / PoC (#16)|C|C|C|A/R|I|C|I|I|
|Provider Capability Matrix (#17)|C|C|A/R|C|C|C|I|I|
|Multi-runtime Pilot (#18)|I|A|R|C|C|I|I|I|
|端侧底座 ownership (#11)|C|R|I|I|C|I|I|A|
|main protection (#12)|I|C|C|I|I|A/R|I|I|
|merged branch GC (#19)|I|A/R|C|I|I|C|I|I|
|A3/A4 自动化边界扩展|I|R|C|I|C|C|I|A|
|A5/A6 设备权限扩展|I|R|C|I|C|A/R|I|A|
|A7 / Production Release 自动化|C|C|C|I|C|C|A/R|A|
|Productionization Review|C|R|C|C|R|C|R|A|

## 角色说明

- **Business/Process Owner**：明确要解决的业务问题、优先级和收益口径。
- **Embedded Engineering Owner**：负责嵌入式 Contract / Workflow / Pilot 的工程落地。
- **AI/Platform Owner**：负责 Runtime、Provider、Gateway 等 AI 平台能力，不拥有业务验收权。
- **Knowledge Owner**：负责 Knowledge Source Inventory、ACL、freshness、authority 和生命周期。
- **Verification/HIL Owner**：负责独立验证能力、测试资产、设备/HIL 证据口径。
- **IT/Security**：负责身份、权限、网络、Secret、审计和主仓治理等平台安全边界。
- **Release Owner**：负责 Release/OTA/生产放行责任，不由 AI 或实施者代签。
- **Architecture Review Board**：批准稳定架构原则及重大权限/边界变更。

## 评审要求

评审结束前，所有 `A/R` 为空的 P0 工作项必须补到具体人；无法指定 Owner 的事项默认 `DEFER`，不得以“团队共同负责”关闭。
