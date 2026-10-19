def recall_at_k(retrieved, relevant, k):
    if not relevant: return None  # Undefined: report separately.
    return len(set(retrieved[:k]) & relevant) / len(relevant)
assert recall_at_k(["a", "b"], {"b", "c"}, 2) == 0.5
