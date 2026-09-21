# 03｜运行环境与 MCP 接口

[阅读路线](README.md) · [上一篇](02-four-tools.md) · [下一篇](04-experiments.md)

```mermaid
flowchart TD
    A["相同工具请求"] --> B{"执行位置"}
    B --> C["本机注册表"]
    B --> D["stdio MCP 子进程"]
    D --> C
    C --> F["可信脚本的本机进程"]
    I["单独容器 CLI 请求"] --> G["受限容器进程"]
    F --> H["计算结果与错误"]
    G --> H
```

工具名解决“执行哪个操作”，执行环境解决“这个操作能接触什么”。MCP 则负责不同进程怎样发现和调用工具。把这三层分开后，更换通信方式不会悄悄增加权限，更换执行位置也不必重写业务仿真。

## 子进程退出与环境隔离是两件事

第二篇用 `subprocess.run()` 启动真实 Python。Python 3.12 的接口在超时时终止并等待它启动的子进程，再抛 `TimeoutExpired`；进程启动本身可能延迟超时返回。这不是自动终止任意后代进程的通用保证。[Python 3.12 subprocess 文档](https://docs.python.org/3.12/library/subprocess.html)

本机执行仍使用当前操作系统身份。即使 `cwd` 指向 `runs/`，脚本也能尝试读取绝对路径；即使没有 API Key 环境变量，操作系统允许的网络仍可用。`run_python` 因此只开放已审阅脚本。`test_child_timeout_and_nonzero` 使用测试临时文件复现等待与异常，未把生成代码交给本机主线工具。

| 本章措施 | 解决什么 | 仍由谁控制 |
|---|---|---|
| 文件路径限制 | 文件工具请求的目标范围 | 宿主文件系统与并发修改者 |
| `shell=False` 参数列表 | 不让参数被 Shell 当表达式解析 | 被启动程序自身的能力 |
| Python `-I` | 减少导入与用户环境干扰 | 文件、网络、进程权限 |
| `timeout` | 限制等待与清理直接子进程 | 后代进程与外部已发生效果 |
| 容器限制 | 文件挂载、网络、进程及资源范围 | 宿主内核、容器运行时与其配置 |

## 容器入口把执行限制写成命令

[run_container.py](code/run_container.py) 继续执行相同 compute.py、相同 demand.csv，结果仍应为 7 天、需求 29。它构造以下容器参数；这是参数说明，完整可运行入口在其后的命令中。

| 参数 | 具体限制 |
|---|---|
| `--network=none` | 不连接容器外部网络 |
| `--read-only` | 根文件系统只读 |
| `/input` 的只读 bind mount | 仅挂载本章 examples；不挂整个工作区 |
| `--user=65534:65534` | 使用非 root 用户 |
| `--cap-drop=ALL`、`no-new-privileges` | 缩减 Linux capabilities，禁止提权 |
| `--memory=128m`、`--cpus=0.5`、`--pids-limit=32` | 内存、CPU、进程数量限制 |
| `/tmp` tmpfs 16m | 提供小型临时写入空间 |

参数语义来自 [Docker 官方运行文档](https://docs.docker.com/engine/containers/run/)。容器共享宿主内核，运行高风险不可信代码时还需要结合更强的虚拟化隔离与宿主治理，不能把这些参数解读为对所有攻击的证明。

在有 Docker 的章节目录运行：

```bash
docker pull python:3.12-slim
python code/run_container.py --image python:3.12-slim --output runs/container
```

预期输出结构为 `container=passed artifacts=runs/container`，真实 stdout、returncode、镜像引用、命令参数保存在 `result.json`。容器全程超过 15 秒时，程序终止等待并在 `finally` 执行 `docker rm -f <唯一名称>`；只杀掉 Docker 客户端不保证容器停止。镜像拉取单列为前置步骤，避免把拉取时间混进计算期限。

当前验证环境没有 Docker，这条分支未执行；本章保存的是这一事实，而非一次预填成功记录。

## MCP 让另一个进程发现同一组工具

把字典通过 stdin 发到子进程、从 stdout 收回，就有了传输；还需双方约定初始化、方法名和结果。配套 [mcp_stdio.py](code/mcp_stdio.py) 使用固定的 MCP `2025-06-18` 协议路径，按行传输 JSON-RPC 消息，运行一个精简 stdio 服务。它实现 initialize、initialized 通知、tools/list、tools/call，没有 HTTP 传输、分页、通知更新、认证或协议版本回退。[MCP 2025-06-18 工具规范](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)

在章节目录执行：

```bash
python code/mcp_stdio.py --output runs/mcp
```

标准输出：

```text
protocol=2025-06-18 tools=5 valid_call=True invalid_call=True
artifacts=runs/mcp
```

客户端真正启动另一个 Python 进程，等待 initialize 响应，再发送 initialized 通知，随后发现五个工具并调用搜索。每个请求都等自己的 id 返回；五秒 watchdog 防止此本地示例子进程无限阻塞。stdout 专用于协议消息，日志不得夹在 JSON 行中。

| MCP 字段 | 本地对应 | 转换 |
|---|---|---|
| JSON-RPC `id` | `call_id` | 保存请求与响应关联；本地转成字符串 |
| `params.name` | `name` | 从注册表查找 |
| `params.arguments` | `arguments` | 已经是 JSON 对象，不再 `json.loads` 字符串 |
| `tools/list` 的 `inputSchema` | `Tool.input_schema` | 描述实际输入限制 |
| `structuredContent` | 成功的 `data` | 保留结构化对象 |
| `content[].text` | data 或 error 的 JSON 文本 | 供文本读取端使用 |
| `isError` | `not ok` | 表示工具执行失败 |

未知工具属于请求错误，本服务返回 JSON-RPC `-32602`。已找到工具但参数上限不符，则返回带 `isError=true` 的工具结果。实验第二次搜索 `limit=200`，客户端收到了规范化错误，服务仍继续运行。

这些代码用于把协议包裹与实际执行连起来；它不是完整 MCP SDK。接入正式服务时，可用支持目标版本的 SDK 处理协议细节，复用本章的输入、输出和执行边界。数据范围、费用与人工批准继续由 [12｜权限与资源控制](../12-permissions-and-resources/README.md)强制执行。

[下一篇：从失败案例检查工具契约](04-experiments.md)
