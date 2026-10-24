#!/usr/bin/env python3
"""
Executable test suite demonstrating the accuracy paradox on imbalanced datasets,
and evaluating full Precision-Recall curves versus deceptive ROC metrics.

Addresses Interview Question 932:
"How do precision, recall and PR metrics expose failure on an imbalanced task?"
"""

from typing import List, Tuple, Dict, Any


def compute_confusion_matrix(y_true: List[int], y_pred: List[int]) -> Dict[str, int]:
    tp, fp, fn, tn = 0, 0, 0, 0
    for yt, yp in zip(y_true, y_pred):
        if yp == 1 and yt == 1:
            tp += 1
        elif yp == 1 and yt == 0:
            fp += 1
        elif yp == 0 and yt == 1:
            fn += 1
        else:
            tn += 1
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def compute_metrics(y_true: List[int], y_pred: List[int]) -> Dict[str, float]:
    cm = compute_confusion_matrix(y_true, y_pred)
    total = len(y_true)
    accuracy = (cm["tp"] + cm["tn"]) / total if total > 0 else 0.0

    denom_p = cm["tp"] + cm["fp"]
    precision = cm["tp"] / denom_p if denom_p > 0 else 0.0

    denom_r = cm["tp"] + cm["fn"]
    recall = cm["tp"] / denom_r if denom_r > 0 else 0.0

    f1 = (2.0 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": cm["tp"],
        "fp": cm["fp"],
        "fn": cm["fn"],
        "tn": cm["tn"],
    }


def compute_pr_curve(y_true: List[int], scores: List[float], thresholds: List[float]) -> List[Dict[str, float]]:
    curve = []
    for t in sorted(thresholds):
        preds = [1 if s >= t else 0 for s in scores]
        m = compute_metrics(y_true, preds)
        curve.append({
            "threshold": t,
            "precision": m["precision"],
            "recall": m["recall"],
            "f1": m["f1"]
        })
    return curve


def run_test_suite() -> None:
    # 1. Concrete Case: 4 Negatives (0) and 1 Positive (1)
    # y_true = [0, 0, 0, 0, 1] (80% negative prevalence)
    y_true_simple = [0, 0, 0, 0, 1]

    # Model A: Trivial majority-class dummy classifier (predicts 0 for everything)
    dummy_pred = [0, 0, 0, 0, 0]
    dummy_metrics = compute_metrics(y_true_simple, dummy_pred)

    # Accuracy paradox: The dummy model has 80% accuracy!
    assert dummy_metrics["accuracy"] == 0.80, f"Expected 80% accuracy, got {dummy_metrics['accuracy']}"
    # BUT positive recall is exactly 0.0:
    assert dummy_metrics["recall"] == 0.0, f"Expected 0.0 recall, got {dummy_metrics['recall']}"
    assert dummy_metrics["f1"] == 0.0

    # Model B: An attentive classifier that catches the 1 positive but has 1 false positive
    alert_pred = [0, 0, 0, 1, 1]
    alert_metrics = compute_metrics(y_true_simple, alert_pred)

    # Accuracy is 80% (same as dummy!), but recall is 100% and precision is 50%:
    assert alert_metrics["accuracy"] == 0.80
    assert alert_metrics["recall"] == 1.0, "Caught the single positive"
    assert alert_metrics["precision"] == 0.5, "1 TP out of 2 predicted alerts"
    assert alert_metrics["f1"] > 0.60

    # 2. Large Scale Imbalanced Production Case:
    # 1,000 cases: 900 negative (0), 100 positive (1) (10% prevalence)
    y_true = [0] * 900 + [1] * 100

    # Model scores: Positives score higher on average [0.4, 0.95], Negatives score lower [0.01, 0.6]
    import random
    rng = random.Random(42)
    scores: List[float] = []
    for y in y_true:
        if y == 1:
            scores.append(0.4 + 0.55 * rng.random())
        else:
            scores.append(0.01 + 0.50 * rng.random())

    thresholds = [0.1, 0.3, 0.5, 0.7, 0.85]
    pr_curve = compute_pr_curve(y_true, scores, thresholds)

    # Invariant: As threshold increases, recall monotonically decreases while precision generally increases
    for i in range(len(pr_curve) - 1):
        assert pr_curve[i]["recall"] >= pr_curve[i+1]["recall"], "Recall must be monotonically non-increasing with threshold"

    # At low threshold (0.1), recall is near 100% but precision is diluted by false alarms:
    assert pr_curve[0]["recall"] > 0.95
    # At high threshold (0.85), precision is high but recall drops:
    assert pr_curve[-1]["precision"] > pr_curve[0]["precision"]

    print("All imbalanced precision-recall curve evaluator assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()

