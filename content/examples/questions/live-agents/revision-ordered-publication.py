"""Revision-Ordered Publication & Event-Time Watermarking.

Demonstrates causal event ordering, monotonic revision horizons, and rejection of
stale out-of-order publications caused by network jitter. Proves why network arrival
order fails as a source of truth and enforces event-time watermark invariants.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class EventEnvelope:
    event_id: str
    entity_id: str
    revision: int
    event_time: float  # Epoch timestamp at source (seconds)
    payload: Dict[str, str]


@dataclass
class AuthoritativeEntityState:
    entity_id: str
    current_revision: int
    last_event_time: float
    data: Dict[str, str]
    revision_history: List[int] = field(default_factory=list)


class RevisionOrderedPublicationManager:
    """Maintains authoritative state horizons and rejects stale out-of-order updates."""

    def __init__(self) -> None:
        self._entities: Dict[str, AuthoritativeEntityState] = {}
        self.rejected_stale_count: int = 0
        self.accepted_count: int = 0

    def ingest_event(
        self, event: EventEnvelope, processing_time: float
    ) -> Tuple[bool, str]:
        """Ingests an event, enforcing monotonic revision and event-time ordering."""
        entity = self._entities.get(event.entity_id)

        if entity is None:
            # Initialize entity state
            self._entities[event.entity_id] = AuthoritativeEntityState(
                entity_id=event.entity_id,
                current_revision=event.revision,
                last_event_time=event.event_time,
                data=dict(event.payload),
                revision_history=[event.revision],
            )
            self.accepted_count += 1
            return True, f"Initialized revision {event.revision}"

        # Invariant: Reject stale or out-of-order revisions
        if event.revision <= entity.current_revision:
            self.rejected_stale_count += 1
            return False, (
                f"STALE_REVISION_REJECTED: incoming revision {event.revision} <= "
                f"authoritative revision {entity.current_revision}"
            )

        # Invariant: Event time must not regress for advancing revisions
        if event.event_time < entity.last_event_time:
            self.rejected_stale_count += 1
            return False, (
                f"TEMPORAL_INVERSION_REJECTED: incoming event_time {event.event_time} < "
                f"last event_time {entity.last_event_time}"
            )

        # Authoritative state transition
        entity.current_revision = event.revision
        entity.last_event_time = event.event_time
        entity.data.update(event.payload)
        entity.revision_history.append(event.revision)
        self.accepted_count += 1
        return True, f"Committed revision {event.revision}"

    def get_state(self, entity_id: str) -> Optional[AuthoritativeEntityState]:
        return self._entities.get(entity_id)


def test_revision_publication() -> None:
    manager = RevisionOrderedPublicationManager()

    # Scenario: User edits a live draft in collaborative session
    # Event 1 created at t=100.0, arrives at t=100.2
    e1 = EventEnvelope(
        event_id="evt_01",
        entity_id="doc_contract_9",
        revision=1,
        event_time=100.0,
        payload={"title": "Master Services Agreement", "status": "draft"},
    )
    ok1, msg1 = manager.ingest_event(e1, processing_time=100.2)
    assert ok1 is True
    assert manager.get_state("doc_contract_9").current_revision == 1

    # Event 3 created at t=102.0, arrives quickly over fiber at t=102.1
    # User updated clause to revision 3
    e3 = EventEnvelope(
        event_id="evt_03",
        entity_id="doc_contract_9",
        revision=3,
        event_time=102.0,
        payload={"liability_cap": "$1,000,000", "status": "under_review"},
    )
    ok3, msg3 = manager.ingest_event(e3, processing_time=102.1)
    assert ok3 is True
    assert manager.get_state("doc_contract_9").current_revision == 3

    # Event 2 was delayed by cellular network jitter (created at t=101.0, arrives late at t=103.5)
    # Payload has obsolete clause: liability_cap = "$500,000"
    e2 = EventEnvelope(
        event_id="evt_02",
        entity_id="doc_contract_9",
        revision=2,
        event_time=101.0,
        payload={"liability_cap": "$500,000"},
    )
    ok2, msg2 = manager.ingest_event(e2, processing_time=103.5)

    # Invariant: Arrival order must NOT overwrite newer authoritative state
    assert ok2 is False
    assert "STALE_REVISION_REJECTED" in msg2
    state = manager.get_state("doc_contract_9")
    assert state.current_revision == 3
    assert state.data["liability_cap"] == "$1,000,000"  # Protected from stale revert!
    assert state.revision_history == [1, 3]
    assert manager.rejected_stale_count == 1
    assert manager.accepted_count == 2

    # Duplicate revision arrival
    ok_dup, msg_dup = manager.ingest_event(e3, processing_time=104.0)
    assert ok_dup is False
    assert manager.rejected_stale_count == 2

    print(
        f"Revision ordered publication verified: current_revision={state.current_revision}, "
        f"rejected_stale={manager.rejected_stale_count}, accepted={manager.accepted_count}"
    )


if __name__ == "__main__":
    test_revision_publication()

