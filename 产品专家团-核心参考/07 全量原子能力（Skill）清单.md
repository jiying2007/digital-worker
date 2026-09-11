# 07 全量原子能力（Skill）清单

# 全量原子能力（Skill）清单

> 依据 `.codebuddy-plugin/plugin.json`（插件版本 **5\.3\.0**）skills 登记、各 `skills/*/SKILL.md` frontmatter（`io:` 段为字段级唯一真相）与正文「Role / Workflow / Output / Constraints」逐项全量同步，覆盖**所有 Skill 的工作流程与作用**，2026\-09\-03 复核。
共 **54 个 Skill**，分布于：主理人管控与交付收口 6 \+ 市场调研 23 \+ 需求分析 6 \+ 产品定义 9 \+ 产品设计 10。
版本字段取自各 `SKILL.md` frontmatter `version`（个别 Skill 正文头部还保留旧版号或产品内部版号，属插件历史痕迹，不影响调用；frontmatter 为权威）。

## 0\. 一图看懂：Skill 归属与串链

|归属|Skill 数|串链 / 角色|
|---|---|---|
|主理人管控|5|影响分析 / 一致性检查 / 质量门禁 / 执行日志 / 项目记忆|
|交付层收口|1|deliverable\-packager（任务级收尾归置，生成《交付清单\.md》\+ deliverable\-manifest\.json）|
|市场调研|23|使能 2（data\-evidence / quality\-gate）\+ 阶段编排 5（stage\-1\~5）\+ 能力级 16（s1×4 / s2×4 / s3×3 / s4×3 / s5×2）|
|需求分析|6|阶段0\~5（req\-problem\-define → req\-scene\-build → req\-pain\-identify → req\-analyze → req\-specify → req\-srs\-builder）|
|产品定义|9|func\-spec / perf\-spec / tech\-intent / architecture / id\-input / roadmap / cost\-breakdown / quality\-baseline → def\-prd（PRD 总装）|
|产品设计|10|数字链：design\-ia\-ixd → design\-hifi\-ui \+ design\-system；实体链：design\-id\-concept → design\-cmf / design\-physical\-ux / design\-bom → design\-3new / design\-packaging\-req；design\-selling\-point 营销侧|
|**合计**|**54**|各 Skill 调用与归属详见 doc02\~doc06|

> io 记号：`schema:xxx` = 阶段产物 JSON 契约；`file:xxx` = 运行期单文件；`xxx ← skill 目录` = Skill 间字段消费；`passthrough` = 使能/收口/记忆层无字段级 io，由编排器或主理人直接调用。

---

## 1\. 主理人管控与交付收口（6）

### 1\.1 `prd-impact-analyzer`（v1\.0\.0）· PRD 变更影响分析

- **作用**：主理人专属跨领域协调工具。PRD 变更（新增/删除/修改/调优先级）时分析对下游（设计/研发/营销/品质等）的影响范围、工作量与风险等级，辅助判断返工或同步。

- **输入 → 输出**：`prd_delta`（← def\-prd）→ `prd_impact`；交付《PRD影响分析\_产品代号\_vX\_日期\.md》（变更摘要 / 影响矩阵 / 返工建议 / 需同步专家 / 风险提示）。

- **工作流程**：解析变更点并标类型 → 按变更类型逐条映射市场/需求/设计/研发/营销/品质下游影响 → 评估影响等级（高返工/中调整/低同步）→ 用 T\-shirt Size（S/M/L/XL）估返工量 → 输出含需同步专家清单的分析报告。

- **纪律**：不修改 PRD、不替代专家专业判断、不直接跨专家派活；返工/仲裁由主理人据报告决策。

### 1\.2 `deliverable-consistency-checker`（v3\.6\.1）· 交付物一致性检查（整合验证）

- **作用**：服务整合验证阶段，检查市场—需求—PRD—模块—设计—验收—技术—资料假设链的一致性、追溯链与交付就绪度；不评价单文档质量。

- **输入 → 输出**：`integration_artifacts`（task\-charter / gate\-ledger / material\-manifest / product\-context / reqspec / prd\-package\-index / module\-prd / design\-spec / technical\-review 等）→ `consistency_report`；交付《交付物一致性检查》MD \+ `integration-verification.json`。

- **工作流程**：收集 artifact 建 inventory → 读 task\-charter 裁剪范围 → 读 gate\-ledger 识别前序放行/降级 → 构建 market→reqspec→PRD 追溯基线 → 模块化 PRD 建 requirement→module→acceptance→design 追溯 → 执行 10 维一致性检查 → 每个问题标 issue\_type/severity/owner/恢复点 → 计算验收覆盖/资料假设/交付就绪度 → 输出 MD 与 JSON。

- **纪律**：只检查不改稿、不替专家补写、不仲裁冲突；存在 BLOCKER 时 cross\_stage\_consistent=false 且 Integration 判 BLOCKED；不绕过人工门禁。

### 1\.3 `deliverable-quality-gate`（v3\.9\.0）· 交付物质量门禁

- **作用**：阶段放行官。以 workflow / task\-modes / material\-requirements / execution\-budgets / prd\-output\-modes / schema / run\-state 为权威来源，对产物执行 Gate 判定、严重度分级、条件放行、恢复点定位与 gate\-ledger 记录。

- **输入 → 输出**：`deliverable_manifest` → `quality_gate_result`；交付《交付物质量门禁》MD \+ gate\-ledger JSON 片段。

- **工作流程**：识别 task\_type/workflow\_mode/stage\_id/gate\_id → 读权威配置与 schema → 判定该 Gate 必跑/可跳过/条件必跑 → 检查 artifact 存在性与 schema（PRD 包实跑 `validate_artifact.py`）→ 对 Markdown 跑 `lint_table_cols.py` 机检表格列数 → 按 P0/P1/P2/P3 分级 → 产出 7 态判定 → 输出返工范围/责任阶段/恢复点 → 写 gate\-ledger。

- **纪律**：只判定不改写产物、不替代人工 Gate；P0 必阻塞且带恢复点；禁止以「JSON 格式 PASS」绕过 schema 校验；恢复从 failed\_stage/step 继续不整段重跑。

### 1\.4 `execution-logger`（v3\.6\.1）· 执行日志与复盘

- **作用**：生产级运行审计/复盘记录器。记录 task\-charter、run\-state、gate\-ledger、预算、事件时间线、专家调用链、跳过原因、资料缺口、降级决策、PRD 输出模式、质量问题、开放风险与最终产物。

- **输入 → 输出**：`run_state`（必）、`gate_ledger`（必）→ `execution_log`；交付 `execution-log.json` \+ `执行日志_代号_runID_日期.md` \+ `复盘纪要_代号_日期.md`。

- **工作流程**：初始化 run\_id/brief/任务模式 → 记录 charter/run\-state/gate 引用与预算 → 构建 run\_started→run\_completed 事件时间线 → 记录专家调用链与跳过原因 → 记录 Gate 快照 → 记录资料/假设/降级 → 记录 PRD 输出模式与模块 → 汇总最终产物 → 生成 retrospective\_findings 与 next\_recommended\_actions → 输出 JSON 与 MD。

- **纪律**：只记事实不主观评价；每个跳过专家必须带 skip\_reason；每个阻塞必须带恢复点（resume\_instructions），不整段重跑。

