"""CDC atomic checkpointing and idempotent replay recovery harness.

Demonstrates the recovery contract between Change Data Capture (CDC) checkpoints and destination state:
1. At-least-once delivery pathology: if a worker commits state to the destination database and
   crashes before committing its offset checkpoint to the message broker (e.g. Kafka/Debezium),
   the broker re-delivers the event upon restart.
2. Non-idempotent duplicate effect: applying incremental arithmetic updates (e.g., balance += 50)
   on re-delivered events causes double-credit accounting corruption.
3. Recovery contract: destination updates must either be transactional with the offset watermark
   (writing state + offset in a single ACID transaction) or use monotonic version gating
   (idempotent state upserts) to ensure exactly-once business effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class CDCEvent:
    event_id: str
    account_id: str
    revision: int
    delta_amount: float


class NonIdempotentConsumer:
    """Anti-pattern: blindly mutates state without checking event revisions."""

    def __init__(self) -> None:
        self.balances: Dict[str, float] = {}

    def process(self, event: CDCEvent) -> None:
        current = self.balances.get(event.account_id, 0.0)
        # BUG: Blind increment applies twice on re-delivery
        self.balances[event.account_id] = round(current + event.delta_amount, 2)


class ResilientIdempotentConsumer:
    """Production pattern: tracks applied revisions atomically per entity."""

    def __init__(self) -> None:
        self.balances: Dict[str, float] = {}
        self.applied_revisions: Dict[str, int] = {}
        self.committed_checkpoint_offset: int = 0

    def process_with_acid_contract(self, event: CDCEvent, broker_offset: int) -> bool:
        # Check monotonic revision gate
        last_rev = self.applied_revisions.get(event.account_id, 0)
        if event.revision <= last_rev:
            # Re-delivered event detected: safe no-op
            return False

        # Atomic state + revision advancement
        current = self.balances.get(event.account_id, 0.0)
        self.balances[event.account_id] = round(current + event.delta_amount, 2)
        self.applied_revisions[event.account_id] = event.revision
        self.committed_checkpoint_offset = broker_offset
        return True


def run_test_suite() -> None:
    # Event sequence: Account ACC-1 receives two consecutive credits
    event_1 = CDCEvent(event_id="EVT-101", account_id="ACC-1", revision=1, delta_amount=100.0)
    event_2 = CDCEvent(event_id="EVT-102", account_id="ACC-1", revision=2, delta_amount=50.0)

    # 1. Simulate Non-Idempotent Crash Scenario:
    non_idemp = NonIdempotentConsumer()
    non_idemp.process(event_1)
    non_idemp.process(event_2)

    # Worker crashes before acknowledging event_2 to broker.
    # Broker re-delivers event_2 on restart:
    non_idemp.process(event_2)  # Re-delivery!

    # Balance was corrupted from $150 to $200:
    assert non_idemp.balances["ACC-1"] == 200.0, "Non-idempotent consumer allowed duplicate credit!"

    # 2. Simulate Resilient Idempotent Consumer:
    resilient = ResilientIdempotentConsumer()

    # Step 1: Process event 1 (offset 10)
    res_1 = resilient.process_with_acid_contract(event_1, broker_offset=10)
    assert res_1 is True
    assert resilient.balances["ACC-1"] == 100.0

    # Step 2: Process event 2 (offset 11)
    res_2 = resilient.process_with_acid_contract(event_2, broker_offset=11)
    assert res_2 is True
    assert resilient.balances["ACC-1"] == 150.0

    # Simulated crash before broker checkpoint confirmation.
    # Broker restarts and re-delivers event 2:
    res_replayed = resilient.process_with_acid_contract(event_2, broker_offset=11)

    # Recovery contract detects already applied revision:
    assert res_replayed is False, "Consumer must detect duplicate re-delivered revision"
    # Balance remains exactly $150.00:
    assert resilient.balances["ACC-1"] == 150.0, "Idempotency preserved exact balance"
    assert resilient.applied_revisions["ACC-1"] == 2

    print("All CDC atomic checkpoint idempotency assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
