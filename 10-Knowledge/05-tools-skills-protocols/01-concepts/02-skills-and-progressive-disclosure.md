# Skills 与渐进披露：需要时再加载执行知识

> 状态：draft。正文用 Pine SDK 教学任务解释方法；可运行练习使用仓库已有的证据比较包，不代表 Mini Agent 已支持自动加载 Skill。

同一个 Agent 已经会读文件、会写报告，第一次比较 Pine SDK 时仍然漏掉旧版出处。你补一句“每项都引用新旧两边”，第二次又忘了排除预览稿。继续往系统提示词里加规则，几周后它就会堆满各种任务的方法：升级比较、日志排查、论文调研，全挤在每次调用中。

更合适的做法是把“如何完成一类任务”单独保存。遇到版本比较时，加载比较方法；排查日志时，换成诊断方法。**Skill 就是可以按需取用的一份工作方法，必要时附上脚本、模板和参考资料。** 它的价值来自步骤确实能帮助任务，而不是目录叫了一个特殊名字。

## 为什么工具齐全，任务仍然可能做错

`read_file` 告诉程序怎样读到资料，却没有规定该先找正式版还是预览稿、怎样比较单位、什么时候可以交付。这些属于方法。对于 Pine SDK，读完资料后应该逐项核对 auth、timeout、retry，每项保留旧值、新值及两侧原文；缺一侧就继续找，找不到则说明缺口。

这个方法可以写进普通提示词，也可以写成按需加载的文件。采用 Skill 后，方法能独立修改、复用和评测，不必每次让用户重述一遍。但它仍通过上下文影响模型，不会改动模型权重，也不会强制模型一定执行所有步骤。必须遵守的权限与验收条件仍由程序检查。

同样叫“保存下来的内容”，三类东西作用不同：工具是 `read_file(path)` 这样的可执行操作；Skill 是“先核对版本，再做双侧引用”的步骤；长期记忆可能记录“用户偏好表格”。一份旧任务的结论“v2 超时为 10 秒”则是带适用版本的事实，不能不经核对就作为以后所有 SDK 的结论。Skill 可以要求读取记忆，但二者不应混在一个无来源的文本堆里。

## 三层加载各解决什么问题

“渐进披露”听起来抽象，实际就是**先看介绍，决定要用后看方法，做到某一步再打开相关附件**。假设宿主登记了三个 Skill：版本比较、日志诊断、论文梳理。用户要 Pine 升级清单，加载过程可以这样发生。

第一步，模型只看到名称和简短适用描述，例如“比较给定版本的资料，输出带双方证据的变更清单”。它还没有看到比较步骤、模板和全部案例。这个描述要足以区别“比较版本”和“润色已有报告”。如果只写“帮助用户完成工作”，三个 Skill 可能都被选中。

第二步，选中版本比较后，宿主读取主说明。此时模型才知道先辨别正式版、保留双侧出处、缺资料时停止哪一部分。注意，选中只是一次决策，读取才是实际动作：轨迹中应能找到读取了哪个文件、哪个版本，不能仅凭模型说“我将使用该技能”就认定加载成功。

第三步，需要生成表格时再读取模板；需要检查结构化引用时再运行脚本。模型不必先读完每个脚本的全部源码才能使用它，但必须知道输入约定和失败含义。相反，如果方法写“运行校验脚本”，却不交代脚本路径和参数，模型仍得猜测，所谓技能包没有解决实际问题。

