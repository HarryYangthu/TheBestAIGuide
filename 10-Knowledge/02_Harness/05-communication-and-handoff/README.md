# 05｜通信与交接

[组件总览](../README.md) · [上一组件：编排与调度](../04-orchestration-and-scheduling/README.md) · [下一组件：上下文管理](../06-context-management/README.md)

本章总览图如下：

```mermaid
flowchart TD
    A["协调者委派库存检查"] --> B["执行者读取库存"]
    B --> C{"返回结果或失败"}
    C -->|失败且可重试| A
    C -->|结果| D["检查关联、版本和证据"]
    D --> E["接手方确认交接"]
    E --> F["新负责人生成处理草稿"]
```

示例订单需要 3 支笔，库存为 2 支。产物是一份等待客户确认的分批发货草稿。代码只读取库存并生成本地草稿，执行者为确定性函数，消息由进程内 JSON 队列传递。

## 阅读顺序

| 顺序 | 主要内容 | 完整入口 |
|---|---|---|
| 01 | [任务委派与消息协议](01-delegation-and-results.md)：函数返回值、请求与回执 | [v1_delegate.py](code/v1_delegate.py)、[v2_messages.py](code/v2_messages.py) |
| 02 | [消息重试与结果合并](02-retries-and-late-messages.md)：消息身份、执行尝试、输入版本与结果清单 | [protocol.py](code/protocol.py)、[experiments.py](code/experiments.py) |
| 03 | [控制权交接](03-context-and-ownership.md)：上下文包、接手确认与负责人校验 | [v3_handoff.py](code/v3_handoff.py) |
| 04 | [通信实验与队列源码](04-experiments-and-source.md)：消息重放与 19 项结果检查 | [experiments.py](code/experiments.py) |

| 版本 | 新增机制 | 负责人 |
|---|---|---|
| v1 | 函数参数与返回值 | 始终是协调者 |
| v2 | JSON 请求、started/result/failure、ID 关联、结果验收 | 始终是协调者 |
| v3 | 上下文包、接手确认、owner 与 epoch 检查 | 确认后转给履约专员 |

## 环境和输入

使用 Python 3.11 或更新版本，仅依赖标准库，不需要模型配置。以下命令都在本章目录运行。从仓库根目录进入：

```bash
cd 10-Knowledge/02_Harness/05-communication-and-handoff
```

命令无标准输出，只改变工作目录。输入已实际放在目录中：

| 文件 | 本章使用的内容 |
|---|---|
| [order.json](fixtures/order.json) | `order-017`，SKU 为 pen，数量 3 |
| [inventory-unavailable.json](fixtures/inventory-unavailable.json) | 版本 stock-1 的快照尚未就绪 |
| [inventory-ready.json](fixtures/inventory-ready.json) | 版本 stock-2，pen 的库存为 2 |
| [policy.json](fixtures/policy.json) | 只允许生成处理草稿，不能承诺补货日期或自动退款 |

## 运行命令

在本章目录运行：

```bash
python code/v1_delegate.py
python code/v2_messages.py
python code/v3_handoff.py
python code/experiments.py
python -m unittest discover -s code -p 'test_*.py' -v
python sources/verify_sources.py
```

命令的准确标准输出在各篇中。v1 写 `runs/v1/`，v2 写 `runs/v2/`，v3 写 `runs/v3/`，实验写 `runs/experiments/`。重复运行覆盖同名产物；v2、v3 与实验支持 `--output` 指定新目录。

| 产物 | 用途 |
|---|---|
| `input.json` | 本次实际使用的订单、库存快照和政策副本 |
| `messages.jsonl` | 经队列传递的原始请求与回执，包括注入的重复和迟到消息 |
| `result.json` | 接收决定、有效结果、owner/epoch、交接上下文 |
| `draft.md` | 尚未发送、等待客户确认的处理草稿 |
| `report.md` | 按真实事件生成的接收与交接记录 |
| `comparison.json` | 每项实验的 expected、actual 和 passed |

v1 只产生 `result.json`。交接的提出与确认通过本地方法完成，记在 `result.json`，不会伪装成经过消息总线的网络包。

已生成的产物：[实验报告](artifacts/reference/report.md)、[消息实验](artifacts/reference/delivery/result.json)、[交接草稿](artifacts/reference/handoff/draft.md)。当前在 CPython 3.12.14 下完成 README 路径验证、12 项自动测试和 19 项实验检查；不请求外部模型。

消息去重表、结果缓存和负责人记录保存在单进程内存中；进程重启后不保留，也不提供跨进程认证或数据库事务。本文的 ID/epoch 检查是业务协议规则，接入真实传输时还需要持久化和身份认证。本地源码快照锁定为 CPython 3.12.14 的实际文件，附哈希与许可证；未与远端发布包逐字节比对。

逐条命令、完整正文片段的标准输出与退出码见[读者走读记录](artifacts/verification.json)。

正文入口：[01｜任务委派与消息协议](01-delegation-and-results.md)。
