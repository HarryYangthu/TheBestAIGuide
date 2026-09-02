# Multi-Agent 系统评测体系搭建指南

## 目录

- [一、核心原则：评测的是系统，不是单个模型](#一核心原则评测的是系统不是单个模型)
- [二、Multi-Agent 评测为什么更难](#二multi-agent-评测为什么更难)
- [三、评测体系总架构](#三评测体系总架构)
- [四、Task 设计：把任务写成“考题”](#四task-设计把任务写成考题)
- [五、Trial 设计：用多次运行对抗随机性](#五trial-设计用多次运行对抗随机性)
- [六、Grader 设计：组合评分器，而不是单点判断](#六grader-设计组合评分器而不是单点判断)
- [七、Multi-Agent 特有评分维度](#七multi-agent-特有评分维度)
- [八、四类系统的评测方案](#八四类系统的评测方案)
- [九、稳定性指标：pass@k 与 pass^k](#九稳定性指标passk-与-passk)
- [十、从零搭建的八步路线图](#十从零搭建的八步路线图)
- [十一、环境隔离与防作弊](#十一环境隔离与防作弊)
- [十二、评测方法组合：多层防线](#十二评测方法组合多层防线)
- [十三、工具选择建议](#十三工具选择建议)
- [十四、落地模板](#十四落地模板)
- [十五、检查清单](#十五检查清单)

## 一、核心原则：评测的是系统，不是单个模型

很多人以为评测的是模型，但在 Agent 或 multi-Agent 系统里，真正被评测的是整个系统：

```text
Multi-Agent System
= Models
+ Supervisor / Router
+ Agent Harness
+ Tool Harness
+ Memory / State
+ Environment
+ Evaluation Harness
```

单模型能力强，不代表 multi-Agent 系统就稳定。一个优秀模型放进糟糕的工具解析、混乱的任务路由、脆弱的状态管理里，最终表现也会很差。

因此，评测目标不是回答“这个模型聪不聪明”，而是回答：

- 这个系统能不能稳定完成任务？
- 多个 Agent 的分工是否合理？
- Supervisor 是否能正确路由？
- 子 Agent 的结果是否能被正确汇总？
- 工具调用、环境状态、最终结果是否可信？
- 系统在多次运行中是否稳定？

核心判断标准：

> Transcript 可能撒谎，Outcome 才是真相。

不要只看 Agent 说了什么，要看环境最终变成了什么样：数据库是否更新、文件是否修改、订单是否创建、测试是否通过、报告里的事实是否有来源。

## 二、Multi-Agent 评测为什么更难

单 Agent 已经有非确定性和多轮交互问题，multi-Agent 会进一步放大这些问题。

### 2.1 错误会跨 Agent 传播

一个子 Agent 早期的错误结论，可能被 Supervisor 当成事实，再传给后续 Agent。后续 Agent 即使本身能力很强，也会在错误前提上继续推理。

评测时不能只看最后答案，还要记录：

- 哪个 Agent 产生了关键中间结论？
- 这个结论有没有证据？
- Supervisor 是否做了验证？
- 下游 Agent 是否盲目信任了上游输出？

### 2.2 任务路由本身需要评测

multi-Agent 系统多了一个关键能力：把任务交给谁。

常见失败：

- 数学任务交给研究 Agent。
- 搜索任务交给代码 Agent。
- 简单任务被拆成过多子任务。
- 明明需要多个专家，却只调用一个 Agent。
- 多个 Agent 重复做同一件事。

所以，评测不仅要看任务完成，还要看路由是否合理。

### 2.3 协作质量会影响最终结果

multi-Agent 不是多个 Agent 各干各的。真正重要的是协作质量：

- 子任务拆分是否清晰？
- 交接信息是否完整？
- 汇总时是否保留关键证据？
- 冲突结果是否被处理？
- 是否存在重复劳动？
- 是否因为上下文过长或信息冗余导致质量下降？

### 2.4 评测对象从“输出”变成“轨迹 + 状态”

multi-Agent 的一次运行需要记录完整轨迹：

- 用户输入。
- Supervisor 的规划和路由。
- 每个子 Agent 的输入、输出、工具调用。
- Agent 之间的交接信息。
- 环境状态变化。
- 最终结果。
- 成本、延迟、工具调用次数、轮次数。

这就是 Trajectory。没有完整 Trajectory，就很难定位失败发生在哪一层。

## 三、评测体系总架构

multi-Agent 评测体系可以按下面的层次搭建：

```text
Evaluation Harness
  ├─ Evaluation Suite
  │   ├─ Task 1
  │   ├─ Task 2
  │   └─ Task N
  │
  ├─ Agent Harness
  │   ├─ Supervisor / Router
  │   ├─ Specialist Agent A
  │   ├─ Specialist Agent B
  │   ├─ Tool Layer
  │   └─ Environment
  │
  ├─ Trials
  │   ├─ Trajectory
  │   ├─ Outcome
  │   └─ Metrics
  │
  └─ Graders
      ├─ Code-based Grader
      ├─ Model-based Grader
      └─ Human Grader
```

每个部分的作用：

| 组件 | 作用 |
| --- | --- |
| Evaluation Harness | 组织任务、运行系统、收集轨迹、调用评分器。 |
| Evaluation Suite | 一组覆盖不同能力、风险和场景的任务集合。 |
| Agent Harness | 真正运行 multi-Agent 系统的脚手架。 |
| Task | 具体考题，包含输入、初始状态、成功标准、评分器。 |
| Trial | 同一个 Task 的一次完整执行。 |
| Trajectory | 一次执行的完整记录，包括消息、工具调用、路由和中间状态。 |
| Outcome | 最终环境状态。 |
| Grader | 根据 Trajectory 和 Outcome 打分。 |

## 四、Task 设计：把任务写成“考题”

不要把 Task 写成一句愿望：

```python
task = "帮我完成一个市场研究报告"  # ❌ 太模糊
```

应该写成有边界、有初始状态、有成功标准的考题：

```yaml
task:
  id: "multi-agent-market-research-001"
  description: "分析某公司 Q3 财报，输出结构化研究报告"

  initial_state:
    user_request: "重点关注营收、利润、交付量、风险和未来展望"
    available_tools:
      - web_search
      - document_reader
      - spreadsheet_analyzer
    seed_documents:
      - company_q3_report.pdf

  expected_agent_roles:
    - supervisor
    - research_agent
    - analysis_agent
    - report_writer_agent

  success_criteria:
    - 报告包含营收、利润、交付量、同比变化、未来展望
    - 每个关键数字都有来源引用
    - 不使用不可接受信源
    - 最终报告结构清晰
    - Supervisor 正确拆分并汇总任务

  expected_outcome:
    report_created: true
    grounded_claim_rate: ">= 95%"
    source_quality: "acceptable"
    total_score: ">= 0.8"
```

Multi-Agent Task 至少要写清楚五件事：

| 项目 | 要回答的问题 |
| --- | --- |
| 用户目标 | 用户到底要什么？ |
| 初始状态 | 系统开始时有哪些数据、文件、工具、环境？ |
| Agent 角色 | 哪些 Agent 可能参与？各自职责是什么？ |
| 成功标准 | 什么叫完成？什么叫失败？ |
| 评分方式 | 用哪些 Grader 验证？看 Outcome 还是 Transcript？ |

### 4.1 无歧义任务标准

一个好 Task 应该满足：

- 两个领域专家独立评估，会得出相同的通过/失败判断。
- 成功标准可检查，而不是“看起来不错”。
- 文件路径、输出格式、工具边界明确。
- 不把隐藏假设塞进 Grader。
- 允许合理路径差异，不强制唯一执行路线。

反例：

```yaml
task: "优化系统性能"
grader:
  criteria: "代码应该更快"
```

问题：多快算快？可以牺牲正确性吗？要优化哪个函数？用什么数据测？

更好的写法：

```yaml
task: |
  优化 compute_stats() 函数的性能。
  当前 baseline：处理 10000 条数据需要 100ms。
  目标：降低到 50ms 以下，同时保持结果正确。

graders:
  - type: performance_test
    baseline: 100ms
    target: 50ms
  - type: correctness_test
    test: test_stats_accuracy.py
```

## 五、Trial 设计：用多次运行对抗随机性

multi-Agent 系统更不能只跑一次。一次通过可能只是运气好，一次失败也可能只是偶发。

建议：

| 场景 | Trial 数量 | 用途 |
| --- | --- | --- |
| 快速验证 | 3 次 | 看明显问题。 |
| 正式评估 | 10 次 | 估算真实通过率。 |
| 关键任务 | 100 次 | 评估稳定性和上线风险。 |

每个 Trial 都应该保存：

- 输入任务。
- 所有 Agent 的消息。
- Supervisor 的路由决策。
- 每次工具调用。
- 中间状态。
- 最终 Outcome。
- 成本、延迟、token、轮次数。
- 通过或失败原因。

建议统一记录结构：

```yaml
trial:
  task_id: "multi-agent-market-research-001"
  trial_id: "trial-007"

  trajectory:
    supervisor_steps: []
    agent_messages: []
    tool_calls: []
    handoffs: []
    state_changes: []

  outcome:
    report_created: true
    tests_passed: true
    database_updated: false

  metrics:
    n_turns: 18
    n_agent_handoffs: 5
    n_toolcalls: 12
    tokens: 43000
    latency_seconds: 95
    total_cost: 3.2

  result:
    passed: true
    score: 0.86
```

## 六、Grader 设计：组合评分器，而不是单点判断

multi-Agent 系统应该组合三类评分器。

| 评分器 | 适合判断 | 优势 | 风险 |
| --- | --- | --- | --- |
| Code-based Grader | 测试是否通过、状态是否正确、工具参数是否正确。 | 快、便宜、客观、可复现。 | 太机械，不懂语义。 |
| Model-based Grader | 质量、语义、完整性、专业性、协作合理性。 | 灵活，适合开放任务。 | 非确定、贵，需要校准。 |
| Human Grader | 高风险决策、主观体验、专家判断。 | 黄金标准。 | 贵、慢、不可大规模日常使用。 |

推荐组合：

```yaml
graders:
  # 结果正确性：必须过
  - name: "Outcome Check"
    type: code-based
    required: true
    checks:
      - final_report_exists
      - required_fields_present
      - tests_passed
    weight: 0.3

  # 协作过程：看路由、交接、重复劳动
  - name: "Collaboration Quality"
    type: model-based
    rubric: "评估 Supervisor 拆分任务、路由、汇总和冲突处理是否合理"
    weight: 0.2

  # 工具使用：是否该用才用
  - name: "Tool Use"
    type: code-based
    checks:
      - expected_tools_used
      - no_unnecessary_tool_calls
      - tool_params_valid
    weight: 0.2

  # 输出质量：专业性与可读性
  - name: "Final Quality"
    type: model-based
    rubric: "评估最终输出是否清晰、完整、专业、有洞察"
    weight: 0.2

  # 成本效率：不能无限堆 Agent
  - name: "Efficiency"
    type: code-based
    metrics:
      - n_agent_handoffs <= 8
      - n_toolcalls <= 20
      - latency_seconds <= 120
    weight: 0.1

scoring_strategy: hybrid
passing_threshold: 0.8
```

### 6.1 不要把 Grader 写得太死

multi-Agent 系统可能找到比预设流程更好的路径。评分器不要只检查“有没有按我设想的步骤走”，更应该检查：

- 最终任务是否真的完成？
- 环境状态是否正确？
- 是否违反安全或业务约束？
- 是否创造了更好的结果？

原则：

> 少卡 Transcript，多看 Outcome。

## 七、Multi-Agent 特有评分维度

除了普通 Agent 的功能、质量、安全、效率，multi-Agent 还需要额外评估协作层。

### 7.1 Supervisor / Router 评分

看它是否把任务交给了正确的人。

| 维度 | 检查方式 |
| --- | --- |
| 路由正确性 | 数学任务是否交给计算 Agent，研究任务是否交给搜索 Agent。 |
| 拆分合理性 | 是否把复杂任务拆成清晰子任务。 |
| 终止判断 | 任务完成后是否停止，而不是继续调用 Agent。 |
| 过度调用 | 是否为了简单任务启动过多 Agent。 |
| 漏调用 | 是否漏掉关键专家 Agent。 |

示例：

```yaml
grader:
  name: "Routing Correctness"
  type: model-based
  rubric: |
    评估 Supervisor 的路由是否合理：
    1. 是否识别了任务类型？
    2. 是否选择了合适的 Agent？
    3. 是否避免了不必要的 Agent 调用？
    4. 是否在任务完成后正确停止？
```

### 7.2 Handoff 评分

看 Agent 之间交接是否清晰。

| 维度 | 检查方式 |
| --- | --- |
| 信息完整 | 下游 Agent 是否拿到了必要背景、约束和目标。 |
| 证据保留 | 关键结论是否带来源、工具结果或状态引用。 |
| 边界清晰 | 子任务是否明确，不互相踩线。 |
| 冲突暴露 | 上游信息冲突时，是否显式标记。 |

示例：

```yaml
grader:
  name: "Handoff Quality"
  type: model-based
  rubric: |
    检查每次 Agent 交接：
    - 是否说明任务目标？
    - 是否说明已知事实？
    - 是否保留证据来源？
    - 是否指出不确定性？
    - 是否避免把猜测包装成事实？
```

### 7.3 协作效率评分

multi-Agent 很容易“看起来很忙”，但效率很低。

需要监控：

- `n_agent_handoffs`：Agent 之间交接次数。
- `n_toolcalls`：工具调用次数。
- `n_turns`：总轮数。
- `tokens`：token 消耗。
- `latency`：整体耗时。
- 重复搜索、重复读文件、重复计算次数。

反模式：

```text
Research Agent 搜了一遍资料。
Analysis Agent 不信，又搜了一遍。
Writer Agent 写报告前，又搜了一遍。
Supervisor 汇总时，又搜了一遍。
```

这类系统可能最终答案正确，但成本和延迟都不可接受。

### 7.4 冲突处理评分

多 Agent 很容易产生不同结论。评测要检查系统是否能处理冲突，而不是随机选一个。

评分点：

- 是否识别出两个 Agent 结论不一致？
- 是否请求补充证据？
- 是否基于可信来源裁决？
- 是否在最终输出中说明不确定性？

## 八、四类系统的评测方案

原指南把 Agent 分成四类。multi-Agent 系统也可以按任务类型设计不同评测方案。

### 8.1 编程型 Multi-Agent

典型结构：

```text
Supervisor
  ├─ Planner Agent
  ├─ Coder Agent
  ├─ Test Agent
  └─ Review Agent
```

核心原则：

> 代码能跑是及格线，代码质量才是分水岭。

评测维度：

| 维度 | 推荐 Grader |
| --- | --- |
| 功能正确性 | Code-based：单元测试、集成测试、回归测试。 |
| 不破坏现有能力 | Code-based：pass-to-pass 测试。 |
| 代码质量 | Model-based：Rubric 评分。 |
| 安全性 | Code-based：静态分析、安全扫描。 |
| 协作质量 | Model-based：看 Planner、Coder、Tester 是否分工清晰。 |
| 工具使用 | Code-based：是否读了相关文件、是否运行测试。 |

示例：

```yaml
task:
  id: "fix-auth-bypass-empty-password"
  description: "修复认证系统的空密码绕过漏洞"

  agents:
    - planner
    - coder
    - tester
    - reviewer

  graders:
    - name: "功能测试"
      type: code-based
      method: pytest
      required: true
      tests:
        - test_empty_password_rejected.py
        - test_null_password_rejected.py
        - test_valid_password_accepted.py
      weight: 0.3

    - name: "代码质量"
      type: model-based
      rubric: "代码是否清晰、安全、可维护"
      weight: 0.3

    - name: "静态分析"
      type: code-based
      tools:
        - ruff
        - mypy
        - bandit
      weight: 0.2

    - name: "协作过程"
      type: model-based
      rubric: "Planner 是否定位问题，Coder 是否按计划修改，Tester 是否验证修复"
      weight: 0.2
```

### 8.2 对话型 Multi-Agent

典型结构：

```text
User Simulator
  ↔ Supervisor
      ├─ Policy Agent
      ├─ Tool Agent
      └─ Response Agent
```

评测难点：对话没有唯一标准答案，交互体验本身就是结果的一部分。

推荐使用用户模拟器：

```python
class AngryCustomerSimulator:
    """愤怒客户模拟器"""

    def __init__(self):
        self.patience = 3

    def respond(self, agent_message):
        if "不能退款" in agent_message and "抱歉" not in agent_message:
            self.patience -= 1
            return "什么态度！我要投诉！"

        if "退款已提交" in agent_message and "3个工作日" in agent_message:
            return "好的，谢谢。"

        return "我不管，我就要退款！"
```

三维评分：

| 维度 | 检查问题 | 推荐 Grader |
| --- | --- | --- |
| 结果层 | 事办成了吗？ | State Check。 |
| 效率层 | 是否重复问、轮次是否过多？ | Transcript Metrics。 |
| 体验层 | 是否有同理心、清晰度、专业性？ | Model-based Rubric。 |

特别注意：要构建正例和反例，防止系统变成“偏执狂”。

例如搜索工具评测：

| 类型 | 例子 | 预期 |
| --- | --- | --- |
| 正例 | 今天北京天气 | 应该搜索。 |
| 正例 | 最新 GDP 数据 | 应该搜索。 |
| 反例 | 什么是机器学习 | 不应搜索。 |
| 反例 | 1+1 等于几 | 不应搜索。 |

需要同时监控：

```python
undertrigger = 该搜不搜
overtrigger = 不该搜乱搜

precision = TP / (TP + FP)
recall = TP / (TP + FN)
f1 = 2 * precision * recall / (precision + recall)
```

### 8.3 研究型 Multi-Agent

典型结构：

```text
Supervisor
  ├─ Search Agent
  ├─ Source Verification Agent
  ├─ Analysis Agent
  └─ Writer Agent
```

最大风险：

> 一本正经地胡说八道。

组合评分策略：

| 维度 | 评分方式 | 作用 |
| --- | --- | --- |
| 扎实度 | Source 引用检查 | 防幻觉。 |
| 覆盖率 | 关键事实清单 | 防遗漏。 |
| 信源质量 | 权威性验证 | 防劣质来源。 |
| 连贯性 | LLM 评分 | 保证逻辑。 |
| 协作质量 | Handoff 检查 | 防止证据在交接中丢失。 |

Groundedness 检查示例：

```python
for claim in agent_output.claims:
    source = agent_output.sources[claim.source_id]

    # 检查 1：有没有引用？
    assert claim.source_id is not None

    # 检查 2：源文件里是否真的包含这个信息？
    assert claim.text in source.content

    # 检查 3：是否曲解原文？
    is_faithful = llm_judge(
        f"原文：{source.excerpt}\n"
        f"声称：{claim.text}\n"
        f"声称是否忠实于原文？"
    )
    assert is_faithful == "YES"
```

研究型系统要特别检查：

- 搜索 Agent 是否找到足够来源。
- 验证 Agent 是否过滤低质量来源。
- 分析 Agent 是否引用证据，而不是凭空推断。
- 写作 Agent 是否保留关键数字和来源。
- Supervisor 是否处理冲突信息。

### 8.4 计算机操作型 Multi-Agent

典型结构：

```text
Supervisor
  ├─ Browser Agent
  ├─ Visual Agent
  ├─ DOM Agent
  └─ Verification Agent
```

核心挑战：到底该看截图，还是读 DOM？

| 方式 | Token 使用 | 速度 | 适用场景 |
| --- | --- | --- | --- |
| DOM 解析 | 高 | 快 | 纯文本提取。 |
| 截图视觉 | 低 | 慢 | 复杂视觉交互。 |

评测重点：

- 工具选择是否正确。
- Token 是否超预算。
- 操作是否真的改变后端状态。
- 不只看确认页，还要检查数据库、库存、文件系统等最终状态。

示例：

```python
# 单纯验证：不够
assert browser.url.contains("/order-confirmation")

# 完整验证：更可靠
assert browser.url.contains("/order-confirmation")
assert database.query("SELECT * FROM orders WHERE user_id=?").exists
assert database.query("SELECT * FROM inventory WHERE item_id=?").stock_decreased
```

## 九、稳定性指标：pass@k 与 pass^k

Multi-Agent 系统有非确定性，所以不能只看单次成功。

### 9.1 pass@k：至少成功一次

公式：

```text
pass@k = 1 - (1 - p)^k
```

含义：k 次尝试里，至少有一次成功。

适用：

- 人类会从多个结果里挑一个。
- 创意生成。
- 代码补全。
- 研究辅助。

优化方式：

- 增加多样性。
- 允许多个候选方案。
- 用排序模型或人工选择最优结果。

### 9.2 pass^k：每次都要成功

公式：

```text
pass^k = p^k
```

含义：k 次尝试全部成功。

适用：

- 自动客服。
- 金融交易。
- 医疗诊断。
- 内容审核。
- 无人类兜底的自动化流程。

优化方式：

- 降低随机性。
- 加自我验证。
- 加确定性测试。
- 加环境隔离。
- 加人工校准。

### 9.3 产品决策

```text
有人类在回路中把关吗？
  ├─ 有：用 pass@k，优化峰值表现
  └─ 无：用 pass^k，优化稳定性
```

multi-Agent 系统如果要无人值守运行，更应该关注 pass^k。因为一次子 Agent 失败，就可能导致整个链路失败。

## 十、从零搭建的八步路线图

### Step 0：尽早开始

不要等到有 1000 个样本再开始。早期 20 个案例就能暴露明显问题。

建议：

- 20 个案例：发现明显问题。
- 50 个案例：验证大改动。
- 100+ 案例：用于精确调优。

### Step 1：从手动测试开始

把团队已经在手动测的流程转成评测任务：

- 发版前必测场景。
- 线上 bug。
- 用户投诉。
- 高频失败任务。
- 关键业务流程。

### Step 2：编写无歧义任务

每个任务都要写清楚：

- 输入是什么。
- 初始环境是什么。
- 哪些 Agent 可以参与。
- 允许用哪些工具。
- 成功标准是什么。
- 失败标准是什么。
- 输出格式是什么。

### Step 3：构建平衡问题集

不要只测“应该触发”的场景，也要测“不应该触发”的场景。

例如：

- 应该搜索的问题。
- 不应该搜索的问题。
- 应该调用专家 Agent 的任务。
- 不应该调用专家 Agent 的简单任务。
- 应该并行拆分的任务。
- 不应该拆分的小任务。

目标：防止系统学成偏执狂。

### Step 4：构建稳定环境

每次 Trial 都要从干净环境开始，避免：

- Git 历史泄漏。
- 缓存残留。
- 数据库污染。
- 共享资源耗尽。
- 进程残留。
- 时间依赖导致随机失败。

### Step 5：设计评分器

决策树：

```text
有明确客观答案？
  ├─ 有：Code-based Grader
  │   ├─ 单元测试
  │   ├─ Schema 验证
  │   ├─ 数据库状态检查
  │   └─ 工具调用检查
  └─ 没有：Model-based Grader
      ├─ Rubric
      ├─ 维度拆分
      ├─ 逃生门
      └─ 人类校准
```

### Step 6：读 Transcripts

不读日志，就不知道系统为什么失败。

要定期抽样阅读：

- 成功但成本异常高的 Trial。
- 失败但看起来接近成功的 Trial。
- 评分器与人工判断不一致的 Trial。
- Supervisor 路由异常的 Trial。

### Step 7：监控评估饱和

如果某个评测集长期超过 85%，说明它可能太简单了，需要加入更难任务。

```python
if eval_score > 0.85:
    print("评估快饱和了，该加难题了")
```

### Step 8：长期维护

把评测变成研发流程：

```text
产品需求 -> 先写评估 -> 优化 Agent -> 达标 -> 晋升为回归测试
```

## 十一、环境隔离与防作弊

Multi-Agent 系统尤其容易被环境污染影响，因为多个 Agent 会读写同一环境。

每次 Trial 前应该清理：

```python
class EnvironmentIsolation:
    """确保每次试验环境干净"""

    def clean(self):
        self.delete_workspace()
        self.create_fresh_workspace()

        os.environ.clear()
        self.load_env_from_config()

        cache.flush_all()

        db.drop_all_tables()
        db.init_schema()
        db.load_seed_data()

        killall_previous_processes()
        logging.handlers.clear()
        mock_time.set("2024-01-01 00:00:00")
```

防作弊检查：

- 每次 Trial 使用全新 workspace。
- 清理 `.git` 历史，避免看到上一次答案。
- 清空缓存和临时文件。
- 重置数据库。
- 限制网络和工具权限。
- 固定时间、随机种子、初始数据。
- 保存完整日志，便于复盘。

## 十二、评测方法组合：多层防线

单一评测方法一定有盲区。推荐使用多层防线：

| 方法 | 能抓住的问题 | 抓不住的问题 | 阶段 |
| --- | --- | --- | --- |
| 自动化评估 | 已知场景回归。 | 未知边界情况。 | 开发 / CI。 |
| 生产监控 | 真实用户遇到的问题。 | 上线前看不到。 | 上线后。 |
| A/B 测试 | 整体效果提升或下降。 | 具体哪里错。 | 重大变更。 |
| 用户反馈 | 意外严重问题。 | 用户懒得报的小问题。 | 持续。 |
| 人工审查 | 质量细节、边界 case。 | 无法规模化覆盖。 | 每周 / 每月。 |

不同阶段配方：

### 12.1 开发前期

```yaml
primary:
  - 自动化评估
secondary:
  - 人工审查
minimal:
  - 内部 dogfooding
```

### 12.2 首次上线

```yaml
primary:
  - 自动化评估
  - 生产监控
secondary:
  - 用户反馈
preparing:
  - A/B 测试基础设施
```

### 12.3 规模化阶段

```yaml
continuous:
  - 自动化评估
  - 生产监控
  - 用户反馈
regular:
  - A/B 测试
  - 人工审查
periodic:
  - 人类研究
```

## 十三、工具选择建议

原指南中提到的工具可以按需求选择：

| 工具 | 适合场景 | 注意点 |
| --- | --- | --- |
| Harbor | 需要容器化隔离、代码执行环境。 | 配置复杂。 |
| Promptfoo | 轻量级 YAML 评测、快速迭代。 | 功能有限。 |
| Braintrust | 全生命周期监控。 | 商业产品。 |
| LangSmith | LangChain 生态。 | 绑定生态。 |
| Langfuse | 开源自托管、数据合规。 | 需要自己运维。 |

选择决策：

```text
需要代码执行隔离吗？
  ├─ 是：Harbor
  └─ 否：是否使用 LangChain？
      ├─ 是：LangSmith / Langfuse
      └─ 否：是否需要生产监控？
          ├─ 是：Braintrust
          └─ 否：Promptfoo 或自建轻量评测
```

务实建议：

> 先选一个够用的，把精力投到写好评测任务上。框架只是工具，任务才是核心。

## 十四、落地模板

### 14.1 Multi-Agent Eval Task 模板

```yaml
task:
  id: ""
  name: ""
  description: ""

  user_request: ""

  initial_state:
    files: []
    database: ""
    tools: []
    environment: ""

  agents:
    supervisor:
      responsibility: ""
    specialists:
      - name: ""
        responsibility: ""
        allowed_tools: []

  success_criteria:
    - ""

  failure_criteria:
    - ""

  expected_outcome:
    state_checks: []
    output_requirements: []

  graders:
    - name: "Outcome"
      type: code-based
      required: true
      weight: 0.3

    - name: "Routing"
      type: model-based
      weight: 0.2

    - name: "Handoff"
      type: model-based
      weight: 0.2

    - name: "Tool Use"
      type: code-based
      weight: 0.1

    - name: "Final Quality"
      type: model-based
      weight: 0.2

  metrics:
    - n_turns
    - n_agent_handoffs
    - n_toolcalls
    - tokens
    - latency
    - cost

  trial_config:
    n_trials: 10
    clean_environment: true
```

### 14.2 Model-based Grader Prompt 模板

```yaml
prompt: |
  你是 multi-Agent 系统评估员。

  请评估以下执行轨迹是否满足评分标准。

  如果信息不足，必须返回 "INSUFFICIENT_INFO"。
  不要猜测，不要假设。

  评分维度：
  1. 路由是否合理
  2. 子任务拆分是否清晰
  3. Agent 之间交接是否完整
  4. 是否保留关键证据
  5. 是否正确处理冲突
  6. 最终结果是否满足用户目标

  输出 JSON：
  {
    "routing": 0-5,
    "handoff": 0-5,
    "evidence": 0-5,
    "conflict_resolution": 0-5,
    "final_quality": 0-5,
    "verdict": "PASS | FAIL | INSUFFICIENT_INFO",
    "reason": ""
  }
```

### 14.3 日常运行策略

```yaml
daily:
  run:
    - core_regression_suite
    - high_risk_tasks
  graders:
    - code-based
    - model-based

weekly:
  run:
    - failed_case_review
    - transcript_sampling
  graders:
    - model-based
    - human spot-check

monthly:
  run:
    - human_calibration
    - benchmark_refresh
    - saturation_check
  graders:
    - human
```

## 十五、检查清单

### 15.1 Task 检查

- [ ] 任务不是一句愿望，而是明确考题。
- [ ] 初始状态清楚。
- [ ] Agent 角色和工具权限清楚。
- [ ] 成功标准可验证。
- [ ] 失败标准清楚。
- [ ] 输出格式明确。
- [ ] 没有隐藏假设。

### 15.2 Trial 检查

- [ ] 同一任务运行多次。
- [ ] 每次运行环境干净。
- [ ] 保存完整 Trajectory。
- [ ] 保存最终 Outcome。
- [ ] 保存 token、延迟、工具调用、handoff 次数。
- [ ] 可以复盘失败原因。

### 15.3 Grader 检查

- [ ] 客观结果优先用 Code-based Grader。
- [ ] 主观质量使用 Model-based Grader。
- [ ] Model-based Grader 有逃生门。
- [ ] 主观维度拆开评分。
- [ ] LLM 评分器定期用 Human Grader 校准。
- [ ] 不过度绑定固定执行路径。

### 15.4 Multi-Agent 协作检查

- [ ] Supervisor 路由正确。
- [ ] 子任务拆分清晰。
- [ ] Agent 之间交接完整。
- [ ] 关键证据没有在交接中丢失。
- [ ] 冲突信息被识别和处理。
- [ ] 没有重复搜索、重复计算、重复工具调用。
- [ ] 简单任务没有被过度拆分。

### 15.5 上线前检查

- [ ] 核心回归评测通过。
- [ ] 高风险任务 pass^k 达标。
- [ ] 成本、延迟、token 没有异常。
- [ ] 生产监控已配置。
- [ ] 用户反馈通道已准备。
- [ ] 人工抽查样本无明显风险。

## 总结

multi-Agent 评测体系的关键不是“多跑几个测试”，而是建立一套能观察、定位、校准和持续维护的系统。

最重要的原则：

- 评测的是完整系统，不是单个模型。
- 不只看最后回答，要看 Trajectory 和 Outcome。
- 不只评估任务结果，也要评估路由、交接、协作和效率。
- 不要迷信单次运行，要用 Trial 和 pass^k 看稳定性。
- 不要依赖单一评分器，要组合 Code-based、Model-based 和 Human Grader。
- 不要等样本很多才开始，20 个高质量案例就足以起步。

最终目标是让 multi-Agent 系统在真实环境里稳定工作，而不是在单次演示里偶然表现很好。
