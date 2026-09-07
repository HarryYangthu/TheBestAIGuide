"""Structured document evidence, using manually labeled synthetic cells.
No OCR, embedding model, VLM, or real document benchmark is run.
"""
from dataclasses import dataclass, asdict
import json
import math

@dataclass(frozen=True)
class Cell:
    evidence_id: str
    doc_id: str
    version: int
    page: int
    row: str
    column: str
    value: float
    unit: str
    bbox: tuple[float, float, float, float]

# All values/coordinates are original teaching fixtures, not measured latencies.
CELLS = [
    Cell('v1-a-mean','latency',1,1,'A','mean',40,'ms',(.35,.30,.50,.38)),
    Cell('v1-a-p95','latency',1,1,'A','p95',100,'ms',(.55,.30,.72,.38)),
    Cell('v1-b-mean','latency',1,1,'B','mean',60,'ms',(.35,.42,.50,.50)),
    Cell('v1-b-p95','latency',1,1,'B','p95',120,'ms',(.55,.42,.72,.50)),
    Cell('v2-b-p95','latency',2,1,'B','p95',110,'ms',(.55,.42,.72,.50)),
]


def json_citation(cell):
    """JSON arrays are the public coordinate representation, including in memory."""
    result = asdict(cell)
    result['bbox'] = list(cell.bbox)
    return result


def structured_answer(cells, *, doc_id, version, row, column):
    matches = [c for c in cells if (c.doc_id,c.version,c.row,c.column)==(doc_id,version,row,column)]
    if len(matches) != 1:
        raise ValueError('missing or ambiguous evidence')
    c = matches[0]
    return {'value':c.value,'unit':c.unit,'citation':json_citation(c)}


def flattened_baseline(cells, *, doc_id, version, row, column):
    """Deliberately weak baseline: row/column relations have been discarded."""
    values = [c.value for c in cells if c.doc_id==doc_id and c.version==version]
    if not values: raise ValueError('no document')
    return values[0]


def verify_claim(cells, answer, query):
    cite = answer.get('citation', {})
    matches = [c for c in cells if c.evidence_id==cite.get('evidence_id')]
    if len(matches)!=1: return False
    c = matches[0]
    expected = (query['doc_id'],query['version'],query['row'],query['column'])
    if (c.doc_id,c.version,c.row,c.column) != expected: return False
    # Require the cited location to match the source record, not just a formatted ID.
    if cite != json_citation(c): return False
    if answer.get('unit') != c.unit or not isinstance(answer.get('value'), (int,float)): return False
    if not math.isfinite(answer['value']) or not math.isclose(answer['value'],c.value,rel_tol=0,abs_tol=1e-9): return False
    x0,y0,x1,y1 = c.bbox
    return 0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1


def demo():
    queries=[dict(doc_id='latency',version=1,row='A',column='mean'),
             dict(doc_id='latency',version=1,row='B',column='p95'),
             dict(doc_id='latency',version=2,row='B',column='p95')]
    answers=[structured_answer(CELLS,**q) for q in queries]
    baseline=[flattened_baseline(CELLS,**q) for q in queries]
    gold=[40,120,110]
    assert all(verify_claim(CELLS,a,q) for a,q in zip(answers,queries))
    wrong={**answers[1],'unit':'s'}
    assert not verify_claim(CELLS,wrong,queries[1])
    assert not verify_claim(CELLS,answers[1],queries[2])
    return {'baseline_values':baseline,'gold_values':gold,
            'baseline_correct':sum(a==g for a,g in zip(baseline,gold)),
            'structured_correct':sum(a['value']==g for a,g in zip(answers,gold)),
            'n_teaching_questions':len(queries)}

if __name__ == '__main__': print(json.dumps(demo(),indent=2))
