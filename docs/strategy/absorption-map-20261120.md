# digital-worker 退役能力去重与证据保全表

**2026-11-20；来源主线：digital-worker @ 18b65dc，ADK @ 9998312，codex @ 996f996，Knowledge Hub @ master。**
状态：归属建议与代码树对照；**不是已迁移、已部署、已评测通过**的声明。实际吸收必须以接收仓库的精确提交和 CI/现场用例证明。

## 一、一个能力一个负责人

| 原资产 | 接收者 | 决定与边界 |
|---|---|---|
| 三个需求/Debug/Review 任务模板 | ADK/Codex 的现有流程 | 已复制到历史 eng/tool，但不再引入新独立模板包；逐项比较现有 workflow，真缺失才修订 |
| 23 个 \`domains/edge-foundation/skills/*\` | ADK（选择性补缺） | 仅 DEFINED，非 EVALUATED。不得批量导入、不得把技能个数当收益 |
| \`嵌入式系统专家团-核心参考/\`、\`产品专家团-核心参考/\` | Knowledge Hub（去重候选） | 先对照 Hub 的 PCR02/UBIFS/OTA/嵌入式条目；按事实、适用范围、来源、owner 审核，不复制全集 |
| \`domains/edge-foundation/pilot/evidence/\` | 历史 Git/Digest + Hub *索引* | 保留原始 Feature/Debug/Review/Knowledge/R2 verdict 及未完成；索引只是链接，不重新签发 |
| \`schemas/\`、\`contracts/\`、正式 R2/Pilot verifier | 旧仓只读历史 | Codex 现已移除活动 Formal L2；llm_agent 已把原 R2 标为 retired-historical-only。无活跃消费者时不迁移执行器 |
| \`docs/adr/\`、过往设计 | 旧仓 Git 历史 | 保留可追溯 URL/commit；ADK/知识库只引用经证明长期有效的原则，不复制整个控制平面 |
| 旧项目 Issue/PR/CI | GitHub 历史 | 不能为了退役将未完成产品问题改写 PASS，先保留映射和精确证据 |

## 二、23 Skills 的实际去重方向

| Digital Worker 领域 Skills | 已有 ADK 相邻能力 | 结论 |
|---|---|---|
| embedded-task-classifier；embedded-material-readiness；embedded-evidence-normalizer | adk-requirements-triage；adk-verification-before-completion；adk-artifact-gating | 只比较任务/证据负例；不新增第三套分类器 |
| architecture-impact-analysis；interface-contract-review | adk-interface-contract-design；adk-component-api-stability；adk-structured-requirements-questioning | 复用 SDD/跨仓契约；若接口真实验证缺口，再补一条负例 |
| boot-chain-analysis；device-tree-review | adk-bsp-analysis；adk-bsp-porting-playbook；adk-driver-bringup-checklist | 复用 BSP 入口，避免重复 Skill |
| irq-dma-analysis；storage-filesystem-analysis | adk-interrupt-dma-patterns；adk-embedded-storage-layout-migration | 结合真实 IRQ/DMA、UBIFS 故障案例增强，先查 Hub 是否已有 |
| mcu-startup-analysis；linker-map-analysis；rtos-concurrency-analysis | adk-hardware-debugging；adk-performance-profiling-embedded；adk-rtos-task-design | 保留具体 ELF/MAP/HardFault 验证材料，方法重复则不迁 |
| driver-integration-review | adk-driver-implementation；adk-protocol-stack-integration | 直接复用 |
| log-triage；crash-hardfault-analysis；memory-corruption-analysis | adk-embedded-remote-debug-log-triage；adk-offline-core-dump-triage；adk-systematic-debugging | 优先吸收真实反例与追溯路径，而非新建角色 |
| performance-analysis | adk-performance-profiling-embedded | 直接复用，差异用真实负载验证 |
| verification-plan-builder；regression-scope-analysis；build-evidence-check | adk-test-strategy；adk-verification-before-completion；adk-cmake-cross-build | 有效来源/产物 SHA、必测用例/skip 的负例可进入现有评测 |
| device-evidence-check；hil-evidence-check | adk-integration-hil-sil；adk-production-field-readiness | ADK 已覆盖 board/firmware/rig/source 与 SIL/HIL 分层；只吸收缺失的机器校验案例 |
| release-readiness-check | adk-embedded-release-orchestration；adk-production-field-readiness | 复用 prepare/publish/device 单独授权；不创建新发布决策权威 |

**成熟度**：23/23 Defined，当前来源没有可合法晋级至 EVALUATED 的持久独立语义正/负例对；在 ADK 中新建评测之前不得声称改善成功。

## 三、优先级与真实验收

- **P0（禁止复活）**：维护者不要重新开启 Digital Worker 的 Agent 任务中心、领域知识副本、周期 R2 资格/巡检和 Formal L2，新项目不需要此仓 checkout。
- **P1（知识审计）**：以 Hub 现存 PCR02/UBIFS/OTA/嵌入式条目为基线；只有实质缺失、来源可验证且获 owner 复核的内容，才新增 Hub 受控文档。本文不自动修改 Hub。
- **P1（真实 HIL/OTA）**：PCR02 OTA Feature 的包 identity/哈希和 CI PASS 不等于实机 boot/rollback；各项目保留设备、固件、工装、日志的原始证据。
- **P2（必要时补 Skill）**：ADK 优先补少量正/负例；评价真实任务的失败覆盖和减少工时，不以 skill 数量或模板长度论成功。
- **保全**：冻结原工作样例 SHA、Pilot/Review/Knowledge/R2 receipt、9 个未完成 Issue 及其未验证边界。归档优先，永久删除需 Git bundle 全量恢复演练、外部引用核验。

## 四、现役消费者检查结果

- **Codex \`main\`**：\`manifests/session_bootstrap.json\` 为 L0/L1，\`docs/session-bootstrap.md\` 明确 Formal L2 入参已移除，旧 receipt schema 历史保留。
- **ADK \`main\`**：旧专属 \`manifests/integrations/digital-worker.json\`、\`.github/contracts/digital_worker_contract.py\`、\`.github/workflows/digital-worker-contract.yml\` 已不在当前 Tree；对应变更记录存在，不凭历史文件推断活跃依赖。
- **llm_agent \`main\`**：\`manifests/digital_worker_runtime_pilot.json\` = \`retired-historical-only / report-only\`，但仍含只读历史绝对来源和合同检查，不当作活跃 R2。
- **未核验**：私人开发主机、非公开 GitLab、设备和其他工作目录是否还有 live 引用。公开 Tree 无引用不是全环境依赖零证明。

## 五、退出顺序

1. 旧主机及用户态任务、cron/systemd、脚本、私有配置、挂载、引用清点；保护凭据。
2. 原仓完整 Git bundle、CI/Release/evidence/Issue 链接映射、checksum、可恢复副本验证。
3. 在仍在使用的消费者和真实开发主机确认没有 live \`digital-worker\` 依赖；若发现，迁到实际业务 owner 并验证。
4. Archive 仓库（优先只读保全）；如另外要求永久删除，先额外审查外部链接和完整备份。
