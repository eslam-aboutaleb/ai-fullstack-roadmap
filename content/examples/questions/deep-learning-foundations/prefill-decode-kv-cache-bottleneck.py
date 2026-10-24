"""LLM serving prefill vs decode bottlenecks and KV cache memory accounting.

Demonstrates the fundamental operational asymmetry between LLM inference phases:
1. Prefill phase (compute-bound): processes all prompt tokens in parallel with high arithmetic intensity,
   saturating GPU Tensor Cores while generating initial Key-Value (KV) cache entries.
2. Decode phase (memory-bandwidth bound): generates tokens one by one sequentially with low arithmetic intensity.
   Each step must stream all model weights from High Bandwidth Memory (HBM) to compute a single token.
3. KV cache memory explosion:
   KV Cache bytes per token = 2 * (num_layers) * (num_kv_heads) * (head_dim) * (precision_bytes).
   While model weights remain static, KV cache memory scales dynamically with Concurrency (B) and Context Length (S),
   causing unexpected VRAM exhaustion on long sessions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class ModelArchitectureConfig:
    name: str
    num_layers: int
    num_attention_heads: int
    num_kv_heads: int  # Grouped Query Attention (GQA) reduces KV heads
    head_dim: int
    precision_bytes: int  # fp16 = 2, fp8 = 1


def calculate_kv_cache_bytes_per_token(config: ModelArchitectureConfig) -> int:
    """Bytes = 2 (K and V) * layers * kv_heads * head_dim * bytes_per_element."""
    return 2 * config.num_layers * config.num_kv_heads * config.head_dim * config.precision_bytes


def calculate_serving_memory(
    config: ModelArchitectureConfig,
    num_params: int,
    concurrent_requests: int,
    avg_seq_len: int,
) -> Tuple[float, float, float]:
    """Returns (weight_memory_gb, kv_cache_memory_gb, total_memory_gb)."""
    weight_bytes = num_params * config.precision_bytes
    bytes_per_token = calculate_kv_cache_bytes_per_token(config)
    kv_cache_bytes = concurrent_requests * avg_seq_len * bytes_per_token

    weight_gb = weight_bytes / (1024 ** 3)
    kv_gb = kv_cache_bytes / (1024 ** 3)
    return weight_gb, kv_gb, weight_gb + kv_gb


def run_test_suite() -> None:
    # Llama-3-8B architecture:
    # 32 layers, 32 query heads, 8 KV heads (Grouped Query Attention), head_dim = 128, fp16 = 2 bytes
    llama_8b = ModelArchitectureConfig(
        name="Llama-3-8B",
        num_layers=32,
        num_attention_heads=32,
        num_kv_heads=8,
        head_dim=128,
        precision_bytes=2,
    )
    num_params_8b = 8_000_000_000

    # 1. Verify exact KV cache bytes per token:
    # Formula: 2 * 32 * 8 * 128 * 2 = 131,072 bytes (128 KB per token!)
    bytes_per_token = calculate_kv_cache_bytes_per_token(llama_8b)
    assert bytes_per_token == 131072
    assert bytes_per_token / 1024 == 128.0  # Exactly 128 KB/token

    # 2. Short prompt scenario (4 requests, 512 tokens each):
    weight_gb, kv_gb_short, total_gb_short = calculate_serving_memory(
        llama_8b, num_params_8b, concurrent_requests=4, avg_seq_len=512
    )
    # Weights = ~14.9 GB, KV cache = 4 * 512 * 128KB = 256 MB (0.25 GB)
    assert round(weight_gb, 1) == 14.9
    assert kv_gb_short < 0.3
    assert total_gb_short < 16.0  # Fits easily on 24 GB GPU

    # 3. Long context concurrent production scenario:
    # 32 concurrent sessions with 8,192 tokens each (e.g. document summarization):
    # Total tokens = 32 * 8,192 = 262,144 tokens
    # KV cache = 262,144 * 128 KB = 33,554,432 KB = 32.0 GB!
    _, kv_gb_long, total_gb_long = calculate_serving_memory(
        llama_8b, num_params_8b, concurrent_requests=32, avg_seq_len=8192
    )

    assert round(kv_gb_long, 1) == 32.0
    # Total memory = 14.9 GB (weights) + 32.0 GB (KV cache) = 46.9 GB!
    # A 24 GB or 40 GB GPU experiences an immediate Out of Memory crash,
    # despite model weights remaining identical:
    assert total_gb_long > 45.0, "Long context KV cache must dominate total memory"

    # 4. Impact of FP8 quantization on KV cache:
    llama_8b_fp8 = ModelArchitectureConfig(
        name="Llama-3-8B-FP8-KV",
        num_layers=32,
        num_attention_heads=32,
        num_kv_heads=8,
        head_dim=128,
        precision_bytes=1,  # 8-bit KV cache
    )
    bytes_per_token_fp8 = calculate_kv_cache_bytes_per_token(llama_8b_fp8)
    assert bytes_per_token_fp8 == 65536  # Drops to 64 KB/token
    assert bytes_per_token_fp8 == bytes_per_token / 2

    print("All prefill decode KV cache bottleneck assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
