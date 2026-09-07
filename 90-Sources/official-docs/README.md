# 官方文档：核对接口，而不靠印象写代码

论文回答算法是什么，API 文档回答某个实现接受什么、返回什么、遇到边界会怎样。二者需要同时看。以下页面核验于 2026-09-06；文档版本是阅读证据，不表示本库已经安装或验证该版本。

| 官方入口 | 本次读取的版本或页面标识 | 实际要查的细节 | 对应学习入口 |
| --- | --- | --- | --- |
| [PyTorch scaled_dot_product_attention](https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.scaled_dot_product_attention.html) | PyTorch 2.14；函数页仍标注 beta | Q/K/V 形状，Softmax 所在维度，布尔掩码 `True` 表示参与注意力；推理时需显式传 `dropout_p=0.0`。不能把 `MultiheadAttention` 的 padding mask 语义直接搬过来 | [基础模型](../../10-Knowledge/02-foundation-models/README.md) |
| [Python asyncio 的任务与协程](https://docs.python.org/3/library/asyncio-task.html) | 本次页面标识 Python 3.14.7；`/3/` 是滚动入口 | `create_task`、`gather`、`TaskGroup`、超时与取消；`TaskGroup` 自 3.11 引入。取消清理逻辑不能只靠把异常吞掉 | [规划与多 Agent](../../10-Knowledge/08-planning-workflow-multi-agent/README.md)、[运行时](../../10-Knowledge/09-runtime-harness-environment/README.md) |
| [Jupyter Notebook 文件格式](https://nbformat.readthedocs.io/en/stable/format_description.html) | 文档标识 nbformat 5.11；库版本和 Notebook 格式版本是不同的量 | Markdown/code cell、输出、执行计数和元数据怎样保存；能打开 JSON 不等于代码执行过 | [实验模板](../../00-Home/templates/lab.md)、[写作要求](../../00-Home/Learning-Writing-Guide.md) |

MCP、JSON Schema、OAuth 和 OpenTelemetry 的版本入口统一放在 [标准与协议](../standards/README.md)。外部评测项目的安装命令从 [固定代码快照](../repositories/README.md) 查，不把滚动 README 的命令写成长期不变的要求。

遇到“公式没错，代码结果却不同”，按输入形状、数据类型、默认参数、掩码、随机性、后端顺序排查。在文章中写明使用的依赖版本；读者若升级依赖，应重新跑对应的小输入对照实验。
