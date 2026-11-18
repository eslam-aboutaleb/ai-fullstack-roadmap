"""Raw score addition, min-max outliers and RRF can rank the same candidates differently."""
DENSE = {"A": 0.90, "B": 0.80, "C": 0.70, "D": 0.20}
BM25 = {"A": 3.0, "B": 12.0, "C": 11.0, "D": 60.0}


def order(scores):
    return [k for k, _ in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))]


def minmax(scores):
    lo, hi = min(scores.values()), max(scores.values())
    return {k: (v - lo) / (hi - lo) for k, v in scores.items()}


def rrf(*rankings, k=60):
    out = {}
    for ranking in rankings:
        for rank, key in enumerate(ranking, 1):
            out[key] = out.get(key, 0.0) + 1 / (k + rank)
    return out


raw = {k: DENSE[k] + BM25[k] for k in DENSE}
normalized = {k: minmax(DENSE)[k] + minmax(BM25)[k] for k in DENSE}
fused = rrf(order(DENSE), order(BM25))
assert order(raw) == order(BM25)            # BM25 scale swamps cosine
print("raw", order(raw), "minmax", order(normalized), "rrf", order(fused))
