"""MaxSim keeps token-level matches that one mean-pooled vector blurs together."""
import math


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def unit(v):
    n = math.hypot(*v)
    return tuple(x / n for x in v)


def maxsim(query_tokens, doc_tokens):
    return sum(max(dot(q, d) for d in doc_tokens) for q in query_tokens)


def pooled(tokens):
    return unit(tuple(sum(t[i] for t in tokens) for i in range(2)))


QUERY = [unit((1, 0)), unit((0, 1))]            # two distinct requirements
BOTH = [unit((1, 0.05)), unit((0.05, 1))]        # one document covers both
BLURRY = [unit((1, 1)), unit((1, 1))]            # tokens sit between them

single = {"both": dot(pooled(QUERY), pooled(BOTH)), "blurry": dot(pooled(QUERY), pooled(BLURRY))}
late = {"both": maxsim(QUERY, BOTH), "blurry": maxsim(QUERY, BLURRY)}
assert late["both"] > late["blurry"]
print({k: round(v, 3) for k, v in single.items()}, {k: round(v, 3) for k, v in late.items()})
