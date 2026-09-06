"""Deterministic arithmetic and crash-window demonstration; not a load test."""
from decimal import Decimal
import json


def capacity(arrival, service_seconds, workers):
    if arrival < 0 or service_seconds <= 0 or workers < 1:
        raise ValueError('invalid capacity inputs')
    throughput = workers/service_seconds
    return {'capacity_per_second':throughput, 'stable_mean_condition': arrival < throughput,
            'offered_inflight':arrival*service_seconds}


def cost_per_success(total_cost, passed):
    if total_cost < 0 or passed < 0:
        raise ValueError('negative cost or count')
    return total_cost/passed if passed else None


def replay_after_crash(idempotent):
    records=[]
    def external_write(operation_id, value):
        if not idempotent or not any(r['id']==operation_id for r in records):
            records.append({'id':operation_id,'value':value})
    external_write('op-1','create-ticket')  # External write succeeds.
    # Crash occurs before local completion is recorded.
    external_write('op-1','create-ticket')  # Recovery retries the same request.
    return records


def demo():
    remaining=Decimal(10000)*(1-Decimal('.99'))-70
    naive=replay_after_crash(False)
    safe=replay_after_crash(True)
    assert len(naive)==2 and len(safe)==1
    assert remaining==30
    assert cost_per_success(30,90)<cost_per_success(20,50)
    assert cost_per_success(10,0) is None
    return {'capacity':capacity(2,30,40),'remaining_error_budget':int(remaining),
            'naive_record_count':len(naive),'idempotent_record_count':len(safe),
            'cost_a':cost_per_success(20,50),'cost_b':cost_per_success(30,90)}

if __name__ == '__main__': print(json.dumps(demo(),indent=2))
