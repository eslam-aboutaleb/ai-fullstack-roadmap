"""Attention tensor shape projection and softmax normalization axis harness.

Demonstrates tracing tensor dimensions and mathematical invariants through a self-attention head:
1. Projection shapes:
   - Input X: [Batch, T, d_model]
   - Projections Q, K, V: [Batch, T, d_k]
   - Raw score matrix S = (Q @ K.T) / sqrt(d_k): [Batch, T, T] (Row = Query token, Column = Key token)
2. The softmax axis defect:
   - Softmax MUST be computed along the KEY axis (dim=-1, across columns). Each query token i
     distributes its attention budget over all keys j, guaranteeing sum_j(A[i, j]) = 1.0.
   - Normalizing along the QUERY axis (dim=-2, across rows) distorts value aggregation, producing
     invalid attention weights that fail to form convex combinations.
3. Output projection:
   - Context output O = A @ V: [Batch, T, d_v]
   - Final projection Y = O @ W_o: [Batch, T, d_model]
"""

from __future__ import annotations

import math
from typing import List, Tuple


def matrix_mult(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    """Multiplies matrix A [M x K] by B [K x N] -> [M x N]."""
    m, k = len(a), len(a[0])
    k2, n = len(b), len(b[0])
    assert k == k2, f"Dimension mismatch: {k} != {k2}"

    out = [[0.0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            out[i][j] = sum(a[i][p] * b[p][j] for p in range(k))
    return out


def transpose_matrix(m: List[List[float]]) -> List[List[float]]:
    """Transposes matrix [M x N] -> [N x M]."""
    rows, cols = len(m), len(m[0])
    return [[m[r][c] for r in range(rows)] for c in range(cols)]


def softmax_rows(matrix: List[List[float]]) -> List[List[float]]:
    """Correct: Softmax along dim=-1 (each row sums to 1.0)."""
    out: List[List[float]] = []
    for row in matrix:
        max_val = max(row)
        exps = [math.exp(x - max_val) for x in row]
        sum_exp = sum(exps)
        out.append([e / sum_exp for e in exps])
    return out


def buggy_softmax_cols(matrix: List[List[float]]) -> List[List[float]]:
    """Buggy: Softmax along dim=-2 (each column sums to 1.0)."""
    t_m = transpose_matrix(matrix)
    t_soft = softmax_rows(t_m)
    return transpose_matrix(t_soft)


def run_test_suite() -> None:
    # Sequence of length T = 4, embedding dimension d_model = 3, head dimension d_k = 2
    t = 4
    d_model = 3
    d_k = 2

    # Simulated input X [4 x 3]
    x = [
        [1.0, 0.0, 0.5],
        [0.0, 1.0, 0.2],
        [0.5, 0.5, 0.1],
        [0.2, 0.8, 0.9],
    ]

    # Projection weights W_q, W_k, W_v [3 x 2]
    w_q = [[0.5, -0.2], [0.1, 0.8], [0.3, 0.4]]
    w_k = [[0.2, 0.1], [-0.5, 0.3], [0.7, -0.1]]
    w_v = [[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]]

    # Step 1: Compute Q, K, V -> [4 x 2]
    q = matrix_mult(x, w_q)
    k = matrix_mult(x, w_k)
    v = matrix_mult(x, w_v)
    assert len(q) == t and len(q[0]) == d_k
    assert len(k) == t and len(k[0]) == d_k
    assert len(v) == t and len(v[0]) == d_k

    # Step 2: Compute Q @ K^T -> [4 x 4]
    k_t = transpose_matrix(k)
    raw_scores = matrix_mult(q, k_t)
    assert len(raw_scores) == t and len(raw_scores[0]) == t

    # Scale by sqrt(d_k)
    scale = math.sqrt(d_k)
    scaled_scores = [[val / scale for val in row] for row in raw_scores]

    # Step 3: Apply Softmax along key axis (dim=-1)
    attn_weights = softmax_rows(scaled_scores)

    # Invariant: Every query row sums to 1.0:
    for row_idx, row in enumerate(attn_weights):
        row_sum = sum(row)
        assert abs(row_sum - 1.0) < 1e-5, f"Row {row_idx} sum was {row_sum}, expected 1.0"

    # Step 4: Demonstrate buggy softmax along query axis:
    buggy_weights = buggy_softmax_cols(scaled_scores)
    # In the buggy version, columns sum to 1.0, but rows do NOT sum to 1.0:
    first_row_sum = sum(buggy_weights[0])
    assert abs(first_row_sum - 1.0) > 1e-4, "Buggy softmax along wrong axis must fail row sum invariant"

    # Step 5: Compute Output Context O = A @ V -> [4 x 2]
    context_out = matrix_mult(attn_weights, v)
    assert len(context_out) == t and len(context_out[0]) == d_k

    print("All attention tensor shape projection assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
