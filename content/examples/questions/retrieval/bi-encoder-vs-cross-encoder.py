"""Demonstrate Bi-Encoder fast candidate retrieval vs Cross-Encoder full-attention reranking."""

class BiEncoderRetriever:
    """
    Bi-Encoder: Query and documents are encoded independently into fixed-dimensional vectors:
      v_q = E(query), v_d = E(doc)
    Scoring is a fast dot product / cosine similarity: score = v_q . v_d
    Allows precomputing 10,000,000 document vectors and indexing in HNSW for sub-10ms retrieval.
    Limitation: No cross-attention between query words and document words (misses negation, modifier scoping).
    """
    def __init__(self, candidates):
        self.candidates = candidates

    def retrieve(self, query, k=5):
        # Return top k candidates based on vector similarity
        return sorted(self.candidates, key=lambda c: c["vector_similarity"], reverse=True)[:k]

class CrossEncoderReranker:
    """
    Cross-Encoder: Query and candidate document are concatenated into a single token sequence:
      [CLS] query [SEP] document [SEP]
    Every query token attends directly to every document token through all transformer layers.
    High accuracy, captures subtle negations, but O(N) full transformer forward passes.
    Feasible only on a small candidate pool (e.g. k=20 to 50 candidates).
    """
    def rerank(self, query, candidate_pool):
        scored = []
        for doc in candidate_pool:
            # Cross-encoder joint attention score
            joint_relevance = self._cross_attention_forward(query, doc["text"])
            scored.append((doc["id"], joint_relevance, doc["text"]))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def _cross_attention_forward(self, query, doc_text):
        # Simulated cross-attention scoring:
        # Cross-encoder detects semantic negation that bi-encoder cosine similarity misses!
        if "cannot" in doc_text.lower() or "not allowed" in doc_text.lower():
            if "can i" in query.lower():
                return 0.15 # Direct policy contradiction / negative match
        if "30-day full refund" in doc_text.lower():
            return 0.95
        return 0.50

# Candidate pool from first-stage vector index:
corpus = [
    {"id": "doc_1", "text": "Refunds are strictly NOT allowed for downloaded digital licenses.", "vector_similarity": 0.89},
    {"id": "doc_2", "text": "Hardware purchases include a 30-day full refund guarantee.", "vector_similarity": 0.82},
    {"id": "doc_3", "text": "Subscription renewals occur automatically each month.", "vector_similarity": 0.70}
]

query = "Can I get a refund for my purchase?"

# 1. Bi-Encoder candidate retrieval:
# Bi-encoder ranks doc_1 highest because of high lexical and vector keyword overlap with 'refund',
# missing the critical negation word 'NOT'!
bi_encoder = BiEncoderRetriever(corpus)
initial_candidates = bi_encoder.retrieve(query, k=2)
assert initial_candidates[0]["id"] == "doc_1", "Bi-encoder tricked by semantic overlap without cross-attention"

# 2. Cross-Encoder reranking:
# Joint cross-attention properly evaluates 'Can I refund' against 'NOT allowed' and reranks doc_2 to #1!
cross_encoder = CrossEncoderReranker()
final_ranked = cross_encoder.rerank(query, initial_candidates)

assert final_ranked[0][0] == "doc_2", "Cross-encoder correctly promoted valid refund policy to rank 1"
print(f"Two-stage retrieval verified: bi_encoder_top={initial_candidates[0]['id']} -> cross_encoder_top={final_ranked[0][0]} (score={final_ranked[0][1]})")
