# 工具质量加固执行包

目标：按已确认的 G0–G5 计划修复 Run 生命周期、安全、CLI、性能与进程可靠性问题；保留按需采用、资格分离和历史证据读取。

非目标：平台化重构、真实设备或 Runtime 放行、修改外部仓库、提交、推送或合并。

领域模型：WorkItem → Run → artifact / receipt / report → qualification。业务流程声明与 Pilot 存储状态分别描述；执行成功不授予资格。

## 接口与边界

- 本地 POSIX、同文件系统；Python 3.11/3.12；直接依赖 PyYAML 6.0.3、jsonschema 4.26.0。
- 所有 Run 写者使用命名锁；候选验证后将不可变 generation 发布，最后原子切换 pilot-run.json；提交前校验原标记和输入摘要。
- 历史相对路径引用继续读取；不自动迁移或删除证据；恢复命令仅诊断。
- 新 Run ID 拒绝路径组件与控制字符；来源 URL 不输出 userinfo/query/fragment。
- JSON 模式输出一个文档；报告 BLOCKED 可返回 0，显式门禁未通过返回 2；内部错误 1，超时 124，取消 130。

## 阶段与验收

| 阶段 | 类别 / 优先级 | Owner / scope | Done when | Required evidence |
|---|---|---|---|---|
| G0 | 增强 / P2 | 维护者 / 基线与接口 | 计划、矩阵、源码快照固定 | G0-baseline.json |
| G1 | 缺陷 / P1 | 维护者 / 生命周期、来源探针 | 四项复现及中断并发测试通过 | G1-lifecycle.json |
| G2 | 增强、技术债务 / P2 | 维护者 / 校验、依赖、CLI | 兼容、JSON、doctor 和错误测试通过 | G2-cli-compatibility.json |
| G3 | 增强 / P2 | 维护者 / 性能与进程 | 热路径中位数下降至少30%，p95回退不超过10%；进程回收通过 | G3-benchmark.json、G3-process-lifecycle.json |
| G4 | 配置、增强 / P2 | 维护者、独立审查者 / 测试与CI | 原218项及新增测试通过，审查结论明确 | G4-regression.json、G4-review.md |
| G5 | 增强 / P2 | 代表使用者、独立审查者 / 使用验收 | 四类流程通过、独立验收完成 | G5-user-acceptance.md、closure.md |

生命周期责任基线：命令执行者持有唯一写锁，读取者只读单次Run标记及其附件引用。

| 操作 | 前态 → 后态 | 资源 owner | 终止与不变量 |
|---|---|---|---|
| init | absent → planned | 创建者 / 命名锁、候选目录 | 候选验证完成才发布；已有Run不覆盖 |
| status | mutable → planned/running/blocked/cancelled | 写者 / Run锁、新generation | 提交前失败保留旧引用；cancelled为终态 |
| bundle | mutable → 原状态 | 写者 / Run锁、附件、bundle | fail-incomplete不提交；不重写旧附件 |
| complete | mutable → completed | 写者 / Run锁、候选附件和标记 | 所有绑定与终态门禁通过后提交；拒绝迟到写入 |
| recover | 任意有效状态 → 原状态 | 读取者 / 标记快照 | 只诊断未引用generation，不删除、不提升资格 |
| 外部进程 | created → running → exited/cancelled/timed-out | 调用者 / 进程组、临时spool | 取消、超时回收进程组；输出超限不返回截断成功 |

提交后同步失败单列COMMIT_DURABILITY_UNCONFIRMED；可见性与断电耐久性分开报告。取消与完成由同一写锁排序；读取者可能看到完整旧Run或完整新Run。

工件：本目录保存需求和执行状态，reports/validation/tool-quality-hardening/ 保存脱敏验证结果；不保存原始日志或身份凭据。

## 执行约束

### 续行验收修订（2026-10-23）

用户明确授权“自动审查验收”，G4/G5原人工待签收项改为：独立技术代理进行whole-diff/whole-lifecycle审查，另一独立验收代理按公开Runbook实际重放CLI场景；主代理核真修复并统一验证。结论仅覆盖本地工具质量，不代表人类主观接受、真实设备、Runtime或产品发布资格。

并行准入=yes：两个独立只读任务，scope_write均为空（仅各自/tmp），共享源码冻结在f8024f894db6338dfedac06c34cd3d10e5c3e7ea42ad591d75b5390eed417612。父代理独占修复、根配置、测试和正式报告；子代理不写报告目录、不改源码、不执行共享输出验收。任务包v2，technical-review负责spec/quality双verdict，usage-acceptance负责expected/observed场景证据；均将脱敏摘要交回主代理，修复后再复审最终快照。

### 独立审查发现的契约补充

- Scaffold也是Run写者：原始Run与working路径拒绝符号链接，task引用受safe_ref约束；持同一Run写锁，终态拒绝scaffold。所有已存在/路径/类型冲突在任何输出前检查；单文件原子替换，避免--force经硬链接修改原附件。实际I/O故障可留下未发布草稿，Run标记保持不变，草稿不作为正式证据。
- 非交互进程的leader退出不足以返回成功。leader被回收后进程组仍存在时返回ORPHANED_PROCESS_GROUP并清理整组，不返回可能丢失迟到输出的成功结果；异常回收不以leader存活为前提。此严格结束判据不支持遗留后台worker，需由命令自身等待其子进程。
- 默认schema错误仅报告约束类型、字段路径及必要的缺失字段，不展开schema/instance；debug模式保留完整诊断。

- task-package v2；kind=implementation；permission=用户已授权本仓实现与验证；exit=阶段证据通过；handoff=下一阶段或独立审查者；retention=脱敏摘要。
- 同一失败最多重试两次；超过两次回到假设检查。15分钟无有效进展时重审；每阶段更新 heartbeat 与状态。
- P1 未关闭阻断总体验收；性能未达标保留 G3 未通过；缺独立审查阻断最终验收；外部资格缺证据仅阻断对应资格。
- 回退仅针对本轮补丁，保留已有 dirty 与所有已发布证据；旧读者兼容性未经验证不得回退读取实现。
- Spec chain：需求 → 能力矩阵 → 测试场景 → 源码快照绑定结果 → 独立审查。安装范围仅本仓；不修改 live 资产。
- Skill：本轮 primary 为 adk-planning-execution-loop；按需使用测试、review、完成验证与 session-wrap。默认单主代理执行。
