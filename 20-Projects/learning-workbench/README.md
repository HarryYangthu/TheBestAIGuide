# 学习工作台：把知识点接成可运行任务

这个项目补上“理解机制之后，怎样把它跑起来”的一段路。默认路径用本地数据和明确规则检查系统行为；可选路径接入真实模型，记录回答、工具动作、token 用量和失败。两类结果分开保存。

建议先运行记忆和审批服务，再读生成式 RAG，最后做模型评测与多源研究。命令均从**仓库根目录**执行。

## 安装与第一个任务

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.lock
python scripts/run_python.py -m learning_workbench.cli memory --output .runs/memory
python scripts/run_python.py -m learning_workbench.server --port 8765
```

打开 `http://127.0.0.1:8765`，创建任务 → 等待批准 → 批准 → 查看结果与事件。默认演示身份 `demo-alice` 属于 alpha 租户，`demo-bob` 属于 beta。它们是固定教学身份，不是真实账号系统。服务只监听本机。

可选的模型/PDF实验：

```bash
pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements-learning.txt
```

直接依赖固定版本，但此文件不是完整传递依赖锁。下载模型需要网络和磁盘；默认服务、记忆、规划和队列不下载模型。

## 项目地图

| 任务 | 入口源码 | 输入与输出 | 应观察什么 |
| --- | --- | --- | --- |
| 两工具 Agent | [cli.py](src/learning_workbench/cli.py)、[providers.py](src/learning_workbench/providers.py) | 12 个固定任务 → 动作、结果、用量、trace | 搜索与加法是否选对；完成状态和答案正确分开 |
| 检索与生成 | [retrieval.py](src/learning_workbench/retrieval.py) | 语料与问题 → 候选、引用、主张/拒答 | 召回、引用真实性、语义支持分开 |
| 结构文档 | [documents.py](src/learning_workbench/documents.py) | Markdown/PDF → 带来源片段 | 表格不拆坏；父段落保留前提 |
| 跨会话记忆 | [memory.py](src/learning_workbench/memory.py) | 8 个多事件任务 → 下一次回答 | 当前指令覆盖旧偏好，主体与 TTL 生效 |
| 动态规划 | [planning.py](src/learning_workbench/planning.py) | DAG 与证据更新 → 局部重算 trace | A 更新后只重跑 A 及后继，B 不重跑 |
| Run 服务 | [server.py](src/learning_workbench/server.py) | HTTP 请求 → SQLite 状态与 SSE | 审批、取消、版本冲突、事件游标、隔离 |
| A2A 交接 | [a2a_demo.py](src/learning_workbench/a2a_demo.py) | 两个本地端点 → task/artifact | 补输入、查询、取消、重复消息 |
| 上下文/统计/负载 | [experiments.py](src/learning_workbench/experiments.py) | 固定案例 → 指标与反例 | 机制检查与模型能力区别 |
| 修复/媒体/科研 | [practice.py](src/learning_workbench/practice.py) | 原始文件或数据 → 补丁、页码、训练报告 | 保留失败基线；每个数值能回溯 |
| 文献比较 | [research.py](src/learning_workbench/research.py) | 两篇固定论文 PDF → 证据表与审阅 | 资料缺失就停；不比较不同条件的指标 |
| Judge/注入 | [model_evaluation.py](src/learning_workbench/model_evaluation.py) | 真实模型 → 候选与判定 | 模型受诱导与非法效果执行是两项指标 |

所有独立工程的统一入口见 [Projects 总表](../README.md)。

## 1. 模型如何接入 Agent Loop

适配器收到当前任务和工具观察，要求模型返回“调用工具”或“结束回答”的 JSON。Runtime 执行工具后把结果写进 State，模型再作下一次决策。JSON 解析失败算失败，不靠猜测补成合法动作。

```bash
python scripts/run_python.py -m learning_workbench.cli agent --one-tool --provider local \
  --model Qwen/Qwen2.5-0.5B-Instruct \
  --revision 7ae557604adf67be50417f59c2c2f167def9a775 --output .runs/agent-01
```

`--one-tool` 是受限工作流：模型选工具，工具成功后由宿主进入回答阶段。去掉它才是模型自由决定是否继续调用的循环。两者不是同一个能力指标。第一版自由循环全部动作契约失败，格式示例版又暴露重复调用；原始报告均保留，受限流程结果见 `artifacts/real-models/bounded-agent/agent.json`。

不传 `--provider` 可运行同一 12 题的确定性基线；它只识别加法与本地风扇资料任务，不是假模型。

每次换新的输出目录，避免覆盖已有 trace。输出包含 12 个任务的真实结果；任务数据在 [agent-tasks.jsonl](fixtures/agent-tasks.jsonl)，不等于单元测试。

远端路径配置 `AI_GUIDE_BASE_URL`、`AI_GUIDE_MODEL`、`AI_GUIDE_API_KEY`，再改用 `--provider api`。Base URL 指向兼容 Chat Completions 的 API 根目录，适配器拼接 `/chat/completions`。密钥由环境提供，不能放进 Notebook、trace 或仓库。

