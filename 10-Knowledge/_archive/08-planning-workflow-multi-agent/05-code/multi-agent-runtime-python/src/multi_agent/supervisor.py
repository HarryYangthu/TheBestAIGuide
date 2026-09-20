"""有界并发、每任务总期限、异常转结果；外部取消传播给全部子任务。"""
import asyncio, copy, json, time
from dataclasses import replace
from .contracts import Task, WorkerResult, RunResult
from .router import Router

class Supervisor:
    def __init__(self, router: Router, concurrency: int = 2, max_tasks: int = 20):
        if concurrency < 1 or max_tasks < 1:
            raise ValueError("positive concurrency/max_tasks required")
        self.router, self.concurrency, self.max_tasks = router, concurrency, max_tasks
        self.last_trace = []

    async def run(self, tasks: list[Task]) -> RunResult:
        if len(tasks) > self.max_tasks:
            raise ValueError("task budget exceeded before any delegation")
        if len({t.task_id for t in tasks}) != len(tasks):
            raise ValueError("duplicate task_id")
        trace, active, max_active = [], 0, 0
        self.last_trace = trace
        start = time.monotonic()
        sem = asyncio.Semaphore(self.concurrency)
        def emit(task_id, event, **fields):
            trace.append(dict(seq=len(trace), task_id=task_id, event=event,
                              elapsed_ms=round((time.monotonic()-start)*1000, 3), **fields))
        async def perform(task):
            nonlocal active, max_active
            async with sem:
                worker = self.router.resolve(task.kind)
                active += 1
                max_active = max(max_active, active)
                emit(task.task_id, "started", kind=task.kind)
                try:
                    # deepcopy 隔开各 Worker 的嵌套输入；输出只在协调器合并。
                    values = await worker(replace(task, payload=copy.deepcopy(task.payload)))
                    if not isinstance(values, dict) or not all(isinstance(k, str) for k in values):
                        raise ValueError("worker output must be object with string keys")
                    json.dumps(values, allow_nan=False)
                    if set(values) != set(task.required_keys):
                        raise ValueError("worker output keys violate task contract")
                    emit(task.task_id, "completed", keys=sorted(values))
                    return WorkerResult(task.task_id, "ok", values)
                finally:
                    active -= 1
        async def guarded(task):
            emit(task.task_id, "queued")
            try:
                # 超时包含等待并发名额的时间。
                return await asyncio.wait_for(perform(task), task.timeout_s)
            except TimeoutError:
                emit(task.task_id, "timeout")
                return WorkerResult(task.task_id, "timeout", error="deadline exceeded")
            except asyncio.CancelledError:
                emit(task.task_id, "cancelled")
                raise
            except Exception as exc:
                emit(task.task_id, "error", error_type=type(exc).__name__)
                return WorkerResult(task.task_id, "error", error=str(exc))
        children = [asyncio.create_task(guarded(t)) for t in tasks]
        try:
            results = await asyncio.gather(*children)
        finally:
            for child in children:
                if not child.done():
                    child.cancel()
            await asyncio.gather(*children, return_exceptions=True)
        return RunResult(results, trace, max_active)
