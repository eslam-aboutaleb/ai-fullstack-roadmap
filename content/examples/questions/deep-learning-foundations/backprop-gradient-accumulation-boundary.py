"""Backpropagation gradient computation vs optimizer parameter update harness.

Demonstrates the vital separation between backpropagation and optimizer updates:
1. Backpropagation mechanism: computes partial derivatives of the loss with respect to parameters
   via the reverse-mode automatic differentiation chain rule, ACCUMULATING gradients into parameter buffers.
2. The missing zero_grad() defect: forgetting to zero gradients between independent minibatches
   causes gradients from prior steps to sum into current steps, distorting effective step size
   and triggering training divergence.
3. Intentional gradient accumulation: scaling and accumulating gradients across K micro-batches
   allows simulating large batch sizes within constrained GPU VRAM before taking an optimizer step.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


class Parameter:
    """Simulates a learnable weight tensor with accumulated gradient."""

    def __init__(self, value: float) -> None:
        self.value: float = value
        self.grad: float = 0.0

    def zero_grad(self) -> None:
        self.grad = 0.0


class SimpleSGD:
    """Applies parameter updates using learning rate."""

    def __init__(self, params: List[Parameter], lr: float = 0.1) -> None:
        self.params = params
        self.lr = lr

    def step(self) -> None:
        for p in self.params:
            p.value -= self.lr * p.grad

    def zero_grad(self) -> None:
        for p in self.params:
            p.zero_grad()


def compute_loss_and_backward(weight: Parameter, x: float, target: float) -> float:
    """Forward: y_hat = w * x, Loss = 0.5 * (y_hat - target)^2

    Backward: dLoss/dw = (y_hat - target) * x. Accumulates into weight.grad!
    """
    y_hat = weight.value * x
    diff = y_hat - target
    loss = 0.5 * (diff ** 2)

    # Accumulate gradient (mirrors PyTorch's default in-place += accumulation)
    grad = diff * x
    weight.grad += grad
    return loss


def run_test_suite() -> None:
    # 1. Simulate the missing zero_grad() pathology:
    # Initial weight = 2.0, lr = 0.1
    w_buggy = Parameter(2.0)
    opt_buggy = SimpleSGD([w_buggy], lr=0.1)

    # Batch 1: x = 1.0, target = 0.0 -> diff = 2.0 -> grad = 2.0
    compute_loss_and_backward(w_buggy, x=1.0, target=0.0)
    assert w_buggy.grad == 2.0
    opt_buggy.step()
    # w_buggy = 2.0 - (0.1 * 2.0) = 1.8

    # BUG: Forgot opt_buggy.zero_grad()!
    # Batch 2: x = 1.0, target = 0.0 -> diff = 1.8 -> new grad = 1.8
    compute_loss_and_backward(w_buggy, x=1.0, target=0.0)

    # Gradient accumulated to 2.0 + 1.8 = 3.8 instead of true 1.8!
    assert w_buggy.grad == 3.8, f"Gradient unexpectedly accumulated to {w_buggy.grad}"
    opt_buggy.step()
    # Weight was updated with inflated gradient: 1.8 - (0.1 * 3.8) = 1.42

    # 2. Simulate correct training with explicit zero_grad():
    w_clean = Parameter(2.0)
    opt_clean = SimpleSGD([w_clean], lr=0.1)

    # Batch 1:
    compute_loss_and_backward(w_clean, x=1.0, target=0.0)
    opt_clean.step()
    opt_clean.zero_grad()  # Clean isolation!
    assert w_clean.grad == 0.0

    # Batch 2:
    compute_loss_and_backward(w_clean, x=1.0, target=0.0)
    assert w_clean.grad == 1.8, f"Expected isolated grad 1.8, got {w_clean.grad}"
    opt_clean.step()
    opt_clean.zero_grad()
    # w_clean = 1.8 - (0.1 * 1.8) = 1.62 (vs corrupted 1.42)
    assert round(w_clean.value, 4) == 1.62

    # 3. Controlled Gradient Accumulation over 2 micro-batches:
    # Goal: simulate batch size 2 with single optimizer step:
    w_accum = Parameter(2.0)
    opt_accum = SimpleSGD([w_accum], lr=0.1)

    # Micro-batch 1:
    compute_loss_and_backward(w_accum, x=1.0, target=0.0)
    # Micro-batch 2:
    compute_loss_and_backward(w_accum, x=2.0, target=0.0)

    # Scale accumulated gradients by micro-batch count (2)
    w_accum.grad /= 2.0
    opt_accum.step()
    opt_accum.zero_grad()

    print("All backpropagation gradient accumulation assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
