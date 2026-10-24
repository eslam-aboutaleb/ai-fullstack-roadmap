"""Wilson score confidence interval vs normal Wald interval for binomial proportions.

Demonstrates the statistical interpretation and calculation of evaluation confidence intervals:
1. Frequentist interpretation: a 95% confidence interval does NOT mean there is a 95% probability
   that the true metric lies within the observed interval. It means that under repeated sampling,
   95% of constructed intervals will contain the fixed, unknown population parameter p.
2. The Wald interval failure near boundaries:
   - Wald formula: p_hat +/- z * sqrt(p_hat * (1 - p_hat) / n).
   - When accuracy is high (e.g. 98/100), Wald produces upper bounds > 1.0 (e.g. 1.0074),
     violating probability axioms. At 100/100, Wald produces a degenerate zero-width interval [1.0, 1.0].
3. Wilson score interval: provides asymmetric, mathematically sound intervals strictly bounded in [0.0, 1.0],
   demonstrating that 98/100 correct implies an interval of approximately [0.9300, 0.9945].
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ConfidenceInterval:
    lower: float
    upper: float

    @property
    def width(self) -> float:
        return self.upper - self.lower


def compute_wald_interval(successes: int, total: int, z: float = 1.96) -> ConfidenceInterval:
    """Anti-pattern: standard normal approximation (breaks near 0 and 1)."""
    p_hat = successes / total
    standard_error = math.sqrt(p_hat * (1.0 - p_hat) / total)
    margin = z * standard_error
    return ConfidenceInterval(lower=p_hat - margin, upper=p_hat + margin)


def compute_wilson_interval(successes: int, total: int, z: float = 1.96) -> ConfidenceInterval:
    """Production pattern: Wilson score interval (asymmetric, bounded in [0, 1])."""
    p_hat = successes / total
    n = float(total)
    z2 = z * z

    denom = 1.0 + z2 / n
    center = (p_hat + z2 / (2.0 * n)) / denom
    margin = (z / denom) * math.sqrt((p_hat * (1.0 - p_hat) / n) + (z2 / (4.0 * n * n)))

    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    return ConfidenceInterval(lower=lower, upper=upper)


def run_test_suite() -> None:
    # 98 correct answers out of 100 benchmark questions (p_hat = 0.98, n = 100)
    successes = 98
    total = 100
    z_95 = 1.96

    # 1. Inspect flawed Wald interval:
    wald = compute_wald_interval(successes, total, z=z_95)
    # The upper bound breaches 1.0 (100.74%):
    assert wald.upper > 1.0, f"Wald interval upper bound {wald.upper} exceeds 1.0!"
    assert round(wald.upper, 4) == 1.0074

    # 2. Inspect Wilson score interval:
    wilson = compute_wilson_interval(successes, total, z=z_95)

    # Invariant: Strictly bounded in [0.0, 1.0]:
    assert wilson.lower >= 0.0 and wilson.upper <= 1.0
    # Expected Wilson range for 98/100 is ~ [0.9300, 0.9945]:
    assert abs(wilson.lower - 0.9300) < 0.005, f"Expected lower ~0.9300, got {wilson.lower:.4f}"
    assert abs(wilson.upper - 0.9945) < 0.005, f"Expected upper ~0.9945, got {wilson.upper:.4f}"

    # 3. Test boundary case 100/100 successes:
    # Wald collapses to zero width [1.0, 1.0]:
    wald_perfect = compute_wald_interval(100, 100, z=z_95)
    assert wald_perfect.width == 0.0, "Wald gives degenerate zero width at 100% success"

    # Wilson acknowledges uncertainty even with 100% observed success:
    # Wilson interval for 100/100 is ~ [0.963, 1.0]:
    wilson_perfect = compute_wilson_interval(100, 100, z=z_95)
    assert wilson_perfect.width > 0.03, "Wilson correctly reflects sample size uncertainty"
    assert abs(wilson_perfect.upper - 1.0) < 1e-6
    assert wilson_perfect.lower > 0.96

    print("All Wilson score confidence interval assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
