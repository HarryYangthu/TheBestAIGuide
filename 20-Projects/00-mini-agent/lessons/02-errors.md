# 02：工具出错之后，怎样继续

```bash
python 20-Projects/00-mini-agent/run.py run --stage 2 --mode demo --output .runs/mini-errors
```

教学轨迹先尝试读取不存在的 `release-notes.md`，再读实际存在的文件。查看 `trace.jsonl`：失败工具结果的 `ok` 为 false，后面仍有读取与写报告动作。`run.json` 的 `tool_errors` 应为 1，最终验收仍应 PASS。这是可恢复的工具错误，不是伪造一个成功结果。

[runtime.py](../mini_agent/runtime.py) 中，stage 1 的工具错误结束运行；stage 2 起把错误转换为工具消息，交给下一轮模型处理。错误的 JSON、未知工具和文件不存在属于这一类。模型网络错误则结束为 `error`，本项目不隐藏异常并改用脚本答案。

步数限制用于防止循环永不结束，不表示任务可以在限制点自动判成功：

```bash
python 20-Projects/00-mini-agent/run.py run --stage 2 --mode demo --max-steps 1 --output .runs/mini-too-short
```

应看到 `status=budget_exhausted`、`passed=false`，退出码 1。没有报告是正常的，因为预算在写报告前就用完了。

**练习：** 把限制改成 2、5、6，预测在哪一步停止，再对照记录。这个 demo 在 stage 2 需要 6 次模型调用；live 模型的调用次数不一定相同。删除单次轨迹中的错误反馈不是修复，修复必须反映在下一步动作和实际产物上。

关联知识：[工具与协议](../../../10-Knowledge/05-tools-skills-protocols/README.md)。
