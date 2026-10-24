"""Distributed W3C Trace Context Propagation across A2A Boundaries and Architectural Justification.

Demonstrates:
1. W3C Trace Context Standard:
   - Formats and propagates standard `traceparent` HTTP header: `00-{trace_id}-{parent_id}-{trace_flags}`.
   - Remote specialist parses incoming traceparent, preserves root trace_id, and generates child span.
   - Preserves end-to-end distributed observability across asynchronous cross-service agent delegations.
2. Architectural Decision Engine:
   - Evaluates whether multi-agent A2A architecture is justified over a local service baseline.
   - Proves that homogeneous tasks with identical context should run in local services to avoid
     network serialization overhead and duplicate token costs.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid


@dataclass
class TraceSpan:
    name: str
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    start_time: float
    end_time: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)


class W3CTraceContext:
    """Encoder and decoder for standard W3C traceparent headers."""

    REGEX = re.compile(r"^00-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$")

    @classmethod
    def generate_trace_id(cls) -> str:
        return uuid.uuid4().hex

    @classmethod
    def generate_span_id(cls) -> str:
        return uuid.uuid4().hex[:16]

    @classmethod
    def format_traceparent(cls, trace_id: str, span_id: str, sampled: bool = True) -> str:
        flags = "01" if sampled else "00"
        return f"00-{trace_id}-{span_id}-{flags}"

    @classmethod
    def parse_traceparent(cls, header: str) -> Tuple[str, str, bool]:
        match = cls.REGEX.match(header.strip())
        if not match:
            raise ValueError(f"Malformed W3C traceparent header: '{header}'")
        trace_id, parent_id, flags = match.groups()
        sampled = (flags == "01")
        return trace_id, parent_id, sampled


class LocalCoordinatorService:
    """Coordinator initiating work and propagating traceparent to remote specialist."""

    def __init__(self):
        self.spans: List[TraceSpan] = []

    def start_root_span(self, name: str) -> TraceSpan:
        trace_id = W3CTraceContext.generate_trace_id()
        span_id = W3CTraceContext.generate_span_id()
        span = TraceSpan(name=name, trace_id=trace_id, span_id=span_id, parent_span_id=None, start_time=time.time())
        self.spans.append(span)
        return span

    def create_outbound_headers(self, current_span: TraceSpan) -> Dict[str, str]:
        traceparent = W3CTraceContext.format_traceparent(current_span.trace_id, current_span.span_id, sampled=True)
        return {
            "traceparent": traceparent,
            "x-a2a-origin-agent": "coordinator_v1"
        }


class RemoteSpecialistService:
    """Remote agent receiving delegated task, extracting traceparent, and recording child span."""

    def __init__(self):
        self.spans: List[TraceSpan] = []

    def handle_delegated_task(self, inbound_headers: Dict[str, str], task_payload: Dict[str, Any]) -> Dict[str, Any]:
        traceparent = inbound_headers.get("traceparent")
        if not traceparent:
            raise ValueError("Missing mandatory traceparent header on A2A boundary")

        trace_id, parent_span_id, sampled = W3CTraceContext.parse_traceparent(traceparent)
        child_span_id = W3CTraceContext.generate_span_id()

        child_span = TraceSpan(
            name="specialist_investigation",
            trace_id=trace_id,
            span_id=child_span_id,
            parent_span_id=parent_span_id,
            start_time=time.time(),
            attributes={"sampled": sampled, "task_type": task_payload.get("task_type")}
        )
        self.spans.append(child_span)

        # Simulate work
        child_span.end_time = time.time() + 0.05

        return {
            "status": "COMPLETED",
            "child_span_id": child_span_id,
            "trace_id": trace_id
        }


# --- Architectural Justification Engine ---
def evaluate_architecture_fit(
    requires_cross_org_trust_boundary: bool,
    requires_isolated_security_sandbox: bool,
    requires_distinct_long_running_lifecycle: bool,
    expected_latency_tolerance_seconds: float
) -> str:
    """Evaluates whether multi-agent A2A architecture is justified or if a local service is superior."""
    # A2A is justified when operations cross trust/network boundaries, require distinct sandbox lifecycles,
    # and have high latency tolerance (>1s).
    if (requires_cross_org_trust_boundary or requires_isolated_security_sandbox or requires_distinct_long_running_lifecycle) and expected_latency_tolerance_seconds >= 1.0:
        return "MULTI_AGENT_A2A_JUSTIFIED"

    return "LOCAL_SERVICE_BASELINE_RECOMMENDED"


def main():
    coordinator = LocalCoordinatorService()
    specialist = RemoteSpecialistService()

    # 1. Distributed Trace Propagation
    print("1. Distributed Trace Propagation Across A2A Boundary:")
    root_span = coordinator.start_root_span("coordinator_orchestration")
    headers = coordinator.create_outbound_headers(root_span)

    print(f"  Root Span ID: {root_span.span_id}")
    print(f"  Traceparent Header: {headers['traceparent']}")

    # Dispatch to remote agent
    task_res = specialist.handle_delegated_task(headers, {"task_type": "deep_contract_audit"})
    child_span = specialist.spans[0]

    print(f"  Remote Child Span ID: {child_span.span_id}")
    print(f"  Remote Parent Span ID: {child_span.parent_span_id}")
    print(f"  Root and Child Trace IDs Match: {root_span.trace_id == child_span.trace_id}")

    assert root_span.trace_id == child_span.trace_id, "Trace ID must be preserved across boundary"
    assert child_span.parent_span_id == root_span.span_id, "Child span must point to coordinator span as parent"

    # 2. Architectural Justification Analysis
    print("\n2. Multi-Agent Architectural Justification Analysis:")
    # Scenario A: Simple customer name lookup (Low latency, single security domain)
    decision_a = evaluate_architecture_fit(
        requires_cross_org_trust_boundary=False,
        requires_isolated_security_sandbox=False,
        requires_distinct_long_running_lifecycle=False,
        expected_latency_tolerance_seconds=0.1
    )
    print(f"  Scenario A (Simple Record Lookup): {decision_a}")
    assert decision_a == "LOCAL_SERVICE_BASELINE_RECOMMENDED"

    # Scenario B: Cross-company legal compliance audit (Distinct trust boundary, sandbox, long running)
    decision_b = evaluate_architecture_fit(
        requires_cross_org_trust_boundary=True,
        requires_isolated_security_sandbox=True,
        requires_distinct_long_running_lifecycle=True,
        expected_latency_tolerance_seconds=30.0
    )
    print(f"  Scenario B (Cross-Org Compliance Audit): {decision_b}")
    assert decision_b == "MULTI_AGENT_A2A_JUSTIFIED"

    print("\nDistributed trace propagation and architecture evaluation verified successfully.")


if __name__ == "__main__":
    main()
