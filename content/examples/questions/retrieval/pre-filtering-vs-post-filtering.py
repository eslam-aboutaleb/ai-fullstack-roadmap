"""Demonstrate candidate starvation in vector post-filtering vs single-stage pre-filtering."""

class VectorRecord:
    def __init__(self, doc_id, tenant_id, similarity):
        self.doc_id = doc_id
        self.tenant_id = tenant_id
        self.similarity = similarity # Higher means closer

# Synthetic dataset: 1,000 documents
# Only 3 documents belong to 'tenant_target'.
# All 3 tenant documents have modest similarity (e.g. 0.72, 0.70, 0.68).
# Other tenants have hundreds of documents with higher similarity (0.95 down to 0.75).
corpus = []
for i in range(1, 998):
    corpus.append(VectorRecord(f"doc_other_{i}", "tenant_other", 0.95 - (i * 0.0002)))

corpus.append(VectorRecord("target_doc_1", "tenant_target", 0.72))
corpus.append(VectorRecord("target_doc_2", "tenant_target", 0.70))
corpus.append(VectorRecord("target_doc_3", "tenant_target", 0.68))

def post_filter_search(k_candidates=20, target_tenant="tenant_target"):
    """
    POST-FILTERING (Flawed):
    1. The vector index retrieves the top k_candidates globally based strictly on similarity.
    2. Application or DB filters the retrieved candidates by tenant_id.
    """
    # Global top-k nearest neighbors:
    global_top_k = sorted(corpus, key=lambda r: r.similarity, reverse=True)[:k_candidates]
    # Filter by tenant:
    filtered_results = [r for r in global_top_k if r.tenant_id == target_tenant]
    return filtered_results

def pre_filter_search(k_final=5, target_tenant="tenant_target"):
    """
    PRE-FILTERING / FILTERED HNSW (Correct):
    The graph traversal or index scan is constrained strictly to the tenant predicate.
    """
    # Traversal restricted strictly to tenant candidate space:
    eligible = [r for r in corpus if r.tenant_id == target_tenant]
    return sorted(eligible, key=lambda r: r.similarity, reverse=True)[:k_final]

# Test Case:
post_filtered = post_filter_search(k_candidates=20)
# CANDIDATE STARVATION FAILURE: None of the tenant documents made the global top 20,
# so post-filtering returns 0 results even though matching documents exist!
assert len(post_filtered) == 0, "Post-filtering suffered candidate starvation"

pre_filtered = pre_filter_search(k_final=3)
# Pre-filtering correctly returns all 3 tenant documents:
assert len(pre_filtered) == 3, "Pre-filtering successfully returned tenant documents"

print(f"Pre-filtering vs Post-filtering: post_filter_hits={len(post_filtered)} (starvation), pre_filter_hits={len(pre_filtered)}")

