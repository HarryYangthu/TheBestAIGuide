# TheBestAIGuide

面向学习和工程实践的 AI 知识库。当前主线按 Agent 的 12 个核心组件与 3 个增强能力组织，从模型调用开始，逐步写出可以运行、观察和检查结果的系统。

## 从这里开始

| 你的目标 | 阅读入口 | 动手做什么 |
|---|---|---|
| 看清各组件怎样协作 | [Agent 组件总览](10-Knowledge/README.md) | 对照总览图找到任务、模型、循环、工具和验收的位置 |
| 从零写出执行循环 | [03：Agent 执行循环](10-Knowledge/03-agent-loop/README.md) | 真实 API 调用 → 读取笔记 → 修复函数 → 检查结果与运行报告 |
| 按顺序补齐组件 | [连续学习路线](00-Home/Learning-Paths.md) | 按一次任务的执行过程逐步加入组件 |
| 完成综合任务 | [项目 00：Mini Agent](20-Projects/00-mini-agent/README.md) | 生成升级清单，对照参考报告验收 |
| 验证检索与回答 | [项目 01：RAG 实验室](20-Projects/01-rag-lab/README.md) | 检索、图表对比、逐题证据复盘 |
| 查询原来的知识领域 | [旧知识库归档](10-Knowledge/_archive/README.md) | 阅读 AI 基础、模型、RAG、评测等已有材料 |

## 先运行一个本地输入检查

在仓库根目录执行：

```bash
cd 10-Knowledge/03-agent-loop
python code/inspect_input.py
```

程序读取目录中实际存在的 `notes.txt`，打印笔记正文，并保存 `runs/input-preview.txt`。随后按[章节配置说明](10-Knowledge/03-agent-loop/README.md#三个配置项决定真实模型的调用目标)填写 URL、API Key 和模型名，依次运行 v0—v4。

每次模型运行都会保存请求、响应、消息历史、修改差异与 `report.md`。15 个组件均提供分章正文、配套代码与实验。各章 README 列出输入文件、执行命令和结果位置。

## 仓库目录

| 目录 | 内容 |
|---|---|
| [00-Home](00-Home/README.md) | 学习路线、组件地图、写作规范和维护记录 |
| [10-Knowledge](10-Knowledge/README.md) | 12 个核心组件与 3 个增强能力的章节 |
| [10-Knowledge/_archive](10-Knowledge/_archive/README.md) | 原 16 个知识领域、配套实现和历史实验 |
| [20-Projects](20-Projects/README.md) | 跨组件的综合项目 |
| [90-Sources](90-Sources/README.md) | 论文、教材、官方文档、协议与数据来源 |
| [99-Inbox](99-Inbox/README.md) | 待消化材料 |
| [assets](assets/README.md) | 共享图像与来源记录 |
| [scripts](scripts/README.md) | 链接、元数据、Notebook 和测试工具 |

阅读要求见[学习型写作规范](00-Home/Learning-Writing-Guide.md)，当前进展见[建设状态](00-Home/Knowledge-Status.md)。
