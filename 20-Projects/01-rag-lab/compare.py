"""Check reproducibility against a saved retrieval reference, excluding timings."""
import argparse
import json
from pathlib import Path
from verify import verify


def compare(output, reference):
    paths=[Path(output),Path(reference)]
    checks=[verify(p) for p in paths]
    if not all(c['passed'] and c['experiment_passed'] for c in checks):
        return {'passed':False,'reason':'invalid_or_failed_experiment','validation':checks}
    bundles=[json.loads((p/'summary.json').read_text()) for p in paths]
    a,b=[x['config'] for x in bundles]
    if a['generation']!='none' or b['generation']!='none':
        return {'passed':False,'reason':'retrieval_only_comparison','hint':'真实生成有随机性，请比较答案、引用和失败案例，不要求逐题完全一致。'}
    keys=['split','questions','scope','chunk_size','top_k','budget','generation']
    mismatches=[k for k in keys if a.get(k)!=b.get(k)]
    methods=list(bundles[0]['summary'])
    if set(methods)!=set(bundles[1]['summary']): mismatches.append('methods')
    if set(methods)&{'dense','neural-hybrid','rerank'} and a.get('neural')!=b.get('neural'): mismatches.append('neural')
    if mismatches:
        return {'passed':False,'reason':'incompatible_configuration','fields':mismatches}
    rows=[{(r['id'],r['method']):r for r in map(json.loads,(p/'results.jsonl').read_text().splitlines())} for p in paths]
    if rows[0].keys()!=rows[1].keys(): return {'passed':False,'reason':'different_tasks'}
    changes=[]
    for key,current in rows[0].items():
        old=rows[1][key]
        fields=[field for field in ('recall','candidate_complete','selected_complete','context_complete') if current[field]!=old[field]]
        if fields: changes.append({'id':key[0],'method':key[1],'fields':fields,'recall5_delta':current['recall']['5']-old['recall']['5']})
    return {'passed':not changes,'reason':'matches_reference' if not changes else 'different_scores',
            'compared_rows':len(rows[0]),'changed_rows':len(changes),'changes':changes,
            'scope':'逐题检索指标复现；忽略耗时。不同不等于算法更差，改进实验应解释差异。'}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True)
    parser.add_argument('--reference',required=True)
    args=parser.parse_args()
    result=compare(args.output,args.reference)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['passed'] else 1)
