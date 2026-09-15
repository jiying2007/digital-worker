# Edge Foundation Knowledge Registry

`registry.yaml` 是 Edge Foundation 本地 bootstrap Registry。长期上下文、Evidence、生命周期和跨仓知识仍以 Knowledge Hub 或原始 Source of Truth 为权威；本地 Registry 只登记可追溯入口，不复制外部 SoT。

规则：
- `source_ref` 必须指向当前仓库存在的 target contract、核心参考或治理文档；
- 不登记已退役 1+7 identity / compatibility tree；
- `owner` 使用 Role / Capability / Assurance 身份；
- provider 仍由 `config/integrations/cross-repo-lock.json` 精确锁定；
- 本地 query 只用于 bootstrap 候选，正式任务优先通过 Knowledge Hub context/evidence-pack。
