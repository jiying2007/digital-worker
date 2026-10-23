# 工具质量审查记录

Review Target: working-tree（本轮在既有dirty上增量实施）
Reviewer Independence: independent automated reviewer（续行用户授权，原作者自审保留为历史）
Review Mode: whole-diff / whole-lifecycle
Requirement Baseline: docs/changes/tool-quality-hardening/requirements.md
Snapshot Identity: 65b8b54b00f1135f1d72aff9030ea269d9f012499f051cb8224f3c907669caa5；HEAD不变，此前脏改不回退。

## 已核实并修复

- 四项P1：无效status写终态、complete丢失并发更新、Run ID路径越界、source remote凭据输出。
- 并发由命名写锁排序，提交前复核输入；已发布附件不覆盖，标记最后切换。跨进程锁、外部更新冲突、发布前中断、终态重试均由行为测试验证。
- 旧平铺Run继续验证，改前读者可读新generation引用；既有Skill冻结测试改为通过Run引用解析bundle，完整性断言保留。
- schema编译缓存限定单次调用；schema内容变更、附件篡改仍重新拒绝，不缓存资格PASS。
- 进程组超时、KeyboardInterrupt和SIGTERM取消清理；输出超限拒绝截断成功，完整机器输出维持原协议。
- 自审补充：标记切换后目录fsync失败必须报告提交已可见、耐久性未确认；invalid summary及带output文件的readiness在JSON模式仍输出单文档。均有定向回归。
- 首轮静态验收发现Quickstart英文固定token大小写不匹配，已修正文案，未放宽校验器。

## 语义边界

- Owner=持锁命令执行者；资源=命名锁、候选目录、generation、Run标记及外部进程组；取消/超时先停止再清理。
- 可见提交后不自动回滚证据。故障注入不代表设备断电耐久、NFS、恶意同权限写者或真实Runtime认证。
- CLI报告成功、产品资格、R2、Provider及人工责任验收仍为独立结论；未改签名、权限、否决和真实证据要求。
- 原有外部checkout核验保留；本地无网络检查不冒充该核验已通过。

## 双 verdict 与剩余项

Spec compliance: PASS，独立代理按新快照复审。
Quality: PASS，限定本地工具合同；整体机械门禁另见G4-regression.json。
Review round: 2；首轮两个major已修复且由独立代理复验关闭，reopened=0，new findings=0，clean round=1。
Independent whole-lifecycle review: PASS（/root/independent_review）。
Independent automatic usage acceptance: PASS（/root/independent_acceptance）。
证据见independent-round-1.md与independent-round-2.json。独立代理未写仓库，父代理按其实际返回结果整合。

修复后的严格进程结束判据已先写入requirement。Scaffold新增写锁、终态/链接/越界/全输出预检，单文件原子替换避免硬链接污染；默认schema错误不展开实例。技术代理独立35项测试17.107秒通过，并单独重放链接force和leader0/7退出负例；使用代理17类场景通过。此记录仅为用户授权的本地自动验收，不代填人类身份，不授权提交、合并或产品发布。
