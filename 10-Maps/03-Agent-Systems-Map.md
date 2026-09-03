# Agent 系统知识地图

> 目标：沉淀一份可持续维护、可导入 Notion、也能拆分成公众号文章的大模型 Agent 知识体系。

完整结构见：[知识体系总纲](./00-Master-Map.md)。

## 维护约定

- 原始材料先进入 `素材收集箱.md`，保留来源、日期和上下文。
- 主文档作为知识树总目录和专题索引，不承载过长正文。
- 每个大主题单独维护一个 Markdown 文件。
- 专题正文只能基于用户提供的内容进行校准和写入，不主动扩写外部资料。

## 知识树总览

1. 大模型基础
2. Context Engineering
3. Agent 核心范式
4. Agent 算法与推理
5. 工具调用与函数调用
6. RAG 与长期记忆
7. 多 Agent 协作
8. 评测、观测与调试
9. 后端工程
10. 前端与交互
11. 部署、成本与安全
12. 产品化与案例复盘

---

## 1. 大模型基础

### 1.1 Transformer 与注意力机制

待整理。

### 1.2 预训练、SFT、RLHF 与偏好优化

待整理。

### 1.3 Token、上下文窗口与推理成本

待整理。

### 1.4 Prompt Engineering 基础

待整理。

---

## 2. Context Engineering

专题文档：[Context Engineering](../20-Knowledge/04-context-engineering/Context-Engineering.md)

资源索引：[Context Engineering Resources](../90-Sources/source-notes/Context-Engineering-Resources.md)

---

## 3. Agent 核心范式

### 3.1 Agent 的定义

待整理。

### 3.2 ReAct：Reasoning + Acting

待整理。

### 3.3 Plan-and-Execute

待整理。

### 3.4 Reflection 与 Self-Improvement

待整理。

### 3.5 Memory-Augmented Agent

待整理。

---

## 4. Agent 算法与推理

### 4.1 Chain-of-Thought 与可控推理

待整理。

### 4.2 Tree of Thoughts / Graph of Thoughts

待整理。

### 4.3 任务分解与规划搜索

待整理。

### 4.4 工具选择策略

待整理。

### 4.5 失败恢复与重试策略

待整理。

---

## 5. 工具调用与函数调用

### 5.1 Function Calling

待整理。

### 5.2 Tool Schema 设计

待整理。

### 5.3 工具权限与沙箱

待整理。

### 5.4 MCP 与外部系统集成

待整理。

---

## 6. RAG 与长期记忆

### 6.1 RAG 基础流程

待整理。

### 6.2 Embedding 与向量数据库

待整理。

### 6.3 Chunking 策略

待整理。

### 6.4 Retrieval、Rerank 与 Context Packing

待整理。

### 6.5 记忆写入、更新与遗忘

待整理。

---

## 7. 多 Agent 协作

### 7.1 多 Agent 的适用场景

待整理。

### 7.2 Supervisor / Worker 架构

待整理。

### 7.3 Debate / Critic / Reviewer 模式

待整理。

### 7.4 任务队列与状态同步

待整理。

---

## 8. 评测、观测与调试

专题文档：[Evaluation](../20-Knowledge/10-evaluation-observability/Evaluation.md)

### 8.1 Agent 评测指标

待整理。

### 8.2 Trace、日志与可观测性

待整理。

### 8.3 Prompt 回归测试

待整理。

### 8.4 幻觉、越权与安全测试

待整理。

---

## 9. 后端工程

### 9.1 API 服务架构

待整理。

### 9.2 异步任务与队列

待整理。

### 9.3 数据库设计

待整理。

### 9.4 缓存与成本优化

待整理。

### 9.5 文件、知识库与对象存储

待整理。

---

## 10. 前端与交互

### 10.1 Chat UI

待整理。

### 10.2 工具调用过程展示

待整理。

### 10.3 多轮任务状态与进度反馈

待整理。

### 10.4 人机协同审批

待整理。

---

## 11. 部署、成本与安全

### 11.1 模型供应商与模型路由

待整理。

### 11.2 限流、重试与降级

待整理。

### 11.3 密钥管理与权限隔离

待整理。

### 11.4 成本监控

待整理。

---

## 12. 产品化与案例复盘

### 12.1 典型 Agent 产品形态

待整理。

### 12.2 从 Demo 到生产

待整理。

### 12.3 案例复盘模板

#### 背景

待整理。

#### 方案

待整理。

#### 效果

待整理。

#### 经验与坑

待整理。

---

## 待处理问题

- 哪些主题需要配图或流程图？
- 哪些内容适合拆成公众号系列？
- 哪些知识点需要代码示例？
