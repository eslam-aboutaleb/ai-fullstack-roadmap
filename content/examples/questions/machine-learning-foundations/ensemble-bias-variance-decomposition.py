#!/usr/bin/env python3
"""
Executable test suite demonstrating the bias-variance trade-off across Decision Trees,
Random Forest Bagging, and Gradient Boosting.

Addresses Interview Question 929:
"How do decision trees, random forests and boosting differ in how errors are controlled?"
"""

from typing import List, Tuple, Callable
import math
import random


class DecisionStump:
    """A 1-split shallow decision tree (weak learner with high bias, low variance)."""
    def __init__(self) -> None:
        self.split_val: float = 0.0
        self.left_pred: float = 0.0
        self.right_pred: float = 0.0

    def fit(self, x: List[float], y: List[float]) -> None:
        best_mse = float("inf")
        # Try candidate split points
        sorted_x = sorted(x)
        for i in range(len(sorted_x) - 1):
            threshold = (sorted_x[i] + sorted_x[i+1]) / 2.0
            left_y = [y_i for x_i, y_i in zip(x, y) if x_i <= threshold]
            right_y = [y_i for x_i, y_i in zip(x, y) if x_i > threshold]

            if not left_y or not right_y:
                continue

            l_mean = sum(left_y) / len(left_y)
            r_mean = sum(right_y) / len(right_y)

            mse = sum((yi - l_mean)**2 for yi in left_y) + sum((yi - r_mean)**2 for yi in right_y)
            if mse < best_mse:
                best_mse = mse
                self.split_val = threshold
                self.left_pred = l_mean
                self.right_pred = r_mean

    def predict_one(self, x: float) -> float:
        return self.left_pred if x <= self.split_val else self.right_pred


class BaggedEnsemble:
    """Random Forest mechanism: Bagging (bootstrap aggregation) to reduce prediction variance."""
    def __init__(self, n_estimators: int = 15) -> None:
        self.n_estimators = n_estimators
        self.estimators: List[DecisionStump] = []

    def fit(self, x: List[float], y: List[float], rng: random.Random) -> None:
        n = len(x)
        self.estimators = []
        for _ in range(self.n_estimators):
            # Bootstrap sample (sampling with replacement)
            indices = [rng.randint(0, n - 1) for _ in range(n)]
            bx = [x[i] for i in indices]
            by = [y[i] for i in indices]
            stump = DecisionStump()
            stump.fit(bx, by)
            self.estimators.append(stump)

    def predict_one(self, x: float) -> float:
        preds = [e.predict_one(x) for e in self.estimators]
        return sum(preds) / len(preds)


class GradientBoostedStumps:
    """Boosting mechanism: Sequentially fits negative gradient residuals to reduce bias."""
    def __init__(self, n_estimators: int = 10, lr: float = 0.3) -> None:
        self.n_estimators = n_estimators
        self.lr = lr
        self.initial_pred: float = 0.0
        self.estimators: List[DecisionStump] = []

    def fit(self, x: List[float], y: List[float]) -> None:
        self.initial_pred = sum(y) / len(y)
        residuals = [yi - self.initial_pred for yi in y]
        self.estimators = []

        for _ in range(self.n_estimators):
            stump = DecisionStump()
            stump.fit(x, residuals)
            self.estimators.append(stump)
            # Update residuals by subtracting learned step
            for i in range(len(x)):
                residuals[i] -= self.lr * stump.predict_one(x[i])

    def predict_one(self, x: float) -> float:
        val = self.initial_pred
        for e in self.estimators:
            val += self.lr * e.predict_one(x)
        return val


def run_test_suite() -> None:
    rng = random.Random(42)

    # True non-linear target function: step-like non-linearity with 3 regimes
    # x in [-2, 2]
    # y = -1 if x < -0.5, 0 if -0.5 <= x <= 0.5, 1 if x > 0.5
    def ground_truth(x: float) -> float:
        if x < -0.5:
            return -1.0
        elif x <= 0.5:
            return 0.0
        else:
            return 1.0

    # Generate training set with additive zero-mean Gaussian noise
    train_x = [-2.0 + 4.0 * (i / 40.0) for i in range(41)]
    train_y = [ground_truth(xi) + rng.gauss(0.0, 0.2) for xi in train_x]

    # Test set (pure ground truth)
    test_x = [-1.8 + 3.6 * (i / 20.0) for i in range(21)]
    test_y = [ground_truth(xi) for xi in test_x]

    # 1. Single Decision Stump (Weak learner: High bias)
    single_stump = DecisionStump()
    single_stump.fit(train_x, train_y)
    stump_preds = [single_stump.predict_one(xi) for xi in test_x]
    stump_mse = sum((y - p)**2 for y, p in zip(test_y, stump_preds)) / len(test_y)

    # 2. Gradient Boosted Stumps (Sequential boosting reduces bias on 3-tier target)
    booster = GradientBoostedStumps(n_estimators=10, lr=0.4)
    booster.fit(train_x, train_y)
    boost_preds = [booster.predict_one(xi) for xi in test_x]
    boost_mse = sum((y - p)**2 for y, p in zip(test_y, boost_preds)) / len(test_y)

    # Boosting significantly reduces bias over a single stump:
    assert boost_mse < stump_mse * 0.6, (
        f"Gradient boosting should reduce bias MSE over single stump: Stump={stump_mse:.4f}, Boost={boost_mse:.4f}"
    )

    # 3. Bagged Ensemble Test: Measure variance across multiple resampled datasets
    # When trained on 20 independent noisy realisations:
    # Bagging reduces variance of the predicted outputs
    single_predictions_at_point: List[float] = []
    bagged_predictions_at_point: List[float] = []
    eval_point = 0.8  # Target is 1.0

    for rep in range(25):
        rep_rng = random.Random(100 + rep)
        rep_y = [ground_truth(xi) + rep_rng.gauss(0.0, 0.4) for xi in train_x]

        # Single stump
        s = DecisionStump()
        s.fit(train_x, rep_y)
        single_predictions_at_point.append(s.predict_one(eval_point))

        # Bagged ensemble of 15 stumps
        bag = BaggedEnsemble(n_estimators=15)
        bag.fit(train_x, rep_y, rep_rng)
        bagged_predictions_at_point.append(bag.predict_one(eval_point))

    # Variance of single learner vs bagged learner:
    mean_s = sum(single_predictions_at_point) / len(single_predictions_at_point)
    var_single = sum((p - mean_s)**2 for p in single_predictions_at_point) / len(single_predictions_at_point)

    mean_b = sum(bagged_predictions_at_point) / len(bagged_predictions_at_point)
    var_bagged = sum((p - mean_b)**2 for p in bagged_predictions_at_point) / len(bagged_predictions_at_point)

    assert var_bagged < var_single, (
        f"Bagging must reduce prediction variance across dataset resamples! Single Var={var_single:.4f}, Bagged Var={var_bagged:.4f}"
    )

    print("All ensemble bias-variance decomposition assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()

