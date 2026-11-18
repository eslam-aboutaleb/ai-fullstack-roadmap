"""Maximal Marginal Relevance: trade relevance against redundancy with the already selected set."""
import math

QUERY = (1.0, 0.0)
CANDIDATES = {
    "notice-a": (0.99, 0.10),
    "notice-b": (0.98, 0.12),
    "refund": (0.80, 0.60),
    "exceptions": (0.75, 0.66),
}


def cosine(a, b):
    return sum(x * y for x, y in zip(a, b)) / (math.hypot(*a) * math.hypot(*b))


def mmr(candidates, query, k, lam):
    selected = []
    pool = dict(candidates)
    while pool and len(selected) < k:
        def score(name):
            redundancy = max((cosine(pool[name], candidates[s]) for s in selected), default=0.0)
            return lam * cosine(pool[name], query) - (1 - lam) * redundancy
        best = max(sorted(pool), key=score)
        selected.append(best)
        pool.pop(best)
    return selected


relevance_only = mmr(CANDIDATES, QUERY, 2, lam=1.0)
diverse = mmr(CANDIDATES, QUERY, 2, lam=0.3)
assert relevance_only == ["notice-a", "notice-b"]
assert diverse == ["notice-a", "exceptions"]
print("lambda=1.0", relevance_only, "lambda=0.3", diverse)
