"""For unit vectors, cosine, dot product and Euclidean distance rank documents identically."""
import math

DOCS = {"a": (3.0, 4.0), "b": (30.0, 10.0), "c": (1.0, 5.0)}
QUERY = (2.0, 3.0)


def unit(v):
    n = math.hypot(*v)
    return tuple(x / n for x in v)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def l2(a, b):
    return math.dist(a, b)


def rank(key, reverse):
    return [n for n, _ in sorted(DOCS.items(), key=lambda kv: key(kv[1]), reverse=reverse)]


raw_dot = rank(lambda d: dot(QUERY, d), True)
nq = unit(QUERY)
norm = {n: unit(v) for n, v in DOCS.items()}
cos_rank = [n for n, _ in sorted(norm.items(), key=lambda kv: dot(nq, kv[1]), reverse=True)]
l2_rank = [n for n, _ in sorted(norm.items(), key=lambda kv: l2(nq, kv[1]))]
assert cos_rank == l2_rank
assert raw_dot != cos_rank
print("raw_dot", raw_dot, "normalized_cosine", cos_rank, "normalized_l2", l2_rank)
