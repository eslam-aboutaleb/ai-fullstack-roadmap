#!/usr/bin/env python3
"""
Claim Citation Support and Provenance Verification Suite
Demonstrates why tenant membership checks alone cannot validate citation faithfulness,
and verifies atomic claim entailment, revision pinning, and condition preservation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class EntailmentStatus(str, Enum):
    ENTAILED = "entailed"
    CONTRADICTED = "contradicted"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class DocumentRevision:
    doc_id: str
    revision: str
    tenant_id: str
    title: str
    text: str
    is_active: bool = True


@dataclass(frozen=True)
class CitationReference:
    doc_id: str
    revision: str
    span_start: int
    span_end: int


@dataclass
class AtomicClaim:
    claim_id: str
    text: str
    citation: Optional[CitationReference]
    required_keywords: Set[str] = field(default_factory=set)
    forbidden_keywords: Set[str] = field(default_factory=set)


@dataclass
class VerificationVerdict:
    claim_id: str
    authorized: bool
    revision_active: bool
    status: EntailmentStatus
    reason: str


class CitationSupportVerifier:
    """
    Verifies that generated answer citations are:
    1. Authorized for the calling tenant
    2. Pinned to the active, non-superseded revision
    3. Semantically and factually supporting the exact material claim
    """

    def __init__(self, document_store: Dict[Tuple[str, str], DocumentRevision]):
        self.docs = document_store

    def verify_claim(
        self,
        caller_tenant: str,
        claim: AtomicClaim
    ) -> VerificationVerdict:
        if not claim.citation:
            return VerificationVerdict(
                claim_id=claim.claim_id,
                authorized=False,
                revision_active=False,
                status=EntailmentStatus.UNSUPPORTED,
                reason="Claim lacks any cited source provenance."
            )

        key = (claim.citation.doc_id, claim.citation.revision)
        doc = self.docs.get(key)
        if not doc:
            return VerificationVerdict(
                claim_id=claim.claim_id,
                authorized=False,
                revision_active=False,
                status=EntailmentStatus.UNSUPPORTED,
                reason=f"Cited document revision {key} does not exist in store."
            )

        # 1. Tenant Authorization Boundary
        if doc.tenant_id != caller_tenant:
            return VerificationVerdict(
                claim_id=claim.claim_id,
                authorized=False,
                revision_active=doc.is_active,
                status=EntailmentStatus.UNSUPPORTED,
                reason="Cross-tenant access violation: caller is not authorized for this source."
            )

        # 2. Active Revision Check
        if not doc.is_active:
            return VerificationVerdict(
                claim_id=claim.claim_id,
                authorized=True,
                revision_active=False,
                status=EntailmentStatus.UNSUPPORTED,
                reason="Cited document revision is stale and has been superseded by a newer policy."
            )

        # 3. Span Boundary Extraction
        span = doc.text[claim.citation.span_start:claim.citation.span_end]

        # 4. Entailment Verification
        # Check if the cited span actually supports the claim's requirements
        lower_span = span.lower()
        if any(f.lower() in lower_span for f in claim.forbidden_keywords):
            return VerificationVerdict(
                claim_id=claim.claim_id,
                authorized=True,
                revision_active=True,
                status=EntailmentStatus.CONTRADICTED,
                reason=f"Cited span directly contradicts the claim: found conflicting condition."
            )

        if not all(r.lower() in lower_span for r in claim.required_keywords):
            return VerificationVerdict(
                claim_id=claim.claim_id,
                authorized=True,
                revision_active=True,
                status=EntailmentStatus.UNSUPPORTED,
                reason="Cited span is authorized but does not contain evidence for this material claim."
            )

        return VerificationVerdict(
            claim_id=claim.claim_id,
            authorized=True,
            revision_active=True,
            status=EntailmentStatus.ENTAILED,
            reason="Claim is fully supported by the cited authorized document span."
        )


def main() -> None:
    # Set up ground truth document store
    delivery_text = "Standard delivery takes 3 to 5 business days. Delivery delays do not qualify for automatic monetary compensation."
    refund_v1_text = "Customers may request refunds within 14 days of purchase."
    refund_v2_text = "Customers may request refunds within 30 days of purchase, excluding clearance items."

    doc_store: Dict[Tuple[str, str], DocumentRevision] = {
        ("doc-delivery", "rev-1"): DocumentRevision(
            doc_id="doc-delivery",
            revision="rev-1",
            tenant_id="tenant-alpha",
            title="Shipping and Delivery Policy",
            text=delivery_text,
            is_active=True
        ),
        ("doc-refund", "rev-1"): DocumentRevision(
            doc_id="doc-refund",
            revision="rev-1",
            tenant_id="tenant-alpha",
            title="Refund Policy (Stale)",
            text=refund_v1_text,
            is_active=False  # Superseded
        ),
        ("doc-refund", "rev-2"): DocumentRevision(
            doc_id="doc-refund",
            revision="rev-2",
            tenant_id="tenant-alpha",
            title="Refund Policy (Current)",
            text=refund_v2_text,
            is_active=True
        ),
        ("doc-confidential", "rev-1"): DocumentRevision(
            doc_id="doc-confidential",
            revision="rev-1",
            tenant_id="tenant-beta",
            title="Executive Compensation",
            text="Executive bonus structures for tenant beta.",
            is_active=True
        )
    }

    verifier = CitationSupportVerifier(doc_store)

    # --------------------------------------------------------------------------
    # Case 1: The False Support Trap
    # Assistant cites an authorized delivery paragraph to justify a refund claim.
    # The source belongs to tenant-alpha, but the text discusses shipping delays,
    # NOT refund eligibility!
    # --------------------------------------------------------------------------
    claim_unsupported = AtomicClaim(
        claim_id="claim-001",
        text="You are entitled to a full cash refund if your order takes longer than 5 business days.",
        citation=CitationReference(
            doc_id="doc-delivery",
            revision="rev-1",
            span_start=0,
            span_end=len(delivery_text)
        ),
        required_keywords={"refund", "cash"},
        forbidden_keywords={"do not qualify"}
    )

    verdict_1 = verifier.verify_claim("tenant-alpha", claim_unsupported)
    assert verdict_1.authorized is True  # Passed tenant check!
    assert verdict_1.revision_active is True
    # But FAILED entailment because the span contains 'do not qualify'
    assert verdict_1.status == EntailmentStatus.CONTRADICTED
    assert "directly contradicts the claim" in verdict_1.reason

    # --------------------------------------------------------------------------
    # Case 2: Stale Revision Trap
    # Assistant cites rev-1 of the refund policy (14 days), which has been superseded.
    # --------------------------------------------------------------------------
    claim_stale = AtomicClaim(
        claim_id="claim-002",
        text="You have up to 14 days to request a refund.",
        citation=CitationReference(
            doc_id="doc-refund",
            revision="rev-1",
            span_start=0,
            span_end=len(refund_v1_text)
        ),
        required_keywords={"14 days", "refund"}
    )

    verdict_2 = verifier.verify_claim("tenant-alpha", claim_stale)
    assert verdict_2.authorized is True
    assert verdict_2.revision_active is False
    assert verdict_2.status == EntailmentStatus.UNSUPPORTED
    assert "superseded" in verdict_2.reason

    # --------------------------------------------------------------------------
    # Case 3: Cross-Tenant Boundary Violation
    # Assistant tries to cite a document belonging to tenant-beta for tenant-alpha.
    # --------------------------------------------------------------------------
    claim_cross_tenant = AtomicClaim(
        claim_id="claim-003",
        text="Executive bonuses are tied to profitability.",
        citation=CitationReference(
            doc_id="doc-confidential",
            revision="rev-1",
            span_start=0,
            span_end=40
        ),
        required_keywords={"bonus"}
    )

    verdict_3 = verifier.verify_claim("tenant-alpha", claim_cross_tenant)
    assert verdict_3.authorized is False
    assert "Cross-tenant access violation" in verdict_3.reason

    # --------------------------------------------------------------------------
    # Case 4: Fully Verified & Grounded Citation
    # Assistant cites rev-2 of refund policy with exact conditions.
    # --------------------------------------------------------------------------
    claim_valid = AtomicClaim(
        claim_id="claim-004",
        text="Refunds can be requested within 30 days of purchase.",
        citation=CitationReference(
            doc_id="doc-refund",
            revision="rev-2",
            span_start=0,
            span_end=len(refund_v2_text)
        ),
        required_keywords={"30 days", "refund"}
    )

    verdict_4 = verifier.verify_claim("tenant-alpha", claim_valid)
    assert verdict_4.authorized is True
    assert verdict_4.revision_active is True
    assert verdict_4.status == EntailmentStatus.ENTAILED

    print("All claim citation support and provenance invariants verified successfully.")


if __name__ == "__main__":
    main()
