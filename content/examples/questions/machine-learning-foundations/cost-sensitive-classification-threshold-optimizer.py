#!/usr/bin/env python3
"""
Executable test suite demonstrating cost-sensitive classification threshold optimization
and the separation between model probabilities and business decision policies.

Addresses Interview Question 928:
"How do linear regression and logistic classification choose different outputs and losses?"
"""

from typing import List, Tuple, Dict, Any
import math


def sigmoid(z: float) -> float:
    """Numerically stable logistic sigmoid function mapping R -> (0, 1)."""
    if z >= 0.0:
        return 1.0 / (1.0 + math.exp(-z))
    else:
        exp_z = math.exp(z)
        return exp_z / (1.0 + exp_z)


def binary_cross_entropy(y_true: float, p_pred: float, eps: float = 1e-15) -> float:
    """Logistic regression objective: Log loss."""
    p_clipped = max(eps, min(1.0 - eps, p_pred))
    return - (y_true * math.log(p_clipped) + (1.0 - y_true) * math.log(1.0 - p_clipped))


class CostSensitiveThresholdOptimizer:
    """
    Separates statistical probability estimation from operational decision policies.
    Cost matrix:
      - C_FP: Cost of False Positive (e.g., $5 friction sending an SMS challenge to an authentic user)
      - C_FN: Cost of False Negative (e.g., $500 direct fraud loss letting an unauthorized charge pass)
      - C_TP: $0 (successful block)
      - C_TN: $0 (legitimate transaction processed)
    """
    def __init__(self, cost_fp: float, cost_fn: float) -> None:
        self.cost_fp: float = cost_fp
        self.cost_fn: float = cost_fn

    def calculate_expected_loss(
        self,
        probabilities: List[float],
        ground_truth: List[int],
        threshold: float
    ) -> Dict[str, float]:
        tp, fp, fn, tn = 0, 0, 0, 0

        for p, y in zip(probabilities, ground_truth):
            predicted_positive = (p >= threshold)
            if predicted_positive and y == 1:
                tp += 1
            elif predicted_positive and y == 0:
                fp += 1
            elif not predicted_positive and y == 1:
                fn += 1
            else:
                tn += 1

        total_cost = (fp * self.cost_fp) + (fn * self.cost_fn)
        return {
            "threshold": threshold,
            "tp": float(tp),
            "fp": float(fp),
            "fn": float(fn),
            "tn": float(tn),
            "total_cost": total_cost,
        }

    def find_optimal_threshold(
        self,
        probabilities: List[float],
        ground_truth: List[int],
        step: float = 0.01
    ) -> Dict[str, float]:
        best_eval = {"total_cost": float("inf"), "threshold": 0.5}
        current_t = step
        while current_t < 1.0:
            res = self.calculate_expected_loss(probabilities, ground_truth, current_t)
            if res["total_cost"] < best_eval["total_cost"]:
                best_eval = res
            current_t += step
        return best_eval


def run_test_suite() -> None:
    # 1. Verify Sigmoid and Binary Cross Entropy Loss:
    assert abs(sigmoid(0.0) - 0.5) < 1e-6
    assert sigmoid(10.0) > 0.999
    assert sigmoid(-10.0) < 0.001

    # Loss is minimal when prediction aligns with true label:
    loss_correct = binary_cross_entropy(1.0, 0.99)
    loss_wrong = binary_cross_entropy(1.0, 0.01)
    assert loss_wrong > 4.0, f"Expected high log loss for confident wrong prediction, got {loss_wrong}"
    assert loss_correct < 0.02

    # 2. Asymmetric Business Cost Scenario:
    # Population of 1,000 transactions: 950 legitimate (y=0), 50 fraud (y=1)
    # Model generates calibrated probabilities
    # Fraud costs $500 if missed (FN), verification SMS costs $5 (FP)
    cost_fp = 5.0
    cost_fn = 500.0
    optimizer = CostSensitiveThresholdOptimizer(cost_fp=cost_fp, cost_fn=cost_fn)

    # Theoretical optimal Bayes threshold for asymmetric costs:
    # tau* = C_FP / (C_FP + C_FN) = 5 / (5 + 500) = 5 / 505 ~ 0.0099 (approx 0.01 to 0.05 depending on distribution)
    theoretical_optimal_tau = cost_fp / (cost_fp + cost_fn)
    assert abs(theoretical_optimal_tau - 0.0099) < 0.001

    # Simulated validation set predictions:
    probs: List[float] = []
    labels: List[int] = []

    # 50 Frauds: probabilities distributed between 0.05 and 0.95
    for i in range(50):
        labels.append(1)
        probs.append(0.05 + 0.9 * (i / 50.0))

    # 950 Legitimate: probabilities distributed between 0.001 and 0.15
    for i in range(950):
        labels.append(0)
        probs.append(0.001 + 0.15 * (i / 950.0))

    # Evaluate naive default threshold (tau = 0.5):
    res_default = optimizer.calculate_expected_loss(probs, labels, threshold=0.5)

    # Find cost-optimal threshold:
    res_optimal = optimizer.find_optimal_threshold(probs, labels, step=0.01)

    # Naive threshold allows numerous false negatives (fraud escapes), incurring massive cost:
    assert res_default["fn"] >= 20, f"Naive 0.5 threshold should miss many frauds, missed: {res_default['fn']}"
    assert res_default["total_cost"] >= 10000.0, f"Expected high cost for naive 0.5 threshold, got ${res_default['total_cost']}"

    # Optimized threshold drastically cuts total business cost by lowering threshold to intercept fraud:
    assert res_optimal["threshold"] < 0.20, f"Optimal threshold should be aggressive (<0.20), got {res_optimal['threshold']}"
    assert res_optimal["total_cost"] < res_default["total_cost"] * 0.4, (
        f"Optimized threshold should reduce total cost by >60%! (Default: ${res_default['total_cost']}, Optimal: ${res_optimal['total_cost']})"
    )

    print("All cost-sensitive classification threshold optimizer assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
