import argparse
import json
from rag_lab.pipeline import run

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output',required=True)
    p.add_argument('--split',choices=['dev','eval'],default='eval')
    p.add_argument('--methods',nargs='+',default=['bm25','tfidf','hybrid'])
    p.add_argument('--top-k',type=int,default=5)
    p.add_argument('--budget',type=int,default=1800)
    p.add_argument('--chunk-size',type=int,choices=[1,3],default=1)
    p.add_argument('--generation',choices=['none','live'],default='none')
    p.add_argument('--limit',type=int)
    b=run(**vars(p.parse_args()))
    print(json.dumps({'config':b['config'],'summary':b['summary'],'acceptance':b['acceptance']},ensure_ascii=False,indent=2))
    raise SystemExit(0 if b['acceptance']['passed'] else 1)
