"""Semantic similarity can tie on near-identical passages; exact values need structured constraints."""
import math
import re
from collections import Counter

PASSAGES = [
    {"id": "p1", "limit": 50000, "text": "Maximum coverage is $50,000 for hospitalization"},
    {"id": "p2", "limit": 500000, "text": "Maximum coverage is $500,000 for hospitalization"},
]


def semantic_vector(text):
    # Toy stand-in: words carry meaning, digits barely register, as in many embedding models.
    return Counter(re.findall(r"[a-z]+", text.lower()))


def cosine(a, b):
    dot = sum(a[t] * b[t] for t in a)
    return dot / (math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values())))


query = "hospitalization maximum coverage 50000"
scores = {p["id"]: round(cosine(semantic_vector(query), semantic_vector(p["text"])), 3) for p in PASSAGES}
exact_amount = int(re.search(r"\d+", query).group())
exact = [p["id"] for p in PASSAGES if p["limit"] == exact_amount]
assert len(set(scores.values())) == 1 and exact == ["p1"]
print("semantic_scores", scores, "exact_filter", exact)
