# 失败驱动的候选与回滚实验

| 版本 | dev | holdout |
|---|---:|---:|
| baseline | 4/8 | 6/8 |
| candidate | 8/8 | 8/8 |

候选由 dev 失败的受控变更规则生成；生成器不读取 holdout 预期。

![comparison](comparison.png)

采用门禁：True。采用后实际运行 whitespace：True；回滚后再次运行：False。

最终 active.json 指向基线，history.jsonl 保存 initialize、adopt、rollback。示例回滚是主动演示，不表示发现了线上事故。

所有尝试保留；模型成本未采集，未作成本改善声明。
