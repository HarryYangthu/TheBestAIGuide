import math
import re
from collections import Counter


def tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def chunks(context, size=1):
    result = []
    for title, sentences in zip(context['title'], context['sentences']):
        for start in range(0, len(sentences), size):
            ids = list(range(start, min(start + size, len(sentences))))
            result.append({'title': title, 'sent_ids': ids,
                           'text': ' '.join(sentences[i] for i in ids),
                           'facts': [[title, i] for i in ids]})
    return result


class Index:
    def __init__(self, documents):
        self.docs = documents
        self.counts = [Counter(tokens(d['title'] + ' ' + d['text'])) for d in documents]
        self.df = Counter(t for counts in self.counts for t in counts)
        self.n = len(documents)
        self.lengths = [sum(c.values()) for c in self.counts]
        self.average = sum(self.lengths) / max(self.n, 1)
        self.idf = {t: math.log((1 + self.n) / (1 + n)) + 1 for t, n in self.df.items()}

    def rank(self, query, method='bm25'):
        q = Counter(tokens(query))
        scores = []
        qnorm = math.sqrt(sum((v * self.idf.get(t, 0)) ** 2 for t, v in q.items()))
        for i, c in enumerate(self.counts):
            if method == 'bm25':
                score = sum(math.log(1 + (self.n - self.df.get(t, 0) + .5) / (self.df.get(t, 0) + .5)) *
                            c[t] * 2.5 / (c[t] + 1.5 * (.25 + .75 * self.lengths[i] / max(self.average, 1)))
                            for t in q if c[t])
            elif method == 'tfidf':
                norm = math.sqrt(sum((v * self.idf[t]) ** 2 for t, v in c.items()))
                score = sum(v * c[t] * self.idf.get(t, 0)**2 for t, v in q.items()) / max(qnorm * norm, 1e-12)
            else:
                raise ValueError('unknown retrieval method')
            scores.append((i, score))
        return sorted(scores, key=lambda x: (-x[1], x[0]))


def fuse(*rankings, constant=60):
    totals = Counter()
    for ranking in rankings:
        for position, (idx, _score) in enumerate(ranking, 1):
            totals[idx] += 1 / (constant + position)
    return sorted(totals.items(), key=lambda x: (-x[1], x[0]))


def assemble(docs, ranking, top_k=5, budget=1800):
    selected, used = [], 0
    for idx, score in ranking[:top_k]:
        item = dict(docs[idx], score=score)
        cost = len(item['title']) + len(item['text']) + 30
        if used + cost <= budget:
            selected.append(item)
            used += cost
    return selected, used


class Neural:
    """Optional pretrained dense retrieval and cross-encoder; no lexical stand-in."""
    def __init__(self):
        import os
        import torch
        torch.set_num_threads(int(os.environ.get('RAG_CPU_THREADS', '2')))
        from sentence_transformers import SentenceTransformer, CrossEncoder
        self.encoder = SentenceTransformer(
            os.environ.get('RAG_ENCODER_PATH', 'sentence-transformers/all-MiniLM-L6-v2'),
            revision='1110a243fdf4706b3f48f1d95db1a4f5529b4d41', device='cpu')
        self.metadata = {'encoder': 'sentence-transformers/all-MiniLM-L6-v2',
                         'encoder_revision': '1110a243fdf4706b3f48f1d95db1a4f5529b4d41',
                         'reranker': 'cross-encoder/ms-marco-MiniLM-L6-v2',
                         'reranker_revision': '233902d25c440f23af6f7d6e94d2946bac0bee0a',
                         'device': 'cpu', 'threads': torch.get_num_threads(),
                         'local_override': bool(os.environ.get('RAG_ENCODER_PATH') or os.environ.get('RAG_RERANKER_PATH'))}
        self.reranker = CrossEncoder(
            os.environ.get('RAG_RERANKER_PATH', 'cross-encoder/ms-marco-MiniLM-L6-v2'),
            revision='233902d25c440f23af6f7d6e94d2946bac0bee0a', device='cpu')

    def dense(self, query, docs):
        vectors = self.encoder.encode([query] + [d['title'] + ' ' + d['text'] for d in docs], normalize_embeddings=True, show_progress_bar=False, batch_size=32)
        return sorted(enumerate((vectors[1:] @ vectors[0]).tolist()), key=lambda x: (-x[1], x[0]))

    def rerank(self, query, docs, ranking):
        candidates = ranking[:20]
        scores = self.reranker.predict([(query, docs[i]['title'] + ' ' + docs[i]['text']) for i, _ in candidates], show_progress_bar=False, batch_size=16)
        head = sorted([(candidate[0], float(score)) for candidate, score in zip(candidates, scores)], key=lambda x: (-x[1], x[0]))
        return head + ranking[20:]
