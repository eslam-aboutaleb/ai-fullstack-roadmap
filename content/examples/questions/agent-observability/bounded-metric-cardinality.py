# /// script
# dependencies = []
# ///
"""
Preventing Time-Series Metric Cardinality Explosion in Prometheus/OTel.

Demonstrates:
1. Low-cardinality label filtering: metric labels contain only bounded enums
   (model_name, provider, status_class).
2. Unbounded high-cardinality identifiers (user_id, task_id, session_id)
   are strictly diverted to trace span attributes.
3. Proves that across 1,000 distinct user requests, the metrics collector
   retains a bounded time-series count, preventing monitoring OOM crashes.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple


class TelemetryEventRouter:
    """Routes events to Prometheus metrics (bounded) and Tracing Spans (high cardinality)."""

    def __init__(self) -> None:
        # Bounded metric time-series: Dict[Tuple[model, status_class], count]
        self.metric_timeseries: Dict[Tuple[str, str], int] = {}
        # Distributed traces holding high-cardinality attributes
        self.trace_spans: List[Dict[str, Any]] = []

    def record_request(
        self,
        task_id: str,
        user_id: str,
        model_name: str,
        http_status: int,
    ) -> None:
        # Compute bounded status class ('2xx', '4xx', '5xx')
        status_class = f"{http_status // 100}xx"

        # --- 1. Prometheus Metric: Strictly Bounded Labels Only ---
        # NEVER include task_id or user_id in metric label tuple!
        metric_key = (model_name, status_class)
        self.metric_timeseries[metric_key] = self.metric_timeseries.get(metric_key, 0) + 1

        # --- 2. Trace Span: Stores High-Cardinality Unbounded Context ---
        span = {
            "task_id": task_id,
            "user_id": user_id,
            "model_name": model_name,
            "http_status": http_status,
        }
        self.trace_spans.append(span)


def main() -> None:
    router = TelemetryEventRouter()

    # Simulate 1,000 distinct user requests with unique user IDs and task IDs
    num_requests = 1000
    for i in range(num_requests):
        router.record_request(
            task_id=f"tsk_req_{i:04d}",
            user_id=f"usr_customer_{i:04d}",
            model_name="gemini-1.5-flash",
            http_status=200 if i % 10 != 0 else 500,
        )

    # Invariant 1: All 1,000 high-cardinality user/task IDs are captured in traces
    assert len(router.trace_spans) == num_requests
    high_cardinality_retained_in_traces = True

    # Invariant 2: Total Prometheus time-series count remains bounded to exactly 2 series!
    # (gemini-1.5-flash, 2xx) and (gemini-1.5-flash, 5xx)
    total_timeseries = len(router.metric_timeseries)
    assert total_timeseries == 2, f"Expected 2 bounded time series, found {total_timeseries}"
    assert router.metric_timeseries[("gemini-1.5-flash", "2xx")] == 900
    assert router.metric_timeseries[("gemini-1.5-flash", "5xx")] == 100

    print(
        f"Bounded metric cardinality verified: unique_requests={num_requests}, "
        f"total_timeseries={total_timeseries}, "
        f"high_cardinality_retained_in_traces={high_cardinality_retained_in_traces}"
    )


if __name__ == "__main__":
    main()

