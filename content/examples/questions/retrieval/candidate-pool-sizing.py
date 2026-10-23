"""Demonstrate candidate pool sizing failure modes: small candidate_k starves downstream rerankers."""

class MockCorpus:
    def __init__(self):
        # 100 retrieved documents ordered by rough first-stage bi-encoder similarity
        # The decisive legal exception is ranked #8 in raw vector similarity because of rare wording:
        self.documents = [
            {"id": f"general_policy_{i}", "vector_rank": i, "is_decisive_exception": False}
            for i in range(1, 101)
        ]
        # Decisive exception sits at rank 8:
        self.documents[7] = {"id": "statutory_exception_doc", "vector_rank": 8, "is_decisive_exception": True}

    def first_stage_search(self, candidate_k):
        return self.documents[:candidate_k]

def second_stage_cross_encoder_rerank(candidates, final_k=3):
    """
    Reranker has full joint cross-attention.
    If the decisive exception is present in the candidate pool, it promotes it to rank 1!
    """
    reranked = sorted(candidates, key=lambda d: 1.0 if d["is_decisive_exception"] else 0.2, reverse=True)
    return reranked[:final_k]

corpus = MockCorpus()

# FAILURE MODE: Undersized candidate pool (candidate_k = 5, final_k = 3)
# Even though the final answer context has room for 3 documents,
# candidate_k=5 truncates the search before rank 8!
small_candidates = corpus.first_stage_search(candidate_k=5)
final_starved = second_stage_cross_encoder_rerank(small_candidates, final_k=3)

# Result: Decisive evidence was never retrieved; LLM generates inaccurate answer!
assert not any(d["is_decisive_exception"] for d in final_starved)

# PROPER SIZING: Bounded candidate funnel (candidate_k = 30, final_k = 3)
# candidate_k=30 captures rank 8; the cross-encoder promotes it to rank 1 for prompt context!
healthy_candidates = corpus.first_stage_search(candidate_k=30)
final_recovered = second_stage_cross_encoder_rerank(healthy_candidates, final_k=3)

assert final_recovered[0]["id"] == "statutory_exception_doc"
print(f"Candidate pool sizing verified: candidate_k=5 failed (starvation); candidate_k=30 recovered decisive evidence to rank 1")
