"""Demonstrate Matryoshka Representation Learning (MRL) dimension truncation and L2 re-normalization."""
import math

def l2_normalize(vector):
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0.0:
        return vector
    return [x / norm for x in vector]

def cosine_similarity(v1, v2):
    return sum(a * b for a, b in zip(v1, v2))

# Synthetic 1024-dimensional embedding from an MRL-trained model (e.g. text-embedding-3-large)
# MRL trains the model so that the earliest dimensions encode the most significant coarse semantics,
# while later dimensions capture fine-grained residual details.
full_dim = 1024
# Construct synthetic MRL vector where early dimensions have high signal:
base_vec_a = [1.0 / (i + 1) for i in range(full_dim)]
base_vec_b = [1.0 / (i + 1) + (0.01 if i > 50 else 0.0) for i in range(full_dim)]

vec_a_1024 = l2_normalize(base_vec_a)
vec_b_1024 = l2_normalize(base_vec_b)

# Full 1024-dimension similarity:
sim_full = cosine_similarity(vec_a_1024, vec_b_1024)

# Truncate to 256 dimensions (75% RAM and storage reduction!):
# CRITICAL STEP: When truncating an MRL embedding, you MUST re-apply L2 normalization!
trunc_a_256 = l2_normalize(vec_a_1024[:256])
trunc_b_256 = l2_normalize(vec_b_1024[:256])

sim_trunc_256 = cosine_similarity(trunc_a_256, trunc_b_256)

# Truncate to 128 dimensions (87.5% RAM reduction):
trunc_a_128 = l2_normalize(vec_a_1024[:128])
trunc_b_128 = l2_normalize(vec_b_1024[:128])
sim_trunc_128 = cosine_similarity(trunc_a_128, trunc_b_128)

# MRL preserves near-perfect relative similarity ranking despite severe truncation:
assert abs(sim_full - sim_trunc_256) < 0.02
assert abs(sim_full - sim_trunc_128) < 0.05

print(f"MRL truncation verified: full_1024_sim={round(sim_full, 5)}, trunc_256_sim={round(sim_trunc_256, 5)}, trunc_128_sim={round(sim_trunc_128, 5)}")

