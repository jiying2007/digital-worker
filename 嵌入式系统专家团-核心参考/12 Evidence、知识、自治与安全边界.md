# 12 Evidence、知识、自治与安全边界

## 1. Evidence 是一等对象

嵌入式专家团不以“模型说得像”为可信度依据，而以可追溯证据支撑 claim。

典型 evidence：

- source code / commit；
- log / dmesg / UART；
- core / dump / register；
- datasheet / TRM；
- schematic；
- waveform / measurement；
- build / CI；
- binary / artifact hash；
- device identity；
- HIL run；
- test report。

重要结论建议形成：

```text
claim
+ evidence_refs[]
+ fact_state
+ confidence
+ verification_status
```

## 2. Fact State 与 Confidence

Debug 三态：Observed / Inferred / Confirmed。

Expert Group 还保留 C0-C6 confidence levels。Confidence 只描述证据强弱，不能绕过 Verification layer。

例如“C6 认为设备一定通过”仍不能替代真实 device/HIL evidence。

---

## 3. Knowledge 边界

研发中心总体方案明确：

- 飞书：人工正式知识主库；
- WeKnora：AI 检索层；
- `digital-worker`：方法论、契约、模板、规则、评测 fixture 的 SSOT。

本专家团本地不再创建第二个企业知识主库。

本地可存：

- methodology；
- checklist；
- template；
- terminology；
- source registry；
- static engineering rules；
- evaluation fixtures。

项目事实、现场敏感日志、客户资料应留在其权威系统，通过 evidence ref 使用。

---

## 4. A0-A7 自治等级

### A0_READ

读取 repo/docs/log/artifact metadata。

### A1_ANALYZE

技术分析、路由、诊断、评审。

### A2_GENERATE

生成方案、patch proposal、测试计划、文档，但不直接执行有副作用动作。

当前 23 个 P0 Skills 上限为 A2。

### A3_MODIFY_WORKTREE

修改代码/文档 worktree；仅工程执行链受控允许。

### A4_BUILD_TEST

Build/Test；仍必须受 package scope 约束。

### A5_DEVICE_READ

读取串口、状态、设备信息；需授权。

### A6_DEVICE_WRITE

烧录、写配置等；必须人工审批。

### A7_RELEASE

Release/OTA/Promotion；必须人工审批。

---

## 5. 永不默认自动的动作

- OTP/Fuse；
- 生产签名密钥；
- Production OTA；
- 不可逆 Boot 配置；
- destructive production data action。

这些即使未来系统自动化程度提高，也需要单独安全设计。

---

## 6. Pilot Evidence Bundle

真实 Pilot 不应把原始日志/core/firmware 一股脑提交进 `digital-worker`。

Pilot CLI 会建立结构化 run directory，并生成 `evidence-bundle.json`：

- artifact kind；
- path/ref；
- SHA256；
- required flag。

`pilot/runs/` 默认 Git ignore。原始敏感证据留在受控存储，只在 repo 中保留契约与引用。

---

## 7. 安全 Fail-closed

系统当前有多层 fail-closed：

1. 未注册 Skill 禁止正式调用；
2. review_only 禁止隐式执行；
3. real Pilot 必须 exact base SHA；
4. run artifact 禁止路径逃逸；
5. completed run 缺 required artifact 拒绝；
6. incorrect PASS fixture 必须被 evaluator 拒绝；
7. unauthorized action 阻断 Productionization eligibility；
8. edge-foundation ownership unresolved 时禁止伪装 resolved。

---

## 8. Secret / Sensitive Data

内部评审建议明确以下后续策略：

- log/core 中 token/password/key 脱敏；
- firmware/binary 的保留周期；
- customer/project confidential artifact 的 evidence ref 访问控制；
- HIL/设备串口日志是否允许进入 AI 上下文；
- 生产 key/签名服务与 AI 永久隔离边界。

当前专家团架构不授权 AI 管理生产 Secret。

---

## 9. Main Governance 风险

当前 `Embedded Expert Contracts` CI 已存在并稳定运行，但 main branch protection/required check 仍待管理员配置。

因此“CI 有红灯”在平台层理论上仍可能被人为绕过。

P0 governance Issue 已登记，正式生产化前应关闭此缺口。

---

## 10. 评审重点

1. A5 Device Read 是否可以默认授权给部分实验室设备？
2. A6 Device Write 是否可在专用测试板上引入一次批准/会话授权？
3. 现场日志进入模型的脱敏与权限由谁负责？
4. Evidence Bundle 是否应接入制品库而非 repo 目录？
5. main protection 何时启用、谁是管理员 owner？
