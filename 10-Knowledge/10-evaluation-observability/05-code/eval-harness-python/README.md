# Eval Harness Python

> 状态：verified
> 验证：2026-09-06，Python 3.12.13；7 项测试通过，4 任务各 2 Trial 的基线/候选均已运行。

一个可以直接阅读和改造的离线评测入口。被测函数可替换；默认实例是确定性资料查询逻辑，无模型调用、无账号、无费用。

## 运行

在本目录执行：

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m eval_harness.cli
```

PowerShell 先执行 `$env:PYTHONPATH = "src"`，再执行上面两条 `python` 命令。依赖仅标准库，见 [requirements.lock](requirements.lock)；可选 editable 安装需要 setuptools。

## 接口

```python
from eval_harness import EvalTask, run_suite, summarize

task = EvalTask("counter", {"delta": 1},
                {"output": {"ok": True}, "state": {"count": 1}},
                fixture={"count": 0}, tags=("state",), critical=True)

def system(request, fixture, emit):
    fixture["count"] += request["delta"]
    emit("updated", count=fixture["count"])
    return {"ok": True}

results = run_suite([task], system, trials=2)
assert all(r.success for r in results)
print(summarize(results))
```

`EvalTask.expected` 只进入 Grader，不作为 system 参数。每个 Trial 独立深拷贝输入/环境，函数异常计入结果分母。`summarize` 分别给 Trial 微平均和 Task 宏平均；重复次数不均时二者可能不同。`compare` 严格匹配任务/版本/Trial 及切片，阻断关键失败和曾通过的配对任务退化。它不是统计非劣检验。

## 代码与学习路径

| 入口 | 作用 |
| --- | --- |
| [tasks.py](src/eval_harness/tasks.py) | EvalTask、TrialFixture、TrialResult 数据契约 |
| [runner.py](src/eval_harness/runner.py) | 顺序调度、状态重置、事件、异常记账 |
| [graders.py](src/eval_harness/graders.py) | 输出/状态字段与类型检查、字面禁止项 |
| [statistics.py](src/eval_harness/statistics.py) | Wilson 和 pass@k 的独立统计函数 |
| [reports.py](src/eval_harness/reports.py) | 逐任务、切片、原始 JSONL 和配对门禁 |
| [cli.py](src/eval_harness/cli.py) | 故意漏掉过滤的基线与修复版 |
| [测试](tests/test_harness.py) | 状态自述、类型偷换、异常、回归、公式边界 |
| [完整教学案例](../../03-cases/01-from-task-dataset-to-regression.md) | 数据构造 → 评分 → 归因 → 优化 → 回归 |
| [Notebook](../../04-labs/01-evaluation-and-regression.ipynb) | 按顺序运行并读取中间量 |

原始输出：[基线](reports/baseline/trials.jsonl)、[候选](reports/candidate/trials.jsonl)、[门禁](reports/comparison.json)。报告保存 fixture 和 outcome 快照，当前只用于教学数据；接业务前必须做数据最小化、去敏与访问控制。

## 明确的能力边界

本版本为串行、进程内、可信函数的教学 Harness，不是执行不可信代码的沙箱，不提供硬超时/取消、进程隔离、远程队列或费用预算。异常类型为 TimeoutError 时仍记 system_error，不暗示 Harness 自己能中止挂起函数。将真实系统包在进程/容器中执行，再接入该结果/评分契约，是进一步工程化的方向。

字面禁止词不覆盖语义泄漏；结构化精确匹配不覆盖开放文本等价；模型 Judge 尚未实现真实调用或独立专家校准。统计函数本身已测试，但确定性重复 Trial 不满足独立总体采样，汇总不自动生成置信区间。数据/评分对象见 [fixtures/README.md](fixtures/README.md)。
