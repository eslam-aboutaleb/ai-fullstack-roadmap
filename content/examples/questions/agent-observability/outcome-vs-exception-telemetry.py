# /// script
# dependencies = []
# ///
"""
Disentangling Technical Exceptions from Business Outcomes in Telemetry.

Demonstrates:
1. Technical Exceptions (database timeout, 500 network drop): set span status ERROR,
   increment system failure metrics, and consume reliability error budget.
2. Legitimate Business Outcomes (0 search results, refund policy denial): set span
   status OK, record structured outcome attributes, and do NOT trigger system alerts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class SpanStatus(str, Enum):
    OK = "OK"
    ERROR = "ERROR"


@dataclass
class TelemetrySpan:
    operation_name: str
    status: SpanStatus = SpanStatus.OK
    attributes: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


class MetricsRegistry:
    def __init__(self) -> None:
        self.system_errors_total: int = 0
        self.business_outcomes_total: Dict[str, int] = {}

    def record_system_error(self, operation: str) -> None:
        self.system_errors_total += 1

    def record_business_outcome(self, outcome: str) -> None:
        self.business_outcomes_total[outcome] = self.business_outcomes_total.get(outcome, 0) + 1


def search_product_catalog(
    query: str,
    simulate_network_failure: bool,
    metrics: MetricsRegistry,
) -> TelemetrySpan:
    """Tool execution demonstrating the outcome vs exception boundary."""
    span = TelemetrySpan(operation_name="tool_search_catalog")

    # Case 1: Infrastructure Exception (e.g. database pool timeout)
    if simulate_network_failure:
        span.status = SpanStatus.ERROR
        span.error_message = "ConnectionPoolTimeout: No available connections in 5000ms"
        span.attributes["error.type"] = "INFRASTRUCTURE_TIMEOUT"
        metrics.record_system_error(span.operation_name)
        return span

    # Case 2: Clean tool execution returning a legitimate business domain outcome
    # Suppose query 'nonexistent_gadget_xyz' returns 0 matches in database
    catalog = {"laptop": "High-performance dev laptop", "mouse": "Ergonomic wireless mouse"}
    item = catalog.get(query.lower())

    if item is None:
        # Crucial: This is NOT a system error! The tool executed perfectly.
        span.status = SpanStatus.OK
        span.attributes["business.outcome"] = "NOT_FOUND"
        span.attributes["catalog.query"] = query
        metrics.record_business_outcome("NOT_FOUND")
    else:
        span.status = SpanStatus.OK
        span.attributes["business.outcome"] = "FOUND"
        span.attributes["catalog.item_id"] = query
        metrics.record_business_outcome("FOUND")

    return span


def main() -> None:
    metrics = MetricsRegistry()

    # --- Scenario 1: Clean execution yielding a legitimate business NOT_FOUND ---
    # User queries for an unindexed item
    business_span = search_product_catalog(
        query="nonexistent_gadget_xyz",
        simulate_network_failure=False,
        metrics=metrics,
    )

    # Invariant: Business outcome does NOT set span status to ERROR or increment system errors
    assert business_span.status == SpanStatus.OK, "Legitimate domain outcome should have status OK"
    assert business_span.attributes["business.outcome"] == "NOT_FOUND"
    assert metrics.system_errors_total == 0, "System errors must not increment for business NOT_FOUND"
    assert metrics.business_outcomes_total["NOT_FOUND"] == 1
    business_outcome_span_status = business_span.status.value
    business_errors_incurred = metrics.system_errors_total

    # --- Scenario 2: Infrastructure Failure (Database Connection Timeout) ---
    infra_span = search_product_catalog(
        query="laptop",
        simulate_network_failure=True,
        metrics=metrics,
    )

    # Invariant: Infrastructure failure MUST set status ERROR and increment system errors
    assert infra_span.status == SpanStatus.ERROR
    assert infra_span.attributes["error.type"] == "INFRASTRUCTURE_TIMEOUT"
    assert metrics.system_errors_total == 1, "Infrastructure failure must increment system errors"
    system_error_span_status = infra_span.status.value

    print(
        f"Outcome vs exception verified: business_outcome_span_status={business_outcome_span_status}, "
        f"system_error_span_status={system_error_span_status}, "
        f"business_errors_incurred={business_errors_incurred}"
    )


if __name__ == "__main__":
    main()

