"""Run from repo root: python scripts/run_python.py -m learning_workbench.cli TASK."""
import argparse
import asyncio
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
from rag_pipeline import Document, Index
from .providers import ActionModel, OneToolModel, ChatAPI, LocalChat, ProviderError

PROJECT = Path(__file__).resolve().parents[2]


def read_jsonl(name):
    return [json.loads(line) for line in (PROJECT/'fixtures'/name).read_text().splitlines() if line.strip()]


def corpus(): return [Document(**row) for row in read_jsonl('corpus.jsonl')]


def make_provider(args):
    if args.provider=='api': return ChatAPI.from_env()
    if args.provider=='local':
        p=LocalChat(args.model, revision=args.revision)
        if args.model_label:p.model=args.model_label
        return p
    raise ValueError('this task requires --provider local or api; it never substitutes fake model output')


class OfflineToolPolicy:
    """Domain-limited deterministic baseline, not a model emulator."""
    calls=()
    def decide(self,state):
        from agent_loop import Action
        import re
        if state.observations:
            data=state.observations[-1].get('data',{})
            answer=str(data['sum']) if 'sum' in data else ' '.join(d['text'] for d in data.get('documents',[]))
            return Action('finish',answer=answer or 'No evidence found.')
        match=re.search(r'(\d+)\s*\+\s*(\d+)',state.task)
        if match:return Action('tool','add',{'a':int(match[1]),'b':int(match[2])})
        return Action('tool','search',{'query':'fan '+state.task})


