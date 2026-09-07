# 委托授权：模型提出动作，身份决定允许范围

> 状态：draft | 来源核验：2026-09-06

用户要求查询自己知识库的资料。主Agent委托检索服务完成搜索，并不意味着检索服务可以读其他人的文件，更不意味着模型在参数里写`subject="admin"`就能切换身份。身份必须来自服务端验证过的会话或凭据，不能来自模型生成的普通参数。

授权至少回答三个问题：谁在请求、对哪个资源、允许什么动作。用逻辑式表达是：

$$allow = authenticated \land scope\_allows(action) \land resource\_allows(subject,resource).$$

这里三个量都是程序检查得到的布尔值。只有`docs:read` scope还不够：它可以表明允许读文档，但不说明允许读某位同事的私有文档。资源层还要核对拥有者、租户、共享名单等条件。

例如 Alice 已登录且令牌含 `docs:read`，但目标属于 Bob 且未共享，则三个条件为 `True、True、False`，最终拒绝。`scope` 是令牌允许的动作类别，`subject` 是经过认证的主体，资源授权是“这个主体对这份具体资料”的检查。三者分别解决问题，不能用“已经登录”替代全部授权。

## 在工具调用的哪里检查

本库TS Runtime的`Identity`由调用代码传入，含`subject`与`scopes`；调用参数只有业务字段。Runtime先查scope，再执行handler。真实文档服务应在handler中按subject过滤文档或向后端传递已验证的身份。示例只有公共教学语料，因此没有冒充完整多租户认证系统。

```typescript
if (!identity.scopes.has(tool.scope)) {
  return { call_id: call.call_id, ok: false,
           error: { code: "permission_denied", retryable: false } };
}
```

读取缓存结果也要先检查权限。若先按调用ID命中缓存，后检查权限，用户权限被撤销后仍可能拿到旧结果。本实现先授权再查幂等缓存，并把主体加入缓存键。复杂系统还需要资源授权版本或缓存失效机制；scope没有变化不代表每份文档的权限没变。

## 委托不是把上游令牌原样转发

OAuth Token Exchange允许表达令牌交换与委托关系，但是否采用它取决于身份平台支持。原则是下游拿到的凭据必须适用于目标服务、具备必要权限且有有效期。将面向A服务的token直接发给B服务，既可能校验失败，也可能泄露凭据。

当前MCP HTTP授权规范要求资源指示与令牌受众检查。客户端要确认向正确服务器发送其适用的token；服务端也要验证token确实签发给自己。认证失败与权限不足应区分，这样客户端才知道需要重新认证还是需要更窄/不同的授权。具体授权服务配置必须按官方规范和使用的身份平台实现。

## 人工同意应绑定对象

“允许写回报告”至少绑定目标路径、要提交的内容或差异、有效范围。若批准后内容改变，就不能复用旧决定。只读查询如果在已有授权范围内可以直接执行；审批应围绕确有副作用和明确规则的动作，不能把每次调用都变成没有意义的确认按钮。

审计记录保存主体、动作、资源、决定、调用ID和时间即可定位大部分权限问题；通常不需要保存完整令牌。禁止把秘密放进模型上下文或异常文字里。

代码见[Runtime](../05-code/tool-runtime-typescript/src/runtime.ts)，跨主体数据过滤见[Memory写读模式](../../07-state-and-memory/02-patterns/01-memory-write-and-retrieval.md)。一手来源：[MCP 2026-07-28授权](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)、[RFC 8693](https://www.rfc-editor.org/rfc/rfc8693)。
