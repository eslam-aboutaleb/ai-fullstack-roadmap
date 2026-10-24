#!/usr/bin/env python3
"""
Executable test suite demonstrating the fundamental differences in learning feedback
between Supervised, Unsupervised, and Reinforcement Learning paradigms.

Addresses Interview Question 926:
"How do supervised, unsupervised and reinforcement learning define different feedback?"
"""

from typing import List, Tuple, Dict, Any
import math
import random


class SupervisedLinearRegressor:
    """
    Supervised learning: Direct, instantaneous feedback on every instance.
    Loss L(y, y_hat) compares prediction directly against authoritative ground-truth target.
    """
    def __init__(self, lr: float = 0.05) -> None:
        self.w: float = 0.0
        self.b: float = 0.0
        self.lr: float = lr

    def train_step(self, x: float, y_true: float) -> float:
        # Prediction
        y_pred = self.w * x + self.b
        # Residual error
        error = y_pred - y_true
        # Analytical gradients: d(error^2)/dw = 2 * error * x
        grad_w = 2.0 * error * x
        grad_b = 2.0 * error
        # Parameter update
        self.w -= self.lr * grad_w
        self.b -= self.lr * grad_b
        return error ** 2


class UnsupervisedKMeans1D:
    """
    Unsupervised learning: No ground-truth outcome labels.
    Feedback is an internal geometric objective (e.g., minimizing within-cluster inertia / reconstruction error).
    Crucial boundary: Cluster identities DO NOT convey business policy or semantic authorization!
    """
    def __init__(self, k: int = 2) -> None:
        self.k: int = k
        self.centroids: List[float] = []

    def fit(self, data: List[float], max_iter: int = 20) -> List[int]:
        # Initialize centroids deterministically for reproducible testing
        sorted_d = sorted(data)
        self.centroids = [sorted_d[0], sorted_d[-1]]

        assignments = [0] * len(data)
        for _ in range(max_iter):
            # E-step: Assign points to nearest centroid
            new_assignments = []
            for x in data:
                distances = [abs(x - c) for c in self.centroids]
                new_assignments.append(0 if distances[0] <= distances[1] else 1)

            if new_assignments == assignments:
                break
            assignments = new_assignments

            # M-step: Recompute centroids as mean of assigned points
            for cluster_idx in range(self.k):
                cluster_pts = [x for x, a in zip(data, assignments) if a == cluster_idx]
                if cluster_pts:
                    self.centroids[cluster_idx] = sum(cluster_pts) / len(cluster_pts)

        return assignments

    def inertia(self, data: List[float], assignments: List[int]) -> float:
        """Within-cluster sum of squared distances."""
        total = 0.0
        for x, a in zip(data, assignments):
            total += (x - self.centroids[a]) ** 2
        return total


class ReinforcementContextualBandit:
    """
    Reinforcement learning: Evaluative, delayed, scalar reward feedback on executed actions.
    No counterfactual feedback is observed for unchosen actions (exploration vs exploitation).
    """
    def __init__(self, n_arms: int = 2, epsilon: float = 0.1) -> None:
        self.n_arms: int = n_arms
        self.epsilon: float = epsilon
        self.arm_counts: List[int] = [0] * n_arms
        self.arm_q_values: List[float] = [0.0] * n_arms

    def select_action(self, rng: random.Random) -> int:
        # Epsilon-greedy exploration
        if rng.random() < self.epsilon:
            return rng.randint(0, self.n_arms - 1)
        # Greedy exploitation: Pick arm with highest estimated reward
        max_q = max(self.arm_q_values)
        best_arms = [i for i, q in enumerate(self.arm_q_values) if q == max_q]
        return rng.choice(best_arms)

    def update(self, arm: int, reward: float) -> None:
        # Incremental sample average update
        self.arm_counts[arm] += 1
        n = self.arm_counts[arm]
        self.arm_q_values[arm] += (reward - self.arm_q_values[arm]) / n


def run_test_suite() -> None:
    rng = random.Random(42)

    # 1. Supervised Learning Test: Direct target loss converges
    # Target function: y = 2*x + 1
    reg = SupervisedLinearRegressor(lr=0.02)
    training_data = [(float(i), 2.0 * float(i) + 1.0) for i in range(1, 6)]
    initial_loss = reg.train_step(training_data[0][0], training_data[0][1])

    for _ in range(100):
        for x, y in training_data:
            final_loss = reg.train_step(x, y)

    # Supervised parameters converge close to true values (w=2, b=1)
    assert abs(reg.w - 2.0) < 0.15, f"Expected w ~ 2.0, got {reg.w:.3f}"
    assert abs(reg.b - 1.0) < 0.35, f"Expected b ~ 1.0, got {reg.b:.3f}"
    assert final_loss < 0.05, f"Expected small final loss, got {final_loss:.4f}"

    # 2. Unsupervised Learning Test: Internal geometric objective
    # Customer transaction amounts: group A ~ 10.0, group B ~ 100.0
    transactions = [9.0, 10.5, 11.2, 8.8, 98.0, 102.5, 99.1, 101.0]
    # Synthetic ground-truth fraud label (independent of transaction amount!)
    # Group A has 1 fraud, Group B has 1 fraud.
    ground_truth_policy = [False, False, True, False, False, True, False, False]

    kmeans = UnsupervisedKMeans1D(k=2)
    clusters = kmeans.fit(transactions)
    inertia = kmeans.inertia(transactions, clusters)

    # Geometric separation succeeded (low inertia, cleanly separated centroids)
    assert inertia < 25.0, f"Expected low inertia, got {inertia}"
    assert min(kmeans.centroids) < 15.0 and max(kmeans.centroids) > 95.0

    # Critical architectural boundary: Cluster 1 does NOT mean 'Fraud' or 'Allowed'
    # Cluster 1 contains both fraud (True) and non-fraud (False)
    cluster_1_labels = [label for label, c in zip(ground_truth_policy, clusters) if c == 1]
    assert True in cluster_1_labels and False in cluster_1_labels, (
        "Unsupervised clusters cannot be assumed to represent authoritative policy classes!"
    )

    # 3. Reinforcement Learning Test: Trial-and-error evaluative reward
    # Arm 0 has true expected reward 0.2, Arm 1 has true expected reward 0.8
    bandit = ReinforcementContextualBandit(n_arms=2, epsilon=0.1)
    arm_true_probs = [0.2, 0.8]

    for _ in range(500):
        action = bandit.select_action(rng)
        # Sample reward from Bernoulli trial
        reward = 1.0 if rng.random() < arm_true_probs[action] else 0.0
        bandit.update(action, reward)

    # Bandit learned that Arm 1 has significantly higher expected reward
    assert bandit.arm_q_values[1] > bandit.arm_q_values[0], (
        f"Bandit should prefer arm 1 (Q0={bandit.arm_q_values[0]:.2f}, Q1={bandit.arm_q_values[1]:.2f})"
    )
    assert bandit.arm_counts[1] > bandit.arm_counts[0] * 2, (
        "Exploitation should pull the higher-reward arm majority of the time"
    )

    print("All supervised, unsupervised, and RL feedback loop assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()

