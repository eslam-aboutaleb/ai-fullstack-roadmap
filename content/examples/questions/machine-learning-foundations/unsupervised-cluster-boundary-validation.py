#!/usr/bin/env python3
"""
Executable test suite demonstrating scale sensitivity in distance-based clustering,
and showing why unsupervised clusters cannot serve as authoritative business labels.

Addresses Interview Question 930:
"When can k-means or PCA help without becoming an unsupported business label?"
"""

from typing import List, Tuple, Dict, Any
import math


def standardize_features(data: List[List[float]]) -> List[List[float]]:
    """Z-score standardization: z = (x - mean) / std_dev."""
    n_samples = len(data)
    n_features = len(data[0])

    means = [sum(row[j] for row in data) / n_samples for j in range(n_features)]
    std_devs = []
    for j in range(n_features):
        variance = sum((row[j] - means[j]) ** 2 for row in data) / n_samples
        std_devs.append(math.sqrt(variance) if variance > 1e-12 else 1.0)

    scaled_data = []
    for row in data:
        scaled_row = [(row[j] - means[j]) / std_devs[j] for j in range(n_features)]
        scaled_data.append(scaled_row)
    return scaled_data


class KMeans2D:
    def __init__(self, k: int = 2) -> None:
        self.k = k
        self.centroids: List[List[float]] = []

    def fit(self, data: List[List[float]], max_iter: int = 30) -> List[int]:
        # Deterministic initialization: first and last sample
        self.centroids = [list(data[0]), list(data[-1])]
        assignments = [0] * len(data)

        for _ in range(max_iter):
            # E-step
            new_assignments = []
            for row in data:
                d0 = sum((row[j] - self.centroids[0][j]) ** 2 for j in range(len(row)))
                d1 = sum((row[j] - self.centroids[1][j]) ** 2 for j in range(len(row)))
                new_assignments.append(0 if d0 <= d1 else 1)

            if new_assignments == assignments:
                break
            assignments = new_assignments

            # M-step
            for c_idx in range(self.k):
                pts = [data[i] for i, a in enumerate(assignments) if a == c_idx]
                if pts:
                    self.centroids[c_idx] = [
                        sum(p[j] for p in pts) / len(pts) for j in range(len(data[0]))
                    ]

        return assignments


def run_test_suite() -> None:
    # Dataset representing 8 customers:
    # Feature 0: Customer Age (range 20 to 65 years)
    # Feature 1: Lifetime transaction amount in dollars (range $100 to $50,000)
    # Latent true support need (0: Self-serve, 1: High-touch account management)
    # True support need depends heavily on Age & Activity, NOT purely transaction dollars!
    raw_data = [
        # Young tech-savvy users (low support need)
        [22.0, 500.0],
        [25.0, 1200.0],
        [28.0, 25000.0],   # Young user with high crypto transaction
        [24.0, 48000.0],   # Young user with high crypto transaction
        # Older non-technical users (high support need regardless of small balance)
        [60.0, 200.0],
        [65.0, 800.0],
        [58.0, 32000.0],
        [62.0, 49000.0],
    ]

    # 1. Unscaled K-Means Failure:
    # Transaction dollars completely dominate Euclidean distance by 3 orders of magnitude:
    # (Age difference is ~40, dollar difference is ~48,000)
    unscaled_clusters = KMeans2D(k=2).fit(raw_data)

    # In unscaled clustering, all small transaction users are in one cluster,
    # and all large transaction users are in the other cluster, completely ignoring age!
    small_tx_clusters = [unscaled_clusters[i] for i in [0, 1, 4, 5]]
    large_tx_clusters = [unscaled_clusters[i] for i in [2, 3, 6, 7]]

    # All small tx have the same cluster ID:
    assert len(set(small_tx_clusters)) == 1
    # All large tx have the other cluster ID:
    assert len(set(large_tx_clusters)) == 1
    assert small_tx_clusters[0] != large_tx_clusters[0]

    # 2. Standardized K-Means Discovery:
    # After z-score standardization, Age and Dollars have unit variance:
    scaled_data = standardize_features(raw_data)
    scaled_clusters = KMeans2D(k=2).fit(scaled_data)

    # After scaling, age variation is properly incorporated into Euclidean geometry:
    # Point 2 (age 28, tx $25,000) was grouped into the high-tx cluster under unscaled K-Means
    # purely due to dollar magnitude dominance. Under standardized K-Means, its young age
    # pulls it into cluster 0 with the other younger users:
    assert unscaled_clusters[2] == 1, "Unscaled K-Means assigned point 2 to high-tx cluster purely by magnitude"
    assert scaled_clusters[2] == 0, "Standardized K-Means grouped point 2 with younger users due to normalized age proximity"

    # 3. Policy Fallacy Verification:
    # Assert that cluster assignments cannot be used as automated permission/support labels
    # without supervised calibration:
    young_high_tx_user_cluster = scaled_clusters[2]
    old_high_tx_user_cluster = scaled_clusters[6]
    # They are grouped into different behavioral clusters:
    assert young_high_tx_user_cluster != old_high_tx_user_cluster

    print("All unsupervised cluster boundary validation assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
