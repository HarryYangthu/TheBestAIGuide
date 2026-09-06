# 模型适配器：把生成结果变成可校验的动作

> 状态：draft | 来源核验：2026-09-06

运行时需要知道“调用哪个工具、传什么参数、什么时候完成”，模型API却可能返回文本、工具调用、拒绝或中断的流式片段。适配器的工作是把这些供应商格式转换成明确的内部动作，并保存失败语义。

本库最小接口只有 `decide(state) -> Action`。`Action(kind="tool", name="search", arguments={"query":"上下文"})` 提出工具动作；`Action(kind="finish", answer="...")` 提出结束。模型无法通过这两个动作修改允许的工具列表，也不能自行给自己补权限。

| 边界 | 应检查什么 | 错误处理 |
| --- | --- | --- |
| API传输 | 连接超时、状态码、请求ID | 分类记录；是否重试取决于服务语义和预算 |
| 完整响应 | 是否正常结束、被截断、拒绝 | 截断JSON不进入工具执行；拒绝不当作格式错误无限修复 |
| 动作解析 | `kind/name/arguments` 类型与必填项 | 返回契约错误，最多有限修复 |
| 工具执行前 | 工具存在、参数schema、主体权限 | 在运行时再检查，模型侧约束不能替代 |
| 工具返回后 | 输出schema、来源、大小 | 大结果外置或裁剪，错误结果不能装成成功 |

## 为什么“返回JSON”还不够

`{"name":"search","arguments":{"query":7}}` 是合法JSON，但查询参数类型错误。`{"query":"上下文","admin":true}` 也能解析，但多出来的字段可能意外触发后端分支。因此要区分三个层次：能解析的JSON、符合schema的对象、业务上允许的动作。结构化生成主要改善前两项；权限和业务限制仍由程序判断。

当供应商返回并行工具调用时，适配器不应偷偷只取第一项。要么内部Action明确支持列表，要么显式拒绝当前实现不支持的多调用。本例选择单调用契约，便于学习每一步状态变化。流式响应同理：参数没有接收完整之前只展示进度，不执行半个调用。

## 接入真实模型时替换哪一层

```python
from agent_loop import Action

class MyModelAdapter:
    def __init__(self, request):
        self.request = request  # 由调用者注入已认证的API函数

    def decide(self, state):
        payload = self.request(state)  # 此处契约：返回完整的dict
        if payload["kind"] == "tool":
            return Action("tool", payload["name"], payload["arguments"])
        if payload["kind"] == "finish":
            return Action("finish", answer=payload["answer"])
        raise ValueError("unsupported action")
```

这段是适配边界示例，不是某家API的完整调用器。真实连接还要绑定模型ID、参数、工具格式、超时、拒绝状态和usage；这些应以对应版本官方SDK为准。仓库没有凭据，因此没有宣称做过真实模型质量验证。你可以先用 [ScriptedModel](../05-code/agent-loop-python/src/agent_loop/models.py) 输入错误动作，确认运行时如何处理，再接真实模型，避免把控制问题和模型问题混在一起。

不要在日志打印完整异常消息。SDK的异常可能带URL、请求内容或认证信息。本例仅记异常类型；进一步诊断时按字段脱敏保存请求ID、响应状态和可公开的错误码。

下一步：[工具契约](../../05-tools-skills-protocols/01-concepts/01-structured-output-and-tool-contracts.md)。规范依据：[JSON Schema 对象语义](https://json-schema.org/understanding-json-schema/reference/object)。
