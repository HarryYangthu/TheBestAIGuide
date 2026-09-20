# 14｜技能库 Skills：把版本比较方法做成可复用包

[组件总览](../README.md) · [上一组件：长期记忆 Memory](../13-memory/README.md) · [下一组件：自进化](../15-self-improvement/README.md)

工具已经会读文件、运行脚本、写报告，但一次版本比较仍可能选错预览稿、漏掉旧版证据、直接比较不同单位。本章把这些稳定步骤整理成一个实际 Skill 包：比较 Pine Example SDK 的两个正式版本，输出有双侧来源、单位一致的参数变更表。

Pine Example SDK 是随章提供的示例产品，所有资料都在本地。我们不安装个人技能，也不依赖某个客户端自动发现它；本章宿主从 `examples/` 发现、加载并执行这个包。

```mermaid
flowchart TD
    A["01 从重复错误提炼方法"] --> B["02 SKILL、脚本与附件"]
    B --> C["03 按任务逐步加载"]
    C --> D["执行参数化脚本"]
    D --> E["04 验收和版本对照"]
    E --> F["报告、证据与包指纹"]
```

| 顺序 | 正文 | 实际入口 |
|---|---|---|
| 01 | [从一个比较任务提炼稳定方法](01-method-from-task.md) | 读取两份真实输入，建立逐项证据规则 |
| 02 | [组织与执行一个技能包](02-package-and-script.md) | `examples/skills/release-comparison/scripts/compare.py` |
| 03 | [宿主怎样逐步加载与执行](03-progressive-loading.md) | `code/host.py` |
| 04 | [验收、版本更新与回归实验](04-validation-and-versioning.md) | `code/run_experiments.py`、`code/validate_output.py` |

## 运行环境与读者路径

工作目录为 `10-Knowledge/14-skills/`。Python 3.10+，只依赖标准库；实际验证为 Python 3.12.14。任务类型由 CLI 显式给出，数据转换由确定性脚本完成，因此无需模型和 API Key。

先直接运行技能脚本，确认包本身可以工作：

```bash
python examples/skills/release-comparison/scripts/compare.py --old examples/inputs/v1.json --new examples/inputs/v2.json --old-version 1.0 --new-version 2.0 --units examples/skills/release-comparison/references/units.json --template examples/skills/release-comparison/assets/report.md --output runs/direct
python code/validate_output.py --output runs/direct --old examples/inputs/v1.json --new examples/inputs/v2.json
```

标准输出：

```text
status=generated rows=3
acceptance=True checks=23
```

再让宿主按需读取同一份方法：

```bash
python code/host.py --task compare --output runs/host
python code/host.py --task polish --output runs/polish
python code/run_experiments.py --output runs/experiments
python code/package_manifest.py --output runs/package-manifest.json
python -m unittest discover -s code -p 'test_*.py' -v
```

可核对的标准输出为：

```text
status=completed acceptance=True
artifacts=runs/host
status=skipped acceptance=None
artifacts=runs/polish
checks=4 passed=4
artifacts=runs/experiments
packages=2 artifacts=runs/package-manifest.json
```

所有任务输出目录应尚不存在；重复运行换一个目录名。polish 入口表示“此任务不加载版本比较技能”，不会替用户执行文本润色。它保留跳过记录供检查。

## 包、输入、输出可以逐项打开

| 位置 | 内容 |
|---|---|
| [v1.json](examples/inputs/v1.json)、[v2.json](examples/inputs/v2.json) | 正式版结构化字段、原文与来源 ID |
| [preview.json](examples/inputs/preview.json) | 会被拒绝的预览版干扰输入 |
| [SKILL.md](examples/skills/release-comparison/SKILL.md) | name、description、version 和执行方法 |
| [scripts/compare.py](examples/skills/release-comparison/scripts/compare.py) | 参数化生成程序 |
| [references/units.json](examples/skills/release-comparison/references/units.json) | 单位、量纲和换算倍率 |
| [assets/report.md](examples/skills/release-comparison/assets/report.md) | 确定性表格模板 |
| [1.0.0 包](examples/skills-v1/release-comparison/SKILL.md) | 没有单位附件的旧方法快照 |
| `runs/host/trace.json` | 先目录、后方法、再附件和执行的实际顺序 |
| `runs/host/comparison/` | comparison.json、report.md、acceptance.json |

已生成的 [版本比较报告](evidence/direct/report.md)、[验收](evidence/direct/acceptance.json)、[加载轨迹](evidence/host/trace.json)、[版本对照](evidence/experiments/report.md)与[包指纹](evidence/package-manifest.json)都可核对。

本章已运行全部入口、4 个版本/路由场景和 10 个边界测试，详见 [validation.json](evidence/validation.json)。渐进加载记录的是 UTF-8 字节，不是 token；显式 compare/polish 路由没有测量模型自动选择技能的准确率。官方格式与本章宿主约定的对应关系见第四篇。

从 [01｜从一个比较任务提炼稳定方法](01-method-from-task.md)开始。
