"""Tombstone backfill and snapshot restore resurrection guard.

Demonstrates why naive database restores and historical backfills resurrect deleted data:
1. The zombie data vulnerability: a snapshot taken at T0 contains entities that were subsequently
   deleted at T1 under GDPR or regulatory compliance. Restoring from T0 resurrects the deleted records.
2. The limitation of structural integrity checks: running row count or checksum checks on restored tables
   reports 100% health while violating privacy and legal deletion mandates.
3. Anti-entropy tombstone reconciliation: post-restore bootstrap procedures must query an append-only,
   durable tombstone ledger to re-apply all deletions that occurred after the snapshot timestamp before
   declaring the system ready for live traffic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple


@dataclass(frozen=True)
class CustomerDocument:
    doc_id: str
    tenant_id: str
    content: str
    created_at: str


@dataclass(frozen=True)
class AuthoritativeTombstone:
    doc_id: str
    tenant_id: str
    deleted_at: str
    deletion_reason: str


class RestoredDatabaseCluster:
    """Simulates a database cluster restored from a point-in-time snapshot."""

    def __init__(self, snapshot_timestamp: str, records: List[CustomerDocument]) -> None:
        self.snapshot_timestamp = snapshot_timestamp
        self.documents: Dict[str, CustomerDocument] = {d.doc_id: d for d in records}
        self.is_ready_for_traffic: bool = False

    def naive_mark_ready(self) -> None:
        """Anti-pattern: marks database ready without reconciling newer tombstones."""
        self.is_ready_for_traffic = True

    def reconcile_against_tombstones(
        self, tombstones: List[AuthoritativeTombstone]
    ) -> List[str]:
        """Production pattern: re-applies deletions recorded after the snapshot timestamp."""
        purged_doc_ids: List[str] = []
        snap_time = datetime.fromisoformat(self.snapshot_timestamp)

        for tombstone in tombstones:
            tomb_time = datetime.fromisoformat(tombstone.deleted_at)

            # If deletion occurred after snapshot was captured:
            if tomb_time >= snap_time:
                if tombstone.doc_id in self.documents:
                    del self.documents[tombstone.doc_id]
                    purged_doc_ids.append(tombstone.doc_id)

        self.is_ready_for_traffic = True
        return purged_doc_ids


def run_test_suite() -> None:
    # Timeline:
    # 02:00: Snapshot taken containing DOC-1 and DOC-PRIVATE-2
    snapshot_time = "2026-10-24T02:00:00+00:00"
    snapshot_docs = [
        CustomerDocument("DOC-1", "tenant-a", "Public product spec", "2026-10-23T10:00:00+00:00"),
        CustomerDocument("DOC-PRIVATE-2", "tenant-a", "Confidential PII document", "2026-10-23T11:00:00+00:00"),
    ]

    # 10:00: User requests GDPR erasure of DOC-PRIVATE-2
    durable_tombstones = [
        AuthoritativeTombstone(
            doc_id="DOC-PRIVATE-2",
            tenant_id="tenant-a",
            deleted_at="2026-10-24T10:00:00+00:00",
            deletion_reason="GDPR_RIGHT_TO_BE_FORGOTTEN",
        )
    ]

    # 14:00: Database failure forces restore from the 02:00 snapshot
    # 1. Naive restore scenario:
    naive_cluster = RestoredDatabaseCluster(snapshot_time, snapshot_docs)
    naive_cluster.naive_mark_ready()

    # Catastrophic failure: Naive restore resurrected the deleted private document!
    assert "DOC-PRIVATE-2" in naive_cluster.documents, "Zombie document was resurrected!"

    # 2. Resilient restore with anti-entropy tombstone reconciliation:
    resilient_cluster = RestoredDatabaseCluster(snapshot_time, snapshot_docs)
    purged_ids = resilient_cluster.reconcile_against_tombstones(durable_tombstones)

    # Reconciliation successfully identified and purged the resurrected document:
    assert purged_ids == ["DOC-PRIVATE-2"]
    assert "DOC-PRIVATE-2" not in resilient_cluster.documents
    assert "DOC-1" in resilient_cluster.documents
    assert resilient_cluster.is_ready_for_traffic is True

    print("All tombstone backfill resurrection guard assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
