# Evaluation Labs

> 状态：verified
> 执行日期：2026-09-06；Python 3.12.13；4 个代码单元真实执行并保存输出。

[01-evaluation-and-regression.ipynb](01-evaluation-and-regression.ipynb)演示固定任务、独立 fixture、结果评分、逐项归因和回归阻断。工程入口为 [Eval Harness](../05-code/eval-harness-python/README.md)，完整解释见[教学案例](../03-cases/01-from-task-dataset-to-regression.md)。

四条人工构造任务，各重复两次：基线 2/8，通过权限/版本修复后 8/8；模拟回退会阻断。数字对应确定性示例函数，不是 LLM 成功率。Wilson `[0.4902,0.9433]` 和 pass@3 `0.5333` 是独立数值算例，不用来给这四条重复任务估计总体可靠性。

环境禁止 TCP/IPC socket；实际以每本独立 Python 进程中的 IPython 顺序执行代码和断言，尚未验证 Jupyter 内核通信。输出为真实代码结果。实验环境 nbformat 5.11.1、IPython 9.17.1；常规 Jupyter 可采用 nbclient 0.11.0、ipykernel 7.3.0。核心 Harness 只依赖标准库。