这种目录约定可采用 [Agent Skills 规范](https://agentskills.io/specification)中的 `SKILL.md`、可选脚本与资源结构。文件名是该格式的要求，具体宿主怎样发现和激活仍由其实现决定；自研 Agent 也可以用别的存储方式加载方法，不是所有 Agent 都必须识别 `SKILL.md`。

## 一份足够具体的小 Skill 应该怎么写

下面是 Pine 场景的**教学示例**，用来说明内容粒度，不是仓库已经安装的新技能：

```markdown
---
name: sdk-upgrade-comparison
description: 比较给定 SDK 的两个正式版本，输出带双方出处的变更清单。
---
先确认产品、旧版、新版和允许读取的资料目录。
读取版本声明；预览稿只作背景，不替代正式版结论。
逐项填写旧值、新值、旧版出处、新版出处。
单位或适用条件不同，先说明差异，不能直接比较数字。
缺少一侧资料时标记缺口，不补造值。
写报告后检查：每项引用存在，而且原文确实支持该项结论。
```

这里的每句话都对应一个可观察的错误。为什么先确认版本？因为 `preview.md` 的 5 秒不是 v2 正式版的 10 秒。为什么保留旧版出处？因为只知道新版值，无法证明它是一项变化。为什么检查语义？因为引用真实存在，也可能讨论另一个参数。

好的方法不需要塞入所有规则。版本比较中适用条件很重要，可以正文强调；详细输出模板则放附件。若方法已经稳定到不需要模型决策，例如按固定字段转成表格，就交给脚本执行。让模型反复生成相同排版，会增加格式出错的机会。

Skill 也不能自己授予权限。主说明即使写了“运行任意命令”或声明可用工具，实际权限仍取决于宿主授权。读取第三方包与执行其脚本是不同动作；脚本会产生真实文件或网络操作，应通过现有工具执行规则处理。已授权的操作无需因为加载 Skill 而重复询问，但加载本身不会扩展授权范围。

## 顺着一个包找到真正运行的部分

仓库已有 [evidence-comparison](../../../20-Projects/learning-workbench/skills/evidence-comparison/SKILL.md)，可用于给定资料的证据比较。按主说明、[案例输入](../../../20-Projects/learning-workbench/skills/evidence-comparison/references/cases.json)、[compare.py](../../../20-Projects/learning-workbench/skills/evidence-comparison/scripts/compare.py)、[输出模板](../../../20-Projects/learning-workbench/skills/evidence-comparison/assets/comparison.md)的顺序看，就能找到方法怎样落地。

下面节选脚本里决定“写结论还是报错”的部分。`sources` 是按来源 ID 建立的字典，`claims` 是调用方整理的主张：

```python
for claim in data['claims']:
    source = sources.get(claim['source_id'])
    quote = claim.get('quote', '')
    if source is None:
        rows.append([claim['axis'], claim['source_id'], '证据不足', '', '缺少来源'])
        continue
    if not quote or quote not in source['text']:
        raise ValueError('quote not found in supplied source')
    rows.append([
        claim['axis'], source['id'] + '@' + source['version'],
        claim['text'], quote,
        claim.get('limits', '仍需人工检查语义支持')
    ])
```

如果来源 A 写着 `A supports CSV.`，引用 `supports CSV` 可以通过。若来源 ID 写成不存在的 B，表格会保留一行“证据不足”；若 A 存在，但引用被改成 `supports JSON`，脚本直接报错。这两种失败分别表示缺来源和错误引用，处理方式不同。

还有一个脚本发现不了的反例：原文写“旧版超时为 30 秒”，引用也完整正确，但结论写“新版超时为 30 秒”。字符串确实存在，脚本仍会通过。它只检查引文是否出现在指定来源中，没有核对行号或字符偏移，也不理解版本对应关系；模型或人工需要继续检查主张是否受到原文支持。脚本也不会搜索网页或补齐资料。

## 用预算说明渐进披露的收益

假设有 100 个 Skill，每个介绍 40 token、正文 1,200 token，一次任务实际只用两个。这些是教学假设，不是实测值。把所有内容放入上下文需要 `100 × (40 + 1200) = 124000` token；先放全部介绍，再加载两个正文，需要 `100 × 40 + 2 × 1200 = 6400` token，暂不算附件。

节省来自没有提前加载用不到的方法。代价是必须正确选中所需 Skill，并允许执行过程中补充加载。若用户明确要版本比较，系统却漏选了比较方法，输入再短也没有意义。因此不应只评估节省多少 token，还应检查选择错误是否导致质量下降。对于只有一种固定任务的小 Agent，直接放一份短方法可能更简单。

## 应怎样评测一项 Skill

先把“选对方法”和“用了方法后做对任务”分开。仓库案例里的 `expected_route` 是作者给出的期望标签：比较温度上限应选用，普通润色应跳过，不同硬件的速度比较应说明条件不可比。这些标签没有经过真实宿主自动选择实验，不能报成 Skill 命中率。

执行部分可以先独立验证。在仓库根目录用 `python -X utf8` 启动 Python 会话，再粘贴下面代码，只依赖标准库。开启 UTF-8 是因为现有脚本读取模板时使用系统默认编码，可避免部分 Windows 环境把中文模板读错。若把代码保存为脚本，也用 `python -X utf8 脚本路径` 运行：

```python
import json, runpy
from pathlib import Path
root = Path("20-Projects/learning-workbench/skills/evidence-comparison")
compare = runpy.run_path(str(root / "scripts/compare.py"))["compare"]
cases = json.loads((root / "references/cases.json").read_text(encoding="utf-8"))
output = Path(".runs/skills-lesson")
output.mkdir(parents=True, exist_ok=True)
for case in cases:
    if "data" in case:
        (output / (case["id"] + ".md")).write_text(
            compare(case["data"]), encoding="utf-8")
```

应生成 `trigger.md`、`ambiguous.md` 和 `insufficient.md`。第一份有 70 C 与 68 C 的两行对照；第二份只报告 CPU-X 上的已有数据；第三份明确 B 缺少来源。没有生成 `negative.md`，因为该案例没有执行数据，不是脚本实测了宿主拒绝触发。可对照[已保存结果](../../../20-Projects/learning-workbench/artifacts/offline/skill-cases.json)。

后续接入真实宿主时，应固定任务与资料，分别保存未加载和加载 Skill 的结果；检查版本错误、漏引用等是否减少，同时记录新增调用和输入长度。若选择正确但仍漏引用，改主说明；若普通润色经常触发，改描述；若正确引用被脚本拒绝，检查脚本。这样才知道修改该落在哪一层。

**练习 1：** 用户只说“把这份升级清单写得通顺”，是否应重新执行全部证据比较？答案：通常不用，除非用户同时要求核实内容。可以只做润色，避免无关加载和意外改变结论。

**练习 2：** 让来源文本保留 `70 C`，把结论改成“温度上限为 700 C”，脚本会拒绝吗？答案：不会，只要引用仍为 `70 C`。这说明引文的字符串匹配没有覆盖数值语义，最终验收还需要核对结论与证据。

返回 [Agent 核心组件总览](../../03-agent-core/01-concepts/04-core-components.md)，结合上下文管理理解何时加载方法。
