# Coding Agent：从复现失败到交付补丁

> 状态：draft · 更新：2026-09-06

本案例把公开方法与一个本地算例分开。公开依据是 [SWE-agent v1，2024-05-06](https://arxiv.org/abs/2405.15793v1)，用于学习 Agent-Computer Interface 如何组织仓库读取、编辑与执行。下面的价格函数是本库原创教学代码，不是 SWE-bench 结果，也没有调用模型自动生成补丁。

输入需求：`discount` 表示折扣比例，100 元打九折应返回 90。错误实现若写成 `amount - discount`，结果会是 99.9。可运行修复在[application_cases.py](../../05-code/application_cases.py)的 `correct_price`：计算 `amount * (1-discount)` 并检查输入边界。

| 阶段 | 具体动作 | 留下的证据 |
|---|---|---|
| 复现 | 运行 `(100,.1) → 90` 断言 | 错误函数返回 99.9 |
| 定位 | 对照参数定义和计算表达式 | 折扣比例被当成绝对金额 |
| 修复 | 更换计算并限制折扣范围 | 可审查函数与差异 |
| 验证 | 常规、0 金额、0/1 折扣、非法输入 | 固定测试结果 |
| 交付 | 说明变化与未验证项 | 补丁及测试记录 |

读者可以运行：

```bash
python 10-Knowledge/13-application-engineering/05-code/application_cases.py
python -m unittest discover -s 10-Knowledge/13-application-engineering/05-code -p 'test_*.py'
```

实际 Agent 还需在隔离工作区保留原 commit、补丁和命令输出；不能改验收测试让它迁就错误实现。只跑作者刚写的测试会遗漏回归，需同时运行仓库原有测试和固定隐藏边界。真实货币计算还要使用明确的小数精度和舍入规则；这个浮点算例只演示接口语义错误。

失败时先区分编译/依赖错误、环境错误、行为错误与测试本身错误，再决定是否继续编辑。测试超时不等于代码一定错误，更不等于可以删除测试。代码 E2E 的更一般组织见[应用域导航](../../README.md)。