### 1\.5 `team-memory-manager`（v1\.0\.0）· 团队项目级 Memory

- **作用**：主理人专属协调工具。初始化并维护项目记忆库 `memory/[项目代号]/PROJECT_MEMORY.md`，记录关键决策、PRD 版本、用户画像、竞品/领域档案引用、专家产出路径，支持多轮会话上下文共享复用。

- **输入 → 输出**：passthrough（操作类型 init/read/update/archive \+ 待写内容）→ project\-memory 文件 \+ `archived/` 归档。

- **工作流程**：init 建目录写初始模板 → read 按需加载并输出摘要 → update 追加决策/版本/画像/竞品/领域/产出路径并写变更日志 → archive 归档失效信息并保留引用。

- **纪律**：不替代专家产出；只存路径与摘要不存大文件；不自动同步实时数据，须显式触发更新。

### 1\.6 `deliverable-packager`（v4\.1\.0）· 交付层收口器

- **作用**：任务收尾时扫描 `<project_id>/`，按产物分类表归入 00\_交付物 / 01\_过程资产 / 02\_门禁与运行日志 / 03\_数据资产，生成《交付清单\.md》与 deliverable\-manifest\.json。

- **输入 → 输出**：passthrough（输入为项目产出目录 \+ config/output\-config\.yaml 分类契约）→ 四分类目录 \+《交付清单\.md》\+ `deliverable-manifest.json`。

- **工作流程**：读 output\-config 契约 → 定位项目目录 → 强制收口闸门跑 `close_out.py` 对每个 PRD 自测（90 分、8 维≥80、流程图门禁 PASS）→ 按 move 模式幂等归置 → 生成机器清单 \+ 人工清单 → 跑 `validate_artifact.py` 校验核心交付物家族。

- **纪律**：只呈现必读交付物；禁止移动产出目录外文件、禁止删源文件；未生成 manifest = 门禁不通过，不得宣称完成。

---

## 2\. 市场调研（23，版本统一 1\.2\.0）

### 2\.1 使能层（横切调用，无字段级 io）

#### `mkt-data-evidence`（v1\.2\.0）· 数据获取与证据校验

- **作用**：为 S1\~S5 提供可信数据与证据底座：实时取数 \+ P6 时效门禁、行业注入契约、统一数据流水线（U0 三级自动补齐）、置信度交叉验证、一手调研触发。

- **工作流程**：实时取数并跑 P6 时效门禁（实际值\>预测\>推估）→ `industry_data.py` 按行业 slug 动态装载防跨行业污染 → `data_pipeline.py` 清洗入库 \+ U0 补齐（检索→衍生→推估，不编造）→ `confidence_rank.py` 交叉验证关键指标（≥2 独立来源）并评级 → 按硬规则判定是否触发一手问卷/访谈（`survey_analyze.py`）→ 校验来源/口径/置信度/证据链并标注。

- **纪律**：禁止「待补/无数据/后续补充」占位；禁止杜撰、禁止把推估凑整；同年度官方实际值已发布后禁沿用旧预测值（硬红线）。

#### `mkt-quality-gate`（v1\.2\.0）· 市场调研质量门禁（G1\~G17）

- **作用**：承载各阶段末机检 \+ 阶段组装（Stage Builder）\+ 评审验证，产出标准化交付包（Industry/Stage2/Customer/Strategy 等 Master Package、Stage Manifest、Quality Report、Validation Result）。

- **工作流程**：聚合各能力级包并去重、统一口径/术语/评分 → 提炼 Strategic Insights 与 Key Insights → 机检（S1 跑 P1\~P8\+lint、S2/S4 八维 Gate、S5 跑 G1\~G17 含决策可信度 G17）→ Dependency Check \+ Stage Boundary Check → 量化/深度分层审核 → 战略收敛机检（§14 企业适配 A/B/C）→ 出具 PASS / PASS WITH WARNING / FAIL（或 GO/CONDITIONAL/REWORK/NO\-GO）与整改清单；同步维护 `*-run-state.json`。

- **纪律**：禁「待补」残留；关键数据须「结论→证据→来源」可回溯且可复算；红线项（P6 时效、缺包 ID、越界）不清零不得置 Approved。

### 2\.2 阶段编排器 S1\~S5

#### `mkt-stage-1`（v1\.2\.0）· S1 行业分析总编排

- **作用**：按序调度 S1 四个能力级技能（foundation → scale\-structure → policy\-subsegment → attractiveness），把行业分析完整跑一遍；编排器不做实质性分析。

- **输入 → 输出**：`task_charter`\(file\) \+ `enterprise_baseline`\(file\) → `s1_industry_package`；交付 `S1-P10-A Industry Analysis Package` \+ `S1-P10-B Stage2 Input Package` \+ Stage Manifest \+ Quality Report \+ Validation Result，作为 S2 唯一输入。

- **工作流程**：接收并澄清分析对象 → 顺序调度四个能力级技能 → foundation 锁定「统一口径声明 \+ 关键词词典」全程沿用 → 每步产物引用前序结论并记假设 → 调 `mkt-quality-gate` 机检 G1\~G17 并组装双包 → 交付 Final Package 摘要并提示 S2 引用。

- **纪律**：只调度不改结论；企业能力仅 ≤20% 轻微修正；不输出最终战略（属 S5）。

#### `mkt-stage-2`（v1\.2\.0）· S2 市场竞争分析总编排

- **作用**：承接 S1 成果与双角色视角，按序调度 S2 四个能力级技能（landscape\-structure → competitor\-portfolio → strategy\-positioning → evaluation）。

- **输入 → 输出**：`s1_industry_package`（← mkt\-stage\-1）→ `s2_competition_package`；交付 `S2-P10-A Stage2 Competitive Analysis Package` \+ `S2-P10-B Market Entry Capability Requirements Package`（7 维市场侧门槛，供 S5）\+ Stage Manifest \+ Quality Gate。

- **工作流程**：接收 S1 双包 → 顺序调度并保持「运营/服务商 vs 产品/设备制造商」双角色不合并 → 每步作下一步输入、记假设 → 调 quality\-gate 聚合双包 \+ G1\~G17 机检 → 提示 S3 引用 Approved 包、S5 引用能力要求包。

- **纪律**：只分析市场侧能力门槛，不做企业自评/Competitive Fit/最终进入建议（属 S5）；支持独立调用并显式标注降级。

#### `mkt-stage-3`（v1\.2\.0）· S3 用户/客户分析阶段编排

- **作用**：路由 3 个 mkt\-s3\-\* 能力级技能（segment\-persona → jtbd\-journey\-needs\-pain → value\-decision），自身不分析。

- **输入 → 输出**：`s2_competition_package`（← mkt\-stage\-2）→ `s3_customer_package`；产出唯一 `Customer Analysis Master Package（Approved）`。

- **工作流程**：按触发意图路由 → 严格顺序派发（下游只读上游 Approved 包）→ 失败回退不向后传播 → 封装前跨 Package 一致性预检（Tier1 客户↔高 Severity 痛点↔关键成交因素）→ 终审 PASS/PASS WITH WARNING/FAIL，仅通过才交付 S4。

- **纪律**：路由层禁止代做分析/改 Approved 包；越出 Stage3 边界（客户收敛）不得做。

#### `mkt-stage-4`（v1\.2\.0）· S4 产品机会与策略阶段编排

