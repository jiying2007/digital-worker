# 案例：UBIFS 异常只读问题走查

> 这是流程示例，用来说明如何组织证据和判断，不代表某个真实项目已经得到相同根因，也不计入 real Pilot evidence。

## 1. 场景

设备长时间运行并存在并发写入，现场出现文件系统切换为只读。重启后可能恢复，也可能再次出现。团队需要判断问题来自 NAND/ECC、MTD、UBI/UBIFS、掉电/并发写，还是应用层使用方式。

## 2. Task Brief

目标：定位只读触发路径，形成最小修复和回归方案。  
不做：没有证据前不更换 Flash、不重做分区布局。  
验收示例：原复现条件下不再触发只读；关键错误码消失；24h stress 无新增 UBI/UBIFS 错误；掉电恢复行为满足产品要求。

## 3. Gate M 需要的材料

- exact kernel/BSP commit；
- board revision；
- Flash 型号和 on-die ECC 配置；
- MTD/UBI/UBIFS 配置；
- boot args / partition layout；
- 出错前后完整 dmesg；
- 应用写入模式；
- 设备 firmware hash；
- 是否有掉电/异常重启；
- 复现概率和运行时长。

缺 kernel/firmware identity 时先 BLOCK，不拿另一台设备日志替代。

## 4. 先建立事实时间线

示例：

```text
03:21:10 app write burst begins
03:21:12 NAND/MTD warning appears
03:21:13 UBI reports I/O error
03:21:14 UBIFS reports error and remounts read-only
03:21:15 application write returns EROFS
```

此时能够确认“只读发生在 UBIFS 报错之后”，但还不能确认真正根因在文件系统。

## 5. Hypothesis Registry

### H1：底层出现不可纠正 ECC，MTD 正确上报错误

实验：读取 controller/on-die ECC status，与 MTD return code 和相同 page 数据对齐。

### H2：ECC 状态解释或 MTD glue 返回值错误

实验：构造可纠正/不可纠正两类 case，对照 driver status mapping；检查 BDMA/RIU 两条读取路径是否一致。

### H3：DMA/cache 或 buffer 生命周期导致读取数据异常

实验：固定 buffer、切换 RIU/BDMA、增加精确 cache maintenance 观测，对比同一 page/hash。

### H4：UBI/UBIFS 在掉电/并发写条件下触发一致性保护

实验：使用可控 power-loss/write pattern，记录 UBI/UBIFS 首个错误及恢复行为。

### H5：应用层误操作或空间/挂载条件触发只读

实验：核对 mount option、space、write pattern、错误处理和并发行为。

## 6. 如何收敛

不要一次改多处。优先选择能够区分 H1/H2/H3 的实验，因为它们都可能在上层表现为 I/O error。

例如若：

- 原始 NAND 数据稳定；
- ECC status 显示“可纠正”；
- 某路径却返回 uncorrectable；
- 修正 status mapping 后原复现不再出现；

则 H2 获得强支持。但仍要用故障注入确认真正 uncorrectable case 仍会正确上报，避免“修复”变成吞错。

## 7. Engineering Package

若最终需要改 MTD/FSP_QSPI 层，应写清：

- exact source base；
- 修改文件和函数；
- 不改变哪些上层语义；
- 可纠正/不可纠正 ECC 的期望返回；
- BDMA/cache 的必要约束；
- required cross-build/device/stress；
- rollback plan。

## 8. Verification

建议至少：

- cross-build；
- 正常读写 smoke；
- 可纠正 ECC case；
- 不可纠正 ECC negative case；
- 原现场并发写复现；
- 长稳；
- 必要时掉电恢复。

每个 case 绑定 firmware hash、board/device 和 log evidence。

## 9. Review

独立审查重点：

- 是否只是屏蔽错误而没有修根因；
- 真正坏块/ECC failure 是否仍能 fail-closed；
- cache/DMA 修改是否影响其他读路径；
- UBIFS 恢复/数据完整性风险；
- 量产设备是否需要数据迁移或特别处理。

## 10. Knowledge Harvest

如果形成稳定结论，可沉淀：

- 某控制器 ECC status 解释规则；
- NAND→MTD→UBI→UBIFS 分层排查 Runbook；
- 可纠正/不可纠正 ECC 回归用例；
- 某平台 BDMA/cache 约束。

如果最终只是单块 Flash 物理损坏且没有可复用规律，可以 `NO_KNOWLEDGE_DELTA`。
