"""HyDE: embed a hypothetical answer, search real documents, keep the original query as a fallback."""
import math
import re
from collections import Counter

DOCS = {
    "ecc-startup": "startup sequence initializes ecc memory before caches are enabled and an uncorrectable ecc error during memory initialization halts boot",
    "can-driver": "the can driver transmits frames through mailbox hardware using the bit timing register",
    "wdg-timeout": "watchdog timeout is configured in startup code before the application main function runs",
}


def vector(text):
    return Counter(re.findall(r"[a-z]+", text.lower()))


def cosine(a, b):
    dot = sum(a[t] * b[t] for t in a)
    norm = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return dot / norm if norm else 0.0


def search(text):
    scored = [(round(cosine(vector(text), vector(body)), 3), name) for name, body in DOCS.items()]
    return sorted(scored, reverse=True)


def fake_hypothesis(question):
    # Stand-in for an LLM call. Its text is a retrieval probe, never evidence.
    return "ecc memory initialization can fail in the startup sequence when an uncorrectable error is found before caches are enabled"


def hyde_search(question, generate=fake_hypothesis):
    try:
        probe = generate(question)
    except Exception:
        return search(question), "fallback-query"
    merged = {}
    for rank_list in (search(question), search(probe)):
        for score, name in rank_list:
            merged[name] = max(score, merged.get(name, 0.0))
    return sorted(((s, n) for n, s in merged.items()), reverse=True), "hyde+query"


question = "why does boot stop"
direct = search(question)
hyde, mode = hyde_search(question)
assert hyde[0][1] == "ecc-startup"
assert hyde_search(question, generate=lambda q: 1 / 0)[1] == "fallback-query"
print("direct_top", direct[0], "hyde_top", hyde[0], mode)