- **作用**：路由 3 个 mkt\-s4\-\* 能力级技能（opportunity\-portfolio\-positioning → value\-biz\-roadmap → synthesis）。

- **输入 → 输出**：`s3_customer_package`（← mkt\-stage\-3）→ `s4_strategy_package`；产出唯一 `Stage4 Product Strategy Master Package（Approved）`（S4\-P09）。

- **工作流程**：按触发意图路由 → 顺序派发、失败回退 → 封装前一致性预检（机会收敛↔组合梯队↔优先级四梯队↔放弃建议）→ 终审 GO/CONDITIONAL GO/REWORK/NO\-GO，仅 GO/CONDITIONAL GO 才交付 S5。

- **纪律**：只输出产品战略，不输出 PRD/详细规格/研发方案，不分析企业能力（属 S5）；独立调用时企业匹配度 A\~D 标「未评估」不硬编。

#### `mkt-stage-5`（v1\.2\.0）· S5 最终战略阶段编排

- **作用**：轻量编排器，按序调度 2 个能力级技能并调用质量门禁，完成 S4→S5→需求分析专家的资料流衔接。

- **输入 → 输出**：`s4_strategy_package`（← mkt\-stage\-4）\+ 上游 Master \+ 企业分析基线 → `market_research_deliverables`；产出 S5\-P01\~P03 \+ quality\-gate 终审 S5\-P04（G1\~G17）。

- **工作流程**：按 strategic\-recommendation → report\-builder 顺序派发（builder 只读 S5\-P01/P02）→ 失败回退 → 核对决策可信度门禁（G17；Low 占主导时降级为「待验证方向 \+ 补证清单」）→ GO → Market Research Completed → 输出 Approved Deliverables 给需求分析专家。

- **纪律**：编排器不做分析/聚合/评分/报告正文；不修改 Approved 包。

### 2\.3 S1 能力级（4）

#### `mkt-s1-foundation`（v1\.2\.0）· 行业定义与宏观环境

- **作用**：把研究对象讲清楚——行业定义与边界 \+ PESTEL 宏观环境（含用户需求行为基线），为全 S1 提供统一口径。

- **输入 → 输出**：研究对象/国家/决策问题（编排器派发）→ `industry_definition`；产物包 `S1-P01 Industry Definition Package` \+ `S1-P02 Macro Environment Package`。

- **工作流程**：确认研究对象与不重复定义 → 取权威分类、给权威\+工作定义 → 建分类层级树 → 划含/不含边界并标模糊项 → 识别关联/替代行业 → 建中英文关键词词典 → 输出统一口径声明（国家/时间/范围/货币）→ PESTEL 六维扫描并硬性输出 2\~4 类典型场景用户需求行为基线 → 汇总宏观机会/风险清单。

- **纪律**：口径一经确定全 S1 沿用；输出前逐条机检 §13\.5 专业底线 P1\~P8。

#### `mkt-s1-scale-structure`（v1\.2\.0）· 市场规模与产业链结构

- **作用**：覆盖规模与增长、生命周期、生态价值链、技术全景四块测算，为赛道打分提供金额锚定。

- **输入 → 输出**：行业口径与定义（← mkt\-s1\-foundation）→ `market_size_tam_sam_som`；产物包 `S1-P03 Market Size & Growth` \+ `S1-P04 Lifecycle` \+ `S1-P05 Ecosystem & Value Chain` \+ `S1-P06 Technology Landscape`。

- **工作流程**：算总量/TAM，SAM 强制三轨（Hardware 设备硬件 / Operations 运营服务 / Retail 消费零售）由 `calc_sam.py` 确定性计算 → SOM 按企业角色锚份额情景 → 测算增速/CAGR/渗透率/拐点 → 判生命周期阶段并给进入时机 → 产业链 BOM 拆解 \+ 议价权利润分布 \+ 毛利 Ceiling \+ 生态利润地图 → 技术全景扫描（主流/替代技术 \+ TRL \+ 壁垒 \+ 供应格局）。

- **纪律**：SAM\_Retail 缺失即判不合格；硬数字须绑 S1\-P01 权威源并经 P6 门禁；严禁捏造。

#### `mkt-s1-policy-subsegment`（v1\.2\.0）· 政策环境与细分赛道

- **作用**：扫描政策法规/市场准入提供合规背景，并用三维矩阵拆解细分赛道机会池并量化打分。

- **输入 → 输出**：行业口径（← mkt\-s1\-foundation）→ `policy_subsegment`；产物包 `S1-P07 Policy & Regulation` \+ `S1-P08 Opportunity Pool`。

- **工作流程**：按国家范围扫描产业/法规/准入/资质认证（附文号来源）→ 评准入难度 → 用【应用场景×技术路线×购买模式】三维矩阵化解耦赛道（购买模式分 B2B / C 端零售）→ 统一量化打分标尺（空间锚定 SAM 分轨）→ 算 Opportunity Score（90 分制）成机会池。

- **纪律**：C 端零售购买模式须至少 1 条赛道否则判缺漏；标尺硬映射不主观定性；不淘汰赛道、不做企业能力判断。

#### `mkt-s1-attractiveness`（v1\.2\.0）· 行业吸引力评分

- **作用**：输出行业客观吸引力排名并完成 Stage1 战略收敛（≥70 优先深入 / 中位观察 / 低位保留摘要），S1 最后一个分析 Skill。

- **输入 → 输出**：市场规模 \+ 政策细分（← 前两级）→ `s1_attractiveness_score`；产物包 `S1-P09 Industry Attractiveness Package`。

- **工作流程**：沿用六维 90 分模型 → 个别维度绝对标量 ±10 修正（废除百分比乘法）→ 每条赛道强制 5 字段（名称/得分/修正/依据/排序）→ 输出行业整体与高低吸引力方向 → Stage1 战略收敛给推荐深入赛道。

- **纪律**：不做企业能力匹配、不输出 Go/Pilot/Watch/Exit；修正须定量依据、累积 ≤20%；最终分 0–100 截断。

### 2\.4 S2 能力级（4）

#### `mkt-s2-landscape-structure`（v1\.2\.0）· 竞争格局与生态结构

- **作用**：识别竞争生态、建立竞争对象地图，并分析市场集中度/竞争结构。

- **输入 → 输出**：S1 Industry/Stage2 Input（编排器派发）→ `competition_landscape`；产物包 `Competitive Landscape Package`（S2\-P01）\+ `Competitive Structure Package`。

- **工作流程**：读取上游沿用 S1 口径 → 识别直接/间接/潜在/替代/上下游/平台/生态伙伴竞争者并建关系图 → 按 R3 梯队标签 \+ 与我关系分类 → 输出产品方案形态对比、替代威胁矩阵 → 对重要发现做八维战略分析输出 3\~8 条 Strategic Insights → 计算 CR3/CR5/CR10/HHI 判集中度与竞争强度。

- **纪律**：CRn 须「算」非「抄」并标口径与期次；生态覆盖第三方平台/渠道/聚合玩家；不做最终决策。

#### `mkt-s2-competitor-portfolio`（v1\.2\.0）· 头部竞品对标与功能矩阵

- **作用**：建立统一竞品库（Competitor Database）与产品组合库，含竞品功能对标矩阵与生态全景。

