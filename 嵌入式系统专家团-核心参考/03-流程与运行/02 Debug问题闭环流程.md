# Debug 问题闭环流程

## 1. 适用范围

用于缺陷、现场异常、长稳问题、性能异常、Crash/Panic/HardFault、存储异常、并发问题等。目标不是尽快给出一个看起来合理的原因，而是把问题从“现象”推进到可重复验证的根因和回归闭环。

## 2. 标准流程

```text
问题/现场现象
   ↓
冻结任务与版本身份
   ↓
建立时间线和原始 Evidence
   ↓
建立一份 Hypothesis Registry
   ↓
设计能够区分假设的实验
   ↓
更新 supported / rejected / confirmed
   ↓
确认 Root Cause
   ↓
形成最小修复方案
   ↓
回归 / Stress / Device / HIL
   ↓
Independent Review
   ↓
RCA / Knowledge Harvest
```

## 3. 第一步：先冻结上下文

在分析之前至少记录：

- 现象、发生时间、复现概率；
- 产品/板卡/设备标识；
- exact source base、firmware/image hash；
- kernel/SDK/RTOS/toolchain；
- 配置差异；
- 测试环境；
- 是否有最近变更；
- 日志、core、dump、寄存器、波形等原始材料。

如果这些信息互相矛盾，先处理 identity gap，不要直接开始猜根因。

## 4. 第二步：把事实和解释分开

示例：

|陈述|正确分类|
|---|---|
|“03:21:14 UBIFS remount read-only”|Observed|
|“可能是底层 NAND ECC 失败触发”|Inferred|
|“在相同块注入不可纠正 ECC 后稳定复现同一路径”|Confirmed supporting evidence|

日志中的错误字符串也只是 Observed，不一定就是 Root Cause。

## 5. 第三步：维护一份 Hypothesis Registry

每个假设至少写：

- `hypothesis_id`；
- statement；
- evidence_for / evidence_against；
- 当前 confidence；
- discriminating experiment；
- status：`open / supported / rejected / confirmed`。

所有参与专业角色向同一份 Registry 更新，不各自维护一套 RCA。

## 6. 第四步：实验优先区分假设

好的实验不是“再多打点日志看看”，而是能一次排除多个方向。

例如怀疑 DMA/Cache 时，可以把候选拆为：

- 地址映射错误；
- cache maintenance 范围错误；
- buffer 生命周期问题；
- completion/timeout 时序问题；
- 硬件返回异常。

实验应说明“如果结果 A，支持/排除哪些假设；如果结果 B，又说明什么”。

## 7. 常见问题的分析分层

### Kernel Panic

先确认 exact kernel/image、call trace、taint、module、last events，再分析 driver、UAF、race、memory、stack 或硬件症状。

### MCU HardFault

至少需要 fault registers、stacked context、PC/LR/SP、ELF/map、task/ISR context。PC 落在某函数只说明 fault 发生在附近，不自动说明该函数是根因。

### UBIFS / Flash

按层分析：

```text
NAND/NOR 介质
  → on-die / controller ECC
  → driver / MTD
  → UBI
  → UBIFS / FS
  → application concurrency / power-loss behavior
```

不要把“文件系统变只读”直接等同于“Flash 坏了”。

### Deadlock / Race

建立 wait-for graph、锁顺序、task priority、ISR interaction 和共享对象 lifetime，不能只 grep mutex 名称。

### 性能问题

严格走 `baseline → measurement → bottleneck → change → re-measurement`。没有基线和测量方法的“变快了”不算性能结论。

## 8. Root Cause 的确认标准

一个根因至少应满足多数条件：

- 能解释主要现象和关键日志；
- 与版本/平台差异一致；
- 有能区分其他候选的证据；
- 修复或故障注入能按预期改变结果；
- 回归未产生新的高风险副作用；
- Verification 能独立复核。

如果只能做到“改了以后暂时不出现”，状态应保持 supported 或 workaround，不应写 confirmed root cause。

## 9. 修复闭环

确认 Root Cause 后执行：

1. 最小必要修改；
2. 影响面分析；
3. regression scope；
4. 原始复现用例；
5. 负向/边界/长稳或故障注入；
6. required verification layers；
7. Independent Review；
8. Knowledge Harvest。

修复方案如果改变接口、资源、时序或启动/OTA，应重新拉架构/BSP/MCU/驱动相应责任人参与。

## 10. 常见失败方式

- **版本漂移**：分析日志来自 A 版本，修复验证却跑 B 版本；
- **结论先行**：先认定根因，再只找支持证据；
- **多专家多根因**：每个专业各写一套互不兼容的结论；
- **现象消失即 PASS**：没有验证原复现条件和回归范围；
- **用高置信度替代证据**：语言更肯定不代表事实更可靠；
- **RCA 只写总结**：没有 exact identity、实验和 evidence refs，后续无法复用。

## 11. 何时允许结束

Debug Run 收口前至少应有：

- 共享 Material/System Context；
- Hypothesis Registry；
- Root Cause 或明确 `evidence insufficient`；
- 若实施修复，存在 engineering package + delivery receipt；
- Verification + Review；
- Acceptance → Evidence；
- Knowledge Harvest。

证据不足可以 BLOCKED 结束阶段工作，但不能包装成“问题已定位”。
