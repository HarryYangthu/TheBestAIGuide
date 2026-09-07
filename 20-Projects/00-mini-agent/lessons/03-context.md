# 03：上下文满了，保留什么

模型每次收到的是一份消息列表。资料越读越多，这份列表越长。这里先实现一个容易观察的策略：保留系统要求、当前任务与最新完整动作组，较早的动作组超出预算时整组移除。提示模型在缺少证据时重新读原文件。

代码在 [context.py](../mini_agent/context.py) 的 `pack`。一个动作组包括模型消息及其全部工具结果；不能留下结果却删掉对应调用。`read_file` 另有 `start`、`limit`，防止一次读取整份大文档。返回的 `next_start` 提示后续从哪里继续。

```bash
python 20-Projects/00-mini-agent/run.py run --stage 3 --mode demo --output .runs/mini-context
```

小样本可能完全不需要裁剪。查看 `run.json` 的 `context` 数组，而不是假定开了功能就一定产生收益。运行 `learn.py` 后，`completion.json` 的 `experiments.context` 会使用较长构造消息，显示裁剪前后字符数及移除组数。参考结果是 4980 → 1128 字符，移除 4 组；这是固定构造实验，不是模型节省 token 的测量。

策略的代价是旧证据被移出请求。这个版本没有语义摘要，裁剪提示也没有保存被删资料的事实。如果最新完整组仍装不进预算，程序明确失败；不破坏消息协议强行截断。宿主侧完整历史仍保存在 `messages.json`。

**练习：** 修改 `context.py` 中保留策略，尝试额外保留最近一次目录列表。比较请求长度与文件定位表现，并记录真实结果。不要把 `json.dumps` 的字符数称为 token 数：中文、英文和标点的 token 切分不相同。

关联知识：[上下文工程](../../../10-Knowledge/04-context-engineering/README.md)。
