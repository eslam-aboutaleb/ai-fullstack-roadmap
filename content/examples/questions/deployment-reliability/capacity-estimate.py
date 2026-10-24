"""Capacity Estimation & Queueing Concurrency via Little's Law.

Demonstrates mathematical modeling of service capacity using Little's Law (L = λ * W).
Calculates average in-flight concurrency, required worker pool capacity, and queue
saturation horizons under peak burst traffic.
"""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class WorkloadProfile:
    arrival_rate_qps: float  # λ (requests per second)
    mean_service_time_sec: float  # W (mean latency in seconds)
    p99_service_time_sec: float
    burst_multiplier: float = 2.5


class CapacityEstimator:
    """Applies Little's Law and queueing invariants to size infrastructure."""

    @staticmethod
    def calculate_inflight_concurrency(workload: WorkloadProfile) -> float:
        """L = λ * W (Average in-flight requests in the system)."""
        return workload.arrival_rate_qps * workload.mean_service_time_sec

    @staticmethod
    def calculate_peak_concurrency_headroom(workload: WorkloadProfile) -> float:
        """Peak concurrency during traffic burst: L_burst = (λ * burst) * p99_latency."""
        burst_qps = workload.arrival_rate_qps * workload.burst_multiplier
        return burst_qps * workload.p99_service_time_sec

    @staticmethod
    def size_worker_fleet(
        workload: WorkloadProfile, target_worker_utilization: float = 0.70
    ) -> Dict[str, float]:
        avg_inflight = CapacityEstimator.calculate_inflight_concurrency(workload)
        peak_inflight = CapacityEstimator.calculate_peak_concurrency_headroom(workload)

        # Baseline worker threads required to maintain safe utilization
        recommended_threads = avg_inflight / target_worker_utilization
        burst_threads = peak_inflight / target_worker_utilization

        return {
            "avg_inflight_requests": round(avg_inflight, 2),
            "peak_inflight_requests": round(peak_inflight, 2),
            "recommended_baseline_threads": int(recommended_threads) + 1,
            "recommended_burst_threads": int(burst_threads) + 1,
        }


def test_capacity_estimate() -> None:
    # Workload: 2.0 requests per second with mean service time of 5.0 seconds
    # (Typical for an LLM generation or complex document analysis pipeline)
    profile = WorkloadProfile(
        arrival_rate_qps=2.0,
        mean_service_time_sec=5.0,
        p99_service_time_sec=12.0,
        burst_multiplier=2.5,
    )

    # 1. Little's Law: L = λ * W = 2.0 * 5.0 = 10.0 in-flight requests
    avg_inflight = CapacityEstimator.calculate_inflight_concurrency(profile)
    assert avg_inflight == 10.0

    # 2. Peak burst concurrency: (2.0 * 2.5) * 12.0 = 5.0 * 12.0 = 60.0 in-flight requests
    peak_inflight = CapacityEstimator.calculate_peak_concurrency_headroom(profile)
    assert peak_inflight == 60.0

    # 3. Fleet sizing targeting 70% max CPU utilization
    sizing = CapacityEstimator.size_worker_fleet(profile, target_worker_utilization=0.70)
    assert sizing["avg_inflight_requests"] == 10.0
    assert sizing["recommended_baseline_threads"] == 15  # ceil(10 / 0.7) = 15
    assert sizing["recommended_burst_threads"] == 86  # ceil(60 / 0.7) = 86

    print(
        f"Capacity estimate verified: avg_inflight={avg_inflight}, "
        f"peak_inflight={peak_inflight}, "
        f"baseline_threads={sizing['recommended_baseline_threads']}"
    )


if __name__ == "__main__":
    test_capacity_estimate()
