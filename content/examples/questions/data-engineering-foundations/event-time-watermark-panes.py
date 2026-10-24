"""Streaming window event time, watermarks, and accumulating panes harness.

Demonstrates how streaming paning modes affect downstream aggregations:
1. Event time vs processing time: event time describes when the event occurred; watermarks govern
   when an event-time window is materialized or closed based on bounded out-of-orderness.
2. Accumulating pane semantics: when late-arriving data updates an already-fired window,
   streaming engines (e.g. Apache Flink, Apache Beam) emit an accumulated pane reflecting the entire
   window state (e.g. initial on-time count = 5, late revision = 12).
3. Downstream double-counting trap: if a downstream dashboard or metrics store blindly sums emitted
   panes (running_total += pane.value), it adds 5 + 12 = 17, double-counting the initial 5 events.
4. Retraction and upsert resolution: sinks must apply keyed upserts (window_key -> latest_total) or
   retraction deltas (-5, +12) to produce mathematically correct dashboard totals.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class StreamEvent:
    event_id: str
    event_time_epoch_min: int  # Logical minute when event occurred
    payload_val: int


@dataclass(frozen=True)
class WindowPane:
    window_id: str
    pane_index: int
    is_final: bool
    accumulated_total: int


class StreamingWindowEngine:
    """Simulates a tumbling window engine with late data allowed."""

    def __init__(self, window_size_min: int = 5) -> None:
        self.window_size_min = window_size_min
        self.window_state: Dict[str, int] = {}
        self.pane_counts: Dict[str, int] = {}

    def ingest(self, event: StreamEvent) -> WindowPane:
        # Determine window bucket (e.g. min 0..4 -> 'win-0')
        win_start = (event.event_time_epoch_min // self.window_size_min) * self.window_size_min
        window_id = f"win-{win_start:04d}"

        current_total = self.window_state.get(window_id, 0)
        new_total = current_total + event.payload_val
        self.window_state[window_id] = new_total

        pane_idx = self.pane_counts.get(window_id, 0) + 1
        self.pane_counts[window_id] = pane_idx

        # Emits an accumulating pane with total accumulated window state
        return WindowPane(
            window_id=window_id,
            pane_index=pane_idx,
            is_final=False,
            accumulated_total=new_total,
        )


def naive_additive_sink(panes: List[WindowPane]) -> int:
    """Anti-pattern: treats every emitted pane as an incremental delta."""
    total = 0
    for p in panes:
        total += p.accumulated_total
    return total


def upsert_keyed_sink(panes: List[WindowPane]) -> Dict[str, int]:
    """Production pattern: upserts by window_id to replace older pane estimates."""
    dashboard_state: Dict[str, int] = {}
    for p in panes:
        dashboard_state[p.window_id] = p.accumulated_total
    return dashboard_state


def run_test_suite() -> None:
    engine = StreamingWindowEngine(window_size_min=5)

    # Sequence 1: 5 on-time events arrive for window win-0000
    on_time_panes: List[WindowPane] = []
    for i in range(5):
        pane = engine.ingest(StreamEvent(f"EVT-{i}", event_time_epoch_min=2, payload_val=1))
        on_time_panes.append(pane)

    # Last on-time pane emitted for win-0000:
    latest_on_time = on_time_panes[-1]
    assert latest_on_time.accumulated_total == 5

    # Sequence 2: Network delay resolves, 7 late events arrive for the same window win-0000
    late_panes: List[WindowPane] = []
    for j in range(5, 12):
        pane = engine.ingest(StreamEvent(f"EVT-{j}", event_time_epoch_min=3, payload_val=1))
        late_panes.append(pane)

    latest_corrected_pane = late_panes[-1]
    # The new pane accumulates both on-time and late events (5 + 7 = 12):
    assert latest_corrected_pane.accumulated_total == 12

    # 1. Demonstrate naive additive consumer pathology:
    # If the dashboard receives the on-time pane (5) and then the corrected pane (12),
    # naive summing double counts:
    emitted_panes = [latest_on_time, latest_corrected_pane]
    naive_total = naive_additive_sink(emitted_panes)
    assert naive_total == 17, "Naive summing yielded 5 + 12 = 17 instead of true 12!"

    # 2. Demonstrate upsert-keyed sink resolution:
    keyed_dashboard = upsert_keyed_sink(emitted_panes)
    # The late pane replaces the earlier estimate:
    assert keyed_dashboard["win-0000"] == 12, "Upsert sink correctly reflects true window total"

    print("All event time watermark pane assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
