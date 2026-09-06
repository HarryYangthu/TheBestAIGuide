from pathlib import Path
import json
from . import EvalTask, run_suite, summarize, compare, write_report


def baseline(request, state, emit):
    """故意漏掉权限检查的确定性被测系统，用于演示定位与回归。"""
    emit("lookup",scope_checked=False)
    state["lookups"]+=1
    return {"answer":state["record"]["value"], "source_id":state["record"]["id"],"abstained":False}


def candidate(request,state,emit):
    state["lookups"]+=1
    authorized=request["tenant"]==state["record"]["tenant"]
    current=request["version"]==state["record"]["version"]
    emit("filter",authorized=authorized,current=current)
    if not authorized or not current:
        return {"answer":"no accessible evidence","source_id":None,"abstained":True}
    emit("lookup",scope_checked=True)
    return {"answer":state["record"]["value"],"source_id":state["record"]["id"],"abstained":False}


def load_tasks(path):
    return [EvalTask(**json.loads(line)) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]


def main():
    tasks=load_tasks("fixtures/tasks.jsonl")
    old,new=run_suite(tasks,baseline,trials=2),run_suite(tasks,candidate,trials=2)
    write_report(old,"reports/baseline")
    write_report(new,"reports/candidate")
    gate=compare(old,new)
    Path("reports/comparison.json").write_text(json.dumps(gate,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"baseline":summarize(old),"candidate":summarize(new),"gate":gate},indent=2))


if __name__ == "__main__": main()
