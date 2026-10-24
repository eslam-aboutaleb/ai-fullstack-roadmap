"""Squared error gradient derivation, mean-sum parity, and finite difference verification harness.

Demonstrates deriving analytical gradients via the chain rule and catching the mean-sum parity defect:
1. Analytical derivative derivation:
   - Forward: y_hat = w * x, Loss_i = (y_hat - y)^2
   - Mean Loss: L = (1/N) * sum_i (w * x_i - y_i)^2
   - Chain rule gradient: dL/dw = (2/N) * sum_i (w * x_i - y_i) * x_i
2. The mean-sum parity defect: if the forward pass computes the MEAN loss but the backward pass
   SUMS the gradients without dividing by N, the effective gradient scales proportionally with batch size N.
   Increasing batch size silently inflates the effective learning rate by N, triggering gradient explosions.
3. Two-sided finite difference validation: verifies analytical gradient against numerical approximation:
   [L(w + eps) - L(w - eps)] / (2 * eps).
"""

from __future__ import annotations

from typing import List, Tuple


def compute_mse_loss(w: float, x_vals: List[float], y_vals: List[float]) -> float:
    """Forward pass: computes mean squared error."""
    n = len(x_vals)
    return sum((w * x - y) ** 2 for x, y in zip(x_vals, y_vals)) / n


def correct_mean_gradient(w: float, x_vals: List[float], y_vals: List[float]) -> float:
    """Analytically correct gradient of mean MSE loss: (2/N) * sum(diff * x)."""
    n = len(x_vals)
    return (2.0 / n) * sum((w * x - y) * x for x, y in zip(x_vals, y_vals))


def buggy_sum_gradient(w: float, x_vals: List[float], y_vals: List[float]) -> float:
    """Buggy gradient: sums individual derivatives without dividing by batch size N."""
    return 2.0 * sum((w * x - y) * x for x, y in zip(x_vals, y_vals))


def numerical_finite_difference(
    w: float, x_vals: List[float], y_vals: List[float], eps: float = 1e-6
) -> float:
    """Two-sided finite difference numerical gradient."""
    loss_plus = compute_mse_loss(w + eps, x_vals, y_vals)
    loss_minus = compute_mse_loss(w - eps, x_vals, y_vals)
    return (loss_plus - loss_minus) / (2.0 * eps)


def run_test_suite() -> None:
    batch_size = 8
    x_data = [1.0, 2.0, 1.5, 3.0, 0.5, 2.5, 1.2, 2.8]
    y_data = [2.1, 3.9, 3.1, 6.2, 1.0, 5.1, 2.5, 5.5]
    w_initial = 1.2

    # 1. Verify analytical mean gradient matches numerical finite difference:
    analytical_grad = correct_mean_gradient(w_initial, x_data, y_data)
    numerical_grad = numerical_finite_difference(w_initial, x_data, y_data, eps=1e-6)

    # Relative tolerance < 1e-5:
    rel_error = abs(analytical_grad - numerical_grad) / (abs(analytical_grad) + 1e-8)
    assert rel_error < 1e-5, f"Gradient derivation mismatch: analytical={analytical_grad}, numerical={numerical_grad}"

    # 2. Expose the mean-sum parity defect:
    buggy_grad = buggy_sum_gradient(w_initial, x_data, y_data)

    # Buggy gradient is exactly N times larger than the true gradient of the loss function:
    assert abs(buggy_grad - (analytical_grad * batch_size)) < 1e-5
    assert abs(buggy_grad) > abs(analytical_grad) * 7.9, "Buggy sum gradient explodes with batch size"

    # Demonstrate batch size scaling risk:
    # If batch size expands from 8 to 64, buggy gradient inflates by another 8x,
    # causing step size to explode even though loss function is identical.
    x_large = x_data * 8  # Batch size 64
    y_large = y_data * 8
    grad_64_correct = correct_mean_gradient(w_initial, x_large, y_large)
    grad_64_buggy = buggy_sum_gradient(w_initial, x_large, y_large)

    assert abs(grad_64_correct - analytical_grad) < 1e-5  # Mean gradient is invariant to replicated batch
    assert abs(grad_64_buggy - (analytical_grad * 64)) < 1e-4  # Buggy gradient is 64x inflated!

    print("All squared error loss mean gradient parity assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()

