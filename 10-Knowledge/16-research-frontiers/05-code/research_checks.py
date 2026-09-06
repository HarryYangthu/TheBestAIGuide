"""Transparent arithmetic illustrations, not reproductions of cited papers."""
import json


def majority_probability(p):
    if not 0<=p<=1: raise ValueError('probability out of range')
    return p**3+3*p*p*(1-p)


def update_scalar_state(w,x,eta):
    return w-eta*(w-x)  # Gradient of 0.5*(w-x)^2.


def demo():
    long_horizon=.98**50
    independent=majority_probability(.7)
    fully_correlated=.7
    candidates=[{'width':8,'params':64,'latency_ms':9}, {'width':16,'params':256,'latency_ms':7}]
    feasible=[c for c in candidates if c['params']<=100 and c['latency_ms']<=10]
    w=update_scalar_state(0.,2.,.5)
    assert w==1 and feasible[0]['width']==8
    reset=0. # A new sequence deliberately has no previous user's adaptation.
    assert update_scalar_state(reset,0.,.5)==0
    assert .36<long_horizon<.37 and abs(independent-.784)<1e-12
    return {'independent_50_step_probability':long_horizon,'independent_majority':independent,
            'fully_correlated_majority':fully_correlated,'feasible':feasible,'scalar_update':w}

if __name__=='__main__': print(json.dumps(demo(),indent=2))
