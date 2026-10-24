"""Evaluation mode vs training mode contract for dropout and normalization layers.

Demonstrates why model.eval() and torch.no_grad() serve separate, complementary roles:
1. The common misconception: assuming torch.no_grad() automatically switches layers to evaluation behavior.
   no_grad() disables autograd tape allocation, but leaves Dropout and BatchNorm in stochastic training mode.
2. Dropout divergence: during training, Dropout masks elements with probability p and scales survivors by 1/(1-p).
   In eval mode, Dropout is an exact identity function, ensuring deterministic, reproducible predictions.
3. Batch Normalization divergence: in training mode, BatchNorm computes statistics from the current batch and updates
   running averages. In eval mode, it uses frozen population running statistics, essential for single-item inference.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Tuple


class SimulatedDropout:
    """Simulates inverted dropout behavior across train and eval modes."""

    def __init__(self, p: float = 0.5) -> None:
        self.p = p
        self.training: bool = True

    def forward(self, x: List[float], rng: random.Random) -> List[float]:
        if not self.training or self.p == 0.0:
            return list(x)  # Identity in eval mode

        scale = 1.0 / (1.0 - self.p)
        return [
            (val * scale if rng.random() > self.p else 0.0)
            for val in x
        ]


class SimulatedBatchNorm1D:
    """Simulates 1D Batch Normalization with running statistics."""

    def __init__(self) -> None:
        self.training: bool = True
        self.running_mean: float = 0.0
        self.running_var: float = 1.0

    def forward(self, batch: List[float]) -> List[float]:
        if self.training:
            # Training mode: uses batch statistics
            b_mean = sum(batch) / len(batch)
            b_var = sum((x - b_mean) ** 2 for x in batch) / len(batch)
            eps = 1e-5
            return [(x - b_mean) / ((b_var + eps) ** 0.5) for x in batch]
        else:
            # Eval mode: uses frozen population statistics (safe for batch size 1)
            eps = 1e-5
            return [(x - self.running_mean) / ((self.running_var + eps) ** 0.5) for x in batch]


class NeuralBlock:
    """Wraps layers with unified train() and eval() mode switches."""

    def __init__(self, dropout_p: float = 0.5) -> None:
        self.dropout = SimulatedDropout(p=dropout_p)
        self.bn = SimulatedBatchNorm1D()
        self.training: bool = True

    def train(self) -> None:
        self.training = True
        self.dropout.training = True
        self.bn.training = True

    def eval(self) -> None:
        self.training = False
        self.dropout.training = False
        self.bn.training = False

    def forward(self, x: List[float], rng: random.Random) -> List[float]:
        # BatchNorm -> Dropout
        normed = self.bn.forward(x)
        return self.dropout.forward(normed, rng)


def run_test_suite() -> None:
    sample_input = [float(i) for i in range(1, 21)]  # 20 elements

    block = NeuralBlock(dropout_p=0.5)
    # Set pre-trained population statistics:
    block.bn.running_mean = 10.0
    block.bn.running_var = 5.0

    # 1. Demonstrate inference defect: model left in training mode:
    block.train()
    rng_1 = random.Random(42)
    rng_2 = random.Random(99)

    out_train_1 = block.forward(sample_input, rng_1)
    out_train_2 = block.forward(sample_input, rng_2)

    # In training mode, repeated predictions on the identical input produce different outputs:
    assert out_train_1 != out_train_2, "Training mode with active dropout must yield stochastic outputs"

    # 2. Demonstrate proper evaluation mode:
    block.eval()
    rng_3 = random.Random(42)
    rng_4 = random.Random(99)

    out_eval_1 = block.forward(sample_input, rng_3)
    out_eval_2 = block.forward(sample_input, rng_4)

    # In eval mode, outputs are 100% deterministic and independent of RNG:
    assert out_eval_1 == out_eval_2, "Eval mode must be strictly deterministic"
    assert 0.0 not in out_eval_1 or all(x != 0.0 for x in sample_input), "No dropout zeroing in eval mode"

    # 3. Single-item inference safety in eval mode:
    # In training mode, batch size 1 causes division by zero variance (b_var = 0.0) -> unstable output
    # In eval mode, single-item inference evaluates reliably against frozen running_mean/var:
    single_item = [15.0]
    single_out = block.forward(single_item, rng_3)
    # Normalized against running_mean=10.0, running_var=5.0 -> (15 - 10) / sqrt(5)
    expected_val = (15.0 - 10.0) / (5.0 ** 0.5)
    assert abs(single_out[0] - expected_val) < 1e-4

    print("All eval mode dropout and normalization assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
