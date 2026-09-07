"""显式拒绝冲突；成功字段与缺失任务同时返回，不把部分成功当完整成功。"""
from dataclasses import dataclass
from typing import Any
from .contracts import WorkerResult

class MergeConflict(ValueError):
    pass

@dataclass
class Merged:
    values: dict[str, Any]
    missing_tasks: list[str]
    owners: dict[str, list[str]]

    @property
    def complete(self):
        return not self.missing_tasks

def merge_results(results: list[WorkerResult], *, expected_task_ids: list[str] | None = None) -> Merged:
    """Merge results; an expected manifest also detects completely absent results.

    Without a manifest, complete means only that all supplied results succeeded.
    It cannot infer tasks that the caller omitted before invoking this function.
    """
    received = [result.task_id for result in results]
    if len(set(received)) != len(received):
        raise ValueError("duplicate task result")
    if expected_task_ids is not None:
        if len(set(expected_task_ids)) != len(expected_task_ids):
            raise ValueError("duplicate expected task id")
        unexpected = set(received) - set(expected_task_ids)
        if unexpected:
            raise ValueError(f"unexpected task results: {sorted(unexpected)}")
    missing = [task_id for task_id in (expected_task_ids or []) if task_id not in received]
    values, owners = {}, {}
    for result in results:
        if result.status != "ok":
            missing.append(result.task_id)
            continue
        for key, value in result.values.items():
            if key in values and values[key] != value:
                raise MergeConflict(f"{key}: {owners[key]} conflicts with {result.task_id}")
            values[key] = value
            owners.setdefault(key, []).append(result.task_id)
    return Merged(values, missing, owners)
