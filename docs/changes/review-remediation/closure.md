# 全面审查整改闭环

目标：关闭六项审查发现与全量签名测试错误。claimant=主代理；verifier=独立自动技术审查及自动使用验收。

## 实施结果

| 条目 | 实施 | 对应证据 |
|---|---|---|
| F1 Review 替代证据 | Verification 增加结构化原因、static/hosted CI passing 引用；完成、验证、receipt/readiness 共用检查 | test_review_remediation 的缺项拒绝及完整消费链 |
| F2 HIL 身份 | 终态 required+available 设备/环境必须有 source/evidence_ref | 同一测试中的两类材料、两字段缺失负例 |
| F3 派生输出 | 所有祖先 Run 固定排序加锁、拒绝链接/冻结引用碰撞/嵌套marker，临时文件原子发布 | 原绕过及新增嵌套owner负例；写入失败保持字节不变 |
| F4 取消清理 | 清理期间延迟重复 TERM/INT，完成 KILL/wait 后恢复信号屏蔽集合 | test_bounded_process_followup，三种取消序列 |
| F5 Provider 预算 | run_hub 显式 category=PROVIDER | 四种公共入口超时负例 |
| F6 CI 过滤 | PR/push 同时覆盖根schema、scripts、tests、领域 | path coverage 定向检查 |
| 签名错误 | GPG public-only import/verify 禁止自动启动agent，保留有限脱敏错误信息 | 真实不可启动agent正例、篡改签名负例 |

旧版 schema 不认识新增 review_substitute，迁移以新增 Verification 和新 Run 重放，历史报告/终态不补写。generation路径本身继续通过旧reader测试；它不代表新字段向旧schema兼容。

## 独立审查与自动使用验收

- /root/independent_review：whole-diff / whole-lifecycle，最终 Spec=PASS、Quality=PASS。
- 首轮发现F3最近祖先owner可遮蔽外层冻结引用；同类修复后独立重放两步绕过均拒绝，原字节不变。reopened=0，修复后新增发现=0，clean review=1。
- 最终独立专项测试：资格与输出7项、子进程4项、签名10项通过。
- /root/independent_acceptance：首轮25条实际CLI，最终同快照7条增量CLI，均符合退出码/状态/原字节保持预期；有效完成、负向缺证据、写锁、输出碰撞/链接/嵌套owner、readiness显式门禁、recover均覆盖。
- 这是独立 AI 自动验收，不是人类签收、外部链接实时核验、设备HIL或产品放行。

## 验证快照和阶段证据

HEAD=6160b33862a3b077fe8d2a21ab1a15416491cf0b。
execution source snapshot=a250994bf9e714b9924b4cca0414add31c8f0748e350e7dcf85a2a1b83ade16c，224文件；schema/scripts/domain/test/workflow/requirements均纳入。
新阶段报告独立写入 reports/validation/review-remediation，保留先前 reports/validation/tool-quality-hardening。

阶段验收：5项全部通过（194.971秒）。其中完整单元测试268项通过（63.041秒），17条命令全部exit0，35项既有行为回归通过，4类用户旅程通过（包含真实Feature资料回放、两track阻断后重试、中断恢复重试）。

性能相对既有优化前精确基线：validate中位366.74→177.61ms（下降51.6%），receipt456.18→243.75ms（下降46.6%），readiness565.51→283.18ms（下降49.9%）；P95均改善。32MiB哈希结果正确，Python峰值2,102,294字节。基准不等于生产SLA，比较对象是原有优化前基线，不是本轮开始时快照。
7份阶段JSON已逐一核对摘要，全部绑定相同224文件源码快照；索引见reports/validation/review-remediation/evidence-index.json。

## 被证伪路径与修复依据

- 初次265项集成：1 failure、1 error；不能用定向通过覆盖全量失败。
- GPG stderr确认两公钥已导入，但自动连接agent触发IPC失败，import exit2。不可启动agent对照稳定复现；no-autostart完整验签通过且坏签名拒绝。没有忽略返回码、变更信任或解除沙箱。
- 新Verification字段被旧schema拒绝是预期契约边界；旧reader测试改用含Review的旧字段集，单独检验generation路径。
- F3首版nearest owner保护不足；最终所有祖先共同保护，新增结构化反例。

## 完成声明和边界

completion_claim=六项建议及签名错误已落地并完成本地验证与独立复审；open_items=[]（本轮本地工具范围）。
Completion Guard：required_checks=[unit,contracts,negative_paths,performance,feature_replay,independent_review,automated_user_acceptance]；passed_checks=全部；failed_checks=[]；stale_checks=[]；completion_allowed=true。
G5自动化报告保留author-run身份及pending独立字段；真正的独立AI结论单列于本文件和索引，未将其改写为真人验收。
运行环境为Linux Python3.11.16；Python3.12/GitHub Actions只保留CI矩阵，未作本机通过声明。
本轮真实Feature是既有资料本地回放；新的policy-v2文件只结构化原证据，非新CI或设备结果。
未执行真实Provider/Runtime、物理设备、断电、NFS资格；未修改受管live资产或权限，未commit/push/merge。
Provider context可解析但仅有reviewing/unverified provisional记录，无权威资格提升；未声明知识已归档。
活动记录经Provider `activity-capture --dry-run` 返回 `PROVIDER_RESPONSE_INVALID`、persisted=false、write_performed=false；未执行apply或绕过Provider写入其他知识目录。该项仅限制知识记录，不影响本地代码验收。

## 回退与复用决策

保留用户原dirty。回退仅撤销本轮精确patch并重建对应schema版本的派生报告；不得reset/覆盖用户文件或改写冻结历史。
reusable_pattern=全部祖先资源所有权保护、显式预算、纯公钥验签不依赖agent。
promotion_candidate=false；do_not_promote_reason=仅项目内验证，未要求推广运行资产。
next_task_friction_reduced=是；reduced_by=稳定反例与有界诊断；reduction_evidence=上述专项测试。
owner_review=用户授权自动审查验收；rollback_path=精确patch及新增报告回退；verification_evidence=新阶段报告与独立复审。
trace_eval/runtime_control_plane/browser/ship=不适用，未改变模型路由、工具权限、浏览器流程或发布授权；运行期入口CLI的外部cwd、取消和失败路径已覆盖。
