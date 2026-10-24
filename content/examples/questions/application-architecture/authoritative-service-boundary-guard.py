#!/usr/bin/env python3
"""
Authoritative Service Boundary Guard Suite
Demonstrates why placing authorization in the HTTP/chat controller layer creates
critical cross-tenant vulnerabilities in background workers and async queues,
and validates mandatory security context enforcement at the domain service boundary.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Set, Tuple


@dataclass(frozen=True)
class SecurityContext:
    tenant_id: str
    user_id: str
    roles: Set[str]


@dataclass
class DocumentRecord:
    doc_id: str
    tenant_id: str
    title: str
    content: str


class NaiveDocumentRepository:
    """Anti-Pattern: Raw repository with no security scoping. Relies on caller to check authorization."""
    def __init__(self):
        self._store: Dict[str, DocumentRecord] = {}

    def insert(self, doc: DocumentRecord) -> None:
        self._store[doc.doc_id] = doc

    def find_by_id(self, doc_id: str) -> Optional[DocumentRecord]:
        return self._store.get(doc_id)


class FlawedChatController:
    """Chat route that correctly checks tenant ownership in the HTTP layer."""
    def __init__(self, repo: NaiveDocumentRepository):
        self.repo = repo

    def handle_chat_document_request(self, ctx: SecurityContext, doc_id: str) -> Tuple[int, Optional[str]]:
        doc = self.repo.find_by_id(doc_id)
        if not doc:
            return 404, None
        # Controller-level authorization check
        if doc.tenant_id != ctx.tenant_id:
            return 403, "Forbidden: Cross-tenant access denied"
        return 200, doc.content


class FlawedBackgroundWorker:
    """
    Background worker (e.g., Celery, SQS, Cron) that calls the naive repository directly.
    Because authorization was only implemented in the HTTP controller, this worker has no scope check!
    """
    def __init__(self, repo: NaiveDocumentRepository):
        self.repo = repo

    def process_task(self, doc_id: str) -> Tuple[int, Optional[str]]:
        # Flaw: No SecurityContext is passed or checked!
        doc = self.repo.find_by_id(doc_id)
        if not doc:
            return 404, None
        return 200, f"Processed document: {doc.content}"


class AuthoritativeDocumentService:
    """
    Production Architecture:
    The domain service boundary is the single source of truth for authorization.
    Every consumer (HTTP API, WebSocket, Background Worker, Agent Tool) MUST pass a verified
    SecurityContext, and queries are strictly scoped by tenant_id.
    """
    def __init__(self):
        self._store: Dict[Tuple[str, str], DocumentRecord] = {}  # (tenant_id, doc_id) -> record

    def insert(self, ctx: SecurityContext, doc: DocumentRecord) -> None:
        if doc.tenant_id != ctx.tenant_id:
            raise PermissionError("Cannot insert document for foreign tenant")
        self._store[(ctx.tenant_id, doc.doc_id)] = doc

    def get_document(self, ctx: SecurityContext, doc_id: str) -> Optional[DocumentRecord]:
        # Enforce tenant isolation at the service boundary
        return self._store.get((ctx.tenant_id, doc_id))


class SecureBackgroundWorker:
    """Secure worker that must execute within a valid tenant SecurityContext."""
    def __init__(self, service: AuthoritativeDocumentService):
        self.service = service

    def process_task(self, ctx: SecurityContext, doc_id: str) -> Tuple[int, Optional[str]]:
        doc = self.service.get_document(ctx, doc_id)
        if not doc:
            return 404, "Document not found or access denied for this tenant"
        return 200, f"Processed document: {doc.content}"


def main() -> None:
    # --------------------------------------------------------------------------
    # Setup: Multi-Tenant Data
    # --------------------------------------------------------------------------
    tenant_a_ctx = SecurityContext(tenant_id="tenant_alpha", user_id="user_a", roles={"member"})
    tenant_b_ctx = SecurityContext(tenant_id="tenant_beta", user_id="user_b", roles={"member"})

    confidential_doc = DocumentRecord(
        doc_id="doc_q3_financials",
        tenant_id="tenant_beta",
        title="Q3 Confidential Financials",
        content="Tenant Beta confidential profit margin: 38%."
    )

    # --------------------------------------------------------------------------
    # Case 1: The Controller-Only Trap
    # --------------------------------------------------------------------------
    naive_repo = NaiveDocumentRepository()
    naive_repo.insert(confidential_doc)

    chat_controller = FlawedChatController(naive_repo)

    # In HTTP Chat, tenant_alpha correctly receives 403 Forbidden
    status, msg = chat_controller.handle_chat_document_request(tenant_a_ctx, "doc_q3_financials")
    assert status == 403
    assert "Forbidden" in msg

    # BUT in the background queue, an asynchronous task enqueued with doc_id="doc_q3_financials"
    # calls the naive repository directly without tenant context!
    bg_worker = FlawedBackgroundWorker(naive_repo)
    bg_status, bg_output = bg_worker.process_task("doc_q3_financials")

    # Critical Security Vulnerability: The background worker leaks Tenant Beta's data!
    assert bg_status == 200
    assert "Tenant Beta confidential profit margin" in bg_output

    # --------------------------------------------------------------------------
    # Case 2: The Authoritative Domain Service Boundary
    # --------------------------------------------------------------------------
    secure_service = AuthoritativeDocumentService()
    secure_service.insert(tenant_b_ctx, confidential_doc)

    secure_worker = SecureBackgroundWorker(secure_service)

    # Attempting to process the task under Tenant Alpha's context fails safe (404/Denied)
    s_status, s_msg = secure_worker.process_task(tenant_a_ctx, "doc_q3_financials")
    assert s_status == 404
    assert "access denied" in s_msg

    # Executing under Tenant Beta's authorized context succeeds
    valid_status, valid_output = secure_worker.process_task(tenant_b_ctx, "doc_q3_financials")
    assert valid_status == 200
    assert "Tenant Beta confidential profit margin" in valid_output

    print("All authoritative service boundary guard invariants verified successfully.")


if __name__ == "__main__":
    main()
