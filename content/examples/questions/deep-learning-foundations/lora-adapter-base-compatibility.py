"""Low-rank adapter (LoRA) parameter reduction and base compatibility verification.

Demonstrates the mechanics and operational risks of Low-Rank Adaptation (LoRA):
1. Parameter reduction mechanics: decomposes weight updates delta_W into two low-rank matrices
   B [d x r] and A [r x k] with rank r << min(d, k), reducing trainable parameters by >98% and
   drastically cutting optimizer state memory.
2. The silent adapter incompatibility trap: an adapter contains only relative deltas (B @ A) tuned
   against a specific base model checkpoint. Loading an adapter onto a base model with different
   pre-trained weights, tokenizer vocabulary, or quantization produces nonsensical output without raising shape errors.
3. Compatibility manifest guard: adapters must store base model cryptographic hashes and vocabulary sizes
   in adapter_config.json to prevent silent semantic corruption at load time.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class LoRAConfig:
    r: int
    lora_alpha: float
    target_modules: List[str]
    base_model_name: str
    base_model_sha256: str
    vocab_size: int


class LoRALinear:
    """Simulates a frozen linear layer with Low-Rank Adapter matrices."""

    def __init__(self, in_features: int, out_features: int, config: LoRAConfig) -> None:
        self.in_features = in_features
        self.out_features = out_features
        self.r = config.r
        self.scaling = config.lora_alpha / config.r
        self.config = config

        # Frozen base weights W_0 [out x in]
        self.weight = [[0.1] * in_features for _ in range(out_features)]

        # Trainable adapter matrices: A [r x in], B [out x r]
        # In real LoRA: A is Gaussian initialized, B is initialized to 0
        self.lora_A = [[0.05] * in_features for _ in range(self.r)]
        self.lora_B = [[0.0] * self.r for _ in range(out_features)]

    def forward(self, x: List[float]) -> List[float]:
        # 1. Base forward: W_0 @ x
        base_out = [sum(self.weight[i][j] * x[j] for j in range(self.in_features)) for i in range(self.out_features)]

        # 2. Adapter forward: (B @ (A @ x)) * scaling
        ax = [sum(self.lora_A[i][j] * x[j] for j in range(self.in_features)) for i in range(self.r)]
        bax = [sum(self.lora_B[i][j] * ax[j] for j in range(self.r)) for i in range(self.out_features)]

        # Combine
        return [base_out[i] + (bax[i] * self.scaling) for i in range(self.out_features)]


def verify_adapter_compatibility(
    adapter_config: LoRAConfig,
    active_base_name: str,
    active_base_hash: str,
    active_vocab_size: int,
) -> Tuple[bool, Optional[str]]:
    """Verifies that an adapter matches the host base model checkpoint."""
    if adapter_config.base_model_sha256 != active_base_hash:
        return (
            False,
            f"Base model checkpoint mismatch: adapter was trained on hash {adapter_config.base_model_sha256[:8]}, "
            f"but active base model is {active_base_hash[:8]}",
        )

    if adapter_config.vocab_size != active_vocab_size:
        return (
            False,
            f"Vocabulary size mismatch: adapter expects {adapter_config.vocab_size}, but active base has {active_vocab_size}",
        )

    return True, None


def run_test_suite() -> None:
    in_dim = 4096
    out_dim = 4096
    rank = 16
    alpha = 32.0

    # 1. Verify parameter reduction:
    base_params = in_dim * out_dim  # 4096 * 4096 = 16,777,216 params
    lora_params = (in_dim * rank) + (rank * out_dim)  # (4096*16) + (16*4096) = 131,072 params

    reduction_pct = (1.0 - (lora_params / base_params)) * 100.0
    assert reduction_pct > 99.0, f"LoRA must reduce parameter footprint by >99%, achieved {reduction_pct:.2f}%"

    # 2. Test forward pass with B=0 initialization (yields exact base output):
    config = LoRAConfig(
        r=rank,
        lora_alpha=alpha,
        target_modules=["q_proj", "v_proj"],
        base_model_name="Llama-3-8B-Base",
        base_model_sha256="sha256-base-model-checkpoint-999",
        vocab_size=128256,
    )

    layer = LoRALinear(in_dim, out_dim, config)
    dummy_input = [1.0] * in_dim

    # At initialization (B=0), adapter contribution is exactly 0:
    out = layer.forward(dummy_input)
    # Expected base output: 4096 * 0.1 = 409.6
    assert abs(out[0] - 409.6) < 1e-4

    # Now train B (set non-zero):
    layer.lora_B[0][0] = 0.1
    out_adapted = layer.forward(dummy_input)
    # Adapter now modifies output:
    assert out_adapted[0] != out[0]

    # 3. Test compatibility validation guard:
    # Scenario A: Correct base model
    is_valid_a, err_a = verify_adapter_compatibility(
        config,
        active_base_name="Llama-3-8B-Base",
        active_base_hash="sha256-base-model-checkpoint-999",
        active_vocab_size=128256,
    )
    assert is_valid_a is True
    assert err_a is None

    # Scenario B: Incompatible base model (e.g. loading onto Instruct checkpoint with different hash)
    is_valid_b, err_b = verify_adapter_compatibility(
        config,
        active_base_name="Llama-3-8B-Instruct",
        active_base_hash="sha256-instruct-checkpoint-different",
        active_vocab_size=128256,
    )
    assert is_valid_b is False
    assert "Base model checkpoint mismatch" in str(err_b)

    # Scenario C: Vocabulary expansion mismatch
    is_valid_c, err_c = verify_adapter_compatibility(
        config,
        active_base_name="Llama-3-8B-Base",
        active_base_hash="sha256-base-model-checkpoint-999",
        active_vocab_size=128300,  # Expanded with custom tokens
    )
    assert is_valid_c is False
    assert "Vocabulary size mismatch" in str(err_c)

    print("All LoRA adapter base compatibility assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
