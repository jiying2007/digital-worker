# Acceptance → Evidence — EXAMPLE-UBIFS-001

|Acceptance Criterion|Verification Layer|Object Identity|Evidence Ref|Status|
|---|---|---|---|---|
|Cross-build passes|cross_build|base `1111111111111111111111111111111111111111`|`evidence://example/cross-build`|PASS|
|Original reproduction no longer triggers false read-only|device|EXAMPLE-DEVICE-001 + example firmware artifact|`evidence://example/device-regression`|PASS|
|True uncorrectable ECC remains fail-closed|hil|EXAMPLE-DEVICE-001 + controlled ECC injection|`evidence://example/uncorrectable-negative`|PASS|

本表只说明如何把验收项映射到直接证据；真实 Run 必须使用真实 identity 和可访问 evidence。
