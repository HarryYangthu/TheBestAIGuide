"""NumPy reference mechanics. No pretrained model or provider API involved."""
from collections import Counter
import numpy as np


def stable_softmax(logits, axis=-1):
    x = np.asarray(logits, float)
    maximum = np.max(x, axis=axis, keepdims=True)
    if not np.isfinite(maximum).all():
        raise ValueError("Every softmax row needs at least one finite logit")
    shifted = x-maximum
    e = np.exp(shifted)
    return e / e.sum(axis=axis, keepdims=True)


def attention(q, k, v, allowed=None):
    """q:(nq,dk), k:(nk,dk), v:(nk,dv), allowed:(nq,nk) True=visible."""
    q, k, v = map(lambda a: np.asarray(a, dtype=float), (q,k,v))
    if q.ndim != 2 or k.ndim != 2 or v.ndim != 2 or q.shape[1] != k.shape[1] or len(k) != len(v):
        raise ValueError("Expected q:(nq,dk), k:(nk,dk), v:(nk,dv)")
    scores = q @ k.T / np.sqrt(q.shape[-1])
    if allowed is not None:
        allowed = np.asarray(allowed, bool)
        if allowed.shape != scores.shape:
            raise ValueError("Mask shape must equal score shape")
        scores = np.where(allowed, scores, -np.inf)
    weights = stable_softmax(scores)
    return weights @ v, weights


def merge_pair(tokens, pair):
    out, i = [], 0
    while i < len(tokens):
        if i+1 < len(tokens) and (tokens[i], tokens[i+1]) == pair:
            out.append(tokens[i]+tokens[i+1]); i += 2
        else:
            out.append(tokens[i]); i += 1
    return out


def train_bpe(corpus, merges=8):
    """Character BPE with explicit word-end symbol; not a production byte tokenizer."""
    words = [(list(word)+['</w>'], count) for word,count in sorted(Counter(corpus.split()).items())]
    rules = []
    for _ in range(merges):
        counts = Counter()
        for tokens, count in words:
            for pair in zip(tokens, tokens[1:]):
                counts[pair] += count
        if not counts:
            break
        # Deterministic tie break is needed for reproducible vocabularies.
        pair = min(counts, key=lambda p: (-counts[p],p))
        rules.append(pair)
        words = [(merge_pair(tokens,pair),count) for tokens,count in words]
    return rules


def bpe_encode(word, rules):
    tokens = list(word)+['</w>']
    for pair in rules:
        tokens = merge_pair(tokens,pair)
    return tokens


def decode_distribution(logits, temperature=1., top_k=None, top_p=1.):
    """Filter k then nucleus; include token crossing cumulative top_p threshold."""
    logits = np.asarray(logits, float)
    if logits.ndim != 1 or temperature <= 0 or not 0 < top_p <= 1:
        raise ValueError("Use vector logits, temperature>0 and 0<top_p<=1")
    if top_k is not None and not 1 <= top_k <= len(logits):
        raise ValueError("top_k out of range")
    scores = logits / temperature
    order = np.argsort(-scores, kind='stable')
    if top_k is not None:
        scores[order[top_k:]] = -np.inf
    probabilities = stable_softmax(scores)
    order = np.argsort(-probabilities, kind='stable')
    # Previous cumulative mass, not current, retains crossing token.
    remove = np.cumsum(probabilities[order])-probabilities[order] >= top_p
    scores[order[remove]] = -np.inf
    return stable_softmax(scores)


def cached_attention(inputs, wq, wk, wv):
    """Single causal attention layer. Full projection per token only once.

    No positional encoding, residual, FFN or sampling; equivalence test, not LLM serving.
    """
    keys, values, outputs = [], [], []
    for x in inputs:
        q, k, v = x[None,:] @ wq, x[None,:] @ wk, x[None,:] @ wv
        keys.append(k); values.append(v)
        out, _ = attention(q, np.concatenate(keys), np.concatenate(values))
        outputs.append(out)
    return np.concatenate(outputs)


def symmetric_quantize(weights, bits=8):
    if not isinstance(bits, int) or not 2 <= bits <= 8:
        raise ValueError("Teaching implementation supports 2..8 bits")
    weights = np.asarray(weights, float)
    limit = 2**(bits-1)-1
    peak = np.max(np.abs(weights))
    scale = peak/limit if peak else 1.
    quantized = np.clip(np.rint(weights/scale), -limit, limit).astype(np.int8)
    return quantized, scale, quantized.astype(float)*scale


def kv_cache_bytes(batch, layers, tokens, kv_heads, head_dim, bytes_per_element=2):
    if min(batch,layers,tokens,kv_heads,head_dim,bytes_per_element) < 0:
        raise ValueError("Sizes must be nonnegative")
    return 2*batch*layers*tokens*kv_heads*head_dim*bytes_per_element