- **输入 → 输出**：竞争格局（← mkt\-s2\-landscape\-structure）→ `competitor_portfolio`、`competitor_benchmark`；产物 Competitor Product Portfolio Package（竞品画像/功能对标矩阵/Benchmark）。

- **工作流程**：筛选代表企业覆盖 ≥80% 影响力建统一 Competitor List → 逐家画像（营收/定位/优势）并标反击潜力 → 建统一 Competitor\_ID 库 → 逐家建 Product Portfolio（系列/型号/矩阵/升级路径）→ 扩展全行业产品生态全景（品类全集/价位梯度/生态位空窗图谱）。

- **纪律**：企业营收/份额须实时取数标来源经 P6 门禁；严禁捏造产品/价格/型号；空窗判断须有公开证据。

#### `mkt-s2-strategy-positioning`（v1\.2\.0）· 差异化空白与战略定位

- **作用**：分析渠道与商业模式、竞争策略、KSF/壁垒/护城河，识别竞争定位空白与机会池。

- **输入 → 输出**：竞品库（← mkt\-s2\-competitor\-portfolio）→ `strategy_positioning`；产物 Go\-to\-Market / Competitive Strategy / KSF \& Industry Barrier / Competitive Positioning Opportunity 各 Package。

- **工作流程**：分析渠道结构与商业模式、渠道—客群映射供 S3 → 分析各竞品竞争策略及效果 → 提炼 KSF（带权重）\+ 壁垒定级 \+ 控制点 \+ 护城河逻辑链 → 构二维竞争定位图识别空白（按 Opportunity\_ID）→ 评估机会可行性/吸引力/风险并排序、映射双角色 → 重要发现八维分析出 Strategic Insights。

- **纪律**：不输出 Market Entry Capability Requirements（归 S2 末）、不做企业能力自评；机会须基于「空白证据 \+ KSF 缺口」。

#### `mkt-s2-evaluation`（v1\.2\.0）· 进入难度、壁垒与替代威胁评估

- **作用**：综合全 S2 上游做竞争态势评估并完成 Stage2 战略收敛，S2 最后一个分析 Skill。

- **输入 → 输出**：定位空白（← mkt\-s2\-strategy\-positioning）\+ S2 全部包 → `s2_evaluation`；产物 `Competitive Assessment Package`（S2\-P02）。

- **工作流程**：综合评估强度/集中度/稳定性/变化速度/风险 → 对可反击在位者做响应推演（反应/时机/触发/预案）出对手响应矩阵 → 评估机会成熟度与时间窗、双角色差异 → Stage2 战略收敛做企业适配过滤（A 高度适配/B 需新增能力/C 超出边界）并给推荐竞争定位。

- **纪律**：集中度数值须与 S2 结构包严格一致；Confidence 禁清一色 Medium；A/B/C 过滤不修改市场客观事实。

### 2\.5 S3 能力级（3）

#### `mkt-s3-segment-persona`（v1\.2\.0）· 客户细分与画像

- **作用**：市场客户细分（Segmentation）并建立目标客户画像（Persona）与目标用户。

- **输入 → 输出**：S2 Master（编排器派发）→ `segment_persona`、`target_users`；产物 Customer Segmentation Package、Customer Persona Package、三角映射表（Segment/Attractiveness/Tier1\-3/DMU/CLV）。

- **工作流程**：识别/分类/聚类客户建 Segment Profile（规模/增长/利润/可达性/复杂度 5\+ 项）→ 计算吸引力与优先级 → 强制做购买者—使用者—渠道三角定位映射 → 输出 3\~8 条战略洞察 → `s3_01/s3_02` 脚本落盘 → Persona：画像/DMU/业务目标/行为/价值导向/战略价值。

- **纪律**：只做细分与画像，禁止越界做需求/JTBD/痛点/产品分析；Persona 不得重划 Segment；量化可追溯。

#### `mkt-s3-jtbd-journey-needs-pain`（v1\.2\.0）· JTBD、客户旅程、需求与痛点

- **作用**：承接细分画像，覆盖 JTBD、客户旅程与场景、需求、痛点/未满足需求四环节（ODI/需求方法，非功能思维）。

- **输入 → 输出**：Segment/Persona（← mkt\-s3\-segment\-persona）→ `jtbd_needs_pain`、`user_scenarios_pains`；产物 JTBD / Customer Journey \& Scenario / Customer Needs / Pain Point \& Unmet Needs 各 Package。

- **工作流程**：识别 Core/对象级/Functional/Emotional/Social Jobs 并算 ODI Opportunity Score 与优先级 → 映射完整旅程与场景、决策点与摩擦 → 建需求体系树、分类与优先级 → 用 5Why/鱼骨识别痛点根因、严重度、未满足需求与市场机会 → 各环节输出洞察与 Review 自检。

- **纪律**：子环节职责递进、上游禁越界做痛点/KANO/方案；痛点/需求/任务须 Top8 并标证据；B2B 与 B2C 双覆盖。

#### `mkt-s3-value-decision`（v1\.2\.0）· 需求价值 KANO 与购买决策

- **作用**：Stage3 需求侧收尾，覆盖需求价值/KANO、购买决策与客户战略综合三环节。

- **输入 → 输出**：JTBD/需求痛点（← 上一级）→ `value_decision`；产物 Customer Value \& KANO Package、Buying Decision Package、Customer Intelligence Package。

- **工作流程**：评估需求价值 \+ KANO 分类（基本/期望/魅力/逆向/无差异）\+ 投资优先级 \+ 差异化 → 分析购买决策流程、DMU、购买者/使用者权重差异输出决策链映射 → 整合 S1\~S3 客户成果做战略综合（企业适配过滤 \+ 推荐目标客户 \+ 知识缺口清单）。

- **纪律**：KANO 不做机械分类；购买决策须含 Barrier、DMU；综合环节禁止重分析只做收敛。

### 2\.6 S4 能力级（3）

#### `mkt-s4-opportunity-portfolio-positioning`（v1\.2\.0）· 机会收敛为产品概念与定位

- **作用**：Stage4 前段，覆盖产品机会识别、产品组合规划、产品定位三环节，把市场机会收敛为可进入的产品概念与定位。

- **输入 → 输出**：S3 Master（编排器派发）→ `opportunity_portfolio`；产物 `S4-P01 Product Opportunity Analysis`（机会池/TOP10/企业匹配度 A\~D）\+ `S4-P02 Product Portfolio Planning` \+ `S4-P03 Positioning Analysis`。

- **工作流程**：汇总跨 S1/S2/S3 机会点四维归类建机会池（含潮流机会 R6 挖掘）→ 100 分制可复算评分落位吸引力×可行性矩阵 → 输出 TOP10 与企业匹配度 → 结构化为品类→产品线→产品→SKU 产品树并按引流/利润/战略归类 → 输出定位声明、差异化与定位空白。

- **纪律**：不做具体功能/商业模式/企业现状评价；B2B 与 B2C·直接购买双覆盖；机会 TOP 须标来源。

#### `mkt-s4-value-biz-roadmap`（v1\.2\.0）· 价值主张、商业模式与路线图

- **作用**：Stage4 中后段，覆盖价值主张、产品策略、商业模式、产品路线四环节，将定位落成价值承诺与中长期路线。

