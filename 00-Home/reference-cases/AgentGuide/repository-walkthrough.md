# AgentGuide 仓库走读

> 状态：reviewed（仓库结构与构建事实）；内容质量仍需逐篇核验
> 源仓库：[adongwanai/AgentGuide](https://github.com/adongwanai/AgentGuide)
> 走读快照：`main@d4fe53f4a9153123b159d0e6b632117a34721a92`
> 完整走读：2026-09-02；远端 HEAD 复核：2026-09-03

## 结论

`AgentGuide` 的主体是 Markdown 知识与资源索引，不是一个可直接运行的 Agent 框架。它的可运行代码主要服务于内容生成、静态站点、浏览器端检索和部署；`projects/` 中的 Agent 项目主要是设计蓝图。

对本知识库最有价值的不是照搬其目录，而是借鉴三件事：

1. 用一条技术主线组织大量分散主题。
2. 把源内容、派生索引和静态展示分开。
3. 用自动生成和 CI 检查减少目录与内容漂移。

求职、面试、简历与谈薪内容不进入本知识库主线，本文也不再复述这些材料。

## 仓库是什么

源仓库由三个内容产品组成：

| 部分 | 作用 | 主要技术 |
| --- | --- | --- |
| 根站 | 汇总 Markdown 资源，提供搜索、筛选和学习入口 | HTML、CSS、浏览器端 JavaScript、Python 生成脚本 |
| Vibe Research | AI 科研工作流专题站 | Astro、MDX、TypeScript |
| InterviewGuide | 面试题专题站 | Astro、TypeScript、Vitest、预生成 JSON |

这一区分很重要：仓库拥有“知识站点代码”，不等于拥有“Agent 运行时实现”。判断一个仓库是否包含可运行 Agent，至少要找到模型调用、循环控制、工具执行、状态管理、依赖和运行入口。

## 内容与代码的主链路

```text
docs / resources / projects 中的 Markdown
                  │
                  ▼
       scripts/generate_resources.py
          ├─> data/resources.json
          └─> sitemap.xml
                  │
                  ▼
       index.html + assets/site.js
                  │
                  ▼
        搜索、筛选、排序与导航

external/ai-research-ebook/ ──> Astro 静态构建 ──> /research/
external/InterviewGuide/    ──> Astro 静态构建 ──> /interview/

三部分构建产物 ──> GitHub Pages 工作流 ──> site-dist/
```

### 根站

`scripts/generate_resources.py` 扫描指定 Markdown 目录，从标题、正文和路径中提取或推断资源元数据，再生成前端消费的 JSON 和 Sitemap。浏览器端搜索属于字符串匹配与规则打分，不是向量检索。

可以借鉴的点：

- 内容文件是事实源，索引文件是可再生派生物。
- 搜索状态写入 URL，刷新和分享后仍可恢复。
- 标签与难度可以辅助导航，但自动推断结果不能等同于人工审查。
- 使用 Git 日期作为内容日期时，应说明浅克隆会改变可复现性。

### Vibe Research

科研专题站使用 Astro Content Collections 管理 MDX，通过动态静态路由生成章节页面，并在布局层统一处理侧栏、目录和前后章节。

可借鉴模式：

```text
内容集合 + 元数据 Schema
        ↓
统一路由与布局
        ↓
侧栏 / 目录 / 前后导航
```

这是把 Markdown 知识库升级为网站时值得保留的结构，但当前 TheBestAIGuide 仍优先维护 Markdown 本体，不急于引入站点框架。

### InterviewGuide

该部分只作为源仓结构事实保留：它展示了“大规模结构化数据 → 静态页面”的构建方式。由于相关主题不在本知识库范围内，不继续整理其题库内容和学习路径。

其中一项通用工程教训是：提交生成后的 JSON 只能让网站继续构建；如果原始汇总数据未入仓，就不能从源数据独立重建全量派生数据。

## 可提炼的技术大纲

去除岗位与面试内容后，源仓技术主线可压缩为：

```text
模型与推理基础
  -> Agent Loop
  -> Context + Memory + Tools
  -> Harness + State + Permission
  -> RAG + Workflow + Multi-Agent
  -> Trace + Evaluation + Safety
  -> 领域项目与失败复盘
```

映射到本知识库：

| 源仓主题 | 本知识库入口 | 处理方式 |
| --- | --- | --- |
| Agent 原理与 ReAct | [Agent Core](../../../10-Knowledge/03-agent-core/README.md) | 保留技术概念，待独立成文 |
| Context Engineering | [Context Engineering](../../../10-Knowledge/04-context-engineering/README.md) | 已重构为短专题 |
| Tool、MCP、Sandbox | [Tools 与协议](../../../10-Knowledge/05-tools-skills-protocols/README.md) | 保留，待补协议与安全边界 |
| RAG 与知识系统 | [RAG](../../../10-Knowledge/06-rag-and-knowledge-systems/README.md) | 已提炼流程和混合检索 |
| State 与 Memory | [State 与 Memory](../../../10-Knowledge/07-state-and-memory/README.md) | 先区分当前权威状态、Checkpoint 和长期记忆 |
| Workflow 与 Multi-Agent | [Planning 与 Multi-Agent](../../../10-Knowledge/08-planning-workflow-multi-agent/README.md) | 保留系统设计，不默认多 Agent |
| Runtime 与 Harness | [Runtime 与 Harness](../../../10-Knowledge/09-runtime-harness-environment/README.md) | 补齐恢复、幂等和环境 |
| Evaluation 与 Trace | [Evaluation](../../../10-Knowledge/10-evaluation-observability/README.md) | 已按评测对象拆分 |
| Safety 与权限 | [Safety](../../../10-Knowledge/11-safety-security-governance/README.md) | 待补威胁模型和治理 |
| 项目蓝图 | [Cases](../../README.md) | 只当设计输入，不当运行证据 |

## 最值得复用的仓库模式

### 1. 内容本体与展示层解耦

Markdown 可继续作为可审阅、可迁移的事实源；网站、搜索索引和 Sitemap 应尽量由脚本生成。这样可以更换展示技术而不迁移全部知识。

### 2. 地图负责导航，正文负责结论

大纲不应重复长篇解释。一个概念只保留一份正式定义，地图、案例和模式通过链接复用。

### 3. 案例必须标注证据等级

项目设计、代码骨架、构建成功、线上可达和实际业务效果是不同证据层。本知识库采用 `seed → draft → reviewed → verified` 状态，避免把“有文件”误认为“已实现”。

### 4. 自动化检查目录漂移

源仓中存在总览滞后、构建产物重复和自动标签误判等风险。知识库后续应自动检查：

- Markdown 内部链接；
- 状态字段与目录索引；
- Notebook 格式和执行状态；
- 生成文件是否与内容源一致；
- 许可证与外部资产来源。

## 快照事实与验证边界

以下结果来自 2026-09-02 对固定提交的完整历史克隆；2026-09-03 仅复核远端 `main` 仍指向同一提交，没有重新执行全部测试。

| 项目 | 固定快照结果 |
| --- | --- |
| 仓库文件 | 417 个 |
| Markdown | 135 个 |
| 根站资源索引 | 124 项 |
| 根站索引与 Sitemap 重生成 | 与提交内容一致 |
| InterviewGuide 测试 | 17 个测试文件、32 个测试通过 |
| InterviewGuide 静态构建 | 13,003 个页面 |
| Vibe Research 静态构建 | npm 10 下生成 21 个页面；npm 11 下因缺少显式 `@types/node` 失败 |
| 关键线上 URL | 当时返回 HTTP 200 |

这些结果只证明固定提交下的构建与可达性，不证明内容逐篇准确、所有交互正确，也不证明 `projects/` 中的 Agent 已实现。

## 源仓风险清单

- 内容分布不均，技术正文和非技术材料混在同一导航体系。
- 部分总览、补洞地图和实际文件状态存在漂移。
- 自动推断的“难度”和“已完善”标签缺少人工审查语义。
- InterviewGuide 缺少部分原始汇总数据，派生 JSON 可用但源数据链不完整。
- 构建依赖对 npm 版本敏感，隐式 peer dependency 影响可移植性。
- 旧构建产物与源码并存，增加漂移风险。
- 根许可证入口断裂，内容与代码复用边界不够清楚。
- 前端硬编码口令只能隐藏界面，不能作为认证或授权机制。

## 走读方法

以后分析同类知识仓库时，按以下顺序可减少误判：

1. 固定提交、日期和分支。
2. 识别事实源、派生数据和构建产物。
3. 画出内容生成、页面构建和部署链路。
4. 分开检查“文档项目”和“运行系统”。
5. 对测试、构建、可达性和业务效果分别记录证据。
6. 提炼通用知识，删除与自身范围无关的内容。
7. 把未核验结论写入待办，不直接提升为正式知识。

## 关键文件索引

| 文件或目录 | 作用 |
| --- | --- |
| `README.md` | 源仓入口与总体定位 |
| `scripts/generate_resources.py` | Markdown 到资源 JSON、Sitemap 的生成器 |
| `data/resources.json` | 根站消费的派生资源索引 |
| `index.html`、`assets/site.js` | 根站页面与浏览器端检索逻辑 |
| `docs/` | 技术、实践、路线与其他正文 |
| `projects/` | Agent 项目设计蓝图 |
| `examples/` | Loop、Tool Card、Trace、Eval 等模板 |
| `external/ai-research-ebook/` | 科研专题站源码 |
| `external/InterviewGuide/` | 题库站源码与派生数据 |
| `.github/workflows/` | 索引更新、测试、部署和健康检查 |

## 本知识库的取舍

从源仓吸收的是技术骨架、内容工程方法和可验证的构建观察；不复制大段原文，不继承求职导向，也不把项目蓝图包装成完成项目。后续新增内容应优先连接到 [知识体系总纲](../../Knowledge-Map.md)，再根据需要落到 Knowledge、Patterns、Cases、Labs 或 Code。
