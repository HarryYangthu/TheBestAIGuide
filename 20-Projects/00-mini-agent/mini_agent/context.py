"""Lesson 03: bound request text; never split a tool-call/result group."""
import json


def pack(messages, budget):
    # A group starts with an assistant message and includes ALL its tool results.
    prefix = messages[:2]
    groups = []
    for message in messages[2:]:
        if message["role"] == "assistant" or not groups:
            groups.append([])
        groups[-1].append(message)
    original = len(json.dumps(messages, ensure_ascii=False))
    removed = 0
    def assembled():
        notice = ([{"role": "system", "content":
                   f"已移除 {removed} 组较早动作。不要猜测已移除内容；必要时重新读取原文件。"}]
                  if removed else [])
        return prefix + notice + [m for group in groups for m in group]
    while len(json.dumps(assembled(), ensure_ascii=False)) > budget and len(groups) > 1:
        groups.pop(0)
        removed += 1
    packed = assembled()
    after = len(json.dumps(packed, ensure_ascii=False))
    if after > budget:
        raise ValueError("context_budget_exceeded: latest complete group cannot fit")
    return packed, {"before_chars": original, "after_chars": after, "removed_groups": removed}
