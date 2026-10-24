#!/usr/bin/env python3
"""
Versioned Tombstone and Deletion Authority Guard
Demonstrates how out-of-order message retries can silently resurrect deleted documents,
and validates monotonic revision gates, tombstones, and atomic compare-and-swap rejection.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class DocumentStatus(str, Enum):
    ACTIVE = "active"
    TOMBSTONED = "tombstoned"


@dataclass
class DocumentMetadataRecord:
    doc_id: str
    revision: int
    status: DocumentStatus
    content_hash: str
    updated_at_epoch: int


@dataclass
class IngestionEvent:
    doc_id: str
    revision: int
    is_deletion: bool
    text: Optional[str] = None
    content_hash: Optional[str] = None


class NaiveIngestionPipeline:
    """Anti-Pattern: Deleting rows without durable tombstones allows delayed retries to resurrect data."""
    def __init__(self):
        self.vector_index: Dict[str, str] = {}  # doc_id -> text

    def process_event(self, event: IngestionEvent) -> None:
        if event.is_deletion:
            self.vector_index.pop(event.doc_id, None)
        else:
            # Blind upsert: delayed retries overwrite or resurrect
            self.vector_index[event.doc_id] = event.text or ""


class ResilientIngestionPipeline:
    """
    Secure Production Pipeline:
    Maintains monotonic revision authority with durable tombstones.
    Any upsert with revision <= stored_revision is rejected as a stale replay.
    """
    def __init__(self):
        self.metadata_store: Dict[str, DocumentMetadataRecord] = {}
        self.vector_index: Dict[str, str] = {}  # doc_id -> text
        self.rejected_replays: List[Tuple[str, int, str]] = []

    def process_event(self, event: IngestionEvent, timestamp: int) -> bool:
        stored = self.metadata_store.get(event.doc_id)

        if stored is not None:
            # Monotonic Invariant: Incoming revision must be strictly greater than stored revision
            if event.revision <= stored.revision:
                self.rejected_replays.append(
                    (event.doc_id, event.revision, f"Stale event revision {event.revision} <= current {stored.revision}")
                )
                return False

        # Apply monotonic update
        if event.is_deletion:
            # Record durable tombstone
            self.metadata_store[event.doc_id] = DocumentMetadataRecord(
                doc_id=event.doc_id,
                revision=event.revision,
                status=DocumentStatus.TOMBSTONED,
                content_hash="DELETED",
                updated_at_epoch=timestamp
            )
            # Remove from searchable vector store
            self.vector_index.pop(event.doc_id, None)
            return True
        else:
            # Active upsert
            self.metadata_store[event.doc_id] = DocumentMetadataRecord(
                doc_id=event.doc_id,
                revision=event.revision,
                status=DocumentStatus.ACTIVE,
                content_hash=event.content_hash or "hash",
                updated_at_epoch=timestamp
            )
            self.vector_index[event.doc_id] = event.text or ""
            return True


def main() -> None:
    doc_id = "policy_refund_clearance"
    initial_text = "Rev 1: Final-sale clearance items are non-refundable."
    updated_text = "Rev 2: Final-sale clearance items receive store credit only."

    # --------------------------------------------------------------------------
    # Case 1: The Naive Pipeline Resurrection Failure
    # --------------------------------------------------------------------------
    naive = NaiveIngestionPipeline()
    # 1. Ingest Rev 2
    naive.process_event(IngestionEvent(doc_id=doc_id, revision=2, is_deletion=False, text=updated_text))
    assert doc_id in naive.vector_index

    # 2. Process Delete at Rev 3 (document is legally purged)
    naive.process_event(IngestionEvent(doc_id=doc_id, revision=3, is_deletion=True))
    assert doc_id not in naive.vector_index

    # 3. A delayed Kafka / worker retry from Rev 2 arrives late
    naive.process_event(IngestionEvent(doc_id=doc_id, revision=2, is_deletion=False, text=updated_text))
    # Disaster: The deleted policy is silently resurrected!
    assert doc_id in naive.vector_index
    assert naive.vector_index[doc_id] == updated_text

    # --------------------------------------------------------------------------
    # Case 2: Resilient Ingestion with Versioned Tombstone Guard
    # --------------------------------------------------------------------------
    resilient = ResilientIngestionPipeline()

    # 1. Ingest Rev 2
    ok = resilient.process_event(
        IngestionEvent(doc_id=doc_id, revision=2, is_deletion=False, text=updated_text, content_hash="hash_rev2"),
        timestamp=100
    )
    assert ok is True
    assert doc_id in resilient.vector_index
    assert resilient.metadata_store[doc_id].status == DocumentStatus.ACTIVE

    # 2. Process Delete at Rev 3
    ok = resilient.process_event(
        IngestionEvent(doc_id=doc_id, revision=3, is_deletion=True),
        timestamp=101
    )
    assert ok is True
    assert doc_id not in resilient.vector_index
    assert resilient.metadata_store[doc_id].status == DocumentStatus.TOMBSTONED
    assert resilient.metadata_store[doc_id].revision == 3

    # 3. Delayed Rev 2 retry arrives late
    ok_delayed = resilient.process_event(
        IngestionEvent(doc_id=doc_id, revision=2, is_deletion=False, text=updated_text, content_hash="hash_rev2"),
        timestamp=102
    )
    # The tombstone guard strictly rejects the delayed retry
    assert ok_delayed is False
    assert doc_id not in resilient.vector_index
    assert len(resilient.rejected_replays) == 1
    assert "Stale event revision 2 <= current 3" in resilient.rejected_replays[0][2]

    # 4. Valid future re-creation at Rev 4 passes
    new_policy_text = "Rev 4: Brand new clearance policy introduced."
    ok_future = resilient.process_event(
        IngestionEvent(doc_id=doc_id, revision=4, is_deletion=False, text=new_policy_text, content_hash="hash_rev4"),
        timestamp=103
    )
    assert ok_future is True
    assert doc_id in resilient.vector_index
    assert resilient.vector_index[doc_id] == new_policy_text
    assert resilient.metadata_store[doc_id].status == DocumentStatus.ACTIVE
    assert resilient.metadata_store[doc_id].revision == 4

    print("All versioned tombstone resurrection guard invariants verified successfully.")


if __name__ == "__main__":
    main()
