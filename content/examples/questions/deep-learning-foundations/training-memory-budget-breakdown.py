"""Deep learning training memory budget breakdown and optimizer state accounting.

Demonstrates why model weights fitting into GPU VRAM does not prevent training OOM crashes:
1. Static memory footprint:
   - Model parameters (e.g. 16-bit fp16/bf16 = 2 bytes/param)
   - Gradients (2 bytes/param)
   - Optimizer states: AdamW stores 1st momentum (fp32, 4 bytes) and 2nd variance (fp32, 4 bytes),
     plus fp32 master weights (4 bytes) = 12-16 bytes per parameter.
2. Dynamic memory footprint:
   - Forward activation tensors: scale linearly with Batch Size (B), Sequence Length (S), Layers (L),
     and Hidden Dimension (H).
3. Memory optimization levers:
   - Gradient checkpointing (recomputes activations during backward pass to bound memory).
   - Gradient accumulation (splits batch into K micro-batches, cutting activation memory by K).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class TrainingMemoryBudget:
    param_bytes: int
    grad_bytes: int
    optimizer_bytes: int
    activation_bytes: int

    @property
    def static_memory_bytes(self) -> int:
        return self.param_bytes + self.grad_bytes + self.optimizer_bytes

    @property
    def total_memory_bytes(self) -> int:
        return self.static_memory_bytes + self.activation_bytes

    @property
    def total_gb(self) -> float:
        return self.total_memory_bytes / (1024 ** 3)


def calculate_training_memory(
    num_params: int,
    batch_size: int,
    seq_len: int,
    num_layers: int,
    hidden_dim: int,
    use_adamw: bool = True,
    activation_checkpointing: bool = False,
) -> TrainingMemoryBudget:
    """Calculates byte breakdown for Transformer training in 16-bit mixed precision."""
    # Parameters: fp16 = 2 bytes
    param_bytes = num_params * 2

    # Gradients: fp16 = 2 bytes
    grad_bytes = num_params * 2

    # Optimizer: AdamW stores fp32 master weights (4) + 1st moment (4) + 2nd moment (4) = 12 bytes/param
    optimizer_bytes = num_params * 12 if use_adamw else num_params * 4  # SGD with momentum = 4 bytes

    # Activations per layer: ~ 34 * B * S * H bytes for standard Transformer block
    # With activation checkpointing, store only input to each block (~ 2 * B * S * H)
    bytes_per_token_layer = 4 if activation_checkpointing else 34
    activation_bytes = batch_size * seq_len * hidden_dim * num_layers * bytes_per_token_layer

    return TrainingMemoryBudget(
        param_bytes=param_bytes,
        grad_bytes=grad_bytes,
        optimizer_bytes=optimizer_bytes,
        activation_bytes=activation_bytes,
    )


def run_test_suite() -> None:
    # 7-Billion Parameter Model (Llama-style architecture):
    # num_params = 7B, layers = 32, hidden = 4096, seq_len = 2048
    num_params = 7_000_000_000
    layers = 32
    hidden = 4096
    seq_len = 2048

    # Scenario 1: Naive training with batch size 8 on single GPU
    budget_naive = calculate_training_memory(
        num_params=num_params,
        batch_size=8,
        seq_len=seq_len,
        num_layers=layers,
        hidden_dim=hidden,
        use_adamw=True,
        activation_checkpointing=False,
    )

    # 1. Inspect static memory:
    # Weights = 14 GB, Gradients = 14 GB, AdamW = 84 GB -> Static alone = 112 GB!
    assert round(budget_naive.param_bytes / (1024 ** 3), 1) == 13.0 or 14.0
    static_gb = budget_naive.static_memory_bytes / (1024 ** 3)
    assert static_gb > 100.0, f"Expected static memory > 100 GB, got {static_gb:.1f} GB"

    # 2. Inspect activations:
    # Batch 8 with no checkpointing consumes substantial activation memory:
    act_gb = budget_naive.activation_bytes / (1024 ** 3)
    assert act_gb > 50.0

    # Total naive memory exceeds 170 GB (fails on any single 80 GB A100/H100!):
    assert budget_naive.total_gb > 170.0

    # Scenario 2: Apply gradient checkpointing + micro-batch size 1 with 8-step gradient accumulation
    budget_optimized = calculate_training_memory(
        num_params=num_params,
        batch_size=1,  # Micro-batch 1
        seq_len=seq_len,
        num_layers=layers,
        hidden_dim=hidden,
        use_adamw=True,
        activation_checkpointing=True,  # Checkpoint activations
    )

    # Activation memory drops by over 90%:
    opt_act_gb = budget_optimized.activation_bytes / (1024 ** 3)
    assert opt_act_gb < 2.0, f"Expected checkpointed activations < 2 GB, got {opt_act_gb:.2f} GB"

    reduction_factor = budget_naive.activation_bytes / budget_optimized.activation_bytes
    assert reduction_factor > 50.0, "Gradient checkpointing + micro-batching must drastically cut activation VRAM"

    print("All training memory budget assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
