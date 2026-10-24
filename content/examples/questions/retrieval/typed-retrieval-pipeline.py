"""Demonstrate a typed retrieval contract, candidate budget boundaries, and score interpretation."""
import math

class RetrievalRequest:
    def __init__(self, query, tenant_id, candidate_k=50, final_k=5, min_score_threshold=0.65):
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        if not tenant_id:
            raise ValueError("Tenant scope is mandatory for safe multi-tenant retrieval")
        # Invariant checks:
        if not (1 <= final_k <= candidate_k <= 200):
            raise ValueError(f"Invalid bounds: final_k ({final_k}) must be <= candidate_k ({candidate_k}) <= 200")
            
        self.query = query.strip()
        self.tenant_id = tenant_id
        self.candidate_k = candidate_k
        self.final_k = final_k
        self.min_score_threshold = min_score_threshold

def convert_distance_to_similarity(metric, raw_value):
    """
    Ensure correct threshold direction:
      Cosine similarity: [-1, 1], higher is closer (1.0 = identical).
      L2 / Euclidean distance: [0, inf), lower is closer (0.0 = identical).
    Normalize to [0, 1] relevance score where higher is always more relevant.
    """
    if metric == "cosine_similarity":
        # Raw value is cos(theta) in [-1, 1]
        return max(0.0, raw_value)
    elif metric == "l2_distance":
        # Convert distance d >= 0 to similarity score in (0, 1] using monotonic exponential decay
        return 1.0 / (1.0 + raw_value)
    else:
        raise ValueError(f"Unknown metric: {metric}")

req = RetrievalRequest(
    query="enterprise SSO SAML configuration",
    tenant_id="tenant_acme",
    candidate_k=40,
    final_k=5,
    min_score_threshold=0.70
)

# Test metric conversion:
cos_score = convert_distance_to_similarity("cosine_similarity", 0.88)
l2_score = convert_distance_to_similarity("l2_distance", 0.25)

assert cos_score >= req.min_score_threshold
assert l2_score >= req.min_score_threshold

print(f"Typed retrieval request validated: query='{req.query}', tenant={req.tenant_id}, candidate_k={req.candidate_k}, final_k={req.final_k}")

