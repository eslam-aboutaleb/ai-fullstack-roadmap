"""Bayes' rule, base-rate fallacy, and positive predictive value harness.

Demonstrates why high model sensitivity (recall) does not guarantee high alert precision in rare-event domains:
1. The base-rate fallacy: when the prior base rate of an event is low (e.g. 1% fraud),
   false positives from the massive negative class easily outnumber true positives from the tiny positive class.
2. The accuracy and sensitivity paradox: a classifier with 90% recall and 99% specificity can boast
   98.9% overall accuracy, yet when an alert fires, the probability that the event is actually positive
   (Precision / Positive Predictive Value) is less than 50%!
3. Bayes' theorem application: P(Positive | Alert) = P(Alert | Positive) * P(Positive) / P(Alert).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class ConfusionMatrix:
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int

    @property
    def total(self) -> int:
        return self.true_positives + self.false_positives + self.true_negatives + self.false_negatives

    @property
    def sensitivity(self) -> float:
        """Recall = TP / (TP + FN)"""
        return self.true_positives / (self.true_positives + self.false_negatives)

    @property
    def specificity(self) -> float:
        """TNR = TN / (TN + FP)"""
        return self.true_negatives / (self.true_negatives + self.false_positives)

    @property
    def precision(self) -> float:
        """PPV = TP / (TP + FP)"""
        return self.true_positives / (self.true_positives + self.false_positives)

    @property
    def overall_accuracy(self) -> float:
        return (self.true_positives + self.true_negatives) / self.total


def evaluate_rare_event_classifier(
    total_population: int,
    positive_count: int,
    tpr: float,  # Sensitivity (e.g. 0.90)
    fpr: float,  # False positive rate (e.g. 0.01)
) -> ConfusionMatrix:
    """Calculates population confusion matrix and Bayesian posterior precision."""
    negative_count = total_population - positive_count

    tp = round(positive_count * tpr)
    fn = positive_count - tp

    fp = round(negative_count * fpr)
    tn = negative_count - fp

    return ConfusionMatrix(
        true_positives=tp,
        false_positives=fp,
        true_negatives=tn,
        false_negatives=fn,
    )


def run_test_suite() -> None:
    # Population of 10,000 security logs with 100 genuine intrusion events (1% base rate)
    total_pop = 10_000
    positives = 100
    tpr = 0.90  # 90% detection rate
    fpr = 0.01  # 1% false alarm rate (99% specificity)

    cm = evaluate_rare_event_classifier(total_pop, positives, tpr=tpr, fpr=fpr)

    # 1. Verify counts:
    # 90 True Positives, 10 False Negatives
    assert cm.true_positives == 90
    assert cm.false_negatives == 10

    # 9,900 Negatives * 1% FPR = 99 False Positives
    assert cm.false_positives == 99
    assert cm.true_negatives == 9801
    assert cm.total == 10_000

    # 2. Verify surface metrics look stellar:
    assert cm.sensitivity == 0.90  # 90% recall
    assert cm.specificity == 0.99  # 99% specificity
    assert cm.overall_accuracy == 0.9891  # 98.91% accuracy!

    # 3. Expose the base-rate fallacy:
    # Total alerts generated = 90 (TP) + 99 (FP) = 189 alerts.
    # Positive Predictive Value (Precision): 90 / 189 = ~47.62%!
    expected_ppv = 90.0 / 189.0
    assert abs(cm.precision - expected_ppv) < 1e-4
    assert cm.precision < 0.50, "More than 52% of all fired alerts are false alarms!"

    # Bayes' Theorem formulation check:
    p_pos = positives / total_pop  # 0.01
    p_neg = 1.0 - p_pos            # 0.99
    p_alert = (tpr * p_pos) + (fpr * p_neg)  # P(Alert)
    bayes_precision = (tpr * p_pos) / p_alert
    assert abs(bayes_precision - cm.precision) < 1e-4

    print("All base-rate fallacy Bayes precision assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()

