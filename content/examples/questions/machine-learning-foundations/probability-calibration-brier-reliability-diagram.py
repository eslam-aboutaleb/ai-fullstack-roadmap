#!/usr/bin/env python3
"""
Executable test suite demonstrating discrimination versus probability calibration,
measuring Expected Calibration Error (ECE) and Brier Score.

Addresses Interview Question 933:
"Why can an accurate ranking still produce poorly calibrated probabilities?"
"""

from typing import List, Tuple, Dict, Any
import math


def compute_roc_auc_binary(y_true: List[int], scores: List[float]) -> float:
    """Computes exact Mann-Whitney U statistic formulation of ROC-AUC."""
    pos_scores = [s for y, s in zip(y_true, scores) if y == 1]
    neg_scores = [s for y, s in zip(y_true, scores) if y == 0]

    n_pos = len(pos_scores)
    n_neg = len(neg_scores)
    if n_pos == 0 or n_neg == 0:
        return 0.5

    concordant = 0.0
    for ps in pos_scores:
        for ns in neg_scores:
            if ps > ns:
                concordant += 1.0
            elif ps == ns:
                concordant += 0.5

    return concordant / (n_pos * n_neg)


def compute_brier_score(y_true: List[int], probabilities: List[float]) -> float:
    """Brier score: Mean squared error between predicted probabilities and binary outcomes."""
    return sum((p - y) ** 2 for y, p in zip(y_true, probabilities)) / len(y_true)


def compute_expected_calibration_error(
    y_true: List[int],
    probabilities: List[float],
    n_bins: int = 5
) -> Dict[str, Any]:
    """
    Computes ECE: Expected Calibration Error across equal-width confidence bins.
    ECE = sum_{b} (|B_b| / N) * |accuracy(B_b) - confidence(B_b)|
    """
    n = len(y_true)
    bin_size = 1.0 / n_bins
    bins: List[Dict[str, Any]] = []

    for b in range(n_bins):
        b_low = b * bin_size
        b_high = (b + 1) * bin_size
        indices = [
            i for i, p in enumerate(probabilities)
            if (b_low <= p < b_high) or (b == n_bins - 1 and b_low <= p <= b_high)
        ]
        if not indices:
            bins.append({"count": 0, "confidence": 0.0, "accuracy": 0.0, "error": 0.0})
            continue

        bin_conf = sum(probabilities[i] for i in indices) / len(indices)
        bin_acc = sum(y_true[i] for i in indices) / len(indices)
        error = abs(bin_acc - bin_conf)
        bins.append({
            "count": len(indices),
            "confidence": bin_conf,
            "accuracy": bin_acc,
            "error": error
        })

    ece = sum((b["count"] / n) * b["error"] for b in bins)
    return {"ece": ece, "bins": bins}


def run_test_suite() -> None:
    # Ground truth: 100 samples (50 positive, 50 negative)
    # Both models rank samples identically (perfect discrimination, ROC-AUC = 1.0)
    # Negatives have scores 0..49, Positives have scores 50..99
    y_true = [0] * 50 + [1] * 50

    # Model A: Uncalibrated, wildly overconfident
    # All 50 negatives have probability 0.85
    # All 50 positives have probability 0.99
    probs_uncalibrated = [0.85] * 50 + [0.99] * 50

    # Model B: Perfectly calibrated probabilities
    # 50 negatives have probability 0.05
    # 50 positives have probability 0.95
    probs_calibrated = [0.05] * 50 + [0.95] * 50

    # 1. Discrimination (Ranking) Equivalence:
    auc_uncal = compute_roc_auc_binary(y_true, probs_uncalibrated)
    auc_cal = compute_roc_auc_binary(y_true, probs_calibrated)

    # Both models achieve identical perfect ROC-AUC = 1.0!
    assert auc_uncal == 1.0
    assert auc_cal == 1.0

    # 2. Probability Calibration Divergence:
    # Model A's Brier score is terrible because it predicted 85% probability for non-events:
    brier_uncal = compute_brier_score(y_true, probs_uncalibrated)
    brier_cal = compute_brier_score(y_true, probs_calibrated)

    assert brier_uncal > 0.35, f"Expected high Brier score for uncalibrated model, got {brier_uncal:.4f}"
    assert brier_cal < 0.01, f"Expected near-zero Brier score for calibrated model, got {brier_cal:.4f}"

    # 3. Expected Calibration Error (ECE):
    ece_uncal = compute_expected_calibration_error(y_true, probs_uncalibrated, n_bins=5)
    ece_cal = compute_expected_calibration_error(y_true, probs_calibrated, n_bins=5)

    # Uncalibrated model has massive ECE (>0.40):
    assert ece_uncal["ece"] > 0.40, f"Expected ECE > 0.40, got {ece_uncal['ece']:.4f}"
    # Calibrated model has tiny ECE (<0.05):
    assert ece_cal["ece"] < 0.05, f"Expected ECE < 0.05, got {ece_cal['ece']:.4f}"

    # 4. Engineering Case from Question 933:
    # "Two models order all alerts identically, but one calls almost every alert 99% likely.
    # Only about 70% of that bin is positive."
    alert_true = [0] * 30 + [1] * 70  # 70% empirical positive rate
    alert_probs = [0.99] * 100         # Model claims 99% confidence for all
    alert_ece = compute_expected_calibration_error(alert_true, alert_probs, n_bins=5)

    # Confidence is 0.99, empirical accuracy is 0.70 -> Error is ~0.29:
    assert abs(alert_ece["ece"] - 0.29) < 0.01, (
        f"Expected calibration error ~0.29, got {alert_ece['ece']:.4f}"
    )

    print("All probability calibration Brier reliability diagram assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()

