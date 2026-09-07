import re
import string
from collections import Counter


def normalize(text):
    text = ''.join(c for c in text.lower() if c not in string.punctuation)
    return ' '.join(re.sub(r'\b(a|an|the)\b', ' ', text).split())


def answer_score(prediction, gold):
    p, g = normalize(prediction), normalize(gold)
    em = int(p == g)
    if p != g and (p in ('yes', 'no', 'noanswer') or g in ('yes', 'no', 'noanswer')):
        return {'em': em, 'f1': 0.0}
    common = sum((Counter(p.split()) & Counter(g.split())).values())
    f1 = 2 * common / (len(p.split()) + len(g.split())) if common else float(em)
    return {'em': em, 'f1': f1}


def evidence_score(predicted, gold):
    p, g = set(map(tuple, predicted)), set(map(tuple, gold))
    hit = len(p & g)
    precision = hit / len(p) if p else 0
    recall = hit / len(g) if g else 0
    return {'precision': precision, 'recall': recall,
            'f1': 2 * precision * recall / (precision + recall) if precision + recall else 0,
            'complete': int(g <= p), 'hits': hit}


def facts(documents):
    return [fact for doc in documents for fact in doc['facts']]


def score_prediction(prediction, gold_answer, gold_facts, context, selected):
    citations = prediction.get('citations', [])
    if not isinstance(prediction.get('answer'), str) or not isinstance(citations, list):
        raise ValueError('invalid prediction schema')
    valid = set((title, i) for title, sentences in zip(context['title'], context['sentences']) for i in range(len(sentences)))
    for cite in citations:
        if not isinstance(cite, list) or len(cite) != 2 or not isinstance(cite[0], str) or type(cite[1]) is not int:
            raise ValueError('citation must be [title, zero-based sentence_id]')
    cited = set(map(tuple, citations))
    visible = set(map(tuple, facts(selected)))
    return {**answer_score(prediction['answer'], gold_answer), **{'citation_' + k: v for k, v in evidence_score(citations, gold_facts).items()},
            'citation_validity': len(cited & valid) / len(cited) if cited else 0,
            'citation_visible': len(cited & visible) / len(cited) if cited else 0}
