"""Unsupervised PCA data leakage and cross-validation isolation harness.

Demonstrates why unsupervised transformations (PCA, SVD, StandardScaler) cause data leakage if fit globally:
1. The unsupervised leakage fallacy: believing that because PCA does not use target labels Y,
   it is safe to fit PCA on the entire dataset (train + test) before cross-validation.
2. The mechanism of leakage: fitting PCA computes global feature means mu and covariance eigenvectors V.
   The validation fold's feature variance and distribution leak into the projection matrix,
   optimistically biasing validation metrics and masking generalization failure on live production data.
3. Strict cross-validation protocol: PCA must be fit STRICTLY on the training fold (fit_transform),
   and the validation fold must only be transformed using frozen training parameters (transform).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple


def compute_mean_and_center(matrix: List[List[float]]) -> Tuple[List[float], List[List[float]]]:
    """Computes column means and returns (means, centered_matrix)."""
    rows = len(matrix)
    cols = len(matrix[0])
    means = [sum(matrix[r][c] for r in range(rows)) / rows for c in range(cols)]
    centered = [[matrix[r][c] - means[c] for c in range(cols)] for r in range(rows)]
    return means, centered


def fit_1d_pca(matrix: List[List[float]]) -> Tuple[List[float], List[float]]:
    """Fits 1D PCA (first principal component via power iteration): returns (mean, component_vector)."""
    means, centered = compute_mean_and_center(matrix)
    cols = len(means)

    # Power iteration to find dominant eigenvector of X^T @ X
    v = [1.0 / math.sqrt(cols)] * cols
    for _ in range(20):
        # x_v = centered @ v
        x_v = [sum(centered[r][c] * v[c] for c in range(cols)) for r in range(len(centered))]
        # v_new = centered^T @ x_v
        v_new = [sum(centered[r][c] * x_v[r] for r in range(len(centered))) for c in range(cols)]
        norm = math.sqrt(sum(x * x for x in v_new))
        v = [x / (norm + 1e-12) for x in v_new]

    return means, v


def transform_pca(matrix: List[List[float]], means: List[float], component: List[float]) -> List[float]:
    """Projects matrix onto 1D principal component using frozen training parameters."""
    rows = len(matrix)
    cols = len(means)
    projected: List[float] = []
    for r in range(rows):
        val = sum((matrix[r][c] - means[c]) * component[c] for c in range(cols))
        projected.append(val)
    return projected


def run_test_suite() -> None:
    # Training fold: Centered around (0, 0)
    train_data = [
        [-2.0, -2.1],
        [-1.0, -0.9],
        [0.0, 0.1],
        [1.0, 0.9],
        [2.0, 2.1],
    ]

    # Validation fold: Features an extreme outlier cluster at (10, 10)
    val_data = [
        [9.5, 10.0],
        [10.5, 9.8],
    ]

    # 1. Flawed Protocol: Fit PCA on Full Dataset (train + val combined):
    full_dataset = train_data + val_data
    global_means, global_v = fit_1d_pca(full_dataset)

    # BUG: Global mean was heavily shifted by the validation outlier cluster:
    # True training mean is ~0.0; global mean is distorted to ~2.8:
    assert global_means[0] > 2.0, "Global mean was contaminated by validation set"

    # 2. Resilient Protocol: Fit PCA strictly on Training Fold:
    train_means, train_v = fit_1d_pca(train_data)

    # Training mean remains isolated near 0.0:
    assert abs(train_means[0]) < 0.2
    assert abs(train_means[1]) < 0.2

    # 3. Compare validation projections:
    val_proj_leaked = transform_pca(val_data, global_means, global_v)
    val_proj_isolated = transform_pca(val_data, train_means, train_v)

    # The projected representations differ significantly due to the leakage of the global mean:
    diff_magnitude = abs(val_proj_leaked[0] - val_proj_isolated[0])
    assert diff_magnitude > 2.0, (
        f"Data leakage materially altered feature coordinates by {diff_magnitude:.2f}"
    )

    print("All unsupervised PCA leakage cross-validation assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()