- **输入 → 输出**：机会组合定位（← 上一级）→ `value_biz_roadmap`；产物 `S4-P04 Value Proposition` / `S4-P05 Product Strategy` / `S4-P06 Business Model & Profitability` / `S4-P07 Development Roadmap`。

- **工作流程**：整合 JTBD/痛点/收益建价值地图并给各产品价值主张与验证方式 → 制定可执行策略并强制多情景 ROI（悲观/中性/乐观 ±20%）\+ 单位经济（CAC/CLV）\+ 成本结构拆解 → 识别商业模式并承接 ROI 做止损/退出触发与横向对标 → 规划短中长期路线与里程碑。

- **纪律**：无数据禁用「待补/无数据」占位，须【推算】\+置信度；对标数据真实可溯；止损触发可量化无歧义；不定义具体功能/精确财务预算。

#### `mkt-s4-synthesis`（v1\.2\.0）· 产品策略综合（含业务边界）

- **作用**：Stage4 收敛器，综合 S4\-01\~07 全部结论为唯一产品战略综合结论与业务边界。

- **输入 → 输出**：价值/商业模式/路线图（← 上一级）\+ S4 全部包 → `s4_synthesis`、`business_boundary`；产物 `S4-P08 Product Strategy Synthesis Package`。

- **工作流程**：核对 S4 全包一致性 → 收敛唯一产品战略主线并按四梯队（一/二/三/观察）排序 → 推导 3\~7 条战略原则与「必须/不能做/边界」约束 → 四类归入产品边界、输出多层产品树与五问推导 → 给升级版放弃建议 \+ 统一风险视图 → 产出 ≥15 条五段式洞察并明确 Stage5 验证项。

- **纪律**：仅做产品战略收敛，禁止分析企业现状/能力（属 Stage5）；战略结论统一五段式结构。

### 2\.7 S5 能力级（2）

#### `mkt-s5-strategic-recommendation`（v1\.2\.0）· 唯一推荐战略

- **作用**：Stage5 唯一允许输出最终战略建议的 Skill，收敛 S1\~S4 与企业基线为唯一推荐战略（Go/Pilot/Watch/Exit）并解释决策理由。

- **输入 → 输出**：S4 综合（← mkt\-s4\-synthesis）\+ 各 Stage Master \+ 企业分析基线 → `strategic_recommendation`；产物 `S5-P01 最终战略方案` \+ `S5-P02 Strategic Decision Rationale Package`。

- **工作流程**：综合 S1→S2→S3→S4 收敛唯一推荐方向（机会契合×能力契合）→ 按推荐指数（0\.40 市场机会 \+ 0\.25 客户需求 \+ 0\.20 产品战略 \+ 0\.15 企业适配）判五星等级 → 定义量化进门槛/止损触发线 → 补决策稳健性与失效触发点说明。

- **纪律**：只引用已批准包、禁止重分析；只允许唯一推荐；对外用中文档位（立即进入/试点/观察/不进入），Go/Pilot/Watch/Exit 仅作内部附注；部分输入降级最多 ★★★。

#### `mkt-s5-report-builder`（v1\.2\.0）· 市场研究报告组装

- **作用**：报告编撰者，不改结论不加观点，把 S1\~S5 全部成果重构为《市场调研报告》并同步形成战略摘要。

- **输入 → 输出**：战略推荐（← mkt\-s5\-strategic\-recommendation）\+ 各 Stage Master → `market_research_strategic_summary`、`market_research_report`；产物《市场调研报告》（S5\-P03）、《市场调研战略摘要》\+ 机器可读 `S5-P03-MR.json`。

- **工作流程**：核对各包完整性并判报告模式（完整/阶段专项/机会主导，写 report\_mode）→ 按「行业→竞争→客户→产品→战略→最终推荐」重构每章（完整组织非摘要）→ 补执行摘要四段锚点与证据链 → 对外语言转换（Package→分析子包、Go→立即进入等）→ 生成机器 JSON → 发布自检。

- **纪律**：禁止新增/改变/删除结论、禁止摘要压缩；对外净网（禁 TL;DR/Package/Gate 等内部词）；按 R5 八模块硬模板组织。

---

## 3\. 需求分析（6，版本统一 5\.0\.0）

#### `req-problem-define`（v5\.0\.0）· 阶段0 业务问题定义

- **作用**：把上游市场调研六要素与主理人任务章程转化为「业务问题陈述 \+ 目标成功指标 \+ 范围内/外清单 \+ 关键假设与风险」，作为后续「为什么做」锚点。

- **输入 → 输出**：`track_position / opportunity_gap / user_profile / boundary_constraint`（schema:market\-research）\+ `task_type`（schema:task\-charter）→ `problem_statement / success_metrics / scope_in_out / assumptions_risks`；落盘 `00-业务问题定义.md`。

- **工作流程**：一句话写清业务问题 → 列业务目标\+量化成功指标表 → 列本期做/不做范围内外 → 列关键假设（标置信度）\+ 主要风险。

- **纪律**：成功指标须可量化可验证；表格≤3列、属性名中文化（全局规范）。

#### `req-scene-build`（v5\.0\.0）· 阶段1 场景梳理与需求获取

- **作用**：把市场六要素、Gate K/M、Mode A/B/C 与 product\-context 客观转译为标准场景画布；只做场景转译，不做方案定义。

- **输入 → 输出**：`problem_statement`（← req\-problem\-define）\+ `target_users`（← mkt\-s3\-segment\-persona）\+ `user_scenarios_pains`（← mkt\-s3\-jtbd\-journey\-needs\-pain）→ `scene_canvas / stakeholder_list / raw_need_library / env_constraint`；主交付 `01-场景分析.md`，副产物 scene\_qa / actors\_conflict / race\_match。

- **工作流程**：锚定边界（in\_scope 判定）→ 识别业务主体与对象级 JTBD（人类/非人类/外部）→ 补齐六要素 actor/scene/goal/action/constraint/context → core 场景异常分支扇出 → 证据绑定与反编造自检 → 依任务类型分层下限建场景画布。

- **纪律**：禁止输出系统方案/优先级/取舍；无来源字段标待澄清不补编；既有产品任务须读 Gate M。

#### `req-pain-identify`（v5\.0\.0）· 阶段2 痛点识别与需求整理

- **作用**：用痛点六维度量化痛点并做需求整理；只有「刚性痛点」才是痛点，柔性爽点/伪诉求/潜在需求不算。

- **输入 → 输出**：`scene_canvas / raw_need_library`（← req\-scene\-build）→ `need_pool / pain_point / pain_evidence`；落盘 `02-需求池与痛点.md`。

- **工作流程**：按六维度（频次/影响/严重度/覆盖/可替代性/证据）量化痛点强度 → 对原始需求整理（去重/归并/保留异常/标歧义/伪需求）→ 按证据分轨 A1/A2/B/C → 对高频刚性痛点做 5Why 根因分析。

- **纪律**：禁止把柔性爽点当痛点；禁止虚构画像/访谈/样本；禁止删伪诉求；禁止做最终优先级裁决。

#### `req-analyze`（v5\.0\.0）· 阶段3 需求分析与分类

- **作用**：一个 Skill 完成分类标注 \+ 价值量化 \+ 冲突识别 \+ 依赖分析 \+ 场景全覆盖检查；价值量化只算用户价值。

