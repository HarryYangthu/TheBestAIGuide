# 02｜Token 预算与工具结果裁剪

本章总览图如下：

```mermaid
flowchart TD
    D["政策与长日志"] --> R["保留来源和关键行"]
    R --> C["序列化实际消息"]
    C --> T["o200k_base 编码计数"]
    T --> B{"是否符合本地预算"}
    B -->|是| P["保存消息与选择记录"]
    B -->|否| X["排除可选块或停止"]
    P --> E["检查发布证据是否齐全"]
    X --> E
```

[阅读路线](README.md) · [上一篇：独立上下文与按需加载](01-isolation-and-loading.md) · [下一篇：历史压缩与事实校验](03-history-compression.md)

## Token 计数

已加载的两份正文中，演练日志有 84 行。预算检查需要明确计数对象。本文固定使用 **tiktoken 0.12.0 的 `o200k_base`**，对明确的 JSON 字符串编码，再统计返回列表长度。

**完整可运行片段**；在章节目录执行，依赖已安装并预热的 tiktoken，无文件输入、不产生文件：

```python
import tiktoken

encoding = tiktoken.get_encoding("o200k_base")
ids = encoding.encode_ordinary("timeout_ms=3000")
print(ids)
print(len(ids))
```

准确输出：

```text
[32264, 50103, 28, 4095, 15]
5
```

`timeout_ms=3000` 不是 5 个字符，也不是按空格拆出的 5 个词。这五个整数才是本例编码 token 的可核验结果。`encode_ordinary` 把特殊 token 样式的文本当普通资料处理；这不改变真正 API 如何包装角色消息。

[context.py](code/context.py) 的 `measure` 对 `ensure_ascii=False`、`sort_keys=True`、紧凑分隔符的 JSON 编码。字段顺序、空白规则和编码器名称固定，才能让 402 这个数字可复现。把字典直接 `str()`、换一种序列化方式，再比较 token 数，比较的已经是另一段输入。

## 输入预算

本文用下面这组**实验参数**，不是宣称某个模型的窗口只有 2400：

| 符号 / 字段 | 值 | 本例意义 |
|---|---:|---|
| W / window | 2400 | 给本次演示分配的总额度 |
| O / output_reserve | 600 | 为后续生成预留 |
| M / framing_margin | 300 | 为未计入的服务包装留余量 |
| B / local_input_limit | 1500 | 本地序列化输入上限，W − O − M |

`serialized_input_tokens` 精确描述的是**本文 JSON 消息串在指定编码器下的 token 数**，不是服务账单的 `prompt_tokens`。真实服务可能使用不同编码、角色分隔符、工具描述和隐藏包装。接入具体模型时应核实其窗口、生成上限与 tokenizer，并用真实响应的 usage 观察偏差；余量不是模型永不超限的证明。

`pack` 的**函数定义节选**如下。依赖同文件的 `copy`、`dumps`、`measure`，完整代码在 [context.py](code/context.py)；定义本身不打印。

```python
limit = window - output_reserve - framing_margin
packed = copy.deepcopy(messages)
packed += [{"role": "user", "content": dumps(item)} for item in mandatory]
if measure(packed) > limit:
    raise ValueError(f"mandatory_overflow: {measure(packed)} > {limit}")
```

系统提示、当前任务、当前政策、已验证的历史事实属于必需块。它们放不下时直接报错，因为继续删除会改变任务或约束。可选块按传入顺序逐一试放，每次重新测量整个消息串；`decisions` 记录 id、是否纳入和试放后的数值。

排序决定资料的装入顺序；事实冲突和缺证据仍要单独处理。

## 工具结果裁剪

[dry-run.log](fixtures/docs/dry-run.log) 前两行是运行元数据，中间 80 行是成功心跳，最后两行才是：

```text
rollback_check=FAILED reason=missing_permission
release_gate=BLOCKED
```

这是**输入文件节选**，不作为代码执行。取 `body[:180]` 得到的几乎全是“启动正常”“心跳正常”，不能回答“回滚演练是否通过”。本例真实实验中，头部裁剪保留失败证据为 False。

`crop_tool_result` 保留头两行、尾两行，同时保留文件版本、总行数、原始 SHA-256、原行号、遗漏区间与 `truncated` 标志。输出的关键字段是：

| 字段 | 本次值或结构 | 后续怎样使用 |
|---|---|---|
| path / version | docs/dry-run.log / run-17 | 确认回读哪份文件、哪次演练 |
| total_lines | 84 | 知道已拿到的不是全部内容 |
| omitted_lines | [3, 82] | 需要中段信息时回读该范围 |
| lines | 1、2、83、84 行及正文 | 引用错误位置，保留失败结论 |
| source_sha256 | 原正文的 64 位十六进制摘要 | 回读前确认源文件未被替换 |

完整函数在 [context.py](code/context.py)。裁剪后的 dict 是待嵌入消息的证据对象；若接回第三章的执行循环，还要放进对应 `tool_call_id` 的 tool 消息。

结构裁剪把该日志对象从 962 个编码 token 减到 150 个，并保留了失败行。但“头尾”只适合本次已知日志结构；如果异常在第 40 行，仍会遗漏。实际工具应按结构化状态字段或错误定位结果选取关键行，随后保留可回读路径；不能把头尾策略当作通用错误搜索。

## 预算与证据验收

**两次完整实验命令**，工作目录、依赖与 fixtures 同 README。输出分别写到两个独立目录：

```bash
python code/run_experiments.py
python code/run_experiments.py --window 1301 --out runs/tight
```

准确对照：

| 实验 | 本地输入 / 上限 | 日志块 | 发布检查 |
|---|---:|---|---|
| default | 402 / 1500 | 纳入，失败证据可见 | BLOCKED |
| tight | 234 / 401 | 试放需要 402，故排除 | NEEDS_EVIDENCE |

把日志放在“可选预算块”仅表示打包器可以排除它，不表示业务允许缺少演练结果。后面的 `acceptance` 检查仍要求演练证据；没有证据时应该换一个更窄的工具查询或提高预算，然后再次检查。

可以把窗口改为 1302，输入上限变成 402，恰好容纳同一份消息；发布状态又变为 BLOCKED。这里改变的是可见证据，不是演练本身。原始 fixture 从未修改。