本地模型已实际运行；远端 API 本轮只通过本机 HTTP 传输契约测试，未消耗真实 API 额度。每次调用有时间、输入/输出 token；本地下载模型没有 API 账单，但会用 CPU 和内存。`token_budget` 是根据已返回用量检查的软预算，最后一次调用可能越界；严格预算应在发送前用对应 tokenizer 预估，并预留输出。缺失 usage 不能当成已知零费用。

## 2. 检索、生成和证据支持不能混为一谈

BM25 依赖词项；Dense 把 query/document 编码为向量；Hybrid 用排名融合；Cross-Encoder 把 query 与候选共同编码后打分。模型适配器分别调用 query/document 编码入口，避免把有不同任务前缀的模型误当成对称编码器。

```bash
python scripts/run_python.py -m learning_workbench.cli retrieval \
  --embedding sentence-transformers/paraphrase-MiniLM-L3-v2 \
  --embedding-revision 4ca70771034acceecb2e72475f72050fcdde4ddc \
  --reranker cross-encoder/ms-marco-MiniLM-L6-v2 \
  --reranker-revision 233902d25c440f23af6f7d6e94d2946bac0bee0a --output .runs/retrieval
python scripts/run_python.py -m learning_workbench.cli rag --provider local \
  --model Qwen/Qwen2.5-0.5B-Instruct \
  --revision 7ae557604adf67be50417f59c2c2f167def9a775 --output .runs/rag
```

[retrieval.json](artifacts/real-models/retrieval.json)保存同一 6 题的 4 种检索模式，共 24 次结果；小型英文构造集不能证明中文业务效果。Recall@k 衡量相关片段是否找全，MRR 看首个相关结果的位置。重排只重排候选，无法找回完全没召回的证据。

生成答案后做三层判断：

| 层次 | 本项目如何检查 | 不能据此声称什么 |
| --- | --- | --- |
| 引用可定位 | source_id 存在；quote 是该片段原文子串 | 引文一定支持主张 |
| 主张与条件受支持 | 固定题目的独立阅读标签；保留待审状态 | 模型自评就等于可靠判定 |
| 回答了问题 | 检查题目目标、版本、单位、前提与拒答 | 有引用或 JSON 合法就算正确 |

[真实生成结果](artifacts/real-models/generation.json)有意保留失败：小模型可能返回不完整 JSON，也可能抄对引文却写错主张。[逐题审阅](artifacts/real-models/generation-review.json)与原始输出分开。需要上线的系统必须对这些失败继续处理；这个适配器交付了完整实验链路，没有承诺该小模型足以服务用户。

`compare_versions` 分别检索两个版本；任何一侧没有证据就不能比较。结构化 Markdown 解析保留表格和代码块的原文偏移，父段落回读可补上“先断电”等条件。它是本仓受限格式解析器，不是完整 CommonMark AST。

## 3. 从一句话到下一次会话的记忆

示例只处理明确、长期、关于自己的格式偏好：“我以后希望用表格”。“这次用表格”和第三人的偏好不写入。数据经过提取、主体绑定、版本写入、召回，再进入回答上下文。

```bash
python scripts/run_python.py -m learning_workbench.cli memory --output .runs/memory
python scripts/run_python.py -m learning_workbench.cli multi --output .runs/planning
```

[记忆结果](artifacts/offline/memory.json)同时列无记忆和有记忆输出，覆盖长期/临时、当前覆盖、他人、过期、删除。回答内容是固定的 State/Memory 概念解释，格式由规则决定，不能称为通用对话模型。规则的好处是能把“写错记忆”和“模型没遵循格式”两个问题先拆开。

[规划 trace](artifacts/offline/planning.json)记录每个角色输入输出和更新后的失效范围。这个版本使用规则角色；真实模型角色比较见文献任务。

## 4. 从任务状态到浏览器

```bash
python scripts/run_python.py -m learning_workbench.server --port 8765 --directory .runs/service
```

API：`POST /runs` 创建，`GET /runs/{id}` 查询，`GET /runs/{id}/events` 接收 SSE，`POST /runs/{id}/approve` 或 `/cancel` 提交当前 `version`。游标用 `Last-Event-ID`；服务保存事件，重连只补后续事件。SSE 每次最多保持 5 秒，客户端可重连。

批准和状态更新在一个数据库事务里；旧版本操作返回 409。租户由演示凭据决定，请求参数不能改变它。进程恢复会重排未完成任务；工作采用每个 run 的隔离目录。取消是协作式的：已开始的只读工作可能继续计算，但不能再把任务发布为完成。

加 `--provider api` 或 `--provider local --model ... --revision ...` 可在同一服务调用模型生成；模型契约失败把任务记为失败，不伪造成功。多个 worker 共享本地模型时通过锁串行调用，防止把并发请求误算成模型并行吞吐。

这不是生产网关：没有真实用户登录、跨实例队列和分布式事务。逐步将它们加入之前，先看[服务测试](tests/test_workbench.py)中的恢复、跨租户与审批用例。

