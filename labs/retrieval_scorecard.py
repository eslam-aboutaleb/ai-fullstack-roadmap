"""Small lexical/fusion and retrieval-metric fixture; no production benchmark."""
from collections import Counter
from math import log, log2
import re


def tokens(text: str) -> list[str]:
    return re.findall(r'\w+', text.lower())


def bm25(query: str, documents: list[dict], owner: str, k1=1.2, b=0.75) -> list[str]:
    scoped = [doc for doc in documents if doc['owner'] == owner and not doc.get('deleted')]
    if not scoped:
        return []
    bags = [Counter(tokens(doc['text'])) for doc in scoped]
    average_length = sum(sum(bag.values()) for bag in bags) / len(bags)
    scores = []
    for doc, bag in zip(scoped, bags):
        score = 0.0
        for term in set(tokens(query)):
            frequency = bag[term]
            df = sum(term in candidate for candidate in bags)
            idf = log(1 + (len(bags) - df + 0.5) / (df + 0.5))
            if frequency:
                length = sum(bag.values())
                score += idf * frequency * (k1 + 1) / (frequency + k1 * (1 - b + b * length / average_length))
        if score > 0:
            scores.append((score, doc['id']))
    return [identity for score, identity in sorted(scores, key=lambda item: (-item[0], item[1]))]


def fuse(rankings: list[list[str]], constant: int = 60) -> list[str]:
    scores = Counter()
    for ranking in rankings:
        seen = set()
        for position, identity in enumerate(ranking, 1):
            if identity not in seen:
                scores[identity] += 1 / (constant + position)
                seen.add(identity)
    return sorted(scores, key=lambda identity: (-scores[identity], identity))


def metrics(ranked: list[str], relevant: set[str], k: int) -> dict:
    if type(k) is not int or k <= 0 or len(set(ranked)) != len(ranked):
        raise ValueError('Positive k and unique ranked IDs required')
    if not relevant:
        return {'recall': None, 'mrr': None, 'ndcg': None}  # Score abstention separately.
    selected = ranked[:k]
    recall = len(set(selected) & relevant) / len(relevant)
    reciprocal = next((1 / rank for rank, identity in enumerate(selected, 1) if identity in relevant), 0)
    dcg = sum(1 / log2(rank + 1) for rank, identity in enumerate(selected, 1) if identity in relevant)
    ideal = sum(1 / log2(rank + 1) for rank in range(1, min(k, len(relevant)) + 1))
    return {'recall': recall, 'mrr': reciprocal, 'ndcg': dcg / ideal}


def verify() -> None:
    docs = [{'id': 'sale', 'owner': 'A', 'text': 'sale items exchange'},
            {'id': 'normal', 'owner': 'A', 'text': 'ordinary items return'},
            {'id': 'private', 'owner': 'B', 'text': 'sale items exchange exception'}]
    ranked = bm25('sale exchange', docs, 'A')
    assert ranked == ['sale'] and bm25('warranty', docs, 'A') == []
    assert fuse([['sale', 'normal'], ['normal', 'sale']]) == ['normal', 'sale']
    result = metrics(['irrelevant', 'sale'], {'sale', 'normal'}, 2)
    assert result['recall'] == 0.5 and result['mrr'] == 0.5
    assert abs(result['ndcg'] - 0.38685280723454163) < 1e-9
    assert metrics([], set(), 3)['recall'] is None
    assert metrics(['sale'], {'sale'}, 1)['recall'] == 1.0
    assert metrics([], {'sale'}, 1)['recall'] == 0.0  # Deliberate dropped-document regression.
    print('Retrieval scorecard: scoped BM25, deterministic RRF, Recall/MRR/nDCG and empty-gold separation passed.')


if __name__ == '__main__':
    verify()
