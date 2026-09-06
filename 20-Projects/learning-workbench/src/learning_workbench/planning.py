"""Executable dependency graph, cancellation and evidence-driven invalidation."""
import asyncio
from copy import deepcopy
from dataclasses import dataclass
import time


@dataclass(frozen=True)
class Task:
    name: str
    dependencies: tuple[str, ...]
    run: object


class Plan:
    def __init__(self, tasks, *, concurrency=2, max_executions=20, timeout=10):
        self.tasks={t.name:t for t in tasks}
        if len(self.tasks)!=len(tasks) or concurrency<1 or max_executions<1 or timeout<=0:
            raise ValueError('duplicate tasks or invalid budgets')
        pending=set(self.tasks); resolved=set()
        while pending:
            ready={n for n in pending if set(self.tasks[n].dependencies)<=resolved}
            if not ready: raise ValueError('cycle or missing predecessor')
            pending-=ready; resolved|=ready
        self.concurrency,self.max_executions,self.timeout=concurrency,max_executions,timeout
        self.results={};self.trace=[];self.version=1;self.executions=0

    def invalidate(self, changed):
        if not set(changed)<=self.tasks.keys():raise ValueError('unknown changed task')
        affected=set(changed)
        while True:
            expanded=affected|{n for n,t in self.tasks.items() if set(t.dependencies)&affected}
            if expanded==affected:break
            affected=expanded
        for n in affected:self.results.pop(n,None)
        self.version+=1
        self.trace.append({'event':'replan','version':self.version,'invalidated':sorted(affected)})
        return affected

    async def execute(self):
        async def all_tasks():
            pending=set(self.tasks)-self.results.keys()
            while pending:
                ready=sorted(n for n in pending if set(self.tasks[n].dependencies)<=self.results.keys())
                if not ready:raise RuntimeError('unresolved dependencies')
                # Batch at most N ready tasks. Dependencies must be committed
                # before scheduling children; partial results remain inspectable.
                batch=ready[:self.concurrency]
                if self.executions+len(batch)>self.max_executions:raise RuntimeError('execution budget exhausted')
                self.executions+=len(batch)
                async def one(name):
                    t=self.tasks[name];inputs=deepcopy({d:self.results[d] for d in t.dependencies})
                    self.trace.append({'event':'start','task':name,'version':self.version,'inputs':inputs})
                    start=time.monotonic()
                    try:
                        result=await t.run(inputs)
                        self.results[name]=deepcopy(result)
                        self.trace.append({'event':'completed','task':name,'version':self.version,
                                           'output':deepcopy(result),'elapsed_seconds':time.monotonic()-start})
                    except BaseException as error:
                        self.trace.append({'event':'failed','task':name,'error':type(error).__name__})
                        raise
                running=[asyncio.create_task(one(n)) for n in batch]
                try:await asyncio.gather(*running)
                except BaseException:
                    for t in running:t.cancel()
                    await asyncio.gather(*running,return_exceptions=True)
                    raise
                pending-=set(batch)
            return deepcopy(self.results)
        return await asyncio.wait_for(all_tasks(),timeout=self.timeout)


async def research_demo(*, concurrency=2):
    sources={'a':{'version':1,'latency_ms':40},'b':{'version':1,'latency_ms':60}}
    async def planner(_):return {'question':'Compare A/B latency under the same fixture','sources':['a','b']}
    async def researcher_a(_):await asyncio.sleep(.01);return deepcopy(sources['a'])
    async def researcher_b(_):await asyncio.sleep(.01);return deepcopy(sources['b'])
    async def writer(inputs):
        a,b=inputs['research-a'],inputs['research-b']
        return {'difference_ms':b['latency_ms']-a['latency_ms'],'evidence':inputs}
    async def reviewer(inputs):
        report=inputs['writer'];e=report['evidence']
        return {'valid':report['difference_ms']==e['research-b']['latency_ms']-e['research-a']['latency_ms']}
    tasks=[Task('planner',(),planner),Task('research-a',('planner',),researcher_a),
           Task('research-b',('planner',),researcher_b),Task('writer',('research-a','research-b'),writer),
           Task('reviewer',('writer',),reviewer)]
    plan=Plan(tasks,concurrency=concurrency)
    first=await plan.execute()
    sources['a']={'version':2,'latency_ms':45}
    invalidated=plan.invalidate({'research-a'})
    second=await plan.execute()
    assert second['writer']['difference_ms']==15 and second['reviewer']['valid']
    assert sum(t.get('task')=='research-b' and t['event']=='start' for t in plan.trace)==1
    return {'policy':'deterministic role workers, not independent model agents','first':first,'second':second,
            'invalidated':sorted(invalidated),'executions':plan.executions,'trace':plan.trace}
