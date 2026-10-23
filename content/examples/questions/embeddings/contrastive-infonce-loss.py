"""Implement InfoNCE (Noise-Contrastive Estimation) loss from first principles for Bi-Encoder training."""
import math

def dot_product(v1, v2):
    return sum(a * b for a, b in zip(v1, v2))

def compute_infonce_loss(query_emb, positive_doc_emb, negative_doc_embs, temperature=0.07):
    """
    InfoNCE Loss:
    L = -log( exp(sim(q, d+) / tau) / ( exp(sim(q, d+) / tau) + sum_j exp(sim(q, d-_j) / tau) ) )
    
    tau (temperature): Controls sharpness of the softmax probability distribution.
    Lower temperature (e.g. 0.05-0.07) forces the model to penalize hard negatives severely.
    """
    # 1. Similarity to ground-truth positive passage:
    pos_sim = dot_product(query_emb, positive_doc_emb) / temperature
    pos_exp = math.exp(pos_sim)

    # 2. Similarity to in-batch negative passages:
    neg_exps = []
    for neg_emb in negative_doc_embs:
        neg_sim = dot_product(query_emb, neg_emb) / temperature
        neg_exps.append(math.exp(neg_sim))

    total_denom = pos_exp + sum(neg_exps)
    softmax_prob = pos_exp / total_denom
    loss = -math.log(softmax_prob)

    return loss, softmax_prob

# Scenario: L2-normalized 3D embeddings
q = [0.8, 0.6, 0.0]
# Positive document: high alignment with query
d_pos = [0.82, 0.57, 0.0]
# Negative documents: orthogonal or misaligned
d_negs = [
    [0.0, 0.0, 1.0],   # Unrelated topic
    [-0.7, -0.7, 0.1]  # Contradictory topic
]

loss, prob = compute_infonce_loss(q, d_pos, d_negs, temperature=0.07)

# The positive document has high probability (> 0.99) under low temperature:
assert prob > 0.95
assert loss >= 0.0

print(f"InfoNCE contrastive loss verified: loss={round(loss, 6)}, positive_probability={round(prob, 6)}")
