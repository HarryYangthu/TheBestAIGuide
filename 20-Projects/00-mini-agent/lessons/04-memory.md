# 04：重启后仍记得的偏好

`messages` 是一次会话中的历史；这里的 Memory 是显式保存到文件、下次运行还能读到的用户偏好。我们只保存 `table` 或 `bullets`，避免把整个对话存下来却误称为可靠记忆系统。

从仓库根目录依次运行，每条命令都是新进程：

```bash
python 20-Projects/00-mini-agent/run.py memory bullets --file .runs/my-mini-memory.json
python 20-Projects/00-mini-agent/run.py run --stage 4 --mode demo --memory .runs/my-mini-memory.json --output .runs/mini-remember
python 20-Projects/00-mini-agent/run.py run --stage 4 --mode demo --memory .runs/my-mini-memory.json --format table --output .runs/mini-override
python 20-Projects/00-mini-agent/run.py memory delete --file .runs/my-mini-memory.json
python 20-Projects/00-mini-agent/run.py run --stage 4 --mode demo --memory .runs/my-mini-memory.json --output .runs/mini-deleted
```

| 运行 | report.md 的格式 | run.json 的 format_source |
| --- | --- | --- |
| mini-remember | 项目符号 | memory |
| mini-override | 表格 | current_request |
| mini-deleted | 默认表格 | default |

三个报告的事实应该相同，只改变呈现方式。记忆进入系统上下文，同时宿主渲染器严格应用选定格式，所以这个实验验证偏好的保存、优先级和应用，不测量模型是否理解自然语言偏好。

读 [memory.py](../mini_agent/memory.py) 的 `resolve_format`：当前明确要求优先，其次持久偏好，最后默认值。`set_format` 只接受显式用户设置，并通过临时文件替换写入。它适用于单个学习者的顺序操作，没有多用户数据库或并发写入协议。

**练习：** 将偏好设为 bullets，但当前明确要求 table。预测结果并解释“听从当前要求”为什么比机械复用记忆更合理。扩展其他偏好时，应同时增加允许值、应用位置、删除与覆盖测试。

关联知识：[状态与记忆](../../../10-Knowledge/07-state-and-memory/README.md)。
