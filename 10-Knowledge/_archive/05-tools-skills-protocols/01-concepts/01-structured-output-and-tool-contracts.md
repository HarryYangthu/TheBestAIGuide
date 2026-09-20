# 工具契约：从“模型想调用”到“程序可以执行”

> 状态：draft | 来源核验：2026-09-06

模型生成 `search(query="上下文")` 并没有执行搜索。它只是提出一个动作；接下来，程序必须判断这个动作能否执行，执行后把结果交回模型。Function Calling 让模型表达动作，Tool Runtime 负责实际调用，两者之间靠契约连接。

本库把一次工具调用定义为 `call_id、name、arguments`。ID区分哪次调用，名称定位注册表中的函数，参数提供输入。结果必须引用同一 `call_id`；否则并行执行时无法判断哪条结果对应哪次请求。

## 四层校验不能混成一步

| 层次 | 看起来像成功但实际有问题的输入 | 负责判断的程序 |
| --- | --- | --- |
| JSON语法 | 少右括号、夹杂说明文字 | JSON解析器 |
| 数据结构 | `query:7`，缺少必填字段 | Schema校验器 |
| 业务语义 | 查询只有空格，日期范围倒置 | 工具业务代码 |
| 授权范围 | 查询格式正确，却读取其他人的私有资料 | 认证与资源授权逻辑 |

JSON Schema 中写了 `properties`，并不自动要求这些字段存在；需要 `required`。未写 `additionalProperties:false` 时，额外字段通常允许存在。对固定工具接口严格拒绝未知字段，可以尽早发现模型写错参数名；但开放扩展对象可明确允许额外字段，不能把全库都设为同一种策略。

```json
{
  "type": "object",
  "properties": {"query": {"type": "string", "minLength": 1}},
  "required": ["query"],
  "additionalProperties": false
}
```

这个Schema仍接受一个空格，所以工具还需检查 `query.trim()`。结构约束能缩小错误范围，却不能替你表达全部业务规则。

## 为什么输出也要有契约

假设下游读取 `result.documents`，工具升级后改成 `result.items`。若没有输出校验，错误可能几步之后才暴露，看起来像模型失误。工具出口校验能把故障定位到实际发生的位置。

成功结果采用 `{call_id,ok:true,data}`，失败采用 `{call_id,ok:false,error:{code,retryable}}`。两种对象通过 `oneOf` 区分，失败时不返回貌似正常的空列表。空列表表示“查询执行成功但没有命中”，超时表示“结果未知”，二者对应不同下一步。

| 字段 | 为什么保留 |
| --- | --- |
| `error.code` | 稳定供程序分类，避免解析自然语言异常 |
| `retryable` | 提供重试提示；仍须结合副作用和预算判断 |
| `data` | 结构化事实，保持来源ID便于引用 |
| `call_id` | 与请求关联，不能直接当成跨系统幂等保证 |

运行 [契约Notebook](../04-labs/01-tool-contracts-and-errors.ipynb)，你会看到合法JSON为什么仍能被Schema拒绝。完整TS实现见 [Registry](../05-code/tool-runtime-typescript/src/registry.ts)，六种交换对象见 [共享Schema](../05-code/shared-schemas/README.md)。官方依据：[JSON Schema对象](https://json-schema.org/understanding-json-schema/reference/object)。
