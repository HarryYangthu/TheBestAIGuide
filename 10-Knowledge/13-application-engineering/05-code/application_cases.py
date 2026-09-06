"""Original deterministic teaching cases; no real tenant data or model call."""
from dataclasses import dataclass


def visible_documents(documents, tenant, principal):
    return [d for d in documents if d['tenant'] == tenant and principal in d['readers']]


def choose_model(candidates, required, max_cost):
    eligible = [m for m in candidates if required <= m['capabilities'] and m['cost'] <= max_cost]
    if not eligible:
        raise ValueError('no compatible model within budget')
    return min(eligible, key=lambda m: (m['cost'], m['name']))['name']


def operations_recommendation(metrics):
    """Return a recommendation only; never execute a production change."""
    if metrics['error_rate'] > .05 and metrics['started_after_release']:
        return {'action':'request_rollback_review','evidence':['error_rate','release_time']}
    return {'action':'collect_more_evidence','evidence':[]}


def correct_price(amount, discount):
    if amount < 0 or not 0 <= discount <= 1:
        raise ValueError('invalid price input')
    return amount * (1 - discount)


def science_search(widths, parameter_limit):
    """Synthetic deterministic objective, not a physical/model benchmark."""
    feasible = [{'width': w, 'parameters': w*w, 'loss': 1/(w+1)} for w in widths if w > 0 and w*w <= parameter_limit]
    if not feasible:
        raise ValueError('no feasible candidate')
    return min(feasible, key=lambda item: item['loss'])


def demo():
    docs=[{'id':'a','tenant':'A','readers':['alice'],'text':'budget 100'},
          {'id':'b','tenant':'B','readers':['bob'],'text':'budget 900'}]
    visible=visible_documents(docs,'A','alice')
    assert [d['id'] for d in visible] == ['a']
    assert not visible_documents(docs,'A','bob')
    providers=[{'name':'text-only','capabilities':{'text'},'cost':1},
               {'name':'tool-ready','capabilities':{'text','tools'},'cost':2}]
    assert choose_model(providers,{'tools'},3) == 'tool-ready'
    assert correct_price(100,.1)==90
    assert correct_price(0,.2)==0
    assert operations_recommendation({'error_rate':.08,'started_after_release':True})['action']=='request_rollback_review'
    result=science_search([4,8,16],100)
    assert result['width']==8
    return {'visible_document_ids':[d['id'] for d in visible], 'model':'tool-ready',
            'price':90, 'operations':'request_rollback_review','synthetic_search':result}

if __name__ == '__main__':
    import json
    print(json.dumps(demo(),ensure_ascii=False,indent=2))
