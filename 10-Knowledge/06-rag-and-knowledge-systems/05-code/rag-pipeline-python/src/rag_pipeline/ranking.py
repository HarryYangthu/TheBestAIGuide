"""排名融合与明确口径的检索指标；缺少相关文档的查询不计 recall/nDCG。"""
import math


def rrf(rankings: list[list[str]], constant: float = 60.0) -> dict[str, float]:
    if constant < 0:
        raise ValueError("constant must be nonnegative")
    scores = {}
    for ranking in rankings:
        # 每一路同一对象只能贡献一次。
        for rank, item in enumerate(dict.fromkeys(ranking), 1):
            scores[item] = scores.get(item, 0.0) + 1 / (constant + rank)
    return scores


def retrieval_metrics(ranking: list[str], relevance: dict[str, int], k: int = 5) -> dict:
    if k < 1 or any(g < 0 for g in relevance.values()):
        raise ValueError("k must be positive and relevance grades nonnegative")
    ordered = list(dict.fromkeys(ranking))[:k]
    relevant = {doc for doc, gain in relevance.items() if gain > 0}
    if not relevant:
        return {"recall": None, "mrr": None, "ndcg": None, "empty": not ordered}
    recall = len(set(ordered) & relevant) / len(relevant)
    mrr = next((1 / rank for rank, doc in enumerate(ordered, 1) if doc in relevant), 0.0)
    def dcg(gains):
        return sum((2**gain - 1) / math.log2(rank + 1) for rank, gain in enumerate(gains, 1))
    ideal = dcg(sorted(relevance.values(), reverse=True)[:k])
    return {"recall": recall, "mrr": mrr,
            "ndcg": dcg([relevance.get(doc, 0) for doc in ordered]) / ideal, "empty": not ordered}