- **输入 → 输出**：`need_pool`（← req\-pain\-identify）→ `classification / value_score / conflict_list / dependency_graph / scene_coverage`；落盘 `03-需求分类与价值.md` / `03-冲突清单.md` / `03-场景覆盖矩阵.md`。

- **工作流程**：树状四层层级归类 → 打八类标签 \+ 软硬件归属 → KANO\+MoSCoW 定级 → 量化用户价值（层次×频次×痛点强度）\+ 战略契合 → 识别并消解五类冲突 → 依赖分析（前置/依赖/并行/循环）→ 输出场景覆盖矩阵。

- **纪律**：不做可行性/成本/ROI；冲突裁决归人工；依赖图无循环；场景覆盖须串联数据流/状态流/异常流/回流。

#### `req-specify`（v5\.0\.0）· 阶段4 需求规格化、建模与验证

- **作用**：把已分类消解的细需求拆为最小可描述单元并形成全局 RTM；输出客观需求条目\+规格，非产品方案/优先级。

- **输入 → 输出**：`classification / value_score / conflict_list / scene_coverage`（← req\-analyze）\+ `scene_canvas`（← req\-scene\-build）→ `detail_req / req_id / uml_models / interface_spec / data_dictionary / nfr_list`；落盘 `04-细需求池.md` / `04-建模图.md` / `04-接口与数据字典.md`。

- **工作流程**：用户故事\+GWT 拆细需求并按树状四层挂接 → 读场景覆盖矩阵串闭环 → UML 四类模型（用例/活动/时序/状态，Mermaid）→ 软硬件项目接口规格六维度 → 数据字典 → 全量 NFR 量化 → 建全局 RTM（覆盖 100%）。

- **纪律**：细需求禁平铺必须树状分层；acceptance 禁主观描述；D/假设不得进入 RTM 证据底座；不做优先级拍板。

#### `req-srs-builder`（v5\.0\.0）· 阶段5 基线发布与变更管理

- **作用**：将阶段 1\-4 散件按 12 章组装为《需求规格说明书》主入口，并产出基线确认页、RTM、三级 CCB 变更机制；只搬运/摘要/标注来源，不新增分析。

- **输入 → 输出**：`detail_req`（← req\-specify）\+ `conflict_list / value_score`（← req\-analyze）→ `reqspec / rtm / baseline / change_mechanism / metrics`；交付 `需求规格说明书-<产品代号>-v1.0.md` \+ SRS manifest。

- **工作流程**：首部写 SRS manifest → 按章节模板从各来源产物组装（引言/总体描述/硬件/软件功能/接口/NFR/数据/业务规则/附录）→ 每节标来源、缺口标待补、不一致显式化 → Mode B/C 纳入变更影响 → 交付前六维检查。

- **纪律**：不新增需求/删改语义、禁止跳章；不编造缺失数据；D 类隔离不进 RTM；变更执行与审批归人工 CCB。

---

## 4\. 产品定义（9）

#### `def-func-spec`（v1\.0\.0）· 功能规格

- **作用**：产出功能框架（系统级→模块级→子功能），逐功能描述边界条件与异常路径，含软硬件功能分配与原子能力依赖。答复「我需要做什么」。

- **输入 → 输出**：`reqspec`（← req\-srs\-builder）→ `func_spec`；正文功能规格文档（功能框架/子功能拆解/边界/异常路径）。

- **工作流程**：梳理系统级功能 → 拆模块级功能 → 划原子能力与业务功能 → 画功能依赖关系图 → 定义子功能边界 → 描述异常路径 → 输出功能规格（含软硬件功能分配矩阵）。

- **纪律**：只声明能力复用与依赖，原子状态机等设计细节归研发概要设计；重大功能边界须产品负责人确认。

#### `def-perf-spec`（v1\.1\.0）· 性能规格

- **作用**：为每项功能定义性能 Goal（差异化追求）\+ Threshold（质量底线），功能\+性能双维度描述并含测试方法。

- **输入 → 输出**：`func_spec`（← def\-func\-spec）→ `perf_spec`；正文逐功能「功能描述 \+ Goal \+ Threshold \+ 测试方法」。

- **工作流程**：逐功能确定性能维度 → 设 Goal → 设 Threshold → 定义测试方法 → 双维度描述 → 输出性能规格。

- **纪律**：Goal/Threshold 缺一不可；系统级 KPI 须可下拆到分专业 KPI；Threshold 归本 Skill 独有，不与 def\-quality\-baseline 重叠。

#### `def-tech-intent`（v1\.0\.0）· 关键技术意向

- **作用**：输出关键器件的能力规格清单，只定「能力规格/技术边界」，不锁实现、不做具体型号/供应商对比，具体选型交研发。

- **输入 → 输出**：`reqspec`（← req\-srs\-builder）\+ `product_outline` → `tech_intent`；交付 `技术意向_产品代号_YYYYMMDD.md`。

- **工作流程**：识别关键器件类别（3\-6 类）→ 逐项输出能力规格（候选方向枚举/边界/风险）→ 标注技术风险与研发待澄清问题 → 输出文件回传主理人。

- **纪律**：零型号铁律——禁写具体型号/品牌/供应商、禁型号对比打分、不替研发选型。

#### `def-architecture`（v1\.0\.0）· 产品架构规划

- **作用**：产出系统总体架构图、模块划分与接口定义。

- **输入 → 输出**：`product_outline` → `architecture`；正文产品架构文档（系统架构图/模块清单/接口定义/通信协议）。

- **工作流程**：绘制系统架构图 → 划分功能模块 → 定义模块间接口 → 确定通信协议 → 输出架构文档。

- **纪律**：复杂架构须提交研发评审；`module_dep_graph.py` 做依赖无环校验；每条结论带 source\_type\+confidence。

#### `def-id-input`（v1\.0\.0）· ID 设计输入定义

- **作用**：输出 ID 设计需求书（六大要素：产品定位风格/物理约束/环境适应性/人机交互/生产制造约束/成本约束）。只给「约束\+方向」，不做具体造型设计。

- **输入 → 输出**：`func_spec`（← def\-func\-spec）\+ `architecture`（← def\-architecture）→ `id_input`；交付 `ID设计输入_产品代号_YYYYMMDD.md`。

- **工作流程**：接收定型卡与产品概念 → 汇总架构/功能/环境/成本约束 → 按六大要素逐要素填约束\+方向 → 标注 ID 输入 vs 输出边界 → 交下游设计专家。

- **纪律**：不做造型（3D/渲染/装配）；禁空泛描述；禁脱离架构物理约束设尺寸；IP/跌落为硬约束不可跳过。

#### `def-roadmap`（v1\.0\.0）· 版本路线图

- **作用**：基于定型卡边界与功能优先级输出 V1\.0 MVP → V1\.1 快速迭代 → V2\.0 战略升级三阶规划及各版本准入/准出条件；核心是控 V1\.0 范围防膨胀。

- **输入 → 输出**：`func_spec`（← def\-func\-spec）→ `roadmap`；交付 `版本路线图_产品代号_YYYYMMDD.md`（可并入 PRD「产品路线图」章节）。

- **工作流程**：接收定型卡与功能优先级 P0/P1/P2 → 复核 V1\.0 范围目标 → 三阶法分配 V1\.0/V1\.1/V2\.0 → 填纳入/推迟标准表 → 明确各版本准入/准出 → 输出并入 PRD。

