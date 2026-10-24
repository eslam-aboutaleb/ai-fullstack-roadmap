"""Defensible RAG retrieval and applicability gating suite.

Demonstrates why semantic similarity alone is insufficient for defensible RAG answers:
1. Stale / Superseded Evidence: Vector similarity frequently ranks expired policies higher
   than active ones due to surface semantic overlap.
2. Multi-Gate Applicability Filtering: Defensible systems enforce caller tenant authorization,
   temporal validity windows (effective dates), and domain scope filters before context assembly.
3. Honest Evidence Gaps: When applicable evidence does not cover an edge case, the system
   returns a structured evidence gap rather than generating plausible confabulation from stale text.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class DefensibilityStatus(str, Enum):
    DEFENSIBLE_ANSWER = "defensible_answer"
    STALE_EVIDENCE_REJECTED = "stale_evidence_rejected"
    EVIDENCE_GAP = "evidence_gap"
    ACCESS_DENIED = "access_denied"


@dataclass(frozen=True)
class PolicyChunk:
    chunk_id: str
    doc_id: str
    revision_id: str
    text: str
    similarity_score: float
    effective_start: date
    effective_end: Optional[date]
    is_superseded: bool
    applicable_categories: Set[str]
    tenant_id: str


@dataclass(frozen=True)
class UserInferenceRequest:
    request_id: str
    caller_tenant: str
    query_date: date
    category: str
    query_text: str


@dataclass(frozen=True)
class RAGPipelineResult:
    status: DefensibilityStatus
    selected_chunk: Optional[PolicyChunk]
    generated_decision: str
    citation_id: Optional[str]


def naive_similarity_retrieval(
    chunks: List[PolicyChunk], request: UserInferenceRequest
) -> RAGPipelineResult:
    """Naive baseline: sorts purely by vector similarity score without applicability gating."""
    if not chunks:
        return RAGPipelineResult(
            status=DefensibilityStatus.EVIDENCE_GAP,
            selected_chunk=None,
            generated_decision="No evidence retrieved.",
            citation_id=None,
        )

    # Sort solely by similarity
    sorted_chunks = sorted(chunks, key=lambda c: c.similarity_score, reverse=True)
    top_chunk = sorted_chunks[0]

    # Naive generator trusts top chunk directly
    return RAGPipelineResult(
        status=DefensibilityStatus.DEFENSIBLE_ANSWER,
        selected_chunk=top_chunk,
        generated_decision=f"Applied policy from {top_chunk.chunk_id}: {top_chunk.text}",
        citation_id=f"{top_chunk.doc_id}:{top_chunk.revision_id}",
    )


def defensible_gated_retrieval(
    chunks: List[PolicyChunk], request: UserInferenceRequest
) -> RAGPipelineResult:
    """Production architecture: applies multi-gate applicability filters before selection."""
    valid_candidates: List[PolicyChunk] = []

    for chunk in chunks:
        # Gate 1: Tenant isolation
        if chunk.tenant_id != request.caller_tenant:
            continue

        # Gate 2: Temporal validity (effective date window)
        if request.query_date < chunk.effective_start:
            continue
        if chunk.effective_end and request.query_date > chunk.effective_end:
            continue
        if chunk.is_superseded:
            continue

        # Gate 3: Scope applicability (product / category match)
        if request.category not in chunk.applicable_categories:
            continue

        valid_candidates.append(chunk)

    if not valid_candidates:
        # Check if high-similarity chunk in the same category was discarded due to staleness
        has_stale_high_match = any(
            c.similarity_score >= 0.85
            and request.category in c.applicable_categories
            and (c.is_superseded or (c.effective_end and request.query_date > c.effective_end))
            for c in chunks
            if c.tenant_id == request.caller_tenant
        )
        status = (
            DefensibilityStatus.STALE_EVIDENCE_REJECTED
            if has_stale_high_match
            else DefensibilityStatus.EVIDENCE_GAP
        )
        return RAGPipelineResult(
            status=status,
            selected_chunk=None,
            generated_decision="Insufficient applicable evidence: Active policy does not cover this case.",
            citation_id=None,
        )

    # Rank surviving valid candidates by similarity
    best_candidate = max(valid_candidates, key=lambda c: c.similarity_score)

    return RAGPipelineResult(
        status=DefensibilityStatus.DEFENSIBLE_ANSWER,
        selected_chunk=best_candidate,
        generated_decision=f"Valid active policy applied: {best_candidate.text}",
        citation_id=f"{best_candidate.doc_id}:{best_candidate.revision_id}:{best_candidate.chunk_id}",
    )


def run_test_suite() -> None:
    # Historical expired policy (High semantic match to user query)
    chunk_v1_stale = PolicyChunk(
        chunk_id="chk-pol-001",
        doc_id="DOC-REFUND",
        revision_id="rev-2023-v1",
        text="All electronics purchases qualify for full refund within 30 days without exception.",
        similarity_score=0.95,  # Top semantic match!
        effective_start=date(2023, 1, 1),
        effective_end=date(2023, 12, 31),  # Expired!
        is_superseded=True,
        applicable_categories={"electronics"},
        tenant_id="tenant-corp-a",
    )

    # Active current policy (Slightly lower similarity score due to nuanced exception clauses)
    chunk_v2_active = PolicyChunk(
        chunk_id="chk-pol-002",
        doc_id="DOC-REFUND",
        revision_id="rev-2024-v2",
        text="Electronics purchases qualify for refund within 30 days, except clearance/sale items which are exchange-only.",
        similarity_score=0.88,
        effective_start=date(2024, 1, 1),
        effective_end=None,  # Active indefinitely
        is_superseded=False,
        applicable_categories={"electronics"},
        tenant_id="tenant-corp-a",
    )

    all_chunks = [chunk_v1_stale, chunk_v2_active]

    request_today = UserInferenceRequest(
        request_id="req-501",
        caller_tenant="tenant-corp-a",
        query_date=date(2024, 6, 15),
        category="electronics",
        query_text="What is the refund rule for electronics items bought on sale?",
    )

    # 1. Evaluate Naive Similarity-Only Pipeline:
    naive_result = naive_similarity_retrieval(all_chunks, request_today)
    assert naive_result.selected_chunk is not None
    # Naive pipeline picks stale chunk purely because 0.95 > 0.88:
    assert naive_result.selected_chunk.chunk_id == "chk-pol-001"
    assert "rev-2023-v1" in str(naive_result.citation_id)
    assert naive_result.selected_chunk.is_superseded is True, "Naive pipeline selected a superseded chunk!"

    # 2. Evaluate Defensible Gated Pipeline:
    defensible_result = defensible_gated_retrieval(all_chunks, request_today)
    assert defensible_result.status == DefensibilityStatus.DEFENSIBLE_ANSWER
    assert defensible_result.selected_chunk is not None
    # Defensible pipeline filters out stale chunk and selects active v2:
    assert defensible_result.selected_chunk.chunk_id == "chk-pol-002"
    assert "rev-2024-v2" in str(defensible_result.citation_id)
    assert defensible_result.selected_chunk.is_superseded is False
    assert "clearance/sale items which are exchange-only" in defensible_result.selected_chunk.text

    # 3. Evaluate Uncovered Domain Scope (Evidence Gap Handling):
    request_uncovered = UserInferenceRequest(
        request_id="req-502",
        caller_tenant="tenant-corp-a",
        query_date=date(2024, 6, 15),
        category="automotive_parts",  # Not covered by either policy chunk
        query_text="What is the return window for automotive battery units?",
    )
    uncovered_result = defensible_gated_retrieval(all_chunks, request_uncovered)
    assert uncovered_result.status == DefensibilityStatus.EVIDENCE_GAP
    assert uncovered_result.selected_chunk is None
    assert "Insufficient applicable evidence" in uncovered_result.generated_decision

    print("All defensible retrieval applicability assertions verified successfully.")


if __name__ == "__main__":
    run_test_suite()
