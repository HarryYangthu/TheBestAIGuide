from collections.abc import Awaitable, Callable
from .contracts import Task

Worker = Callable[[Task], Awaitable[dict]]

class Router:
    """kind 是已经校验的任务类型，不由角色自述决定权限。"""
    def __init__(self, workers: dict[str, Worker]):
        self.workers = dict(workers)

    def resolve(self, kind: str) -> Worker:
        try:
            return self.workers[kind]
        except KeyError as exc:
            raise ValueError(f"unsupported task kind: {kind}") from exc
