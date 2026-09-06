"""Validate supplied evidence locators and render a comparison table."""
import json
from pathlib import Path
import sys


def compare(data):
    sources={s['id']:s for s in data['sources']}
    rows=[]
    def cell(value):return str(value).replace('|','\\|').replace('\n',' ')
    for claim in data['claims']:
        source=sources.get(claim['source_id'])
        quote=claim.get('quote','')
        if source is None:
            rows.append([claim['axis'],claim['source_id'],'证据不足','','缺少来源']);continue
        if not quote or quote not in source['text']:raise ValueError('quote not found in supplied source')
        rows.append([claim['axis'],source['id']+'@'+source['version'],claim['text'],quote,claim.get('limits','仍需人工检查语义支持')])
    header=Path(__file__).resolve().parents[1]/'assets/comparison.md'
    return header.read_text()+''.join('| '+' | '.join(cell(c) for c in row)+' |\n' for row in rows)


if __name__=='__main__':print(compare(json.loads(Path(sys.argv[1]).read_text())),end='')
