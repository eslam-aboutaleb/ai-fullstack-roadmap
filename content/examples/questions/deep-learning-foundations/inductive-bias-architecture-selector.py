"""Inductive bias analysis and architectural selection suite (CNN vs RNN vs Attention).

Demonstrates the trade-offs of architectural inductive biases across deep learning paradigms:
1. Convolutional architectures (CNN): strong spatial inductive bias (translation equivariance, local connectivity).
   Highly parameter-efficient on grid data (images, audio spectrograms) and ideal for low-latency edge deployment.
2. Recurrent architectures (RNN/GRU/LSTM): sequential temporal inductive bias (Markovian hidden state updates).
   Processes sequences in O(T) compute and O(1) state memory, but strictly sequential execution prevents training parallelism.
3. Self-Attention architectures (Transformers): minimal inductive bias (permutation equivariance, data-dependent routing).
   Enables all-to-all context aggregation and parallel training, but exhibits quadratic O(T^2) complexity and requires massive data to generalize.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Tuple


ArchitectureType = Literal["CNN", "RNN", "ATTENTION"]


@dataclass(frozen=True)
class TaskRequirements:
    modality: str  # "image_grid", "streaming_sensor", "open_domain_text"
    dataset_size_samples: int
    max_latency_ms: float
    requires_parallel_training: bool
    context_length: int


@dataclass(frozen=True)
class ArchitectureProfile:
    name: ArchitectureType
    inductive_bias_strength: str  # "HIGH", "MEDIUM", "LOW"
    time_complexity_seq: str     # "O(1)", "O(T)", "O(T^2)"
    edge_suitability: str        # "EXCELLENT", "MODERATE", "POOR"


def select_optimal_architecture(task: TaskRequirements) -> Tuple[ArchitectureType, str]:
    """Selects deep learning architecture based on domain inductive bias and resource constraints."""
    if task.modality == "image_grid" and task.dataset_size_samples < 100_000 and task.max_latency_ms < 10.0:
        return (
            "CNN",
            "Local spatial connectivity and translation equivariance generalize efficiently from small image datasets under tight edge latency.",
        )

    if task.modality == "streaming_sensor" and not task.requires_parallel_training:
        return (
            "RNN",
            "Sequential hidden state updates process real-time sensor streams in O(1) memory without quadratic context overhead.",
        )

    if task.modality == "open_domain_text" or task.requires_parallel_training:
        return (
            "ATTENTION",
            "Data-dependent routing and parallel self-attention capture arbitrary long-range semantic dependencies.",
        )

    return "CNN", "Default fallback to compact convolutional baseline"


def calculate_receptive_field_vs_attention(seq_len: int) -> Tuple[int, int]:
    """Compares pairwise interactions: CNN local kernel (e.g. k=3) vs Full Attention."""
    # CNN with kernel 3 over 1 layer: each element attends to 3 neighbors
    cnn_pairwise_ops = seq_len * 3
    # Self-attention: each element attends to all T elements -> T * T ops
    attention_pairwise_ops = seq_len * seq_len
    return cnn_pairwise_ops, attention_pairwise_ops


def run_test_suite() -> None:
    # 1. Edge Image Classification task (compact dataset, tight 5ms latency):
    edge_image_task = TaskRequirements(
        modality="image_grid",
        dataset_size_samples=25_000,
        max_latency_ms=5.0,
        requires_parallel_training=True,
        context_length=1024,
    )
    arch_image, reason_image = select_optimal_architecture(edge_image_task)
    assert arch_image == "CNN"
    assert "translation equivariance" in reason_image

    # 2. Continuous real-time sensor processing on IoT microcontroller:
    sensor_task = TaskRequirements(
        modality="streaming_sensor",
        dataset_size_samples=50_000,
        max_latency_ms=2.0,
        requires_parallel_training=False,
        context_length=10_000,
    )
    arch_sensor, reason_sensor = select_optimal_architecture(sensor_task)
    assert arch_sensor == "RNN"
    assert "O(1) memory" in reason_sensor

    # 3. Open domain language modeling / in-context learning:
    llm_task = TaskRequirements(
        modality="open_domain_text",
        dataset_size_samples=10_000_000,
        max_latency_ms=100.0,
        requires_parallel_training=True,
        context_length=4096,
    )
    arch_llm, reason_llm = select_optimal_architecture(llm_task)
    assert arch_llm == "ATTENTION"
    assert "Data-dependent routing" in reason_llm

    # 4. Complexity comparison: CNN linear vs Attention quadratic scaling:
    t = 1000
    cnn_ops, attn_ops = calculate_receptive_field_vs_attention(seq_len=t)
    assert cnn_ops == 3000
    assert attn_ops == 1_000_000
    assert attn_ops / cnn_ops > 300.0, "Attention exhibits quadratic computational growth"

    print("All inductive bias architecture selection assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
