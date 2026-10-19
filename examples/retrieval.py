from collections import defaultdict
def rrf(rankings, k=60):
    scores = defaultdict(float)
    for ranking in rankings:
        for rank, item in enumerate(dict.fromkeys(ranking), 1):
            scores[item] += 1 / (k + rank)
    return sorted(scores, key=lambda item: (-scores[item], item))
assert rrf([["a", "b"], ["b", "c"]])[0] == "b"
