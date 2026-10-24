"""Dot product vs cosine similarity and L2 normalization ranking harness.

Demonstrates when and why dot product and cosine similarity produce divergent retrieval rankings:
1. Mathematical divergence:
   - Dot product (u . v) = ||u|| * ||v|| * cos(theta). It is sensitive to both angular direction AND vector magnitude.
   - Cosine similarity = (u . v) / (||u|| * ||v||). It is purely scale-invariant, measuring directional orientation only.
2. The magnitude domination trap: an unnormalized embedding with large Euclidean norm can dominate
   dot-product ranking despite poor directional alignment with the query.
3. Unit sphere normalization invariant: when vectors are L2-normalized (||u|| = 1.0), dot product and
   cosine similarity become mathematically identical, guaranteeing consistent retrieval ranking.
"""

from __future__ import annotations

import math
from typing import List, Tuple


def vector_norm(v: List[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def dot_product(u: List[float], v: List[float]) -> float:
    return sum(x * y for x, y in zip(u, v))


def cosine_similarity(u: List[float], v: List[float]) -> float:
    norm_u = vector_norm(u)
    norm_v = vector_norm(v)
    assert norm_u > 0.0 and norm_v > 0.0, "Zero-vector has undefined cosine similarity"
    return dot_product(u, v) / (norm_u * norm_v)


def l2_normalize(v: List[float]) -> List[float]:
    norm = vector_norm(v)
    assert norm > 0.0
    return [x / norm for x in v]


def run_test_suite() -> None:
    # Query vector pointing along the X-axis:
    query = [1.0, 0.0]

    # Candidate A: Near-perfect directional alignment with query (theta ~ 5.7 degrees), small magnitude
    # Vector: [1.0, 0.1] -> length ~ 1.005
    cand_a = [1.0, 0.1]

    # Candidate B: Moderate directional alignment (theta = 45 degrees), but massive magnitude
    # Vector: [5.0, 5.0] -> length ~ 7.071
    cand_b = [5.0, 5.0]

    # 1. Compute unnormalized scores:
    dot_a = dot_product(query, cand_a)  # 1.0 * 1.0 + 0.0 * 0.1 = 1.0
    dot_b = dot_product(query, cand_b)  # 1.0 * 5.0 + 0.0 * 5.0 = 5.0

    cos_a = cosine_similarity(query, cand_a)
    cos_b = cosine_similarity(query, cand_b)

    # 2. Demonstrate ranking inversion:
    # Cosine correctly identifies Candidate A as far closer directionally (0.995 vs 0.707):
    assert cos_a > 0.99
    assert abs(cos_b - (1.0 / math.sqrt(2))) < 1e-4  # ~0.7071
    assert cos_a > cos_b, "Candidate A is directionally superior"

    # But Dot Product inverts the ranking because Candidate B has 7x larger magnitude:
    assert dot_b > dot_a, "Magnitude dominates raw dot product ranking"
    assert dot_b == 5.0 and dot_a == 1.0

    # 3. Demonstrate L2 normalization reconciliation:
    q_norm = l2_normalize(query)
    cand_a_norm = l2_normalize(cand_a)
    cand_b_norm = l2_normalize(cand_b)

    norm_dot_a = dot_product(q_norm, cand_a_norm)
    norm_dot_b = dot_product(q_norm, cand_b_norm)

    # On the unit hypersphere, dot product equals cosine similarity:
    assert abs(norm_dot_a - cos_a) < 1e-6
    assert abs(norm_dot_b - cos_b) < 1e-6

    # Normalized dot product restores true semantic ranking:
    assert norm_dot_a > norm_dot_b, "Normalized dot product must match cosine ranking"

    print("All dot product vs cosine similarity assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()

