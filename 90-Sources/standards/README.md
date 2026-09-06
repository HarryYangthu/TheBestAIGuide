# 标准与协议：先确定版本，再讨论是否符合要求

这里的材料分别属于协议规范、数据验证规范、安全最佳实践和遥测语义约定，权威范围不同。某个工具用了相同字段名，不等于实现了整套协议。核验日期：2026-09-06；本页提供规范阅读入口，不代表本库通过互操作性或合规认证。

| 官方材料 | 固定版本／状态 | 本库为什么要读 | 最容易写错的边界 |
| --- | --- | --- | --- |
| [Model Context Protocol](https://modelcontextprotocol.io/specification/2026-07-28) 与 [变更说明](https://modelcontextprotocol.io/specification/2026-07-28/changelog) | 2026-07-28 修订 | 核对工具、资源与请求传输约定，连接 [工具与协议](../../10-Knowledge/05-tools-skills-protocols/README.md) | 该版本移除 `initialize` / `notifications/initialized` 握手，改为自包含请求；旧版初始化流程只能标注为对应历史版本。协议核心无状态不等于业务没有持久状态 |
| [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12) | 方言名 2020-12；本次官方目录的修订文档发布日 2022-06-16 | 核对工具输入、结果和共享数据的结构校验 | 方言名与文档发布日期不同；`format` 的注解与断言是不同词汇表，不能默认所有校验器都检查邮箱、日期等语义。结构通过也不能证明业务权限正确 |
| [RFC 9700：OAuth 2.0 Security BCP](https://www.rfc-editor.org/rfc/rfc9700.html) | 2025-01，BCP 240；更新 RFC 6749、6750、6819 | 核对授权码流程、重定向、令牌重放和权限限制，连接 [安全与治理](../../10-Knowledge/11-safety-security-governance/README.md) | 它是 OAuth 2.0 安全最佳实践；“接上 OAuth”不自动解决工具权限、提示注入或敏感数据流向问题 |
| [OpenTelemetry GenAI 语义约定](https://github.com/open-telemetry/semantic-conventions-genai/blob/94f432d7126f5884d30a2cdde6f4e89908ebb6fd/docs/gen-ai/README.md) | 固定提交 `94f432d7126f5884d30a2cdde6f4e89908ebb6fd`，提交日 2026-09-03；所读总览与 model span 页标识 Development | 核对模型、Agent、工具调用的 span、metric、event 约定，连接 [评测与可观测性](../../10-Knowledge/10-evaluation-observability/README.md) | [旧官方入口](https://opentelemetry.io/docs/specs/semconv/gen-ai/) 已声明迁移；不要将滚动字段表说成已永久稳定，也不要把本库自定义字段称为官方字段 |

阅读规范时记录三件事：适用版本、必需行为、实现中的验证位置。例如工具服务宣称支持某个 MCP 修订，应有对应请求和错误路径的协议测试；只有一个叫 `call_tool` 的函数不足以证明协议支持。

本轮还核对了 OTel 固定提交的 [仓库 README](https://github.com/open-telemetry/semantic-conventions-genai/blob/94f432d7126f5884d30a2cdde6f4e89908ebb6fd/README.md)：其 Schema URL 仍未填写。因此这里使用提交 SHA 作为证据定位，不根据搜索摘要猜测发布版本。逐字段接入时还要检查该字段自身的稳定性、要求级别和敏感内容处理要求。
