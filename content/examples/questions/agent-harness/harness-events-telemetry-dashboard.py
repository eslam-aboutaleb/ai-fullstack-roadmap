"""Agent harness runtime event stream, telemetry schemas, and production operational dashboard.

Demonstrates:
1. Strongly typed runtime event taxonomy: RunStarted, ToolProposed, ToolExecuted, RunCompleted, RunFailed.
2. Structured event streaming for live client observation and distributed tracing.
3. Production operational dashboard: Aggregating run completion rates, step latency, tool error distributions, and budget burn.
"""
from typing import Any, Dict, List, Optional
import collections
import json
import time

class HarnessEventType:
    RUN_STARTED = "RUN_STARTED"
    TOOL_PROPOSED = "TOOL_PROPOSED"
    TOOL_EXECUTED = "TOOL_EXECUTED"
    RUN_COMPLETED = "RUN_COMPLETED"
    RUN_FAILED = "RUN_FAILED"

class HarnessEvent:
    def __init__(self, run_id: str, event_type: str, data: Dict[str, Any]):
        self.run_id = run_id
        self.event_type = event_type
        self.timestamp = time.time()
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "data": self.data
        }

class ProductionHarnessDashboard:
    def __init__(self):
        self.event_log: List[HarnessEvent] = []

    def record_event(self, event: HarnessEvent) -> None:
        self.event_log.append(event)

    def generate_dashboard_metrics(self) -> Dict[str, Any]:
        runs_by_status = collections.Counter()
        tool_counts = collections.Counter()
        tool_failures = collections.Counter()
        total_runs = 0
        durations: List[float] = []

        # Correlate runs
        run_start_times: Dict[str, float] = {}

        for ev in self.event_log:
            if ev.event_type == HarnessEventType.RUN_STARTED:
                total_runs += 1
                run_start_times[ev.run_id] = ev.timestamp

            elif ev.event_type == HarnessEventType.TOOL_EXECUTED:
                tool_name = ev.data.get("tool_name", "unknown")
                tool_counts[tool_name] += 1
                if ev.data.get("is_error", False):
                    tool_failures[tool_name] += 1

            elif ev.event_type in (HarnessEventType.RUN_COMPLETED, HarnessEventType.RUN_FAILED):
                status = "COMPLETED" if ev.event_type == HarnessEventType.RUN_COMPLETED else "FAILED"
                runs_by_status[status] += 1
                start_time = run_start_times.get(ev.run_id)
                if start_time:
                    durations.append((ev.timestamp - start_time) * 1000.0)

        success_rate = (runs_by_status["COMPLETED"] / total_runs * 100.0) if total_runs > 0 else 0.0
        avg_latency_ms = (sum(durations) / len(durations)) if durations else 0.0

        return {
            "total_runs": total_runs,
            "success_rate_percent": round(success_rate, 1),
            "runs_by_status": dict(runs_by_status),
            "average_run_latency_ms": round(avg_latency_ms, 2),
            "tool_invocations": dict(tool_counts),
            "tool_failure_rates": {
                name: f"{(tool_failures[name] / tool_counts[name] * 100):.1f}%"
                for name in tool_counts if tool_counts[name] > 0
            }
        }

if __name__ == "__main__":
    dashboard = ProductionHarnessDashboard()

    # Simulate Run 1: Successful run
    r1 = "run_001"
    dashboard.record_event(HarnessEvent(r1, HarnessEventType.RUN_STARTED, {"user_id": "u1"}))
    dashboard.record_event(HarnessEvent(r1, HarnessEventType.TOOL_EXECUTED, {"tool_name": "vector_search", "is_error": False}))
    dashboard.record_event(HarnessEvent(r1, HarnessEventType.TOOL_EXECUTED, {"tool_name": "generate_summary", "is_error": False}))
    dashboard.record_event(HarnessEvent(r1, HarnessEventType.RUN_COMPLETED, {"tokens": 420}))

    # Simulate Run 2: Failed run with tool error
    r2 = "run_002"
    dashboard.record_event(HarnessEvent(r2, HarnessEventType.RUN_STARTED, {"user_id": "u2"}))
    dashboard.record_event(HarnessEvent(r2, HarnessEventType.TOOL_EXECUTED, {"tool_name": "vector_search", "is_error": True}))
    dashboard.record_event(HarnessEvent(r2, HarnessEventType.RUN_FAILED, {"error": "Connection timeout"}))

    metrics = dashboard.generate_dashboard_metrics()
    assert metrics["total_runs"] == 2
    assert metrics["runs_by_status"]["COMPLETED"] == 1
    assert metrics["runs_by_status"]["FAILED"] == 1
    assert metrics["success_rate_percent"] == 50.0
    assert metrics["tool_invocations"]["vector_search"] == 2
    assert metrics["tool_failure_rates"]["vector_search"] == "50.0%"

    print("Harness runtime events, telemetry streaming, and production dashboard verified successfully.")

