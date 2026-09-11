# Four-Repo AI R&D Operating System — 当前阶段集成基线

- Status: `current-stage-baseline`
- Scope: `digital-worker` / `knowledge-hub` / `agent-dev-kit` / `llm_agent`
- Provider selection: `not_frozen`

## 1. 目标

把四个仓库收敛为一个职责清晰、Source of Truth 不分裂的研发 AI 操作体系，而不是四套彼此重叠的平台。

```text
                    digital-worker
                 R&D Operating Model
        Work / Expert / Gate / Evidence / Review
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
 knowledge-hub    agent-dev-kit     llm_agent
 Knowledge CP     Agent Asset CP    Practice/Eval Lab
        │              │              │
        └──────────────┼──────────────┘
                       ▼
           Engineering Agent Runtime(s)
                       │
                 Git / CI / HIL
```

## 2. 权威边界

### digital-worker

唯一拥有研发域 Operating Model：Work Item/Run、Expert identity/routing、Gate、Action Policy、Technical Decision、Engineering Handoff、工程身份链、Verification、Independent Review、Pilot 与 Domain Maturity。

不得发展第二套完整知识生命周期引擎、Runtime-specific exporter 或外部实践吸收实验室。

### knowledge-hub

长期 Knowledge Control Plane：Registry、Context/Evidence Pack、知识生命周期、Owner Review/Promotion、Compatibility Intelligence。

digital-worker 只允许通过 Adapter 读取；Knowledge Harvest 只能形成 Proposal，不得直接写 active knowledge。

当前 `digital-worker` governed project route 尚未完成 `projects/repositories/project-routes` 三 registry 正式登记，因此 Knowledge Hub 集成保持 candidate；路由不可证明时必须 BLOCK/NEEDS_REVIEW，不得回退成“假装已接入”。

### agent-dev-kit

平台中立 Agent Asset Control Plane：Reusable Agent/Skill/Profile/Workflow、target export/install/rollback、资产验证和发布。digital-worker 的组织专家身份保留在本仓，但通用执行 Skill 应优先复用/包装 ADK。

### llm_agent

Practice/Runtime Evaluation Lab：外部实践 intake/adoption evidence、Runtime target health、跨 Runtime 对照、Loop Readiness。它不是生产 Runtime，也不得对 digital-worker 的 Verification 给 PASS。

### Git / CI / HIL / Artifact Store

继续保存 Source SHA、Build identity、Artifact hash、Device/Test/Release 等强事实。Knowledge Hub 只引用，不复制为第二 SSOT。

## 3. Cross-repo Identity Spine

跨仓可复现必须至少关联：

```text
work_item_id / run_id
knowledge-hub provider commit + source fingerprint / evidence pack
ADK provider commit + version + profiles + asset bundle hash
runtime provider / target / version / execution receipt
repo base/result SHA + build/artifact/device identity
verification_run_id + review evidence
```

机器视图：`contracts/cross-repo/identity-envelope.yaml`。

## 4. Provider Lock

当前 provider/contract exact pin 位于：

`config/integrations/cross-repo-lock.json`

Lock 只固定一次实验/集成所消费的接口身份，不等于把总体架构 Provider 选择冻结。Provider CI 红、接口不可达或 identity 不完整时必须显式 BLOCKED/NOT_READY。

## 5. Skill Ownership

`expert-groups/embedded-system/config/skill-ownership-matrix.yaml` 对全部 P0 Skill 做 `KEEP_DOMAIN_CONTRACT / WRAP_ADK / ADK_REUSE_CANDIDATE` 分类。

规则：

- Domain role / Gate / Evidence semantics 留 digital-worker；
- 可跨域复用的执行方法优先放 ADK；
- 没有 real Pilot evidence 不删除现有 Domain Skill；
- 不因为名字相似就认定语义等价。

## 6. Knowledge 使用与 Harvest

任务期优先路径：

```text
Work Item / scope
 -> digital-worker Knowledge Adapter
 -> Knowledge Hub context/evidence-pack
 -> Expert/Runtime 使用候选与事实
 -> claim/evidence
```

任务关闭：

```text
Knowledge Harvest
 -> evidence-backed candidate
 -> Knowledge Hub proposal route
 -> reviewing
 -> owner review
 -> active / reject / archive
```

机器 handoff：`contracts/cross-repo/knowledge-harvest-handoff.yaml`。

如果 Knowledge Hub 当前不可用，允许使用本仓 50 条 internal-seed 作为 bootstrap catalog，但必须标记为 bootstrap candidate，不能等价于 E3 Knowledge Closed Loop。

## 7. Runtime Pilot

#18 Runtime Pilot 使用三层职责：

- digital-worker 冻结任务、Context、Acceptance、Action、Verification；
- ADK 固定 Profile/Skill asset bundle 与 target contract；
- llm_agent 读取 runtime health、Loop Readiness 与对照指标。

Runtime 输出不共享上一方最终 patch/答案；Runtime success 永远不等于 Verification PASS。

## 8. 当前证据状态

- Knowledge Hub integration contract 已存在，但其当前原生 CI 在既有 `tools/ci/rtk` transport/public-wrapper gate 红；且 digital-worker governed project route 尚未登记。状态：`BLOCKED_CI_TRANSPORT / route-pending`。
- ADK integration contract 已通过 contract/static/deterministic/full-regression 主体门禁；promotion-evidence job 曾发生 null-step/job-level failure，不能据此宣称 release-certified。
- llm_agent joint runtime contract 曾有 immutable contract PASS；最新 workflow 出现 null-step/job-level failure并已请求 rerun，当前仍不作为 clean release evidence。

以上状态必须以 `config/integrations/cross-repo-lock.json` 和最新 CI 为准，不允许文档把红灯改写成 PASS。

## 9. 当前不建设

- digital-worker 自建 RAG / Vector DB / Knowledge Graph；
- digital-worker 自建 Codex/Claude/OpenCode exporter；
- Knowledge Hub 保存 Binary/HIL 强事实副本；
- llm_agent 变成生产 Agent Runtime；
- 未经真实 Pilot 直接删除 P0 Skill；
- 单一统一“AI 成熟度数字”。

## 10. 下一退出条件

四仓 integration 从 candidate 升级为 pilot-ready 至少需要：

1. digital-worker 自身跨仓 validator fresh green；
2. Knowledge Hub governed project route 正式登记并原生 gate green；
3. ADK candidate provider 的 required profile/assets 有 exact bundle evidence；
4. llm_agent 至少两个 Runtime 的健康证据可用；
5. #6/#7/#8 至少一个 real run 消费 Knowledge Context + ADK asset identity + Runtime identity；
6. Knowledge Harvest 至少一次进入 Hub Proposal，并经历 owner review；
7. Verification/Review 仍由 digital-worker 独立裁决。
