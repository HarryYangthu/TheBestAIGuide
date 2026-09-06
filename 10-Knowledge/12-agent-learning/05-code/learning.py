"""Offline arithmetic and data checks; no language model training."""
import math
from collections import defaultdict


def validate_splits(rows):
    """Reject a source task family appearing in more than one split."""
    groups = defaultdict(set)
    for row in rows:
        groups[row['task_group']].add(row['split'])
    leaked = sorted(group for group, splits in groups.items() if len(splits) > 1)
    if leaked:
        raise ValueError(f'split leakage: {leaked}')
    return len(groups)


def masked_nll(probabilities, mask):
    if len(probabilities) != len(mask) or any(m not in (0, 1) for m in mask) or not sum(mask):
        raise ValueError('invalid mask')
    if any(not math.isfinite(p) or not 0 < p <= 1 for p in probabilities):
        raise ValueError('probability must be finite and in (0, 1]')
    return -sum(math.log(p) * m for p, m in zip(probabilities, mask)) / sum(mask)


def dpo_loss(policy_chosen, policy_rejected, ref_chosen, ref_rejected, beta=0.1):
    """Inputs are sequence log probabilities; stable -log(sigmoid(z))."""
    if beta <= 0 or not all(math.isfinite(x) for x in (policy_chosen, policy_rejected, ref_chosen, ref_rejected, beta)):
        raise ValueError('finite inputs and positive beta required')
    z = beta * ((policy_chosen - ref_chosen) - (policy_rejected - ref_rejected))
    return max(0.0, -z) + math.log1p(math.exp(-abs(z)))


def group_advantages(rewards, epsilon=1e-8):
    if len(rewards) < 2 or epsilon <= 0 or not all(math.isfinite(r) for r in rewards):
        raise ValueError('at least two finite rewards and positive epsilon required')
    mean = sum(rewards) / len(rewards)
    std = math.sqrt(sum((r - mean) ** 2 for r in rewards) / len(rewards))
    return [(r - mean) / (std + epsilon) for r in rewards]


def weak_reward(record):
    return float('PASS' in record['answer'])


def guarded_reward(record):
    # These fields must come from the trusted evaluator, not model-produced JSON.
    if not record['policy_allowed']:
        return -1.0
    return float(record['external_tests_passed'])
