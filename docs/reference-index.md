# 方法、正式工具与历史证据索引

采用范围更新：2026-11-18。日常工作使用[三类任务模板](../README.md#从一个实际任务开始)，已有项目 Issue/PR、源码、测试和责任人决定继续作为工程事实来源。

## 先按问题查方法

| 当前问题 | 参考 |
|---|---|
| UBIFS 只读与存储故障 | [UBIFS 走查](../嵌入式系统专家团-核心参考/07-案例/01%20UBIFS只读问题走查.md) |
| MCU HardFault、RTOS 并发 | [HardFault 与 RTOS 走查](../嵌入式系统专家团-核心参考/07-案例/03%20MCU%20HardFault与RTOS并发走查.md) |
| 新板和平台 Bring-up | [Bring-up 走查](../嵌入式系统专家团-核心参考/07-案例/04%20新板Bring-up走查.md) |
| 多仓功能、OTA 与发布 | [多仓与 OTA 走查](../嵌入式系统专家团-核心参考/07-案例/02%20多仓功能与OTA发布走查.md) |
| 器件替代与兼容性 | [器件替代走查](../嵌入式系统专家团-核心参考/07-案例/05%20器件替代兼容性走查.md) |
| 方法是否已经验证有效 | [Skill 成熟度台账](../嵌入式系统专家团-核心参考/05-工程交付/06%20Skill评审成熟度台账.md)、[SKILLS 索引](../SKILLS.md) |

案例提供分析方法与适用边界，使用时补充当前项目的真实材料。ADK 已有相同方法时先复用；只有确认独特缺口和实际收益后，再通过独立变更吸收。不会整包合并本仓，也不在这里新建 Skill 安装或资格平台。

## 显式选用的正式集成

| 需要解决的事 | 入口和限制 |
|---|---|
| 冻结、校验一份正式 Pilot 材料 | [Pilot Quickstart](runbooks/embedded-closed-loop-quickstart.md)、[完整 Runbook](runbooks/embedded-pilot.md)；真实执行和验证由任务提供 |
| 本地依赖、错误和中断后的文件核对 | [本地工具操作](runbooks/tool-quality.md)；recover 是只读预览，不会自动续跑模型 |
| 查询合同和责任定义 | [合同目录](../contracts/catalog.json)、[Edge Foundation](../domains/edge-foundation/domain.yaml)、[ADR](adr/) |
| 查看冻结状态和证据引用 | [当前机器 Review Snapshot](../嵌入式系统专家团-核心参考/00-评审导览/03%20当前机器状态快照.md)；派生视图不替代任务效果或产品验收 |
| 研究 Runtime 替换 | [R2 资格策略](../manifests/runtime-r2-qualification-policy.json)、[本地终端操作](runbooks/runtime-r2-local-terminal.md)；R2 不进入普通项目热路径 |
| 理解原有跨仓设计 | [策略索引](strategy/README.md)；这些正式集成基线不要求日常项目同时部署全部仓库 |

选择正式流程后，继续遵守其精确来源、材料和验证规则。使用三类普通模板不会自动创建 Formal Evidence，也不会因为未部署正式流程而失去项目自己的验证义务。`engineering-platform` 与本仓互不作为安装或执行依赖。

## 历史证据与版本边界

下列说明基于采用收敛前的主线 `32af8a82b6967cbbdd665c851b5394bc900fd417`（2026-10-24）。保留资料按原始任务、版本和证据范围解释；本次入口整理不宣称产生了新的模型、设备或生产验收结果。

| 保留材料 | 能说明什么 | 不能据此推导什么 |
|---|---|---|
| [FEATURE-PCR02-OTA-001](../domains/edge-foundation/pilot/evidence/FEATURE-PCR02-OTA-001/) | 2026-09-14 的 OTA 包身份 manifest/verifier、原 source/result commit 和当时检查引用 | 设备 install/boot/rollback、发布通过或新的工程执行 |
| [Real Feature CI](../.github/workflows/real-feature-pilot-evidence.yml) | 从保留文件重新生成、冻结和校验回执；断言 Feature eligible=1、总体 BLOCKED | 每次运行都完成了一项新的 Feature，或验证了整套 Skills |
| [Knowledge E3 材料](../domains/edge-foundation/pilot/evidence/) | 各文件所描述的一次知识使用或来源/权限/新鲜度检查 | 全部知识服务或当前项目已经合格 |
| [R2 冻结记录](../reports/runtime-r2/) | 已冻结的任务、运行时身份和已有观察 | 缺少的真实执行已发生，或所有 Runtime 可互换 |
| [工具加固记录](changes/tool-quality-hardening/closure.md)与[验证报告](../reports/validation/) | 所列快照和环境下的工具测试、自动审查与边界 | 人工主观接受、设备验证或产品上线 |
| [原始材料](source-materials/)、[早期草案](archive/)、[架构探索](brainstorm/) | 需求来源、设计理由与演进过程 | 当前已实现功能或当前交付承诺 |

原 Product readiness 中 Debug、Review/Release 的缺口保持原样；历史未完成和未知结果不会因新的采用范围变成 PASS、未执行或安全取消。需要续做时使用新的项目任务并引用原材料，已冻结的来源和结论不重标。
