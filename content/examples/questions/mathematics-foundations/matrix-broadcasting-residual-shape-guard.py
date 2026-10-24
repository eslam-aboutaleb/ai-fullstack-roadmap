"""Matrix multiplication shapes and silent broadcasting bug detection harness.

Demonstrates the linear model shape contract and the classic NumPy/PyTorch broadcasting trap:
1. Linear model dimensions: for input X [B x D] and weight W [D x 1], the prediction Y_hat is [B x 1].
2. The silent [B x 1] vs [B] broadcasting catastrophe:
   - If predictions are shaped [B, 1] and targets are 1D array of shape [B],
   - Evaluating (Y_hat - Y) does NOT compute B sample residuals. Instead, NumPy/PyTorch broadcasting
     expands both tensors into a [B, B] outer difference matrix!
   - Loss functions like (residual ** 2).mean() execute WITHOUT raising any dimension error,
     silently optimizing an invalid pairwise difference objective and destroying model training.
3. Shape guard contract: strict shape assertions or explicit squeeze/reshape operations before loss computation.
"""

from __future__ import annotations

from typing import List, Tuple


def simulate_linear_prediction(
    x_matrix: List[List[float]], weights: List[float], bias: float
) -> List[List[float]]:
    """Computes X @ W + b -> shape [B, 1]."""
    b = len(x_matrix)
    d = len(weights)
    assert len(x_matrix[0]) == d, f"Dimension mismatch: expected {d}, got {len(x_matrix[0])}"

    predictions: List[List[float]] = []
    for row in x_matrix:
        val = sum(row[j] * weights[j] for j in range(d)) + bias
        predictions.append([val])  # 2D column vector [B, 1]
    return predictions


def buggy_broadcasting_subtraction(
    y_pred_2d: List[List[float]], y_true_1d: List[float]
) -> List[List[float]]:
    """Simulates NumPy broadcasting between [B, 1] and [B] -> produces [B, B]!"""
    b = len(y_pred_2d)
    assert len(y_true_1d) == b
    outer_diff: List[List[float]] = []
    for i in range(b):
        row_diffs: List[float] = []
        for j in range(b):
            # Element [i, 0] broadcasts across all elements [j] of target
            row_diffs.append(y_pred_2d[i][0] - y_true_1d[j])
        outer_diff.append(row_diffs)
    return outer_diff


def safe_aligned_subtraction(
    y_pred_2d: List[List[float]], y_true_1d: List[float]
) -> List[float]:
    """Safe: aligns shapes strictly -> produces [B] sample residuals."""
    b = len(y_pred_2d)
    assert len(y_true_1d) == b, "Shape mismatch between predictions and targets"
    return [y_pred_2d[i][0] - y_true_1d[i] for i in range(b)]


def run_test_suite() -> None:
    batch_size = 5
    features = 3

    # X [5 x 3]
    x_batch = [
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0],
        [2.0, 0.0, 1.0],
        [3.0, 1.0, 4.0],
    ]
    w = [0.5, -0.2, 0.1]
    b = 0.0

    # Predictions [5 x 1]
    y_pred = simulate_linear_prediction(x_batch, w, b)
    assert len(y_pred) == batch_size and len(y_pred[0]) == 1

    # Ground truth targets 1D array of shape [5]
    y_true = [0.4, 0.8, 1.5, 1.1, 1.7]

    # 1. Demonstrate the silent broadcasting defect:
    buggy_diff = buggy_broadcasting_subtraction(y_pred, y_true)
    # The output exploded from 5 residuals to a 5x5 matrix (25 elements!):
    assert len(buggy_diff) == batch_size
    assert len(buggy_diff[0]) == batch_size

    # Average squared loss under buggy broadcasting:
    buggy_loss = sum(val ** 2 for row in buggy_diff for val in row) / (batch_size * batch_size)

    # 2. Demonstrate safe aligned computation:
    safe_diff = safe_aligned_subtraction(y_pred, y_true)
    assert len(safe_diff) == batch_size

    safe_loss = sum(val ** 2 for val in safe_diff) / batch_size

    # The buggy loss diverges significantly from true MSE loss:
    assert buggy_loss != safe_loss, "Buggy broadcasting distorts loss objective"

    # Verify true residuals:
    for i in range(batch_size):
        expected_residual = y_pred[i][0] - y_true[i]
        assert abs(safe_diff[i] - expected_residual) < 1e-6

    print("All matrix broadcasting residual shape assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()

