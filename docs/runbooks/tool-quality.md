# 本地工具环境与可靠操作

Digital Worker 按需采用。小任务仍可直接使用项目 CLI、ADK 与项目验收。本页适用于 Linux 本地文件系统；Python 支持 3.11、3.12。共享网络文件系统与其他操作系统未验证。

先使用所选解释器安装根目录 `requirements-dev.txt` 的直接依赖，再运行 `python scripts/edge_pilot.py doctor --json`。doctor 使用标准库，缺依赖时仍可给出可操作结果。`--help` 和绝对路径入口均可从其他 cwd 使用。

## 六个主要命令

1. `python scripts/edge_pilot.py doctor --json`：检查环境。
2. `python scripts/edge_pilot.py init --help`：按帮助填写任务、owner、来源和输出根目录，创建 Run。真实任务使用完整40位SHA。
3. `python scripts/edge_pilot_scaffold.py <run-dir>`：生成待填写材料；人工补齐真实材料与验收证据。
4. `python scripts/edge_pilot.py complete <run-dir> --help`：按帮助传入已准备的附件，校验后冻结。
5. `python scripts/edge_pilot.py validate <run-dir> --json`：验证冻结内容及其绑定。
6. `python scripts/edge_pilot.py pilot-receipt <run-dir> --json`：生成派生评估回执。

具体参数与完整例子见[现有Pilot Runbook](embedded-pilot.md)。上面含 `--help` 的命令用于展示所需参数，实际创建和冻结时使用该页中的完整命令。

## 状态、引用与恢复

- 所有写者使用每Run命名锁；出现 `RUN_LOCKED` 时等待现有写者结束后重试。不要删除锁文件：锁由内核随进程退出释放，文件本身保留以避免锁身份竞争。
- Scaffold同样持Run写锁，拒绝终态、符号链接及越界task引用。重复运行前检查全部目标；`--force`仅允许替换安全工作文件，保留其他用户草稿。预条件失败不写任何输出，实际I/O失败可能留下未发布草稿，Run标记不变。
- 新写入生成 `artifacts/<generation>/` 附件，最后原子切换 `pilot-run.json`。消费者始终读取 Run 的 `*_ref`，不要假定附件位于根目录。旧平铺证据继续读取。
- `status`、`bundle`、`complete` 在提交前失败不切换候选；completed/cancelled 保持终态。提交后目录同步失败返回 `COMMIT_DURABILITY_UNCONFIRMED`：提交已可见但耐久性未确认，须先检查恢复预览，不盲目重试。修订终态证据须创建 superseding Run。
- `RUN_CONFLICT` 表示标记或输入被其他写者修改；先检查最新Run，再决定是否重试。
- 中断后运行 `python scripts/edge_pilot.py recover <run-dir> --dry-run --json`，核对未引用generation。命令仅诊断，不删除证据、不自动续写。未引用不等于可立即删除。
- 事务保证限定遵守协议的本地写者；不防御有权限的恶意进程。已验证故障注入，不等于物理断电、跨文件系统或NFS认证。

## 机器输出与退出码

`--json` 可放在子命令前后；stdout为一个JSON文档。错误给出 `error_code/message/field_path/next_actions`，显式 `--debug` 可查看Traceback。

默认schema错误只列约束及字段路径，不展开整个schema和输入实例。
`summary` 的 `invalid_runs` 保持 v1 字符串列表，使用相同的错误码、字段路径和脱敏消息，
每条诊断最多2048字符；普通输出、`--json` 和 `--output` 均不展开非法输入全文。

| 退出码 | 含义 |
|---|---|
| 0 | 命令执行成功；报告中的BLOCKED仍表示资格未满足 |
| 2 | 参数、写锁/冲突，或显式请求的门禁未满足 |
| 1 | 校验输入、I/O或内部错误；以error_code定位 |
| 124 | 外部进程超时 |
| 130 | 用户取消 |

`product-readiness --require-ready` 未满足资格时返回2，普通报告模式可返回0并报告BLOCKED。独立readiness入口也支持 `--json`；使用 `--output` 时结果同时写到该文件，JSON模式stdout仍是一个结果文档，不追加人类摘要。

## 外部进程预算

非交互子进程按进程组回收。默认 Git 60秒、Provider/GPG 120秒、host 300秒、原生Runtime 3600秒；可通过 `DW_GIT_TIMEOUT_SECONDS`、`DW_PROVIDER_TIMEOUT_SECONDS`、`DW_HOST_TIMEOUT_SECONDS`、`DW_RUNTIME_TIMEOUT_SECONDS` 显式设置有限正值。超时或取消先TERM，5秒后KILL。

命令自身必须等待其子进程。leader退出后仍有遗留进程组时返回 `ORPHANED_PROCESS_GROUP` 并清理整组，不能将丢失迟到输出的结果当作成功；该入口不支持遗留后台worker。

KILL 发出后还会等待 `/proc` 确认该组没有活动成员；僵尸由其父进程回收。
确认等待有界，若仍有活动成员则返回 `CLEANUP_UNCONFIRMED`，不把“已发信号”当作清理完成。

输出先流式写入临时文件，默认总上限64MiB，可用 `DW_MAX_OUTPUT_BYTES` 设置有限正值。超过上限返回 `OUTPUT_LIMIT`，不以截断结果继续解析或授予资格。成功机器输出保持完整；失败诊断最多携带64KiB脱敏尾部。临时spool在调用结束时关闭，需保留的正式日志仍由原调用方写入既有日志路径。

来源URI输出移除userinfo、query、fragment；这不表示任意Runtime原始日志都已自动脱敏。

## 验证

快速回归：`python -m unittest discover -s tests/unit -p 'test_tool_quality.py' -v`。

完整本地回归：`python -m unittest discover -s tests/unit -p 'test_*.py' -v`。

性能及阶段验收：准备隔离的改前源码副本，通过 `DW_QUALITY_BASELINE` 指定其根目录，再运行 `python -m unittest discover -s tests/acceptance -p 'test_tool_quality_acceptance.py' -v`。该入口生成脱敏阶段报告；它是作者本地验证，不替代独立审查和代表使用者验收。
