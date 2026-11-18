"""Corrective retrieval: assess evidence, apply one bounded correction, then answer or abstain."""
CORPUS = {
    "d1": "general canbus overview of frames and arbitration",
    "d2": "diagnostic error wdgif_e_param_device is raised when the device id is invalid",
}
REQUIRED = {"wdgif_e_param_device"}


def dense_like(query):
    words = set(query.lower().split())
    return [d for d, text in CORPUS.items() if words & set(text.split()) and "overview" in text]


def lexical(query):
    return [d for d, text in CORPUS.items() if REQUIRED & set(text.split())]


def assess(hits):
    covered = {term for d in hits for term in REQUIRED if term in CORPUS[d]}
    return "sufficient" if covered == REQUIRED else "insufficient"


def answer_path(query, max_corrections=1):
    trace = []
    hits = dense_like(query)
    trace.append(("dense", hits, assess(hits)))
    corrections = 0
    while assess(hits) != "sufficient" and corrections < max_corrections:
        hits = lexical(query)
        corrections += 1
        trace.append(("lexical", hits, assess(hits)))
    return ("answer" if assess(hits) == "sufficient" else "abstain"), trace


decision, trace = answer_path("explain can frames error code")
assert decision == "answer" and [step[0] for step in trace] == ["dense", "lexical"]
assert answer_path("explain can frames error code", max_corrections=0)[0] == "abstain"
print(decision, trace)