- **纪律**：禁止把 Could（兴奋型）功能塞进 V1\.0；推迟必须有理由；时间窗须结合产能与难度。

#### `def-cost-breakdown`（v1\.0\.0）· 成本分解

- **作用**：功能级成本目标分配、关键器件成本限制与整体 BOM 成本预估，并从市场零售价向下倒推 BOM 上限。

- **输入 → 输出**：`func_spec`（← def\-func\-spec）\+ `target_price`（可选）→ `cost_breakdown`；正文成本分解文档（功能级分配/器件限制/BOM 汇总）。

- **工作流程**：按功能模块分配成本 → 定关键器件成本上限 → 汇总 BOM → 与目标成本对比 → 标超支风险 → 成本倒推模型（零售价→出厂→产品成本→BOM 目标→模块分解）→ 标三级估算精度。

- **纪律**：BOM 以供应链报价为准不替代询价；超支按「降指标→换方案→砍功能→提售价→降毛利」五策略顺序启用。

#### `def-quality-baseline`（v1\.2\.0）· 品质及格线

- **作用**：逐品质检验类特性（良率/失效率/合规判定/可靠性等非性能质量特性）给出最低可接受值 Threshold，作为下游品质部门制定检验标准的依据。

- **输入 → 输出**：`perf_spec`（← def\-perf\-spec）→ `quality_baseline`；正文品质检验类及格线文档（逐特性 Threshold \+ 建议测试条件 \+ 判定规则）。

- **工作流程**：逐特性给 Threshold → 与 perf\-spec 对齐避免重叠 → 定义建议测试条件（不定稿）→ 设判定规则 → 标优先级 → 输出文档。

- **纪律**：性能 Threshold 归 def\-perf\-spec，本 Skill 不重复产出；不替代品质部门正式检验标准；须与性能 KPI 总表逻辑自洽。

#### `def-prd`（v4\.2\.0）· 智能 PRD 撰写与澄清（PRD 总装）

- **作用**：把前序定型卡/功能/性能/技术意向/架构/成本/品质/ID/路线图整合为可评审、可验收、可追溯、可机器校验的 PRD 产物（single / hybrid / modular 三种模式），并做机械自检。

- **输入 → 输出**：`func_spec / perf_spec / tech_intent / cost_breakdown / quality_baseline`（← 各 def\-\*）\+ `rtm`（← req\-srs\-builder）→ `prd / prd_package_index / prd_delta`（另有 decision\_freeze\_table / pending\_confirmation\_register / review\_gate\_report）；交付 `single_prd`，或 `hybrid_prd`（00\_总览 \+ 模块 PRD），或 `modular_prd_package`（00\_总览 \+ 每模块 `NN_功能点名_PRD.md`；机器件含 module\-prd / prd\-package\-index / product\-definition\.json / product\-definition\-run\-state\.json）。

- **工作流程**：读 task\-charter/Gate 资料 → 缺口盘点与决策收敛（C0/C1 先追问不写成事实）→ 判输出模式（single/hybrid/modular）与产品类型/复杂度 → 功能点 1:1 映射拆任务 → 按模板路由生成 Markdown\+JSON → 生成 PRD\-RTM 双向追溯 → 机械自检（章节职责/空泛词/验收可测/零型号/界面穷举/异常闭环）→ 输出 PM 复核清单、基线评审与 CCB 分级。

- **纪律**：写前必盘点缺口；1 功能点=1 任务=1 次调用，禁大而泛模块；零型号铁律；假设与待确认分开标注；Markdown 与 JSON 冲突以 JSON 为准。软件/一体机产品在 PRD 内定义交互需求规格、数据采集与埋点（tracking\_spec）、验证策略与 AB 实验（validation\_strategy）等章节。

---

## 5\. 产品设计（10）

#### `design-ia-ixd`（v1\.0\.0）· 信息架构与交互流程

- **作用**：基于 PRD 搭建信息架构、页面层级、核心旅程与交互流程，输出可被研发承接的流程说明与线框骨架，是高保真 UI 的前置。

- **输入 → 输出**：`prd`（← def\-prd）→ `ia / interaction_flow / wireframe`；交付 `信息架构_产品代号_vX_日期.md` \+ 同规格 `.json`（ia\_tree / user\_journeys / page\_flow / wireframes / interaction\_rules）。

- **工作流程**：确认核心场景优先级 → 梳理 Persona → 搭 3 层信息架构树（优先级/入口/权限）→ 画 2\-5 条含异常分支（消费 PRD exception\_path）核心旅程 → Mermaid 页面流转图（含异常与回退）→ 每页 ASCII 线框 → 定义导航/反馈/手势交互规则 → P0 全覆盖与死胡同检查 → 落盘 MD \+ JSON。

- **纪律**：不做高保真视觉与可交互原型；缺 ASCII 线框即被打回；不替需求专家改功能、不替研发判技术。

#### `design-hifi-ui`（v1\.1\.0）· 高保真 UI \+ 可交互原型 \+ 设计交付

- **作用**：把 IA/交互转成高保真视觉与可交互原型（核心交付为浏览器可直接打开的 HTML，含异常分支闭环），做设计工具路由（默认 HTML，可询问 Figma/MasterGo）。

- **输入 → 输出**：`ia / interaction_flow`（← design\-ia\-ixd）\+ `design_system`（← design\-system，可选）→ `hifi_ui / prototype / design_spec / tool_route`；交付 `高保真UI_产品代号_vX_日期.html` \+ `.md`（Spec/人工调整点）\+ `.json`（pages/prototype\_interactions/consumed\_refs）。

- **工作流程**：读上游 ia JSON 与 token JSON 真消费字段 → 提品牌关键词定视觉方向 → 覆盖 P0 页面与关键状态 → 出设计说明（色/字/间距）→ 一致性自检 → 用 HTML/CSS/JS 产可交互高保真（内嵌 token、覆盖 Happy Path\+异常）→ 输出 MD 说明与人工调整点 → 工具路由决策 → 落盘 JSON。

- **纪律**：必须消费上游 token JSON 不另起炉灶；工具路由默认 HTML、不要求先配 MCP；不写后端/工程化前端。

#### `design-system`（v1\.1\.0）· 设计系统与组件库

- **作用**：建立/复用设计系统与组件库，定义 Design Token，产出可预览 HTML 组件库 \+ 机器可读 Token JSON，保证跨页面/平台一致性。

- **输入 → 输出**：`prd`（← def\-prd）→ `design_system`；交付 `设计系统_产品代号_vX_日期.html` \+ `设计令牌_产品代号_vX_日期.json` \+ `.md` 说明。

- **工作流程**：梳理品牌基调提色彩/字体/形态语言 → 定义 color/typography/spacing/radius/shadow/断点 Token → 定义按钮/输入/展示/反馈/导航组件规范 → 组件状态（默认/Hover/焦点/禁用/错误）→ 使用规则 → 设计与代码命名映射 → 一致性检查 → 输出 HTML 组件库 \+ 对齐 schema 的 Token JSON \+ MD。

- **纪律**：组件 states 必含默认；token\_refs 不得悬空引用（validate 打回）；不输出可运行前端、不设计具体页面。

#### `design-id-concept`（v1\.0\.0）· 工业设计概念生成（外观造型）

- **作用**：提供 2\-3 套外观造型方案、多角度视图文字表达、设计语言一致性审查与趋势参考，聚焦「长什么样」。

