"""Causal language model tokenization, label shifting, and causal masking harness.

Demonstrates the formulation of an autoregressive causal language model training example:
1. Tokenizer mapping: converts raw Unicode text into discrete vocabulary token IDs.
2. Label shifting (next-token prediction):
   - Input tokens: sequence[:-1] (tokens 0 to T-2)
   - Target labels: sequence[1:] (tokens 1 to T-1)
   The prediction target for token t is strictly token t+1.
3. The future information leakage defect: if the causal attention mask is omitted or misaligned,
   tokens can attend to future targets. Training loss collapses to near-zero by trivial copying,
   but autoregressive generation fails completely at inference time.
4. Loss masking: padding tokens must be marked with ignore_index (-100) to exclude them from cross-entropy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


IGNORE_INDEX = -100


@dataclass(frozen=True)
class TrainingExample:
    input_ids: List[int]
    target_labels: List[int]
    causal_mask: List[List[int]]  # 1 = allowed to attend, 0 = masked (future)


def create_causal_training_example(
    token_ids: List[int], max_seq_len: int, pad_token_id: int = 0
) -> TrainingExample:
    """Constructs shifted input/target tensors and lower-triangular causal mask."""
    # Truncate to max_seq_len
    tokens = token_ids[:max_seq_len]

    # Shift inputs and targets:
    # input = tokens[:-1]
    # target = tokens[1:]
    raw_inputs = tokens[:-1]
    raw_targets = tokens[1:]

    current_len = len(raw_inputs)
    pad_needed = max_seq_len - 1 - current_len

    # Pad inputs with pad_token_id, pad targets with IGNORE_INDEX
    input_ids = raw_inputs + [pad_token_id] * pad_needed
    target_labels = raw_targets + [IGNORE_INDEX] * pad_needed

    seq_size = len(input_ids)
    # Build lower-triangular causal attention mask (1 where i >= j, 0 where j > i)
    # Also mask out padding positions
    causal_mask: List[List[int]] = []
    for i in range(seq_size):
        row: List[int] = []
        for j in range(seq_size):
            if j <= i and j < current_len and i < current_len:
                row.append(1)  # Can attend
            else:
                row.append(0)  # Masked (future token or padding)
        causal_mask.append(row)

    return TrainingExample(
        input_ids=input_ids,
        target_labels=target_labels,
        causal_mask=causal_mask,
    )


def run_test_suite() -> None:
    # Raw sentence tokens: "The", "cat", "sat", "on", "the", "mat"
    # Token IDs: [101, 205, 308, 412, 101, 550] (Length 6)
    sample_tokens = [101, 205, 308, 412, 101, 550]
    max_len = 8

    example = create_causal_training_example(sample_tokens, max_seq_len=max_len, pad_token_id=0)

    # 1. Verify exact label shift:
    # Inputs: [101, 205, 308, 412, 101] (tokens 0..4)
    # Targets: [205, 308, 412, 101, 550] (tokens 1..5)
    assert example.input_ids[:5] == [101, 205, 308, 412, 101]
    assert example.target_labels[:5] == [205, 308, 412, 101, 550]

    # Target at index 0 (205) is the token that immediately follows input at index 0 (101):
    for idx in range(4):
        assert example.target_labels[idx] == example.input_ids[idx + 1]

    # 2. Verify padding and ignore_index:
    # Inputs are padded with 0, targets with -100 (IGNORE_INDEX)
    assert example.input_ids[5:] == [0, 0]
    assert example.target_labels[5:] == [IGNORE_INDEX, IGNORE_INDEX]

    # 3. Verify lower-triangular causal attention mask:
    # Row 0 (position 0) can ONLY attend to itself (col 0):
    assert example.causal_mask[0][0] == 1
    assert example.causal_mask[0][1] == 0, "Position 0 must NOT attend to future position 1!"

    # Row 2 (position 2) can attend to positions 0, 1, 2, but NOT 3 or future:
    assert example.causal_mask[2][:3] == [1, 1, 1]
    assert example.causal_mask[2][3] == 0

    # Padding positions cannot attend to anything:
    assert example.causal_mask[5] == [0] * len(example.input_ids)

    print("All causal LM token shift and mask assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
