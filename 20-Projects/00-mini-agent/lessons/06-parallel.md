# 06：并行读取与两个子 Agent

第一项实验是工具并发：

```bash
python 20-Projects/00-mini-agent/run.py run --stage 6 --mode demo --output .runs/mini-parallel
```

一个模型发出 `parallel_read`，Python 的 `ThreadPoolExecutor` 用两个工作线程读取互不依赖的 v1/v2 文件。汇总保持请求中的文件顺序，避免线程完成顺序改变结果。[parallel.py](../mini_agent/parallel.py) 中有实现。

`learn.py` 还比较串行与并行。因为教学文件极小，实验**人为给每次读取增加 40ms 等待**，让调度差异可见。参考时间约 80ms 与 40ms；每次不同，不是系统性能承诺。验收只要求两者结果一致，不设加速倍数阈值。

第二项实验才是子 Agent：

```bash
python 20-Projects/00-mini-agent/delegate.py --mode demo --output .runs/mini-children
```

两个 Reader 各有自己的模型实例、消息列表、工具调用循环和四轮预算。一个只读 v1，一个只读 v2；宿主核对读取回执并按指定顺序收集结果。查看两份 `*.trace.json`，确认它们没有共享消息历史。这里的编排是宿主固定分工，不是主 Agent 自主创建团队。

配置模型环境变量后，把 `--mode demo` 改成 `--mode live`，两个 Reader 才会独立调用真实模型。demo 的 Reader 仍是脚本驱动。`delegation.json` 的 PASS 只表示每个 Reader 真正读过指定资料且正常结束，不代表自然语言总结正确，也不替代主项目的升级清单验收。

[subagents.py](../mini_agent/subagents.py) 给子 Agent 只读工具，并在宿主再次检查文件是否属于该子任务。独立上下文可以减少互相干扰，却增加模型请求、汇总和错误处理成本。

**练习：** 对比 `parallel_read` 与两个 Reader 的轨迹，数一数模型调用次数。再把两个子任务改成有前后依赖的任务，解释为什么此时不能直接同时执行。没有对照结果之前，不声称多 Agent 更好。

关联知识：[规划与多 Agent](../../../10-Knowledge/08-planning-workflow-multi-agent/README.md)。
