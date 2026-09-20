"""教学候选评审。无模型 API；用于隔离测量调度与合并，不评价 LLM 智力。"""
import asyncio, json
from . import Task, Router, Supervisor, merge_results

CANDIDATES = [
    {"name": "A", "quality": 0.91, "latency_ms": 18, "memory_mb": 200},
    {"name": "B", "quality": 0.93, "latency_ms": 29, "memory_mb": 150},
    {"name": "C", "quality": 0.88, "latency_ms": 12, "memory_mb": 90},
]

def deterministic_baseline(candidates):
    valid = [x for x in candidates if x["latency_ms"] <= 20 and x["memory_mb"] <= 220]
    return max(valid, key=lambda x: x["quality"])["name"] if valid else None

async def quality_worker(task):
    await asyncio.sleep(task.payload.get("delay", 0.02))
    return {"quality": {x["name"]: x["quality"] for x in task.payload["candidates"]}}

async def constraint_worker(task):
    await asyncio.sleep(task.payload.get("delay", 0.02))
    return {"feasible": [x["name"] for x in task.payload["candidates"]
                         if x["latency_ms"] <= 20 and x["memory_mb"] <= 220]}

def tasks():
    return [Task("quality", "quality", {"candidates": CANDIDATES}, ("quality",)),
            Task("constraints", "constraints", {"candidates": CANDIDATES}, ("feasible",))]

def choose(merged):
    if not merged.complete:
        raise ValueError("cannot decide with missing review")
    feasible = merged.values["feasible"]
    return max(feasible, key=lambda n: merged.values["quality"][n]) if feasible else None

async def experiment():
    router = Router({"quality": quality_worker, "constraints": constraint_worker})
    rows, traces = [], {}
    for mode, concurrency in [("single_worker_serial", 1), ("two_workers_parallel", 2)]:
        requested = tasks()
        result = await Supervisor(router, concurrency).run(requested)
        merged = merge_results(result.results, expected_task_ids=[task.task_id for task in requested])
        rows.append({"mode": mode, "selected": choose(merged), "calls": len(result.results),
                     "max_active": result.max_active, "elapsed_ms": result.trace[-1]["elapsed_ms"]})
        traces[mode] = result.trace
    rows.append({"mode": "deterministic_baseline", "selected": deterministic_baseline(CANDIDATES),
                 "calls": 0, "max_active": 0})
    return {"data": "synthetic teaching fixture", "rows": rows, "traces": traces}

if __name__ == "__main__":
    print(json.dumps(asyncio.run(experiment()), ensure_ascii=False, indent=2))
