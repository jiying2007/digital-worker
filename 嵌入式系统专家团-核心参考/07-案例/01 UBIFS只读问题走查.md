# 案例：UBIFS 异常只读问题走查

> 流程示例，用于说明一次诊断任务如何组织事实、Hypothesis、Evidence 和工程闭环；**不代表真实项目已经得到相同 Root Cause，也不计入 real Pilot evidence**。  
> 通用规则见 [任务类型运行矩阵](../03-流程与运行/05%20任务类型运行矩阵.md)、[任务生命周期与 Gate](../03-流程与运行/01%20任务生命周期与Gate.md)、[验证/评审/发布](../03-流程与运行/04%20验证评审发布与异常恢复.md)。专业方法见 [调试与可靠性](../04-专业能力/05%20调试与可靠性领域指南.md) 和 [Linux/BSP](../04-专业能力/02%20Linux%20BSP领域指南.md)。

## 1. Task

设备长时间运行并存在并发写入，现场出现文件系统切换为只读。目标是定位只读触发路径，形成最小修复和回归方案；没有证据前不更换 Flash、不重做分区布局。

Acceptance 示例：原复现条件下不再触发只读；关键错误码消失；24h stress 无新增 UBI/UBIFS 错误；掉电恢复满足产品要求。

## 2. Context / Material

至少冻结：exact kernel/BSP commit、board revision、Flash 型号与 on-die ECC 配置、MTD/UBI/UBIFS 配置、boot args/partition、完整 dmesg、应用写入模式、firmware hash、异常重启/掉电信息、复现概率和运行时长。

缺 kernel/firmware identity 时保持 BLOCK，不拿另一台设备日志替代。

## 3. Routing

任务类型：缺陷/现场诊断；采用 diagnostic 路径。P06 Debug/Reliability 维护唯一 Hypothesis Registry，P03 Linux/BSP 提供 NAND→MTD→UBI→UBIFS 平台事实；需要驱动资源事实时再拉 P05。

## 4. Analysis / Hypothesis

先建立事实时间线，例如：

```text
03:21:10 app write burst begins
03:21:12 NAND/MTD warning appears
03:21:13 UBI reports I/O error
03:21:14 UBIFS reports error and remounts read-only
03:21:15 application write returns EROFS
```

此时只能确认“EROFS 出现在 UBIFS 错误之后”，不能直接确认 Root Cause 在文件系统。

候选假设：

- **H1**：底层出现不可纠正 ECC，MTD 正确上报；
- **H2**：ECC status 解释或 MTD glue 返回值错误；
- **H3**：DMA/cache 或 buffer lifetime 导致读取数据异常；
- **H4**：UBI/UBIFS 在掉电/并发写条件下触发一致性保护；
- **H5**：应用层 mount/space/write/error handling 条件触发只读。

## 5. Evidence / 区分实验

优先做能区分 H1/H2/H3 的实验：对齐 controller/on-die ECC status、MTD return code 和同一 page/hash；构造 correctable/uncorrectable case；比较 RIU/BDMA 路径和 cache maintenance；再扩展到 power-loss/write pattern 和应用写入条件。

例如若原始 NAND 数据稳定、ECC status 为 correctable、某路径却返回 uncorrectable，修正 mapping 后原复现消失，则 H2 获得强支持。但仍必须用真正 uncorrectable negative case 证明修复没有“吞错”。

## 6. Decision / Engineering

Root Cause 足够后才形成 Technical Decision。若修改 MTD/FSP_QSPI，应明确 exact source base、修改函数、不变语义、ECC 返回约束、BDMA/cache 约束、required cross-build/device/stress 和 rollback plan。

一次只改最小责任点，不把 ECC、DMA、UBIFS 和应用层同时修改后再凭结果倒推原因。

## 7. Verification

围绕本任务 Claim 建议覆盖：cross-build、正常读写、correctable ECC、uncorrectable ECC negative case、原并发写复现、长稳，以及 required 时的 power-loss recovery。每个 case 绑定 firmware hash、board/device 和原始 log/evidence。

Verification 只报告直接 Evidence 支持的层级，不因“问题暂未复现”扩大 PASS。

## 8. Review

Independent Review 重点检查：是否只是屏蔽错误、真正坏块/ECC failure 是否仍 fail-closed、cache/DMA 修改是否影响其他读路径、UBIFS 恢复/数据完整性风险，以及量产设备是否需要特别迁移或处置。

## 9. Knowledge Harvest

若形成稳定结论，可沉淀 ECC status 解释规则、NAND→MTD→UBI→UBIFS 分层排查 Runbook、correctable/uncorrectable 回归用例、BDMA/cache 约束。若最终只是单块 Flash 物理损坏且无可复用规律，则 `NO_KNOWLEDGE_DELTA`。
