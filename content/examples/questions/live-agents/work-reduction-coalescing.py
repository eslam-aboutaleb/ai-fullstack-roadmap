"""Work Reduction Strategies: Debouncing, Coalescing, and Discrete Command Invariants.

Demonstrates how live agents reduce compute load by debouncing bursty keystrokes
and coalescing rapid intermediate entity state updates, while strictly preserving
discrete, non-conflatable business commands (such as orders or mutations).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class EventType(str, Enum):
    STATE_UPDATE = "state_update"  # Conflatable (latest revision wins)
    DISCRETE_COMMAND = "discrete_command"  # Non-conflatable (every action must execute)


@dataclass(frozen=True)
class InboundEvent:
    event_id: str
    event_type: EventType
    entity_id: str
    revision: int
    payload: Dict[str, Any]
    arrival_time_ms: int


class WorkReductionBuffer:
    """Manages event queues, coalescing conflatable updates and preserving discrete commands."""

    def __init__(self, debounce_window_ms: int = 300) -> None:
        self.debounce_window_ms = debounce_window_ms
        self.conflated_state_table: Dict[str, InboundEvent] = {}
        self.discrete_command_ledger: List[InboundEvent] = []
        self.dropped_intermediate_updates: int = 0
        self.keystroke_history: List[str] = []
        self.last_keystroke_time_ms: int = 0

    def ingest_keystroke(self, char: str, timestamp_ms: int) -> None:
        """Accumulates characters into typing buffer."""
        self.keystroke_history.append(char)
        self.last_keystroke_time_ms = timestamp_ms

    def evaluate_debounce(self, current_time_ms: int) -> Optional[str]:
        """Triggers search query only if silence window has elapsed (quiescence reached)."""
        if not self.keystroke_history:
            return None
        silence_duration = current_time_ms - self.last_keystroke_time_ms
        if silence_duration >= self.debounce_window_ms:
            assembled_query = "".join(self.keystroke_history)
            self.keystroke_history.clear()
            return assembled_query
        return None  # Still active typing, suppress LLM dispatch

    def ingest_event(self, event: InboundEvent) -> None:
        if event.event_type == EventType.DISCRETE_COMMAND:
            # Discrete business actions must NEVER be coalesced or dropped!
            self.discrete_command_ledger.append(event)
        elif event.event_type == EventType.STATE_UPDATE:
            # Conflate by entity_id: replace pending intermediate revisions with higher revision
            existing = self.conflated_state_table.get(event.entity_id)
            if existing is None or event.revision > existing.revision:
                if existing is not None:
                    self.dropped_intermediate_updates += 1
                self.conflated_state_table[event.entity_id] = event
            else:
                self.dropped_intermediate_updates += 1

    def flush_pending_work(self) -> Dict[str, Any]:
        """Flushes coalesced state updates and discrete commands ready for execution."""
        state_dispatches = list(self.conflated_state_table.values())
        command_dispatches = list(self.discrete_command_ledger)
        self.conflated_state_table.clear()
        self.discrete_command_ledger.clear()
        return {
            "state_updates": state_dispatches,
            "discrete_commands": command_dispatches,
        }


def test_work_reduction() -> None:
    buffer = WorkReductionBuffer(debounce_window_ms=300)

    # 1. Debouncing bursty user typing ("apple")
    # User types 'a', 'p', 'p', 'l', 'e' with 50ms gaps
    t = 1000
    for char in ["a", "p", "p", "l", "e"]:
        buffer.ingest_keystroke(char, timestamp_ms=t)
        t += 50
        # While typing, debounce check returns None (suppresses 4 unnecessary LLM calls)
        assert buffer.evaluate_debounce(current_time_ms=t) is None

    # After waiting 300ms of quiescence (silence window)
    t += 300
    debounced_query = buffer.evaluate_debounce(current_time_ms=t)
    assert debounced_query == "apple"

    # 2. Coalescing rapid intermediate entity state updates
    # Document doc_report receives revisions 1, 2, 3 in rapid succession
    buffer.ingest_event(
        InboundEvent(
            event_id="e_rev1",
            event_type=EventType.STATE_UPDATE,
            entity_id="doc_report",
            revision=1,
            payload={"text": "Introduction..."},
            arrival_time_ms=1500,
        )
    )
    buffer.ingest_event(
        InboundEvent(
            event_id="e_rev2",
            event_type=EventType.STATE_UPDATE,
            entity_id="doc_report",
            revision=2,
            payload={"text": "Introduction and executive summary..."},
            arrival_time_ms=1520,
        )
    )
    buffer.ingest_event(
        InboundEvent(
            event_id="e_rev3",
            event_type=EventType.STATE_UPDATE,
            entity_id="doc_report",
            revision=3,
            payload={"text": "Introduction, executive summary, and findings."},
            arrival_time_ms=1550,
        )
    )

    # 3. Discrete commands (e.g. approve quote, notify team)
    buffer.ingest_event(
        InboundEvent(
            event_id="cmd_quote_approve",
            event_type=EventType.DISCRETE_COMMAND,
            entity_id="quote_901",
            revision=1,
            payload={"action": "approve"},
            arrival_time_ms=1560,
        )
    )
    buffer.ingest_event(
        InboundEvent(
            event_id="cmd_payment_capture",
            event_type=EventType.DISCRETE_COMMAND,
            entity_id="quote_901",
            revision=1,
            payload={"action": "capture_payment", "amount_cents": 50000},
            arrival_time_ms=1570,
        )
    )

    # Verify coalescing behavior
    assert buffer.dropped_intermediate_updates == 2
    assert "doc_report" in buffer.conflated_state_table
    assert buffer.conflated_state_table["doc_report"].revision == 3
    assert len(buffer.discrete_command_ledger) == 2  # Both commands preserved!

    # Execute flushed work
    batch = buffer.flush_pending_work()
    assert len(batch["state_updates"]) == 1
    assert batch["state_updates"][0].revision == 3
    assert len(batch["discrete_commands"]) == 2

    print(
        f"Work reduction coalescing verified: debounced_query={debounced_query}, "
        f"coalesced_revision={batch['state_updates'][0].revision}, "
        f"preserved_commands={len(batch['discrete_commands'])}, "
        f"dropped_intermediate={buffer.dropped_intermediate_updates}"
    )


if __name__ == "__main__":
    test_work_reduction()

