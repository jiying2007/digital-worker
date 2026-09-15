# Embedded Pilot real source probe

`embedded_pilot_source_probe.py` 用于 **real Pilot 初始化之前**，从本地 Source-of-Truth 只读采集不可猜测的 Git source identity，并可对指定原始日志/证据文件计算 size + SHA-256。

它解决的操作问题是：远端 Digital Worker/Knowledge Hub 已知道真实项目或 source family，但没有保存产品仓的 exact Git HEAD、原始日志 identity，因而不能合法创建 real Pilot。

## 边界

该 probe：

- 只读执行 Git 查询和文件 hash；
- 不修改产品仓；
- 不创建 Pilot run；
- 不生成 Material Manifest；
- 不判定 Verification / Independent Review / Release PASS；
- 不生成 `phase3_evidence_eligible` receipt；
- 不切换 canonical routing；
- 输出始终包含 `promotion_eligible=false`。

因此 probe 输出只能用于**真实任务绑定前的 source/evidence identity 输入**。

## 基本用法

```bash
python scripts/embedded_pilot_source_probe.py \
  --repo-root /path/to/product/repo \
  --require-clean \
  --output /tmp/real-source-probe.json
```

输出包括：

- requested repo root；
- Git top-level；
- full 40-hex `HEAD`；
- `remote.origin.url`（若存在）；
- worktree clean/dirty；
- dirty entry count；
- dirty status 的 SHA-256（不复制完整 dirty path 列表）。

`--require-clean` 下，dirty worktree 仍会先写出 probe report，然后 exit 2。real Pilot 应绑定能由 exact commit 表达的基线；不得把未提交工作树猜成 base commit。

## 绑定原始日志/证据 identity

```bash
python scripts/embedded_pilot_source_probe.py \
  --repo-root /path/to/product/repo \
  --evidence ubifs_log=/path/to/dmesg-ubi-ubifs.log \
  --evidence reproduction=/path/to/repro.txt \
  --require-clean \
  --output /tmp/real-source-probe.json
```

每个 evidence item 只登记：

- kind；
- absolute local path；
- byte size；
- SHA-256。

probe 不把“文件存在”外推成材料完整或工程结论正确。后续仍必须按 `docs/runbooks/embedded-pilot.md` 形成 Task Brief、Material Manifest、Verification、Pilot Result 和 frozen evidence bundle。

## PCR02 / SSC305 Debug 当前建议

对已登记的本地 source family，可先在实际 Git repository root 执行：

```bash
python scripts/embedded_pilot_source_probe.py \
  --repo-root /home/leiwenjun/work/sigmastar/pcr02_ssc305/SourceCode \
  --evidence ubifs_log=/path/to/original-ubifs.log \
  --require-clean \
  --output /tmp/pcr02-ssc305-ubifs-source-probe.json
```

若 `SourceCode` 不是 Git top-level，probe 会通过 `git rev-parse --show-toplevel` 返回真实 top-level；若该路径根本不属于 Git 仓，则 fail-closed。

拿到 report 后，仍需补齐 device / SPI-NAND part / partition / kernel-build / test identity 和 required Verification，才允许初始化 #6 对应的 real Debug Pilot。
