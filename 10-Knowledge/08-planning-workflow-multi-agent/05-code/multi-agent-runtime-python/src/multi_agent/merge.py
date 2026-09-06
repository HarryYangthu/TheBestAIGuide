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

def merge_results(results: list[WorkerResult]) -> Merged:
    values, owners, missing = {}, {}, []
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
