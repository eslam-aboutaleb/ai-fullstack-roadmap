"""ELT raw replay repair and authoritative tombstone deletion harness.

Demonstrates where failures are repaired in ETL versus ELT pipelines:
1. ETL limitation: transforming in-flight before loading discards raw source representations.
   When a transformation bug is discovered months later, historical projections cannot be recomputed
   without expensive or impossible source extractions.
2. ELT replayability: landing immutable raw events (Bronze tier) enables deterministic backfills
   and code-fix replays into downstream transformed tables (Silver/Gold tiers).
3. Deletion authority invariant: during historical raw replays, the pipeline must join against
   authoritative tombstone records to prevent resurrecting entities deleted under GDPR or privacy requests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set


@dataclass(frozen=True)
class RawIngestionEvent:
    event_id: str
    user_id: str
    event_timestamp: str
    gross_revenue: float
    tax_rate: float


@dataclass(frozen=True)
class DeletionTombstone:
    user_id: str
    deleted_at: str


@dataclass(frozen=True)
class TransformedProjection:
    user_id: str
    net_revenue: float
    is_active: bool


def buggy_transform(event: RawIngestionEvent) -> TransformedProjection:
    """Flawed logic: mistakenly subtracted tax twice."""
    tax = event.gross_revenue * event.tax_rate
    net = event.gross_revenue - (tax * 2)  # BUG: double tax deduction
    return TransformedProjection(user_id=event.user_id, net_revenue=round(net, 2), is_active=True)


def corrected_transform(event: RawIngestionEvent) -> TransformedProjection:
    """Fixed logic: correct net revenue formula."""
    tax = event.gross_revenue * event.tax_rate
    net = event.gross_revenue - tax
    return TransformedProjection(user_id=event.user_id, net_revenue=round(net, 2), is_active=True)


def replay_elt_pipeline(
    raw_store: List[RawIngestionEvent],
    tombstones: List[DeletionTombstone],
    use_fixed_transform: bool,
) -> Dict[str, TransformedProjection]:
    """Replays raw events while filtering out users with authoritative tombstone deletions."""
    tombstoned_users: Set[str] = {t.user_id for t in tombstones}
    transform_fn = corrected_transform if use_fixed_transform else buggy_transform

    projections: Dict[str, TransformedProjection] = {}

    for raw in raw_store:
        # Invariant: Never resurrect deleted entities during replay
        if raw.user_id in tombstoned_users:
            continue

        projections[raw.user_id] = transform_fn(raw)

    return projections


def run_test_suite() -> None:
    # 1. Raw landed events in bronze storage:
    raw_events = [
        RawIngestionEvent("EVT-1", "user-alice", "2026-09-01T10:00:00Z", 100.0, 0.10),
        RawIngestionEvent("EVT-2", "user-bob", "2026-09-02T11:00:00Z", 200.0, 0.15),
        RawIngestionEvent("EVT-3", "user-charlie", "2026-09-03T12:00:00Z", 300.0, 0.20),
    ]

    # Authoritative deletion requested mid-month: user-bob requested account deletion under GDPR
    tombstones = [
        DeletionTombstone("user-bob", "2026-09-15T09:00:00Z")
    ]

    # 2. Initial run under buggy transform:
    initial_gold = replay_elt_pipeline(raw_events, tombstones, use_fixed_transform=False)

    # user-alice: 100 - (10 * 2) = 80.0 (buggy!)
    assert initial_gold["user-alice"].net_revenue == 80.0
    # user-bob is absent due to tombstone:
    assert "user-bob" not in initial_gold

    # 3. Bug discovered: Replay historical raw store with corrected transform:
    repaired_gold = replay_elt_pipeline(raw_events, tombstones, use_fixed_transform=True)

    # user-alice net revenue repaired to 90.0:
    assert repaired_gold["user-alice"].net_revenue == 90.0
    # user-charlie net revenue: 300 - 60 = 240.0:
    assert repaired_gold["user-charlie"].net_revenue == 240.0

    # CRUCIAL INVARIANT: user-bob must NOT be resurrected by the replay of EVT-2:
    assert "user-bob" not in repaired_gold, "Tombstone must prevent entity resurrection on replay!"

    print("All ELT raw replay repair assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