- **输入 → 输出**：`func_spec`（← def\-func\-spec）\+ `id_input`（← def\-id\-input）→ `id_concept`；交付 `外观造型_产品代号_YYYYMMDD.md`（造型方案 \+ 对比矩阵 \+ 一致性审查）。

- **工作流程**：需求理解（品类/用户/场景/品牌）→ 趋势与竞品扫描 → 从形态语义/线条/比例定义设计语言 → 输出 2\-3 套差异化造型方案（每套含正/侧/顶/背/透视文字描述）→ 产品线一致性/家族化审查 → 表格对比推荐。

- **纪律**：不生成渲染/效果/工程图；不涉及 CMF 参数与内部结构；不做量产工艺可行性判断。

#### `design-cmf`（v1\.0\.0）· CMF Design

- **作用**：提供配色方案、材质选型建议、表面处理工艺推荐，以及可更换外壳/部件的 CMF 组合。

- **输入 → 输出**：`id_concept`（← design\-id\-concept）→ `cmf`；交付 `色彩材质工艺_产品代号_YYYYMMDD.md`（2\-3 套配色 \+ 按部件材质工艺 \+ 对比矩阵）。

- **工作流程**：确认设计约束（品类/审美/品牌色/成本工艺）→ CMF 趋势与竞品对标 → 输出 2\-3 套含主/辅/点缀色值的配色方案 → 按部件材质选型\+表面处理\+备选 → 可更换部件独立 CMF → 按审美/成本/工艺可行性对比推荐。

- **纪律**：不做实物样板/色差测量；不涉及造型形态与结构力学；不做供应商评估/采购决策。

#### `design-physical-ux`（v1\.0\.0）· 实体产品可用性（人因检查）

- **作用**：从人因工程角度评估优化物理交互体验（握持/放置稳定性、按键可及性、指示灯可视角度、安全距离、防误触），横切 ID→堆叠→结构全程的约束校验。

- **输入 → 输出**：`id_concept`（← design\-id\-concept）→ `physical_ux_check`；交付 `人因评估_产品代号_YYYYMMDD.md`。

- **工作流程**：确认使用姿势与手型范围 → 评估握持/放置稳定性 → 逐一评估按键可达性/间距/触觉/误触 → 评估指示灯/屏幕可视性 → 审查热区/旋转件/锐边/电池安全间隙 → 按键与接口误触防护 → 在 D1'/D2'/D3' 三时点均过人因检查。

- **纪律**：不代替真人可用性测试与生物力学仿真；不涉及 UI 软件交互与外观造型；不签发安规认证报告。

#### `design-bom`（v1\.0\.0）· 关键物料清单 BOM

- **作用**：从产品定义规格反推关键物料清单，输出成本区间、单台用量、长周期/单点风险标记，供采购前置布局。

- **输入 → 输出**：`cost_breakdown`（← def\-cost\-breakdown）\+ `id_concept`（← design\-id\-concept）→ `bom`；交付《关键物料 BOM》MD（物料/规格反推/成本区间/单台用量/风险标记）。

- **工作流程**：从 PRD 反推关键物料清单（主控/屏幕/电池/传感器/结构件等）→ 每条补规格\+成本区间\+单台用量 → 标长周期（交期\>8 周）与单点供应风险 → 汇总并标置信度与待确认项。

- **纪律**：无 PRD/供应链基线不得启动；禁杜撰物料、禁直接指定型号/供应商（只到能力规格级）；成本与选型须人工确认。

#### `design-3new`（v1\.0\.0）· 三新需求

- **作用**：提炼新材料/新工艺/新技术「三新」方向清单，随产品设计交付供研发评估。

- **输入 → 输出**：`bom`（← design\-bom）→ `three_new`；交付《三新需求》MD（方向\+应用部位\+替代价值\+风险\+置信度）。

- **工作流程**：从设计与 PRD 反推三新点 → 分维度逐条列方向 → 每条标应用部位/替代价值/风险/置信度 → 汇总清单。

- **纪律**：无 PRD 与设计链路成果不得启动；禁杜撰未经证实材料/工艺；只做方向翻译，工艺可行性须研发评审人工确认。

#### `design-selling-point`（v1\.0\.0）· 卖点提炼

- **作用**：提炼产品卖点（一句话卖点 → 三段论证 → 竞争性差异），将 PRD 与调研转译为营销语言，供外部营销模块消费。

- **输入 → 输出**：`func_spec`（← def\-func\-spec）\+ `strategic_recommendation`（← mkt\-s5\-strategic\-recommendation，可选）→ `selling_point`；交付《卖点提炼》MD。

- **工作流程**：从 PRD 核心价值 \+ 竞品差距提炼一句话卖点 → 功能价值→用户收益→差异化证据三段论证 → 对照竞品提竞争性差异点 → 汇总供营销消费。

- **纪律**：无 PRD 或竞品洞察不得启动；禁止夸大功效、脱离 PRD 事实杜撰卖点；品牌口径须产品负责人确认。

#### `design-packaging-req`（v1\.0\.0）· 包装需求提给

- **作用**：向包装设计/供应链输出包装需求（尺寸/主色调/约束），不产出设计稿。

- **输入 → 输出**：`bom`（← design\-bom）→ `packaging_req`；交付《包装需求提给》MD。

- **工作流程**：从产品外观尺寸反推包装尺寸 → 定包装主色调（对齐品牌调性）→ 列防护/运输/环保合规/成本约束 → 输出需求提给并明确不做设计稿。

- **纪律**：禁止越界产包装设计稿；禁杜撰合规要求；品牌口径与合规须产品/法规人工确认。

---

## 6\. 统计与映射

|归属|Skill 数|内部编排说明|
|---|---|---|
|主理人|5|影响分析/一致性/门禁/日志/记忆|
|交付层收口|1|deliverable\-packager（任务级收尾归置）|
|市场调研|23|使能 2 \+ 阶段编排 5 \+ 能力级 16（S1×4、S2×4、S3×3、S4×3、S5×2）|
|需求分析|6|阶段0\~5（req\-problem\-define → req\-srs\-builder）|
|产品定义|9|def\-func\-spec / perf\-spec / tech\-intent / architecture / id\-input / roadmap / cost\-breakdown / quality\-baseline → def\-prd（PRD 总装）|
|产品设计|10|数字链 design\-ia\-ixd→design\-hifi\-ui（\+design\-system）；实体链 design\-id\-concept→design\-bom 等；design\-selling\-point 营销侧|
|**合计**|**54**|各 Skill 归属与专家级调用见 doc02\~doc06|

说明：

- io 前置 `schema:xxx` = 阶段产物 JSON 契约；`file:xxx` = 运行期单文件；其余 `xxx ← skill 目录` = Skill 间字段消费。

- 使能/收口/记忆四 Skill（mkt\-data\-evidence、mkt\-quality\-gate、deliverable\-packager、team\-memory\-manager）为 passthrough 无字段级 io，由编排器或主理人直接调用，不参与字段级链路校验。

- 每阶段 Skill 的完整纪律、边界与断点规则以对应 `SKILL.md` 正文及其所属 `references/` 运行手册为准。

- 产出物落盘、命名与四分类口径见 `config/output-config.yaml` 与 `references/00_总纲与治理/产出物放置与命名规范.md`（详见 doc08）。

