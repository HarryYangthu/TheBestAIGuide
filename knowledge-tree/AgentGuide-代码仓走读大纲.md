# AgentGuide 代码仓走读与内容大纲

> 仓库：[adongwanai/AgentGuide](https://github.com/adongwanai/AgentGuide)
> 走读快照：`main@d4fe53f4a9153123b159d0e6b632117a34721a92`
> 快照日期：2026-08-25；走读日期：2026-09-02
>
> 面向个人学习与内部培训的技术抽取版：[AI Agent 个人学习与内部培训知识库总纲](./AI-Agent-个人学习与内部培训知识库总纲.md)

## 一句话结论

`AgentGuide` 不是一个可直接运行的 Agent 框架，也不是某个 Agent 产品的完整源码。它本质上是一个以 Markdown 为主体、以求职和项目落地为导向的 AI Agent 知识库，并在外层配了三个静态站点：

1. 根站：资源检索与学习路线门户。
2. `Vibe Research`：AI 科研工作流专题站。
3. `InterviewGuide`：AI 算法面试题专题站。

仓库真正可运行的代码主要负责“内容索引、静态页面生成、前端筛选和部署”；`projects/` 下的 Paper Agent、Travel Agent、Web Agent 是设计蓝图，不是已经实现好的 Agent 程序。

---

## 一、仓库全景

### 1.1 产品定位

- 目标人群：AI Agent 算法工程师、开发工程师、RAG 工程师、大模型求职者和科研人员。
- 核心目标：把“理论学习 → 工程实践 → 评测验证 → 项目包装 → 面试求职”串成一条路径。
- 内容主线：Agent、Context Engineering、Memory、Tools/MCP、RAG、Evaluation、Safety、Post-training、Agentic RL。
- 组织特点：内容量大、覆盖面广、求职材料占比高，代码只是内容产品化的支撑层。

### 1.2 快照规模

| 指标 | 当前快照 |
| --- | ---: |
| 仓库文件 | 417 个 |
| Markdown | 135 个 |
| PDF 资料 | 58 个 |
| TypeScript | 33 个 |
| Astro 页面/组件 | 23 个 |
| MDX 科研章节 | 18 个 |
| 首页资源索引 | 124 项 |
| 面试专题题目 | 12,960 道 |
| 面试公司 | 28 家 |
| 面试分类 | 9 类 |
| 高频题 | 444 道 |
| Sitemap URL | 13,023 个 |

124 项首页资源由 121 个本地 Markdown 文件和 3 个手工策划入口组成。`examples/` 不进入首页资源索引。

### 1.3 内容分布

| 首页分类 | 数量 | 说明 |
| --- | ---: | --- |
| 面试求职 | 33 | 最大板块，含题库、面经、简历、HR、谈薪和专项 playbook |
| 资源合集 | 30 | Agent、RAG、多模态、论文、工具与 PDF 资料 |
| 技术栈 | 26 | Context、Memory、Harness、Eval、训练、安全等 |
| 理论 | 10 | Agent 原理、ReAct、评测及模型系列笔记 |
| 开源项目 | 8 | 7 篇项目目录文档 + 1 个外部项目入口 |
| 学习路线 | 6 | 算法、开发、求职、VLA 等路线 |
| 快速开始 | 5 | 学习地图、7 天计划、资源筛选、补洞地图 |
| 项目实战 | 4 | 项目落地、安全，以及两个占位主题 |
| 研究前沿 | 2 | 2026 研究方向与展开分析 |

这里的“已完善/建设中”和“入门/进阶/高阶”是生成脚本通过关键词和篇幅自动推断的标签，不等于人工内容审查结论。

---

## 二、代码与构建架构

```text
docs/*.md ───────────┐
resources/*.md ──────┼─> scripts/generate_resources.py
projects/*.md ───────┘       ├─> data/resources.json
                              └─> sitemap.xml
                                         │
index.html + assets/site.js <─────────────┘
        │
        └─> 根站：搜索 / 分类 / 难度 / 类型 / 排序 / 路线切换

external/ai-research-ebook/
  MDX + Astro components ──> Astro static build ──> /research/

外部汇总 Markdown（仓库未包含）
  └─> external/InterviewGuide/scripts/build-data.ts
        └─> questions / companies / categories / search-index / stats JSON
              └─> Astro static build ──> /interview/

三部分产物
  └─> .github/workflows/deploy-pages.yml
        └─> site-dist/ ──> GitHub Pages
```

### 2.1 根站：静态资源门户

关键文件：

- `index.html`：页面骨架、Hero、资源区、推荐区、路线区、两个专题站入口和 SEO 元数据。
- `assets/site.css`：全站样式、响应式布局、深浅色主题。
- `assets/site.js`：资源加载、搜索打分、筛选、排序、分页、URL 状态、主题和 GitHub 数据。
- `data/resources.json`：首页真正消费的数据源。

主调用链：

```text
DOMContentLoaded
  -> initResources()
  -> fetch('data/resources.json')
  -> 为每条资源构建 _searchText
  -> 从 URL 恢复 q/category/type/level/sort
  -> applyFilters()
  -> scoreResource() + sortResources()
  -> renderResults()
  -> resourceCard()
```

搜索实现不是向量检索，而是浏览器端字符串归一化和规则打分：

- 标题精确匹配、前缀匹配、包含匹配权重最高。
- 标签、分类、简介和全文索引字段依次降权。
- 对“智能体、求职、检索增强、记忆、强化学习、评估”等词做有限别名扩展。
- 筛选状态会同步到 URL，便于分享和刷新恢复。
- 每次先展示 8 项，点击后继续增量显示。
- GitHub Star/Fork 通过公开 API 获取，在 `localStorage` 缓存 1 小时。

注意：绝大多数资源卡最终跳转到 GitHub 上的 Markdown 文件。根站是“目录和检索门户”，不是完整 Markdown 文档渲染器。

### 2.2 内容索引生成器

`scripts/generate_resources.py` 扫描：

- `docs/**/*.md`
- `resources/**/*.md`
- `projects/**/*.md`

对每篇文档自动提取或推断：

- 标题：第一处 Markdown heading。
- 简介：第一段有效正文。
- 分类：由目录位置决定。
- 类型：题库、路线图、项目、原理教程、资源清单等。
- 难度：根据“入门、生产级、源码、评测、强化学习”等关键词推断。
- 标签：Agent、RAG、Context、Memory、MCP、Eval、安全、训练、多模态等规则匹配。
- 状态：根据占位关键词与篇幅推断“建设中/已完善”。
- 日期：优先读取文件最后一次 Git 提交日期。

输出两份派生数据：

1. `data/resources.json`：124 项首页资源索引。
2. `sitemap.xml`：根站、科研站、面试站共 13,023 个规范 URL。

生成器依赖完整 Git 历史才能稳定复现日期和排序；浅克隆会让大量文件日期退化为浅克隆边界提交日期。

### 2.3 Vibe Research 科研专题站

源码目录：`external/ai-research-ebook/`

技术栈：Astro 5 + Tailwind CSS + MDX + TypeScript，纯静态输出。

核心链路：

```text
src/content/docs/**/*.mdx
  -> Astro Content Collection + frontmatter schema
  -> [...slug].astro 静态路由
  -> DocsLayout
      ├─ Sidebar：按 category/order 分组
      ├─ Content：渲染 MDX
      ├─ TableOfContents：抽取 H2/H3
      └─ Prev/Next：上一篇/下一篇
```

站点共 18 个 MDX 章节，构建后生成 21 个页面。页面类别包括：

1. 导读。
2. Idea 生成。
3. 代码实现。
4. 论文图表。
5. 论文写作。
6. 审稿与 Rebuttal。
7. 工具生态。
8. 资料库。

`/skills` 页面只是 6 张科研 Skill 说明卡和示例命令，不包含对应 Skill 的真实实现。

### 2.4 InterviewGuide 面试专题站

源码目录：`external/InterviewGuide/`

技术栈：Astro 5 + Tailwind CSS + TypeScript + Vitest，纯静态输出。

#### 数据构建链

```text
knowledge_summary.md
  -> parseKnowledge()
company_summary.md
  -> parseCompany()
        -> filterAiScope()
        -> company/category 聚合
        -> questions.json
        -> companies.json
        -> categories.json
        -> search-index.json
        -> stats.json
```

当前仓库已经提交了生成后的 JSON，但默认依赖的两份上游汇总 Markdown 不在仓库中，因此“网站构建”可复现，“从原始面经重新生成全量数据”不可在本仓库内独立复现。

#### 页面路由

- `/`：题目、公司、分类、高频题统计和三种学习入口。
- `/companies/`：公司维度入口。
- `/companies/[company]/`：每家公司题目列表。
- `/categories/`：知识分类入口。
- `/categories/[category]/`：每类题目列表。
- `/hot/`：按频次排序，浏览器端按关键词、公司、分类筛选。
- `/questions/[id]/`：题目详情、变体、出现公司、收藏和完成状态。
- `/progress/`：本地学习进度面板。
- `/admin/`：生成结构化 GitHub Issue 的辅助表单。

12,960 道题会被展开为 12,960 个静态详情页。整个专题站构建后共 13,003 个 HTML 页面。

#### 状态与权限边界

- 收藏、完成状态和主题都只存于浏览器 `localStorage`，没有账号、云同步或后端数据库。
- `/admin/` 的默认口令直接写在前端，代码也明确称为“弱门禁”。它不提供服务端管理权限，只是解锁一个生成 GitHub Issue 链接的表单。
- 当前表单的 Issue 目标仍指向原始 `yiweinanzi/InterviewGuide` 仓库，而不是当前 `adongwanai/AgentGuide`。

### 2.5 CI、发布与在线健康检查

仓库有四条 GitHub Actions 流水线：

1. `ci.yml`：执行根站静态 smoke test 和两个专题站的集成断言。
2. `deploy-pages.yml`：安装两个 Astro 项目、分别构建，再合并到 `site-dist/` 发布 GitHub Pages。
3. `update-resources.yml`：重新生成 `resources.json` 和 `sitemap.xml`，有变化时自动提交。
4. `site-health.yml`：每 6 小时检查根站、数据文件、科研站、面试站和深层路由的 HTTP 状态码。

线上探测只验证 HTTP 状态码，不验证页面内容、交互和数据正确性。

---

## 三、按知识体系展开的大纲

### 3.1 快速入门与学习方法

1. Agent、Workflow、Multi-Agent、Computer-Use Agent 的边界。
2. Agent 的七个核心模块：Goal、State、Context、Tools、Loop、Guardrails、Eval。
3. 前 7 天学习计划：
   - 建立概念边界。
   - 手写最小 Agent Loop。
   - 设计工具 Schema 和错误协议。
   - 搭建 Context Builder。
   - 建 20 条 Eval Case。
   - 完成 README、Trace、评测报告。
   - 复盘并转成简历表达。
4. 高质量资源筛选：可运行、可验证、可追溯、能解释失败。
5. 仓库补洞地图与内容维护原则。

### 3.2 模型与 Agent 理论基础

1. AI Agent 定义与能力边界。
2. Agent 技术演进史。
3. Transformer 架构。
4. ReAct：Reasoning + Acting 循环。
5. Chain-of-Thought、规划、反思和搜索。
6. Agent Benchmark 与评测指标。
7. 模型系列深度笔记：
   - DeepSeek。
   - LLaMA。
   - Qwen。

### 3.3 Agent 工程技术栈

#### A. 框架与运行范式

1. LangChain/LangGraph。
2. Multi-Agent 框架。
3. AgentScope。
4. 12-Factor Agent 架构。
5. Parlant 合规型 Agent。
6. 从零构建 Agent Framework。

#### B. Context Engineering

1. System Prompt 与任务指令。
2. 用户输入与 Query Augmentation。
3. 短期状态和长对话压缩。
4. 长期记忆与外部存储。
5. Retrieval/RAG 注入。
6. 工具描述和工具结果压缩。
7. Structured Output。
8. 上下文中毒、干扰、混乱和冲突。
9. Offload、Retrieve、Reduce、Isolate。
10. Claude Code、Manus、Kiro 等工程案例。

#### C. Memory

1. Working/Short-term/Long-term Memory。
2. Episodic/Semantic/Procedural Memory。
3. 写入、检索、更新、冲突、淘汰和遗忘。
4. MemGPT、Mem0、Zep、HippoRAG。
5. 向量检索、知识图谱和多模态记忆。
6. Memory Eval 与可训练记忆策略。

#### D. Tools、协议与 Sandbox

1. Tool Schema、注册表和错误返回。
2. MCP 的 Client/Server 与权限边界。
3. Skills、A2A、ACP 等能力封装思路。
4. 浏览器和 Computer-Use 工具。
5. 权限确认、最小权限和审计。
6. Sandbox、超时、重试和资源限制。

#### E. RAG 与知识系统

1. 文档解析、OCR、版面、表格和公式。
2. Chunking、Embedding 和向量数据库。
3. Hybrid Retrieval 与 Rerank。
4. GraphRAG、Agentic RAG。
5. Multimodal RAG 与视觉文档检索。
6. 引用溯源、证据打包和幻觉控制。
7. RAG Eval、失败归因和高可用设计。

#### F. Evaluation、Observability 与 Safety

1. LLM Eval 与 Agent Eval 的区别。
2. 规则评分、人工评分、LLM-as-a-Judge。
3. Capability Eval 与 Regression Eval。
4. Dataset、Grader、Runner、Report、Replay。
5. Promptfoo、DeepEval、Inspect、RAGAS 等工具。
6. Trace、Replay、成本、延迟和稳定性指标。
7. Prompt Injection、Tool Abuse、Secret 和数据泄露。
8. Human-in-the-loop 和上线 Gate。

#### G. 训练与 Agentic RL

1. SFT、LoRA/QLoRA。
2. Reward Model、RLHF、RLAIF。
3. PPO、DPO、GRPO 及变体。
4. 轨迹数据和工具调用数据合成。
5. Reward/Verifier 与过程监督。
6. Credit Assignment、长程规划和 Memory RL。
7. 分布式训练、推理优化、MoE 和长上下文。
8. 多模态 Post-training 和 GUI Agent。

### 3.4 项目实践

#### A. 项目落地方法

1. 建立问题和用户边界。
2. 配置 AI 编程环境。
3. 建立项目理解 Skill。
4. 先写 Spec，再写代码。
5. 设计 Eval、归因和消融实验。
6. 补齐幂等、超时、重试、成本、权限和可观测性。
7. 输出 README、Demo、Trace、Eval Report 和简历表达。

#### B. 三个主项目蓝图

1. Paper Agent：
   - 学术检索。
   - PDF 解析。
   - Evidence Store。
   - 多论文对比。
   - 可追溯综述。
   - 引用准确率、覆盖率和幻觉率评测。
2. Travel Agent：
   - 偏好收集与约束标准化。
   - POI、路线、天气和预算工具。
   - 行程生成与解释。
   - 预订、付款等 Human-in-the-loop。
   - 约束满足、安全和不确定性评测。
3. Web Agent：
   - 浏览器状态观察。
   - Playwright 动作执行。
   - DOM、可访问性树和截图证据。
   - Planner、Executor、Verifier。
   - 恢复率、安全动作拦截和任务成功率评测。

#### C. 项目导航

1. Research/Report Agent。
2. Coding Agent。
3. Multi-Agent 与通用框架。
4. Graph/Workflow 型 Agent。
5. Web/Computer-Use Agent。
6. 文档与多模态 Agent。
7. Eval/Observability 项目。
8. Dify、n8n、Flowise、Coze 等低代码工作流。

### 3.5 学习路线

1. 2026 Agent 求职路线：从 Agent 边界到真实项目的 9 个 Stage。
2. 算法岗路线：模型、RAG、Memory、RL、实验和论文。
3. 开发岗路线：RAG、Tool Calling、性能、可观测性、部署和 Multi-Agent。
4. 前沿算法完整路线：环境、数学、模型、数据、训练、Agent、多模态、安全、Infra、Serving、研究与作品集。
5. 具身智能/VLA 路线：VLM、机器人、模仿学习、VLA、World Model、Sim2Real、训练部署和作品集。

### 3.6 面试与求职

#### A. 技术题库

1. LLM、VLM、RLHF 理论。
2. RAG 原理、检索、评测和工程实践。
3. Agent、Memory、Tool Use、框架和 Multi-Agent。
4. 编程实战、Transformer 手撕和 AI 算子。
5. 算法岗：创新、推导、实验设计和论文解读。
6. 开发岗：系统设计、工程实践、框架选型和业务落地。
7. 模型评测、未来趋势和开放讨论。
8. 12,960 道公司/分类/频次结构化题库。

#### B. Agent 专项 Playbook

1. Agent Harness。
2. Agent Evaluation。
3. Agent Memory。
4. Agent Skills/Procedural Memory。
5. Agentic RAG/Deep Research。
6. 数据合成。
7. Claude Code 源码解读。
8. OpenClaw 源码解读。
9. Hermes 自进化。
10. STAR 项目讲述。

#### C. 求职软技能

1. 算法岗与开发岗选择。
2. 转行与秋招策略。
3. 简历编写和项目讲述。
4. 公司面经案例。
5. HR 问题、谈薪和 Offer 判断。
6. 求职心态和个人品牌。

### 3.7 研究前沿

1. 长程任务与 Harness 工程：
   - 状态外置。
   - 稠密过程评分。
   - Context Compaction。
   - 子 Agent 隔离。
   - 失败恢复。
   - Harness 自进化。
   - Skills。
   - 长程评测集。
2. 自进化与 Fully Self-Training：
   - 经验内化。
   - 可训练记忆。
   - 脚手架自修改。
   - Agent/Environment 协同进化。
   - 持续学习和失败模式。
3. Agentic RL 与 Verifier：
   - Credit Assignment。
   - 环境合成。
   - 奖励与验证器。
   - 训练稳定性。
   - RL 基础设施。
4. 横向方向：Memory、Deep Research、多模态/Computer Use、安全、AI for Science。

### 3.8 Vibe Research 科研工作流

1. 调研方法和研究空白。
2. Claude/GPT/多 Agent 实验开发。
3. 架构图、流程图、结果图和视觉规范。
4. 论文论证链、Prism 和多模型协作写作。
5. 结构化审稿、会议模板和 Rebuttal。
6. 科研工具矩阵和从 Idea 到投稿的完整时间线。
7. 科研资料库与投稿参考。

### 3.9 资源导航

1. Agent 框架、官方指南、Memory、Benchmark 和 Harness。
2. RAG 项目、向量库、文档解析、GraphRAG 和 Agentic RAG。
3. 多模态 RAG 管线、工具和评测清单。
4. Agent Memory、Agent RL、数据合成等论文索引。
5. LLM 经典论文速读和 PDF 行业资料。
6. 开发工具、数据资源和推荐工作流。

---

## 四、建议阅读顺序

### 4.1 只想快速建立 Agent 全局认知

```text
docs/00-getting-started/01-agent-map.md
  -> docs/00-getting-started/02-first-7-days.md
  -> examples/minimal-agent-loop.md
  -> docs/02-tech-stack/27-agent-harness-engineering.md
```

### 4.2 偏 Agent 工程落地

```text
Agent Map
  -> 12-Factor Agent
  -> Context Engineering
  -> Memory
  -> MCP / Tools / Sandbox
  -> Agent Security
  -> Evaluation Harness
  -> Travel Agent 或 Web Agent 蓝图
  -> Ship Agent Project
```

### 4.3 偏算法与研究

```text
Transformer / ReAct / Planning
  -> RAG 与 Memory
  -> SFT / Post-training / Agentic RL
  -> Evaluation
  -> 2026 Research Frontiers
  -> Paper Agent 蓝图
  -> Vibe Research
```

### 4.4 偏求职冲刺

```text
目标岗位选择
  -> 对应算法岗/开发岗路线
  -> 一个项目蓝图
  -> Eval + 失败分析
  -> 技术题库
  -> 专项 Playbook
  -> 简历 + STAR + HR + 谈薪
```

---

## 五、当前完成度与边界

### 5.1 已形成闭环的部分

- 根站资源索引可生成、可检索、可筛选、可部署。
- 资源生成脚本在完整 Git 历史下可重复生成且工作区无差异。
- InterviewGuide 的测试、静态路由和页面生成链路完整。
- Vibe Research 的 MDX、导航、目录和静态构建链路完整。
- GitHub Pages 已组合发布三个站点，并有定时 URL 探测。
- 快速开始、Harness、Context、Memory、Eval、Post-training、面试和路线图已有较多正文。

### 5.2 仍是蓝图或占位的部分

当前资源索引自动识别出 13 篇“建设中”文档：

- Agent 技术演进史。
- Transformer 架构详解。
- Chain-of-Thought 与规划。
- AgentBench 详解。
- LangChain 框架指南。
- Multi-Agent 框架详解。
- AgentScope 入门。
- 向量数据库基础。
- RAG 全链路实战。
- Agent 强化学习。
- 从零构建 Agent 框架。
- 高可用 RAG 系统实战。
- 毕业设计选题指南。

此外，三个主 Agent 项目只有架构、工具、评测和里程碑设计，没有对应实现代码、依赖文件、运行入口或真实评测结果。

### 5.3 结构和维护风险

1. **内容分布不均**：面试求职约占自动统计文本单元的一半，项目实战正文相对薄弱。
2. **部分总览已过时**：`PROJECT_SUMMARY.md` 仍停留在 2025-11-03，文档数、路径、Star/Fork 和后续计划都不再代表当前仓库。
3. **补洞地图有滞后**：其中若干“仍待补”的文件后来已补正文，但地图没有同步更新。
4. **题库原始数据缺失**：InterviewGuide 能从已提交 JSON 构建，却不能仅靠本仓库重跑原始数据汇总。
5. **科研站有 npm 可移植性差异**：npm 10 会安装 Astro/Vite 的 optional peer `@types/node` 并正常构建；npm 11 下该类型可能缺失，导致 `process.env` 类型检查失败。应显式声明 `@types/node`。
6. **源码与历史产物重复**：根目录 `research/` 是受版本控制的旧构建产物；正式部署实际从 `external/ai-research-ebook/` 重建并复制。
7. **许可证入口断裂**：FAQ 链接到根目录 `LICENSE`，但根 `.gitignore` 明确忽略该文件，当前仓库没有根许可证文件。学习使用说明不能替代清晰的软件/内容许可证。
8. **管理入口不是认证系统**：前端硬编码口令只能隐藏表单，不能承担真正权限控制。

---

## 六、验证记录

本次走读在临时完整历史克隆上执行：

| 验证项 | 结果 |
| --- | --- |
| 根站静态 smoke test | 通过 |
| 两个专题站集成断言 | 通过 |
| 资源索引重新生成 | 124 项；与仓库提交内容一致 |
| Sitemap 重新生成 | 13,023 URL；与仓库提交内容一致 |
| InterviewGuide Vitest | 17 个测试文件、32 个测试通过 |
| InterviewGuide 构建 | 13,003 页面成功生成 |
| Vibe Research 构建（npm 10） | 21 页面成功生成 |
| Vibe Research 构建（npm 11） | 因缺少 `@types/node` 失败 |
| 当前 Pages 部署工作流 | 同一提交成功 |
| 当前定时站点健康检查 | 成功 |
| 6 个关键线上 URL | 全部返回 HTTP 200 |

线上 HTTP 200 和工作流成功只证明页面可达及构建成功，不证明所有内容准确、所有交互正确或 12,960 道题经过逐条事实审校。

---

## 七、关键文件索引

| 文件/目录 | 作用 |
| --- | --- |
| `README.md` | 项目定位、六步学习与求职总入口 |
| `index.html` | 根静态门户入口 |
| `assets/site.js` | 根站搜索、筛选、排序、主题和 GitHub 数据 |
| `scripts/generate_resources.py` | Markdown 到资源索引和 Sitemap 的生成器 |
| `data/resources.json` | 根站资源目录数据 |
| `docs/00-getting-started/` | 新手入口和 7 天计划 |
| `docs/01-theory/` | Agent 与模型理论 |
| `docs/02-tech-stack/` | Context、Memory、Harness、Eval、训练等核心技术 |
| `docs/03-practice/` | 项目落地、安全和实践主题 |
| `docs/04-interview/` | 面试题、专项 Playbook 和求职材料 |
| `docs/05-roadmaps/` | 算法、开发、求职和 VLA 学习路线 |
| `docs/06-research-frontiers/` | 2026 研究方向专题 |
| `examples/` | Loop、Tool Card、Trace、Eval 和 README 模板 |
| `projects/` | 三个项目蓝图和项目导航 |
| `resources/` | Agent/RAG/多模态/论文/PDF 资源库 |
| `external/ai-research-ebook/` | Vibe Research Astro 源码 |
| `external/InterviewGuide/` | InterviewGuide Astro 源码与题库 JSON |
| `.github/workflows/` | CI、索引更新、Pages 发布和线上健康检查 |

---

## 八、把整个仓库压缩成一条主线

```text
模型基础
  -> Agent Loop
  -> Context + Memory + Tools
  -> Harness + State + Permission
  -> RAG + Multi-Agent + Browser/Computer Use
  -> Trace + Eval + Safety
  -> Paper / Travel / Web Agent 项目
  -> README + Demo + 评测报告 + 失败分析
  -> 简历、系统设计与面试表达
```

这条主线是仓库最值得保留的骨架。其他大量论文、框架、面经和工具清单，都可以挂在这条骨架上理解，而不必按仓库文件顺序逐篇阅读。
