"""Numerically stable softmax, LogSumExp, and floating-point overflow prevention harness.

Demonstrates why subtracting the maximum logit is mandatory before computing softmax:
1. IEEE 754 floating-point overflow: in 64-bit float, exp(x) overflows to 'inf' when x > 709.78.
   If logits reach 1000 (e.g. unnormalized dot products or early confident predictions),
   naive exp(z_i) produces 'inf', resulting in inf / inf = NaN.
2. Softmax shift-invariance:
   softmax(z)_i = exp(z_i) / sum_j exp(z_j) = exp(z_i - C) / sum_j exp(z_j - C) for any scalar C.
3. Stable implementation: setting C = max(z) guarantees the largest exponent is exp(0) = 1.0,
   and all other exponents lie strictly in (0.0, 1.0], completely eliminating overflow.
4. LogSumExp stability: logsumexp(z) = C + log(sum_j exp(z_j - C)) prevents underflow in cross-entropy loss.
"""

from __future__ import annotations

import math
from typing import List, Tuple


def naive_unstable_softmax(logits: List[float]) -> List[float]:
    """Anti-pattern: computes raw exponentials without subtracting max."""
    try:
        exps = [math.exp(z) for z in logits]
        sum_exp = sum(exps)
        return [e / sum_exp for e in exps]
    except OverflowError:
        return [float("nan")] * len(logits)


def stable_softmax(logits: List[float]) -> List[float]:
    """Production pattern: subtracts C = max(logits) before exponentiating."""
    c = max(logits)
    shifted_exps = [math.exp(z - c) for z in logits]
    sum_shifted = sum(shifted_exps)
    return [e / sum_shifted for e in shifted_exps]


def stable_logsumexp(logits: List[float]) -> float:
    """Computes log(sum(exp(logits))) stably."""
    c = max(logits)
    return c + math.log(sum(math.exp(z - c) for z in logits))


def stable_log_softmax(logits: List[float]) -> List[float]:
    """Computes log(softmax(z)) = z_i - logsumexp(z) without intermediate probability underflow."""
    lse = stable_logsumexp(logits)
    return [z - lse for z in logits]


def run_test_suite() -> None:
    # 1. Normal range logits (stable and naive match):
    normal_logits = [2.0, 1.0, 0.1]
    naive_out = naive_unstable_softmax(normal_logits)
    stable_out = stable_softmax(normal_logits)

    for n_val, s_val in zip(naive_out, stable_out):
        assert abs(n_val - s_val) < 1e-6
    assert abs(sum(stable_out) - 1.0) < 1e-6

    # 2. Extreme logits that cause overflow in naive softmax:
    # Logits: [1000.0, 1001.0, 1002.0]
    # In float64, math.exp(1000.0) raises OverflowError or returns inf:
    extreme_logits = [1000.0, 1001.0, 1002.0]

    naive_extreme = naive_unstable_softmax(extreme_logits)
    # Naive version failed and returned NaN:
    assert any(math.isnan(x) for x in naive_extreme), "Naive softmax must overflow on large logits"

    # Stable version succeeds without any overflow:
    stable_extreme = stable_softmax(extreme_logits)
    assert not any(math.isnan(x) for x in stable_extreme)
    assert abs(sum(stable_extreme) - 1.0) < 1e-6

    # Expected values for [1000, 1001, 1002] are identical to [0, 1, 2]:
    expected_probs = stable_softmax([0.0, 1.0, 2.0])
    for s_val, exp_val in zip(stable_extreme, expected_probs):
        assert abs(s_val - exp_val) < 1e-6

    # 3. LogSumExp numerical stability:
    lse = stable_logsumexp(extreme_logits)
    # Expected: 1002 + log(exp(-2) + exp(-1) + 1.0)
    expected_lse = 1002.0 + math.log(math.exp(-2.0) + math.exp(-1.0) + 1.0)
    assert abs(lse - expected_lse) < 1e-6

    log_probs = stable_log_softmax(extreme_logits)
    for lp, p in zip(log_probs, stable_extreme):
        assert abs(math.exp(lp) - p) < 1e-6

    print("All numerically stable softmax LogSumExp assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()

