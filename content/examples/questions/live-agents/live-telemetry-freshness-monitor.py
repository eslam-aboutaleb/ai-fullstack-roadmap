"""Live Telemetry & Semantic Freshness Monitor.

Distinguishes transport-level connection liveness from semantic data freshness.
Monitors served revision lag (source_revision - served_revision) and queue age to
detect pipeline stall conditions even when transport heartbeats remain green.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class TelemetrySnapshot:
    session_id: str
    transport_heartbeat_ok: bool
    source_revision: int
    served_revision: int
    oldest_queue_age_seconds: float
    p95_execution_latency_ms: float

    @property
    def revision_lag(self) -> int:
        return max(0, self.source_revision - self.served_revision)

    @property
    def is_semantically_fresh(self) -> bool:
        """Freshness requires zero revision lag and queue age under threshold."""
        return self.revision_lag == 0 and self.oldest_queue_age_seconds < 5.0


class LiveTelemetryFreshnessMonitor:
    """Evaluates telemetry signals across active agent sessions and flags hidden stalls."""

    def __init__(self, max_allowed_lag: int = 2, max_queue_age_sec: float = 10.0) -> None:
        self.max_allowed_lag = max_allowed_lag
        self.max_queue_age_sec = max_queue_age_sec
        self.alerts: List[str] = []

    def evaluate_session(self, snapshot: TelemetrySnapshot) -> Dict[str, Any]:
        lag = snapshot.revision_lag
        queue_age = snapshot.oldest_queue_age_seconds
        has_silent_stall = False

        # Silent stall: Transport heartbeat is green, but application state is lagging severely
        if snapshot.transport_heartbeat_ok and (
            lag > self.max_allowed_lag or queue_age > self.max_queue_age_sec
        ):
            has_silent_stall = True
            alert_msg = (
                f"ALERT_SILENT_STALL: Session {snapshot.session_id} has green heartbeat "
                f"but revision_lag={lag} and queue_age={queue_age}s"
            )
            self.alerts.append(alert_msg)

        return {
            "session_id": snapshot.session_id,
            "transport_healthy": snapshot.transport_heartbeat_ok,
            "revision_lag": lag,
            "queue_age_seconds": queue_age,
            "is_semantically_fresh": snapshot.is_semantically_fresh,
            "silent_stall_detected": has_silent_stall,
        }


def test_live_telemetry_freshness() -> None:
    from typing import Any

    monitor = LiveTelemetryFreshnessMonitor(max_allowed_lag=2, max_queue_age_sec=10.0)

    # 1. Healthy session: Heartbeat green, served revision matches source revision
    healthy_snap = TelemetrySnapshot(
        session_id="sess_healthy_01",
        transport_heartbeat_ok=True,
        source_revision=15,
        served_revision=15,
        oldest_queue_age_seconds=0.4,
        p95_execution_latency_ms=120.0,
    )
    res_healthy = monitor.evaluate_session(healthy_snap)
    assert res_healthy["transport_healthy"] is True
    assert res_healthy["revision_lag"] == 0
    assert res_healthy["is_semantically_fresh"] is True
    assert res_healthy["silent_stall_detected"] is False

    # 2. Pathological session: Green heartbeat, but worker queue is stalled!
    # Source document is at revision 15, but served UI is stuck on revision 12 (lag=3).
    # Oldest queued event is 40 seconds old!
    stalled_snap = TelemetrySnapshot(
        session_id="sess_stalled_02",
        transport_heartbeat_ok=True,
        source_revision=15,
        served_revision=12,
        oldest_queue_age_seconds=40.0,
        p95_execution_latency_ms=2800.0,
    )
    res_stalled = monitor.evaluate_session(stalled_snap)
    assert res_stalled["transport_healthy"] is True  # Transport reports OK!
    assert res_stalled["revision_lag"] == 3
    assert res_stalled["queue_age_seconds"] == 40.0
    assert res_stalled["is_semantically_fresh"] is False
    assert res_stalled["silent_stall_detected"] is True
    assert len(monitor.alerts) == 1

    print(
        f"Live telemetry freshness verified: healthy_lag={res_healthy['revision_lag']}, "
        f"stalled_lag={res_stalled['revision_lag']}, "
        f"stalled_queue_age={res_stalled['queue_age_seconds']}, "
        f"silent_stall_detected={res_stalled['silent_stall_detected']}"
    )


if __name__ == "__main__":
    test_live_telemetry_freshness()
