"""Implement Reciprocal Rank Fusion (RRF) combining Dense and Sparse (BM25) search rankings."""
from collections import defaultdict

def reciprocal_rank_fusion(ranked_lists, k=60):
    """
    RRF Score formula: RRF(d) = sum_{m in rankers} 1 / (k + rank_m(d))
    Constant k (standard=60) smooths the impact of high ranks and prevents a #1 rank
    in one sparse list from completely drowning out consensus across lists.
    """
    rrf_scores = defaultdict(float)
    appearances = defaultdict(dict)

    for ranker_name, doc_list in ranked_lists.items():
        for rank_1_based, doc_id in enumerate(doc_list, 1):
            contribution = 1.0 / (k + rank_1_based)
            rrf_scores[doc_id] += contribution
            appearances[doc_id][ranker_name] = rank_1_based

    # Sort candidates by accumulated RRF score descending
    sorted_candidates = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)
    return sorted_candidates, appearances

# Scenario:
# Query: "How to fix ERR_AUTH_TIMEOUT_401 in oauth token exchange?"
# Dense retrieval: Understands semantic context ("oauth token authentication issues"),
#                  ranks doc_B #1, doc_C #2, doc_A #3
dense_results = ["doc_B", "doc_C", "doc_A"]

# Sparse (BM25) retrieval: Exact keyword match on unique identifier 'ERR_AUTH_TIMEOUT_401',
#                          ranks doc_A #1, doc_D #2, doc_B #3
sparse_results = ["doc_A", "doc_D", "doc_B"]

hybrid_input = {
    "dense_semantic": dense_results,
    "sparse_lexical": sparse_results
}

fused_ranking, rank_details = reciprocal_rank_fusion(hybrid_input, k=60)

# doc_A and doc_B have strong consensus across both retrieval systems:
# doc_A: sparse rank 1, dense rank 3 -> 1/61 + 1/63 = 0.01639 + 0.01587 = 0.03226
# doc_B: dense rank 1, sparse rank 3 -> 1/61 + 1/63 = 0.03226
top_doc_id, top_score = fused_ranking[0]
assert top_doc_id in ["doc_A", "doc_B"]
assert len(fused_ranking) == 4

print(f"RRF Hybrid Fusion verified: top_doc={top_doc_id}, score={round(top_score, 5)}, rankings={[(d, round(s, 5)) for d, s in fused_ranking]}")
