"""Recompute metrics from saved evidence and predictions; reject tampered artifacts."""
import argparse
import json
import math
from pathlib import Path
from rag_lab.pipeline import read_data
from rag_lab.retrieval import chunks, assemble
from rag_lab.metrics import evidence_score, facts, score_prediction


def verify(output):
    output=Path(output);errors=[];experiment_passed=False
    try:
        saved=json.loads((output/'summary.json').read_text())
        rows=[json.loads(line) for line in (output/'results.jsonl').read_text().splitlines()]
        config=saved['config'];gold={r['id']:r for r in read_data(config['split'])[:config['questions']]}
        methods=list(saved['summary'])
        if not methods or type(config['questions']) is not int or config['questions'] < 1 or len(gold)!=config['questions']:
            errors.append('invalid_task_count')
        if config['generation'] not in ('none','live') or config['chunk_size'] not in (1,3) or not 1<=config['top_k']<=20 or config['budget']<100:
            errors.append('invalid_configuration')
        def finite(value):
            if isinstance(value,float) and not math.isfinite(value): raise ValueError('non-finite metric')
            if isinstance(value,dict):
                for v in value.values(): finite(v)
            if isinstance(value,list):
                for v in value: finite(v)
        finite(saved);finite(rows)
        expected={(key,method) for key in gold for method in methods}
        if len(rows)!=len(expected) or {(r['id'],r['method']) for r in rows}!=expected: errors.append('missing_or_duplicate_tasks')
        for r in rows:
            source=gold[r['id']];support=list(map(list,zip(source['supporting_facts']['title'],source['supporting_facts']['sent_id'])))
            if r['gold_answer']!=source['answer'] or r['gold_facts']!=support: errors.append('gold_tampered:'+r['id'])
            lookup=dict(zip(source['context']['title'],source['context']['sentences']))
            if r['question']!=source['question'] or r['gold_evidence']!=[{'title':t,'sent_id':i,'text':lookup[t][i]} for t,i in support]: errors.append('display_gold:'+r['id'])
            documents=chunks(source['context'],config['chunk_size'])
            doc_lookup={(d['title'],tuple(d['sent_ids'])):i for i,d in enumerate(documents)}
            rank_ids=[doc_lookup[(d['title'],tuple(d['sent_ids']))] for d in r['ranking']]
            if len(rank_ids)!=min(20,len(documents)) or len(set(rank_ids))!=len(rank_ids): errors.append('invalid_ranking:'+r['id'])
            expected_context,used=assemble(documents,[(i,d['score']) for i,d in zip(rank_ids,r['ranking'])],config['top_k'],config['budget'])
            if r['context']!=expected_context or r['context_chars']!=used: errors.append('context_assembly:'+r['id'])
            for d in r['ranking']+r['context']:
                if d['text']!=' '.join(lookup[d['title']][i] for i in d['sent_ids']) or d['facts']!=[[d['title'],i] for i in d['sent_ids']]: errors.append('source_mapping:'+r['id'])
            for k in (1,3,5,10,20):
                actual=evidence_score(facts(r['ranking'][:k]),support)['recall']
                if abs(actual-r['recall'][str(k)])>1e-10: errors.append('recall:'+r['id'])
            for field,docs in [('candidate_complete',r['ranking'][:20]),('selected_complete',r['ranking'][:config['top_k']]),('context_complete',r['context'])]:
                if evidence_score(facts(docs),support)['complete']!=r[field]: errors.append(field+':'+r['id'])
            if sum(len(d['title'])+len(d['text'])+30 for d in r['context'])>config['budget']: errors.append('context_budget')
            if config['generation']=='none':
                if r['prediction'] is not None or r['answer_metrics'] is not None: errors.append('fabricated_prediction')
                if r['calls']!=0 or r['error'] is not None or r.get('model_events'): errors.append('unexpected_model_execution')
            elif r['error']:
                if r['answer_metrics']!={'em':0,'f1':0,'citation_f1':0,'citation_validity':0,'citation_visible':0}: errors.append('failure_score:'+r['id'])
            elif not r['error']:

                actual=score_prediction(r['prediction'],source['answer'],support,source['context'],r['context'])
                if actual!=r['answer_metrics']: errors.append('answer_metrics:'+r['id'])
        for method in methods:
            group=[r for r in rows if r['method']==method];summary=saved['summary'][method]
            for key in ('candidate_complete','selected_complete','context_complete'):
                if abs(sum(r[key] for r in group)/len(group)-summary[key])>1e-10: errors.append('summary:'+key)
            for k in ('1','3','5','10','20'):
                if abs(sum(r['recall'][k] for r in group)/len(group)-summary['recall'][k])>1e-10: errors.append('summary:recall')
            if sum(r['calls'] for r in group)!=summary['calls'] or sum(r['error'] is not None for r in group)!=summary['errors']: errors.append('summary:execution')
            for key,field in [('answer_em','em'),('answer_f1','f1')]:
                actual=None if config['generation']=='none' else sum(r['answer_metrics'][field] for r in group)/len(group)
                if actual!=summary[key]: errors.append('summary:'+key)
        checks={'all_tasks_recorded':len(rows)==len(gold)*len(methods),
                'unique_task_method':len({(r['id'],r['method']) for r in rows})==len(rows),
                'context_within_budget':all(r['context_chars']<=config['budget'] for r in rows),
                'generation_errors_absent':all(r['error'] is None for r in rows),
                'no_fabricated_predictions':all(r['prediction'] is None for r in rows) if config['generation']=='none' else True}
        experiment_passed=all(checks.values())
        if saved['acceptance']['checks']!=checks or saved['acceptance']['passed']!=experiment_passed: errors.append('acceptance_mismatch')
        paired_path=output/'paired-recall.json'
        if paired_path.exists():
            baseline={r['id']:r['recall']['5'] for r in rows if r['method']=='bm25'}
            paired={}
            for method in methods:
                if method=='bm25': continue
                delta=[r['recall']['5']-baseline[r['id']] for r in rows if r['method']==method]
                paired[method]={'improved':sum(x>1e-10 for x in delta),'same':sum(abs(x)<=1e-10 for x in delta),'regressed':sum(x< -1e-10 for x in delta)}
            if json.loads(paired_path.read_text())!=paired: errors.append('paired_comparison_mismatch')
        html=(output/'index.html').read_text()
        embedded=json.loads(html.split('<script id="data" type="application/json">',1)[1].split('</script>',1)[0])
        if embedded['rows']!=rows or any(embedded[k]!=saved[k] for k in ('config','summary','acceptance')): errors.append('dashboard_data_mismatch')
    except (OSError,ValueError,KeyError,IndexError,TypeError,ZeroDivisionError) as exc:
        errors.append(type(exc).__name__)
    return {'passed':not errors,'experiment_passed':experiment_passed and not errors,'errors':errors,'scope':'来源映射、逐题评分、汇总与HTML数据一致性；不评判学习者理解程度'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args()
    result=verify(args.output);print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['passed'] and result['experiment_passed'] else 1)