def model_loop(provider, output, *, one_tool=False):
    from agent_loop import Tool, run_agent
    data=[{'id':'fan','text':'FAN-01: power off before inspecting the cooling fan.'}]
    def search(args):
        if set(args)!={'query'} or not isinstance(args['query'],str):raise ValueError('query required')
        return {'documents':[d for d in data if 'fan' in args['query'].lower() or 'FAN-01' in args['query']]}
    def add(args):
        if set(args)!={'a','b'} or any(type(args[k]) not in {int,float} for k in ['a','b']):raise ValueError('two numbers required')
        return {'sum':args['a']+args['b']}
    results=[]
    for case in read_jsonl('agent-tasks.jsonl'):
        policy=(OneToolModel if one_tool else ActionModel)(provider, {'search':'Read fan manual; arguments {query:string}',
                                      'add':'Add two numbers; arguments {a:number,b:number}'}, max_calls=4)
        if provider is None:policy=OfflineToolPolicy()
        state=run_agent(policy,{'search':Tool(search),'add':Tool(add)},case['query'],
                         max_steps=4,trace_path=str(output/(case['id']+'.trace.jsonl')))
        events=[json.loads(line) for line in (output/(case['id']+'.trace.jsonl')).read_text().splitlines()]
        called=[e['data']['name'] for e in events if e['kind']=='tool_call']
        # Runtime observations carry the tool name under `name` in this version;
        # final answer scoring uses independent task labels, not the model's claim.
        result={'id':case['id'],'state':asdict(state),'usage':[asdict(c) for c in policy.calls],
                'expected_tool':case['expected_tool'], 'called_tools':called,
                'tool_selection_correct':case['expected_tool'] in called,
                'answer_match':all(s.casefold() in state.answer.casefold() for s in case['answer_contains']),
                'completed':state.status=='completed','workflow':'deterministic' if provider is None else ('one-tool-then-answer' if one_tool else 'free-loop')}
        results.append(result)
    from .redaction import publishable
    for case in read_jsonl('agent-tasks.jsonl'):
        path=output/(case['id']+'.trace.jsonl')
        rows=[publishable(json.loads(line)) for line in path.read_text().splitlines() if line.strip()]
        path.write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in rows))
    return publishable(results)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('task',choices=['agent','retrieval','rag','memory','multi','documents','context','stats','queue','judge','pairwise','injection','tokenizer','versions'])
    parser.add_argument('--output',default='.runs/learning-workbench')
    parser.add_argument('--provider',choices=['local','api'])
    parser.add_argument('--one-tool',action='store_true',help='host routes one tool result to an answer stage')
    parser.add_argument('--model',default='Qwen/Qwen2.5-0.5B-Instruct')
    parser.add_argument('--model-label');parser.add_argument('--revision')
    parser.add_argument('--embedding');parser.add_argument('--embedding-revision')
    parser.add_argument('--reranker');parser.add_argument('--reranker-revision')
    args=parser.parse_args();output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    if args.task=='agent': result=model_loop(make_provider(args) if args.provider else None,output,one_tool=args.one_tool)
    elif args.task=='retrieval':
        from .retrieval import SentenceEncoder,CrossEncoderRanker,retrieval_comparison
        encoder=SentenceEncoder(args.embedding,args.embedding_revision) if args.embedding else None
        ranker=CrossEncoderRanker(args.reranker,args.reranker_revision) if args.reranker else None
        result={'embedding':args.embedding,'embedding_revision':args.embedding_revision,
                'reranker':args.reranker,'reranker_revision':args.reranker_revision,
                'trials':retrieval_comparison(corpus(),read_jsonl('retrieval-tasks.jsonl'),encoder,ranker)}
    elif args.task=='rag':
        from .retrieval import generated_answer
        index=Index()
        for doc in corpus():index.upsert(doc)
        provider=make_provider(args);result=[]
        for task in read_jsonl('generation-tasks.jsonl'):
            try:
                answer=generated_answer(index,task['query'],provider,tenant=task['tenant'],version=task['version'])
                result.append({'id':task['id'],'question':task['query'],'answer':answer,
                               'expected_abstained':task['expected_abstained'],
                               'abstention_correct':answer['abstained']==task['expected_abstained']})
            except ProviderError as error:
                result.append({'id':task['id'],'error':str(error),'abstention_correct':False})
    elif args.task=='memory':
        from .memory import evaluate_memory
        with tempfile.TemporaryDirectory() as temp:result=evaluate_memory(read_jsonl('memory-tasks.jsonl'),temp)
    elif args.task=='multi':
        from .planning import research_demo
        result={mode:asyncio.run(research_demo(concurrency=n)) for mode,n in [('single',1),('parallel',2)]}
    elif args.task in {'context','stats','queue','judge','pairwise','injection','tokenizer','versions'}:
        from .experiments import context_experiment,statistics_experiment,queue_experiment,judge_answers
        if args.task=='stats':result=statistics_experiment()
        elif args.task=='queue':result={name:asyncio.run(queue_experiment(max_queue=n)) for name,n in [('unbounded',0),('bounded',3)]}
        elif args.task=='context':result=context_experiment(make_provider(args).tokenizer if args.provider=='local' else None)
        elif args.task=='judge':result=judge_answers(read_jsonl('judge-tasks.jsonl'),make_provider(args) if args.provider else None)
        elif args.task=='versions':
            from .retrieval import compare_versions
            index=Index()
            for doc in corpus():index.upsert(doc)
            result={name:compare_versions(index,'FAN-01',versions,tenant='alpha') for name,versions in [('available',['1','2']),('missing',['1','3'])]}
        elif args.task=='tokenizer':
            from .practice import tokenizer_experiment
            if args.provider!='local':raise ValueError('tokenizer needs local provider')
            result=tokenizer_experiment(make_provider(args).tokenizer)
        else:
            from .model_evaluation import injection,pairwise
            provider=make_provider(args)
            result=injection(provider) if args.task=='injection' else pairwise(read_jsonl('pairwise-tasks.jsonl'),provider)
    else:
        from .documents import markdown_blocks,parent_evidence,parse_pdf
        text=(PROJECT/'fixtures/structured-manual.md').read_text()
        blocks=markdown_blocks(text)
        result={'blocks':[asdict(b) for b in blocks],
                'parent_of_table':[asdict(b) for b in parent_evidence(next(b for b in blocks if b.kind=='table'),blocks)],
                'pdf':parse_pdf(PROJECT/'fixtures/comparison.pdf')}
    target=output/(args.task+'.json')
    from .redaction import publishable
    target.write_text(json.dumps(publishable(result),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'task':args.task,'report':str(target),'status':'executed'},ensure_ascii=False))


if __name__=='__main__':main()
