"""Implement and evaluate offline retrieval metrics: MRR@k, MAP, and NDCG@k from first principles."""
import math

def reciprocal_rank(retrieved_ids, ground_truth_relevant_ids, k=10):
    """MRR@k: Evaluates the reciprocal rank of the FIRST relevant document."""
    for rank_idx, doc_id in enumerate(retrieved_ids[:k], 1):
        if doc_id in ground_truth_relevant_ids:
            return 1.0 / rank_idx
    return 0.0

def average_precision(retrieved_ids, ground_truth_relevant_ids, k=10):
    """AP@k: Average Precision across all recall points up to rank k."""
    hits = 0
    sum_precisions = 0.0
    for rank_idx, doc_id in enumerate(retrieved_ids[:k], 1):
        if doc_id in ground_truth_relevant_ids:
            hits += 1
            precision_at_rank = hits / rank_idx
            sum_precisions += precision_at_rank
    num_relevant = len(ground_truth_relevant_ids)
    return (sum_precisions / min(num_relevant, k)) if num_relevant > 0 else 0.0

def ndcg_at_k(retrieved_ids, relevance_grades, k=5):
    """
    NDCG@k: Normalized Discounted Cumulative Gain with graded relevance (e.g. 0 to 3).
    DCG = sum_{i=1}^k (2^{rel_i} - 1) / log2(i + 1)
    """
    dcg = 0.0
    for rank_idx, doc_id in enumerate(retrieved_ids[:k], 1):
        grade = relevance_grades.get(doc_id, 0)
        dcg += (2.0 ** grade - 1.0) / math.log2(rank_idx + 1)

    # Ideal DCG (IDCG): Sort true grades in descending order
    ideal_grades = sorted(relevance_grades.values(), reverse=True)[:k]
    idcg = 0.0
    for rank_idx, grade in enumerate(ideal_grades, 1):
        idcg += (2.0 ** grade - 1.0) / math.log2(rank_idx + 1)

    return (dcg / idcg) if idcg > 0.0 else 0.0

# Evaluation Test Case:
retrieved = ["doc_A", "doc_B", "doc_C", "doc_D", "doc_E"]
ground_truth_set = {"doc_B", "doc_D"} # doc_B at rank 2, doc_D at rank 4
grades = {"doc_B": 3, "doc_D": 2, "doc_A": 0, "doc_C": 0, "doc_E": 0}

mrr = reciprocal_rank(retrieved, ground_truth_set, k=5)
map_score = average_precision(retrieved, ground_truth_set, k=5)
ndcg = ndcg_at_k(retrieved, grades, k=5)

# First hit is doc_B at rank 2 -> MRR = 1/2 = 0.50
assert math.isclose(mrr, 0.50, rel_tol=1e-3)
# Hits at rank 2 (P=1/2=0.5) and rank 4 (P=2/4=0.5) -> MAP = (0.5 + 0.5) / 2 = 0.50
assert math.isclose(map_score, 0.50, rel_tol=1e-3)
assert 0.0 < ndcg <= 1.0

print(f"Retrieval offline evaluation verified: MRR@5={round(mrr, 3)}, MAP@5={round(map_score, 3)}, NDCG@5={round(ndcg, 3)}")
