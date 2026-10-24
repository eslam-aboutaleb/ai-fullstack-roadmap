#!/usr/bin/env python3
"""
Executable test suite demonstrating the taxonomy and detection of distribution shifts:
Covariate Shift P(X), Target Prevalence Shift P(Y), and Concept Drift P(Y|X).

Addresses Interview Question 934:
"How do you distinguish covariate shift, target prevalence shift and concept drift?"
"""

from typing import List, Tuple, Dict, Any
import math


def compute_population_stability_index(
    baseline: List[float],
    current: List[float],
    n_bins: int = 5,
    eps: float = 1e-4
) -> float:
    """
    Computes Population Stability Index (PSI) to detect covariate shift in continuous features:
    PSI = sum ( (Actual% - Expected%) * ln(Actual% / Expected%) )
    Standard production thresholds:
      - PSI < 0.1: No significant change
      - 0.1 <= PSI < 0.2: Moderate shift (monitor)
      - PSI >= 0.2: Significant shift (investigate schema/upstream pipeline)
    """
    min_val = min(min(baseline), min(current))
    max_val = max(max(baseline), max(current))
    step = (max_val - min_val) / n_bins

    psi = 0.0
    for b in range(n_bins):
        low = min_val + b * step
        high = max_val if b == (n_bins - 1) else min_val + (b + 1) * step

        # Proportion in baseline (expected)
        count_base = sum(1 for x in baseline if low <= x <= high)
        pct_base = max(eps, count_base / len(baseline))

        # Proportion in current (actual)
        count_curr = sum(1 for x in current if low <= x <= high)
        pct_curr = max(eps, count_curr / len(current))

        psi += (pct_curr - pct_base) * math.log(pct_curr / pct_base)

    return psi


class DriftDiagnosticsEngine:
    """
    Diagnoses distribution shifts using inputs and delayed ground truth:
    1. Covariate Shift: P(X) changes significantly, but P(Y|X) is preserved.
    2. Target Shift: Prior class balance P(Y) changes.
    3. Concept Drift: The relationship P(Y|X) fundamentally alters.
    """

    @staticmethod
    def evaluate(
        baseline_x: List[float],
        current_x: List[float],
        baseline_error_rate: float,
        current_error_rate: float,
        baseline_prevalence: float,
        current_prevalence: float
    ) -> str:
        psi = compute_population_stability_index(baseline_x, current_x)
        covariate_shift = psi >= 0.20
        concept_drift = abs(current_error_rate - baseline_error_rate) >= 0.15
        target_shift = abs(current_prevalence - baseline_prevalence) >= 0.20

        if concept_drift:
            return "CONCEPT_DRIFT"
        elif covariate_shift:
            return "COVARIATE_SHIFT"
        elif target_shift:
            return "TARGET_PREVALENCE_SHIFT"
        else:
            return "STABLE"


def run_test_suite() -> None:
    # Baseline population: Standard normal input distribution (mean 0, std 1)
    import random
    rng = random.Random(42)
    base_x = [rng.gauss(0.0, 1.0) for _ in range(500)]

    # 1. Test Stable Environment (No Drift):
    curr_x_stable = [rng.gauss(0.0, 1.0) for _ in range(500)]
    psi_stable = compute_population_stability_index(base_x, curr_x_stable)
    # PSI should be well below 0.1:
    assert psi_stable < 0.10, f"Expected stable PSI < 0.10, got {psi_stable:.4f}"
    status_stable = DriftDiagnosticsEngine.evaluate(
        base_x, curr_x_stable,
        baseline_error_rate=0.08, current_error_rate=0.09,
        baseline_prevalence=0.05, current_prevalence=0.06
    )
    assert status_stable == "STABLE"

    # 2. Test Covariate Shift P(X):
    # Form change or user demographic shift moves input distribution mean to 3.0:
    curr_x_shifted = [rng.gauss(3.0, 1.0) for _ in range(500)]
    psi_shifted = compute_population_stability_index(base_x, curr_x_shifted)
    # PSI should exceed 0.20 threshold significantly:
    assert psi_shifted > 0.50, f"Expected high PSI for shifted inputs, got {psi_shifted:.4f}"

    # If error rate is still stable on the true relationship:
    status_covariate = DriftDiagnosticsEngine.evaluate(
        base_x, curr_x_shifted,
        baseline_error_rate=0.08, current_error_rate=0.09,
        baseline_prevalence=0.05, current_prevalence=0.05
    )
    assert status_covariate == "COVARIATE_SHIFT"

    # 3. Test Concept Drift P(Y|X):
    # Inputs appear unchanged (PSI < 0.1), but macro conditions change customer behavior,
    # causing error rate on delayed ground-truth labels to explode from 8% to 32%:
    status_concept = DriftDiagnosticsEngine.evaluate(
        base_x, curr_x_stable,
        baseline_error_rate=0.08, current_error_rate=0.32,
        baseline_prevalence=0.05, current_prevalence=0.05
    )
    assert status_concept == "CONCEPT_DRIFT"

    # Retraining blindly on corrupted inputs without diagnosing drift type would preserve an invalid pipeline!
    print("All distribution shift drift detector assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()