## 5. 进阶任务的实际入口

```bash
python scripts/run_python.py -m learning_workbench.a2a_demo
python scripts/run_python.py -m learning_workbench.practice repair --output .runs/repair
python scripts/run_python.py -m learning_workbench.practice media --output .runs/media
python scripts/run_python.py -m learning_workbench.practice science --output .runs/science
python scripts/run_python.py -m learning_workbench.research \
  --papers .runs/papers --fetch --output .runs/research
```

A2A 固定为 [0.3.0](https://a2a-protocol.org/v0.3.0/specification/) 的本地 text/JSON-RPC 子集。两个端点会交换真实 HTTP 消息，支持任务查询、补充输入、取消和产物。去重由本项目以 `messageId` 实现；任务只存内存，未声称完整协议一致性或生产认证。

代码修复任务新建临时 Git 仓库，读入有错的价格函数，先跑出失败，再检查原文件哈希、应用补丁、重新测试、输出 diff。策略固定，目的是验证修复闭环。临时目录不是任意模型生成代码的安全沙箱。

媒体任务生成本仓原创 PDF，再用 pypdf 提取文字和页面坐标。坐标是 PDF 左下角原点的**文字起点**，不是伪造的精确 bbox。第三页没有文字，明确标记需要 OCR。错型号、错单位拒答。附带 WER 对齐算例使用人工转写，尚未实现音频识别；PDF 页面解析是本轮交付的媒体主路径。

科研任务实际运行线性模型梯度下降，固定训练/验证划分，比较训练均值基线和线性候选。配置、数据、训练日志、验证 MSE 与数据哈希分别保存。只能支持“这次构造数据上”的结论。

## 6. 多源文献和模型评测

文献任务下载固定版本的 Transformer 与 LoRA 论文，提取关键词附近的短引文、页码与 PDF 哈希。问题限定为“架构和适配解决的是不是同一个问题”，不拿不同任务/硬件的论文指标作排名。完整 PDF 存在运行目录，不再分发进 Git。

默认比较使用已标明的作者阅读笔记；关键词命中不自动生成语义结论。加 `--provider local --model ... --revision ...` 可运行 reader/writer 模型角色，分别记录单流程与角色分工的调用、错误和引用。[实际模型记录](artifacts/real-models/research-multi.json)保留每个角色输入输出。固定拆解和自动定位审阅不等于开放式自主科研。

Judge 的 [6 个标签](fixtures/judge-tasks.jsonl)覆盖数值、单位、否定、证据不足；[位置交换案例](fixtures/pairwise-tasks.jsonl)让 A/B 顺序对调。标签是作者编写的教学参考，不是专家标注集。注入实验把真实外部文本交给模型，再送入独立策略，分别记录离题提案和非法效果。

[8 类 Context 故障索引](fixtures/context-faults.jsonl)指向相应运行证据。完整消息按真实聊天模板计数；默认无模型演示明确以字节计数。位置探针只运行 3 个构造提示，不能据此宣布解决 Context Rot。

统计实验按 Task 抽样：同一道题的多个 Trial 往往相关，打散后当独立样本会让区间过窄。队列实验真的运行 asyncio workers；相同到达流对比无限队列与有界队列，记录等待、p95、拒绝和重试。用 sleep 模拟服务时间，因此不代表真实模型吞吐。

下面的入口可以重跑评分、上下文和负载实验；真实模型任务再加上与上面相同的 `--provider local --model ... --revision ...`：

```bash
python scripts/run_python.py -m learning_workbench.cli stats --output .runs/stats
python scripts/run_python.py -m learning_workbench.cli queue --output .runs/queue
python scripts/run_python.py -m learning_workbench.cli context --output .runs/context
python scripts/run_python.py -m learning_workbench.cli judge --output .runs/judge-baseline
# pairwise、injection、tokenizer 需要真实模型配置，不会自动替换成假输出。
```

## 7. Skill 与复现

教学 Skill 位于 `skills/evidence-comparison/`。将整个目录放入宿主支持的技能目录，或让宿主显式读取其中的 `SKILL.md`；具体自动发现路径由宿主决定。本项目没有改动你的全局技能配置。

四类案例包括应触发、不触发、条件不可比和缺少资料。脚本能重放带数据案例并生成比较表；[结果](artifacts/offline/skill-cases.json)标明路由期望尚不是宿主自动选择的实测。

```bash
python scripts/run_python.py -m unittest discover -s 20-Projects/learning-workbench/tests -v
```

本轮环境、结果汇总与限制见[补齐记录](../../00-Home/Round2-Completion.md)。知识正文与项目入口相互链接；先理解机制，再运行结果，最后修改一个条件观察失败，是建议的学习顺序。

网页流程验收：安装原浏览器工程的 Playwright 和 Chromium 后，在根目录执行 `node scripts/check_workbench_browser.cjs`。它启动本地服务并实际点击审批/取消，不依赖人工填写运行结果。

本工程通过仓库根目录的 `scripts/run_python.py` 复用多个领域源码；目前不作为脱离仓库的独立 PyPI wheel 分发。
