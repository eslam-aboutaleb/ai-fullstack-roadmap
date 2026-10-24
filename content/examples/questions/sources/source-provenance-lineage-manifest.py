"""
source-provenance-lineage-manifest.py

Production-grade Document Provenance, Lineage Manifest, and Cascade Invalidation Suite.
Demonstrates:
1. The text-only ingestion failure: storing raw strings without document revision hashes,
   page/span offsets, parser configurations, access control lists (ACLs), or retention policies.
2. Complete Provenance Manifest architecture binding:
   - Source content hash (SHA-256) and source revision / ETag
   - Page coordinates, bounding boxes, and character span offsets
   - Access control scopes (tenant_id, allowed_roles)
   - Temporal validity intervals (effective_from, effective_to)
3. Cascade Invalidation:
   - Automatic supersession when document revisions drift
   - GDPR / Right-to-be-forgotten deletion cascade ensuring zero orphaned chunks remain in vector indexes.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
import hashlib
import json
from datetime import datetime, timezone


@dataclass(frozen=True)
class SpanCoordinate:
    page_number: int
    char_start: int
    char_end: int
    bounding_box: Optional[Tuple[float, float, float, float]] = None


@dataclass
class DocumentChunk:
    chunk_id: str
    source_doc_id: str
    source_revision: str
    text_content: str
    span: SpanCoordinate
    content_hash: str
    acl_roles: List[str]
    effective_from: str
    effective_to: Optional[str] = None
    is_superseded: bool = False


@dataclass
class SourceDocumentManifest:
    doc_id: str
    filename: str
    current_revision: str
    file_sha256: str
    parser_name: str
    parser_version: str
    acl_roles: List[str]
    created_at_utc: str
    chunks: List[DocumentChunk] = field(default_factory=list)

    def add_chunk(self, text: str, page: int, start: int, end: int) -> DocumentChunk:
        chunk_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        chunk = DocumentChunk(
            chunk_id=f"{self.doc_id}:{self.current_revision}:chunk_{len(self.chunks):03d}",
            source_doc_id=self.doc_id,
            source_revision=self.current_revision,
            text_content=text,
            span=SpanCoordinate(page_number=page, char_start=start, char_end=end),
            content_hash=chunk_hash,
            acl_roles=list(self.acl_roles),
            effective_from=self.created_at_utc
        )
        self.chunks.append(chunk)
        return chunk


class IngestionRepository:
    def __init__(self):
        self.documents: Dict[str, SourceDocumentManifest] = {}
        self.vector_index: Dict[str, DocumentChunk] = {}

    def ingest_document(self, manifest: SourceDocumentManifest) -> None:
        self.documents[manifest.doc_id] = manifest
        for c in manifest.chunks:
            self.vector_index[c.chunk_id] = c

    def update_document_revision(
        self,
        doc_id: str,
        new_revision: str,
        new_content_bytes: bytes,
        new_chunks_data: List[Dict[str, Any]]
    ) -> None:
        """
        Updates document to a new revision and supersedes all prior chunks in the index.
        """
        if doc_id not in self.documents:
            raise KeyError(f"Document {doc_id} not found")

        old_manifest = self.documents[doc_id]
        new_sha256 = hashlib.sha256(new_content_bytes).hexdigest()

        # Mark all old chunks as superseded
        for old_c in old_manifest.chunks:
            old_c.is_superseded = True
            if old_c.chunk_id in self.vector_index:
                del self.vector_index[old_c.chunk_id]

        new_manifest = SourceDocumentManifest(
            doc_id=doc_id,
            filename=old_manifest.filename,
            current_revision=new_revision,
            file_sha256=new_sha256,
            parser_name=old_manifest.parser_name,
            parser_version=old_manifest.parser_version,
            acl_roles=list(old_manifest.acl_roles),
            created_at_utc=datetime.now(timezone.utc).isoformat()
        )

        for c_data in new_chunks_data:
            new_manifest.add_chunk(
                text=c_data["text"],
                page=c_data["page"],
                start=c_data["start"],
                end=c_data["end"]
            )

        self.ingest_document(new_manifest)

    def purge_document_cascade(self, doc_id: str) -> int:
        """
        Executes a cascade deletion (e.g. for GDPR right-to-be-forgotten compliance),
        purging the document and all associated chunks from memory and vector indexes.
        """
        if doc_id not in self.documents:
            return 0

        manifest = self.documents[doc_id]
        purged_count = 0
        for chunk in manifest.chunks:
            if chunk.chunk_id in self.vector_index:
                del self.vector_index[chunk.chunk_id]
                purged_count += 1

        del self.documents[doc_id]
        return purged_count


def main() -> None:
    print("=== Testing Source Provenance Lineage Manifest & Invalidation Suite ===")
    repo = IngestionRepository()

    # 1. Ingest Revision 1 of an Enterprise Policy PDF
    pdf_v1_bytes = b"Enterprise Return Policy 2025: Customers receive full refund within 30 days."
    sha_v1 = hashlib.sha256(pdf_v1_bytes).hexdigest()

    doc_v1 = SourceDocumentManifest(
        doc_id="policy_doc_001",
        filename="return_policy_v1.pdf",
        current_revision="rev_1.0",
        file_sha256=sha_v1,
        parser_name="pdfminer.six",
        parser_version="20240315",
        acl_roles=["employee", "tier1_support"],
        created_at_utc="2025-01-01T00:00:00Z"
    )

    chunk1 = doc_v1.add_chunk(
        text="Customers receive full refund within 30 days.",
        page=2,
        start=120,
        end=166
    )
    repo.ingest_document(doc_v1)

    print(f"Ingested Doc ID '{doc_v1.doc_id}', Revision '{doc_v1.current_revision}'")
    print(f"Chunk ID '{chunk1.chunk_id}' on Page {chunk1.span.page_number}, Spans {chunk1.span.char_start}:{chunk1.span.char_end}")
    assert len(repo.vector_index) == 1
    assert chunk1.chunk_id in repo.vector_index

    # 2. Simulate Document Update (Revision 2.0)
    # The policy changes: restocking fee applies, page location shifts
    pdf_v2_bytes = b"Enterprise Return Policy 2026: Restocking fee of $15 applies on all returns."
    new_chunks = [
        {"text": "Restocking fee of $15 applies on all returns.", "page": 3, "start": 80, "end": 125}
    ]

    print("\nUpdating document to Revision 2.0 (superseding old chunks)...")
    repo.update_document_revision(
        doc_id="policy_doc_001",
        new_revision="rev_2.0",
        new_content_bytes=pdf_v2_bytes,
        new_chunks_data=new_chunks
    )

    # Invariant: Old chunk is superseded and evicted from active vector index
    assert chunk1.is_superseded is True
    assert chunk1.chunk_id not in repo.vector_index
    assert len(repo.vector_index) == 1

    new_chunk = list(repo.vector_index.values())[0]
    print(f"New Active Chunk: '{new_chunk.chunk_id}' (Revision: {new_chunk.source_revision}) on Page {new_chunk.span.page_number}")
    assert new_chunk.source_revision == "rev_2.0"
    assert new_chunk.span.page_number == 3

    # 3. Simulate Cascade Deletion (GDPR Right-to-be-Forgotten)
    print("\nSimulating GDPR cascade deletion of 'policy_doc_001'...")
    purged = repo.purge_document_cascade("policy_doc_001")
    print(f"Purged {purged} chunk(s) from index.")
    assert purged == 1
    assert len(repo.vector_index) == 0
    assert "policy_doc_001" not in repo.documents

    print("\nAll document provenance, lineage, and cascade invalidation invariants verified successfully.")


if __name__ == "__main__":
    main()
