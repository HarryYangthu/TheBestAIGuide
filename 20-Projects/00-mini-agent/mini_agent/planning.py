"""Lesson 05: editable plan state. A plan is not proof of completion."""


def update_plan(steps, reason):
    if not isinstance(steps, list) or not 1 <= len(steps) <= 8:
        raise ValueError("plan needs 1..8 steps")
    for item in steps:
        if (not isinstance(item, dict) or set(item) != {"task", "status"}
                or not isinstance(item["task"], str) or not item["task"].strip()
                or item["status"] not in ("pending", "doing", "done")):
            raise ValueError("each step needs task and pending/doing/done status")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("explain why this plan is created or changed")
    return {"steps": steps, "reason": reason}
