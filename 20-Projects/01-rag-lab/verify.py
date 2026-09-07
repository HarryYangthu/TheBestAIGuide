"""Recompute metrics from saved evidence and predictions; reject tampered artifacts."""
import argparse
import json
from pathlib import Path
from rag_lab.pipeline import read_data
from rag_lab.metrics import evidence_score, facts, score_prediction


def verify(output):
    output=Path(output);errors=[]
    try:
        saved=json.loads((output/'summary.json').read_text())
        rows=[json.loads(line) for line in (output/'results.jsonl').read_text().splitlines()]
        config=saved['config'];gold={r['id']:r for r in read_data(config['split'])[:config['questions']]}
        methods=list(saved['summary'])
        expected={(key,method) for key in gold for method in methods}
        if len(rows)!=len(expected) or {(r['id'],r['method']) for r in rows}!=expected: errors.append('missing_or_duplicate_tasks')
        for r in rows:
            source=gold[r['id']];support=list(map(list,zip(source['supporting_facts']['title'],source['supporting_facts']['sent_id'])))
            if r['gold_answer']!=source['answer'] or r['gold_facts']!=support: errors.append('gold_tampered:'+r['id'])
            lookup=dict(zip(source['context']['title'],source['context']['sentences']))
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
        html=(output/'index.html').read_text()
        embedded=json.loads(html.split('<script id="data" type="application/json">',1)[1].split('</script>',1)[0])
        if embedded['rows']!=rows or embedded['summary']!=saved['summary']: errors.append('dashboard_data_mismatch')
    except (OSError,ValueError,KeyError,IndexError,TypeError,ZeroDivisionError) as exc:
        errors.append(type(exc).__name__)
    return {'passed':not errors,'errors':errors,'scope':'来源映射、逐题评分、汇总与HTML数据一致性；不评判学习者理解程度'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args()
    result=verify(args.output);print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['passed'] else 1)
