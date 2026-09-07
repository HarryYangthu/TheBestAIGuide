import hashlib
import json
from pathlib import Path
from time import perf_counter
from .retrieval import Index, chunks, fuse, assemble, Neural
from .metrics import evidence_score, facts, score_prediction
from .model import Model
from .report import render

ROOT = Path(__file__).resolve().parents[1]


def read_data(split):
    manifest = json.loads((ROOT/'data/manifest.json').read_text())
    rows=[]
    for file, digest in manifest['files'].items():
        if not file.startswith(split + '-'):
            continue
        raw=(ROOT/'data'/file).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest: raise ValueError('dataset checksum mismatch')
        rows.extend(json.loads(line) for line in raw.decode().splitlines())
    if not rows or len({r['id'] for r in rows})!=len(rows): raise ValueError('missing or duplicate dataset')
    return rows


def run(output, split='eval', methods=('bm25','tfidf','hybrid'), top_k=5, budget=1800, chunk_size=1, generation='none', limit=None):
    output=Path(output)
    if output.exists(): raise ValueError('output exists; choose a new directory')
    if not 1<=top_k<=20 or budget<100 or chunk_size not in (1,3): raise ValueError('invalid configuration')
    allowed={'bm25','tfidf','hybrid','dense','neural-hybrid','rerank','active'}
    if not methods or len(set(methods))!=len(methods) or not set(methods)<=allowed: raise ValueError('invalid methods')
    if 'active' in methods and generation!='live': raise ValueError('active requires live model')
    data=read_data(split)
    if limit is not None:
        if limit<1: raise ValueError('limit must be positive')
        data=data[:limit]
    neural=Neural() if set(methods)&{'dense','neural-hybrid','rerank'} else None
    model=Model() if generation=='live' else None
    output.mkdir(parents=True)
    rows=[]
    for item in data:
        documents=chunks(item['context'],chunk_size)
        index=Index(documents)
        gold=list(map(list,zip(item['supporting_facts']['title'], item['supporting_facts']['sent_id'])))
        for method in methods:
            start=perf_counter();queries=[item['question']];prediction=None;answer_metrics=None;error=None
            calls=model.calls if model else 0;usage=model.tokens if model else 0
            bm=index.rank(item['question']) if method!='tfidf' else None
            before_rerank=None
            if method in ('bm25','active'): ranking=bm
            elif method=='tfidf': ranking=index.rank(item['question'],'tfidf')
            elif method=='hybrid': ranking=fuse(bm,index.rank(item['question'],'tfidf'))
            else:
                dense=neural.dense(item['question'],documents)
                ranking=dense if method=='dense' else fuse(bm,dense)
                if method=='rerank':
                    before_rerank=[i for i,_ in ranking]
                    ranking=neural.rerank(item['question'],documents,ranking)
            selected,used=assemble(documents,ranking,top_k,budget)
            retrieval_ms=(perf_counter()-start)*1000
            initial=before_rerank or [i for i,_ in ranking]
            rounds=[{'query':item['question'],'context':selected,'ranking_ids':[i for i,_ in ranking[:20]]}]
            try:
                if method=='active':
                    for _ in range(2):
                        choice=model.ask(item['question'],selected,True)
                        query=choice.get('query')
                        if query is None: break
                        if not isinstance(query,str) or not query.strip() or len(query)>500: raise ValueError('bad followup query')
                        queries.append(query)
                        t=perf_counter();ranking=fuse(ranking,index.rank(query));selected,used=assemble(documents,ranking,top_k,budget)
                        retrieval_ms+=(perf_counter()-t)*1000
                        rounds.append({'query':query,'context':selected,'ranking_ids':[i for i,_ in ranking[:20]]})
                if model:
                    prediction=model.ask(item['question'],selected)
                    answer_metrics=score_prediction(prediction,item['answer'],gold,item['context'],selected)
            except Exception as exc:
                error=type(exc).__name__
                answer_metrics={'em':0,'f1':0,'citation_f1':0,'citation_validity':0,'citation_visible':0}
            recall={str(k):evidence_score(facts([documents[i] for i,_ in ranking[:k]]),gold)['recall'] for k in (1,3,5,10,20)}
            candidate=evidence_score(facts([documents[i] for i,_ in ranking[:20]]),gold)['complete']
            pre=evidence_score(facts([documents[i] for i,_ in ranking[:top_k]]),gold)['complete']
            context=evidence_score(facts(selected),gold)['complete']
            diagnosis='前20候选缺少证据' if not candidate else 'Top-K筛选丢失证据' if not pre else '上下文预算丢失证据' if not context else '证据已齐全；未运行生成' if not model else '模型调用或格式异常' if error else '证据齐全但答案错误' if not answer_metrics['em'] else '答案正确（仍需检查引用）'
            visible={tuple(f) for f in facts(selected)}
            lookup=dict(zip(item['context']['title'],item['context']['sentences']))
            row={'id':item['id'],'question':item['question'],'method':method,'gold_answer':item['answer'],'gold_facts':gold,
                 'gold_evidence':[{'title':t,'sent_id':i,'text':lookup[t][i]} for t,i in gold],
                 'recall':recall,'candidate_complete':candidate,'selected_complete':pre,'context_complete':context,
                 'context_chars':used,'context':selected,'ranking':[dict(documents[i],score=float(score),initial_rank=initial.index(i)+1,in_context=any(tuple(f) in visible for f in documents[i]['facts'])) for i,score in ranking[:20]],
                 'queries':queries,'rounds':rounds,'prediction':prediction,'answer_metrics':answer_metrics,'error':error,'diagnosis':diagnosis,
                 'retrieval_ms':retrieval_ms,'elapsed_ms':(perf_counter()-start)*1000,'calls':model.calls-calls if model else 0,'tokens':model.tokens-usage if model else None}
            rows.append(row)
            with (output/'results.jsonl').open('a',encoding='utf-8') as stream: stream.write(json.dumps(row,ensure_ascii=False)+'\n')
    summary={}
    for method in methods:
        group=[r for r in rows if r['method']==method];n=len(group)
        summary[method]={'recall':{str(k):sum(r['recall'][str(k)] for r in group)/n for k in (1,3,5,10,20)},
                         **{key:sum(r[key] for r in group)/n for key in ('candidate_complete','selected_complete','context_complete')},
                         'answer_em':sum(r['answer_metrics']['em'] for r in group)/n if model else None,
                         'answer_f1':sum(r['answer_metrics']['f1'] for r in group)/n if model else None,
                         'errors':sum(r['error'] is not None for r in group),'calls':sum(r['calls'] for r in group)}
    checks={'all_tasks_recorded':len(rows)==len(data)*len(methods),'unique_task_method':len({(r['id'],r['method']) for r in rows})==len(rows),
            'context_within_budget':all(r['context_chars']<=budget for r in rows),'generation_errors_absent':all(r['error'] is None for r in rows),
            'no_fabricated_predictions':all(r['prediction'] is None for r in rows) if not model else True}
    bundle={'config':{'split':split,'questions':len(data),'scope':'HotpotQA distractor: per-question supplied documents','chunk_size':chunk_size,'top_k':top_k,'budget':budget,'generation':generation,'model':model.name if model else None},'summary':summary,'rows':rows,
            'acceptance':{'passed':all(checks.values()),'checks':checks,'meaning':'工程检查，不是答案全对或泛化能力通过'}}
    (output/'summary.json').write_text(json.dumps({k:v for k,v in bundle.items() if k!='rows'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    render(bundle,output)
    return bundle
