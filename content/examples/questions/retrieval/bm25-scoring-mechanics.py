"""Implement Okapi BM25 scoring from first principles; analyze k1 and b parameter mechanics."""
import math
from collections import Counter

class OkapiBM25:
    def __init__(self, corpus, k1=1.5, b=0.75):
        """
        k1: Controls term frequency saturation. Higher k1 gives more weight to repeated terms;
            k1=0 reduces term frequency to binary presence.
        b: Controls document length normalization. b=1 heavily penalizes documents longer than
           average; b=0 disables length normalization completely.
        """
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus)
        self.doc_lens = [len(doc) for doc in corpus]
        self.avgdl = sum(self.doc_lens) / self.corpus_size
        self.doc_freqs = Counter()
        self.doc_term_freqs = []

        for doc in corpus:
            tf = Counter(doc)
            self.doc_term_freqs.append(tf)
            for term in tf:
                self.doc_freqs[term] += 1

    def idf(self, term):
        """Standard Lucene / Robertson-Spärck Jones IDF with smoothing."""
        df = self.doc_freqs.get(term, 0)
        return math.log(1.0 + (self.corpus_size - df + 0.5) / (df + 0.5))

    def score_document(self, query_terms, doc_index):
        score = 0.0
        doc_len = self.doc_lens[doc_index]
        tf_dict = self.doc_term_freqs[doc_index]

        for term in query_terms:
            if term not in tf_dict:
                continue
            tf = tf_dict[term]
            idf = self.idf(term)
            
            # BM25 term weight formula:
            # tf * (k1 + 1) / (tf + k1 * (1 - b + b * (doc_len / avgdl)))
            len_norm = 1.0 - self.b + self.b * (doc_len / self.avgdl)
            tf_component = (tf * (self.k1 + 1.0)) / (tf + self.k1 * len_norm)
            score += idf * tf_component
            
        return score

corpus = [
    ["refund", "policy", "for", "software", "subscriptions"],                      # Doc 0: Concise relevant doc
    ["general", "terms", "of", "service", "and", "legal", "compliance", "notice"], # Doc 1: Irrelevant doc
    ["refund", "refund", "refund", "spam", "unrelated", "lengthy", "text", "body", "of", "clauses", "and", "details"] # Doc 2: Long doc with keyword stuffing
]

bm25 = OkapiBM25(corpus, k1=1.5, b=0.75)
query = ["refund", "policy"]

scores = [(i, bm25.score_document(query, i)) for i in range(len(corpus))]
scores.sort(key=lambda x: x[1], reverse=True)

# Doc 0 ranks highest because length normalization (b=0.75) and saturation (k1=1.5)
# prevent Doc 2's repetitive 'refund' stuffing from dominating:
best_doc_idx = scores[0][0]
assert best_doc_idx == 0, f"Expected Doc 0 to rank first, got {best_doc_idx}"

print(f"BM25 scoring verified: top_doc={best_doc_idx}, scores={[round(s[1], 4) for s in scores]}")

