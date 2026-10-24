"""Clustered correlation, variance estimation, and effective sample size harness.

Demonstrates why assuming independent samples on correlated evaluation data creates false certainty:
1. The i.i.d. fallacy: generating 100 evaluation questions from a single source document introduces high
   intra-cluster correlation (rho).
2. Naive variance underestimation: the standard error formula sigma / sqrt(N) assumes zero correlation.
   When correlation rho > 0 exists, true variance expands by the Variance Inflation Factor (VIF):
   VIF = 1 + (m - 1) * rho, where m is the cluster size.
3. Effective sample size (N_eff): N_eff = N / VIF. 100 questions from one document provide the statistical
   power of only ~1.2 independent observations, not 100.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class EvaluationClusterStats:
    total_samples: int
    cluster_size: int
    intra_cluster_correlation: float
    sample_variance: float

    @property
    def variance_inflation_factor(self) -> float:
        """Design Effect VIF = 1 + (m - 1) * rho"""
        return 1.0 + (self.cluster_size - 1) * self.intra_cluster_correlation

    @property
    def naive_standard_error(self) -> float:
        """Assumes all N samples are completely independent."""
        return math.sqrt(self.sample_variance / self.total_samples)

    @property
    def cluster_robust_standard_error(self) -> float:
        """Adjusts for intra-cluster correlation."""
        true_variance = (self.sample_variance / self.total_samples) * self.variance_inflation_factor
        return math.sqrt(true_variance)

    @property
    def effective_sample_size(self) -> float:
        """N_eff = N / VIF"""
        return self.total_samples / self.variance_inflation_factor


def run_test_suite() -> None:
    # 100 evaluation questions derived from 1 single policy document
    total_q = 100
    cluster_sz = 100
    rho = 0.80  # High correlation: questions share the same document nuances
    sigma2 = 1.0  # Normalized variance

    stats = EvaluationClusterStats(
        total_samples=total_q,
        cluster_size=cluster_sz,
        intra_cluster_correlation=rho,
        sample_variance=sigma2,
    )

    # 1. Inspect Variance Inflation Factor:
    # VIF = 1 + (99 * 0.8) = 1 + 79.2 = 80.2!
    vif = stats.variance_inflation_factor
    assert abs(vif - 80.2) < 1e-4

    # 2. Inspect Standard Error underestimation:
    # Naive SEM: sqrt(1.0 / 100) = 0.10
    assert abs(stats.naive_standard_error - 0.10) < 1e-5

    # True Cluster-Robust SEM: sqrt(80.2 / 100) = sqrt(0.802) ~ 0.8955 (almost 9x larger error bar!):
    robust_sem = stats.cluster_robust_standard_error
    assert abs(robust_sem - math.sqrt(0.802)) < 1e-4
    assert robust_sem / stats.naive_standard_error > 8.5, "True uncertainty is nearly an order of magnitude wider!"

    # 3. Inspect Effective Sample Size:
    # N_eff = 100 / 80.2 = ~1.2468 independent questions:
    n_eff = stats.effective_sample_size
    assert abs(n_eff - (100.0 / 80.2)) < 1e-4
    assert n_eff < 2.0, "100 correlated questions provide less than 2 independent data points of evidence!"

    print("All clustered correlation variance estimator assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()

