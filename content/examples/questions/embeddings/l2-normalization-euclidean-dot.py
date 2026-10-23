"""Demonstrate mathematical equivalence of Cosine Similarity, Dot Product, and squared L2 Distance for normalized vectors."""
import math

def l2_norm(vec):
    return math.sqrt(sum(x * x for x in vec))

def normalize(vec):
    n = l2_norm(vec)
    return [x / n for x in vec]

def dot_product(u, v):
    return sum(a * b for a, b in zip(u, v))

def euclidean_distance_squared(u, v):
    return sum((a - b) ** 2 for a, b in zip(u, v))

# Two raw non-normalized vectors
raw_u = [3.0, 4.0, 0.0]  # norm = 5
raw_v = [1.0, 2.0, 2.0]  # norm = 3

# Compute standard cosine similarity on raw vectors:
raw_dot = dot_product(raw_u, raw_v)
raw_cos_sim = raw_dot / (l2_norm(raw_u) * l2_norm(raw_v))

# 1. L2 Normalize vectors to unit sphere: ||u|| = 1, ||v|| = 1
u = normalize(raw_u)
v = normalize(raw_v)

assert math.isclose(l2_norm(u), 1.0, rel_tol=1e-7)
assert math.isclose(l2_norm(v), 1.0, rel_tol=1e-7)

# 2. Mathematical Property 1: Cosine Similarity EQUALS Dot Product
# For unit vectors: cos(u, v) = (u . v) / (1 * 1) = u . v
norm_dot = dot_product(u, v)
assert math.isclose(raw_cos_sim, norm_dot, rel_tol=1e-7)

# 3. Mathematical Property 2: Squared Euclidean Distance is bounded by Dot Product:
# ||u - v||^2 = ||u||^2 + ||v||^2 - 2(u . v) = 1 + 1 - 2(u . v) = 2 - 2(u . v)
dist_sq = euclidean_distance_squared(u, v)
expected_dist_sq = 2.0 - 2.0 * norm_dot

assert math.isclose(dist_sq, expected_dist_sq, rel_tol=1e-7)

# Monotonic equivalence: Maximizing Cosine Similarity is IDENTICAL to minimizing Euclidean Distance!
print(f"L2 normalization equivalence verified: raw_cos={round(raw_cos_sim, 5)}, norm_dot={round(norm_dot, 5)}, dist_sq={round(dist_sq, 5)} (2 - 2*dot)")
