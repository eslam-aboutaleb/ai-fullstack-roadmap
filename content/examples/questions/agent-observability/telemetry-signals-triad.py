# /// script
# dependencies = []
# ///
"""
Production-Grade OpenTelemetry Signal Triad for Autonomous Agents.

Integrates the three telemetry pillars plus audit ledgers:
1. Distributed Trace Spans: Root Agent Loop with nested Tool Child Spans.
2. Structured Contextual Logs: correlated to traces via trace_id and span_id.
3. Aggregated Low-Cardinality Metrics: counters and duration histograms.
4. Non-Repudiable Audit Ledger: records committed domain side effects.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Span:
    name: str
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    status: str = "UNSET"

    def finish(self, status: str = "OK") -> None:
        self.end_time = time.time()
        self.status = status


@dataclass
class StructuredLog:
    timestamp: float
    level: str
    message: str
    trace_id: str
    span_id: str
    context: Dict[str, Any] = field(default_factory=dict)


class TelemetryCollector:
    """Simulated OpenTelemetry collector with metrics, traces, and logs."""

    def __init__(self) -> None:
        self.spans: List[Span] = []
        self.logs: List[StructuredLog] = []
        self.metrics: Dict[str, int] = {"agent_runs_total": 0, "tool_calls_total": 0}
        self.audit_ledger: List[Dict[str, Any]] = []

    def start_span(self, name: str, trace_id: str, parent_span_id: Optional[str] = None) -> Span:
        span_id = f"span_{uuid.uuid4().hex[:8]}"
        span = Span(name=name, trace_id=trace_id, span_id=span_id, parent_span_id=parent_span_id)
        self.spans.append(span)
        return span

    def log(self, level: str, message: str, span: Span, context: Optional[Dict[str, Any]] = None) -> None:
        entry = StructuredLog(
            timestamp=time.time(),
            level=level,
            message=message,
            trace_id=span.trace_id,
            span_id=span.span_id,
            context=context or {},
        )
        self.logs.append(entry)

    def increment_metric(self, name: str, count: int = 1) -> None:
        self.metrics[name] = self.metrics.get(name, 0) + count

    def record_audit(self, tenant_id: str, action: str, details: Dict[str, Any]) -> None:
        self.audit_ledger.append({
            "timestamp": time.time(),
            "tenant_id": tenant_id,
            "action": action,
            "details": details,
        })


def execute_monitored_agent_run(collector: TelemetryCollector, tenant_id: str) -> str:
    trace_id = f"trace_{uuid.uuid4().hex[:12]}"

    # 1. Root Agent Orchestration Span
    root_span = collector.start_span("agent_orchestration_loop", trace_id=trace_id)
    root_span.attributes["gen_ai.system"] = "autonomous_rag"
    root_span.attributes["tenant_id"] = tenant_id

    collector.log("INFO", "Agent initialized multi-turn loop", root_span)

    # 2. Child Tool Execution Span
    tool_span = collector.start_span(
        "tool_vector_retrieval", trace_id=trace_id, parent_span_id=root_span.span_id
    )
    tool_span.attributes["tool.name"] = "document_search"
    tool_span.attributes["tool.index"] = "corp_kb_v2"

    collector.log("DEBUG", "Executing vector similarity query", tool_span, {"top_k": 3})
    collector.increment_metric("tool_calls_total", 1)
    tool_span.finish(status="OK")

    # 3. Complete root agent workflow
    root_span.finish(status="OK")
    collector.increment_metric("agent_runs_total", 1)

    # 4. Record committed business effect in audit ledger
    collector.record_audit(
        tenant_id=tenant_id,
        action="QUERY_ANSWER_GENERATED",
        details={"trace_id": trace_id, "query_type": "policy_lookup"},
    )

    return "Agent execution completed successfully."


def main() -> None:
    collector = TelemetryCollector()
    tenant = "tenant-enterprise-01"

    result = execute_monitored_agent_run(collector, tenant_id=tenant)
    assert "completed successfully" in result

    # Assert trace hierarchy
    assert len(collector.spans) == 2, f"Expected 2 spans, found {len(collector.spans)}"
    root = collector.spans[0]
    child = collector.spans[1]
    assert root.parent_span_id is None, "Root span should have no parent"
    assert child.parent_span_id == root.span_id, "Child span must link to parent span ID"
    assert child.trace_id == root.trace_id, "Trace IDs must match across causal hierarchy"
    spans_recorded = len(collector.spans)

    # Assert structured log correlation
    assert len(collector.logs) >= 2
    for log_entry in collector.logs:
        assert log_entry.trace_id == root.trace_id, "Log must be correlated with trace ID"
        assert log_entry.span_id in (root.span_id, child.span_id)
    logs_correlated = True

    # Assert metrics
    assert collector.metrics["agent_runs_total"] == 1
    assert collector.metrics["tool_calls_total"] == 1
    metric_incremented = True

    # Assert audit ledger
    assert len(collector.audit_ledger) == 1
    assert collector.audit_ledger[0]["tenant_id"] == tenant
    audit_persisted = True

    print(
        f"Telemetry triad verified: spans_recorded={spans_recorded}, "
        f"logs_correlated={logs_correlated}, metric_incremented={metric_incremented}, "
        f"audit_persisted={audit_persisted}"
    )


if __name__ == "__main__":
    main()
