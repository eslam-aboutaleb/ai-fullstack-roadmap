#!/usr/bin/env python3
"""
Permission-Scoped Semantic Cache Verification Suite
Demonstrates why caching RAG responses purely on query text or embeddings causes
catastrophic multi-tenant and privilege escalation leaks, and validates
permission-scoped cache key composition and epoch invalidation.
"""

from dataclasses import dataclass, field
from enum import Enum
import hashlib
from typing import Dict, List, Optional, Set, Tuple


class Role(str, Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"
    EXTERNAL = "external"


@dataclass(frozen=True)
class SecurityContext:
    user_id: str
    tenant_id: str
    role: Role
    authorized_doc_ids: Set[str]
    permission_epoch: int = 1


@dataclass
class CachedRAGResponse:
    query_text: str
    generated_text: str
    cited_doc_ids: Set[str]
    required_role: Role
    tenant_id: str
    permission_epoch: int


class NaiveQueryCache:
    """Anti-Pattern: Caching purely on query text bypasses retrieval access controls."""
    def __init__(self):
        self.store: Dict[str, str] = {}

    def get(self, query: str) -> Optional[str]:
        return self.store.get(query)

    def put(self, query: str, response: str) -> None:
        self.store[query] = response


class PermissionScopedCache:
    """
    Secure Production Cache:
    Binds cache identity to tenant, permission scope, and active epoch.
    Enforces post-retrieval authorization re-check on all cited documents.
    """
    def __init__(self):
        self.store: Dict[str, CachedRAGResponse] = {}

    def _compute_cache_key(self, ctx: SecurityContext, query: str) -> str:
        # Key is strictly partitioned by tenant and permission level
        hasher = hashlib.sha256()
        hasher.update(ctx.tenant_id.encode())
        hasher.update(ctx.role.value.encode())
        hasher.update(str(ctx.permission_epoch).encode())
        hasher.update(query.strip().lower().encode())
        return hasher.hexdigest()

    def get(self, ctx: SecurityContext, query: str) -> Optional[CachedRAGResponse]:
        key = self._compute_cache_key(ctx, query)
        entry = self.store.get(key)
        if not entry:
            return None

        # Double Defense: Verify epoch and active document access
        if entry.permission_epoch != ctx.permission_epoch:
            # Stale permission epoch
            del self.store[key]
            return None

        if not entry.cited_doc_ids.issubset(ctx.authorized_doc_ids):
            # Caller lacks authorization to one or more cited documents in the cached answer
            return None

        return entry

    def put(self, ctx: SecurityContext, query: str, answer: str, cited_docs: Set[str]) -> None:
        key = self._compute_cache_key(ctx, query)
        self.store[key] = CachedRAGResponse(
            query_text=query,
            generated_text=answer,
            cited_doc_ids=cited_docs,
            required_role=ctx.role,
            tenant_id=ctx.tenant_id,
            permission_epoch=ctx.permission_epoch
        )

    def invalidate_tenant_epoch(self, tenant_id: str) -> None:
        # Invalidates all cached entries for this tenant when permissions change
        keys_to_delete = [
            k for k, v in self.store.items()
            if v.tenant_id == tenant_id
        ]
        for k in keys_to_delete:
            del self.store[k]


def main() -> None:
    # 1. Establish User Contexts
    admin_ctx = SecurityContext(
        user_id="user_admin_01",
        tenant_id="tenant_acme",
        role=Role.ADMIN,
        authorized_doc_ids={"doc_public_handbook", "doc_confidential_payroll"},
        permission_epoch=1
    )

    regular_employee_ctx = SecurityContext(
        user_id="user_emp_42",
        tenant_id="tenant_acme",
        role=Role.EMPLOYEE,
        authorized_doc_ids={"doc_public_handbook"},  # No access to payroll!
        permission_epoch=1
    )

    query = "What is the executive bonus pool allocation for this fiscal year?"
    admin_answer = "According to the confidential payroll policy, the executive bonus pool is $5.2M [doc_confidential_payroll]."

    # --------------------------------------------------------------------------
    # Case 1: The Naive Semantic Cache Failure Trap
    # --------------------------------------------------------------------------
    naive_cache = NaiveQueryCache()
    # Admin runs query; RAG generates answer and stores in naive cache
    naive_cache.put(query, admin_answer)

    # Regular employee asks the exact same question
    leaked_answer = naive_cache.get(query)
    # The naive cache returns the admin's answer, leaking confidential payroll data!
    assert leaked_answer is not None
    assert "$5.2M" in leaked_answer
    assert "doc_confidential_payroll" in leaked_answer

    # --------------------------------------------------------------------------
    # Case 2: Permission-Scoped Cache Protects Against Cross-Role Leaks
    # --------------------------------------------------------------------------
    secure_cache = PermissionScopedCache()
    # Admin runs query; stores in secure cache
    secure_cache.put(admin_ctx, query, admin_answer, cited_docs={"doc_confidential_payroll"})

    # Regular employee asks the exact same question
    secure_result = secure_cache.get(regular_employee_ctx, query)
    # Assert cache MISS: regular employee cannot access admin cache key
    assert secure_result is None

    # Another admin from the same tenant asks the question
    admin_peer_ctx = SecurityContext(
        user_id="user_admin_02",
        tenant_id="tenant_acme",
        role=Role.ADMIN,
        authorized_doc_ids={"doc_public_handbook", "doc_confidential_payroll"},
        permission_epoch=1
    )
    admin_hit = secure_cache.get(admin_peer_ctx, query)
    assert admin_hit is not None
    assert admin_hit.generated_text == admin_answer

    # --------------------------------------------------------------------------
    # Case 3: Cross-Tenant Isolation
    # --------------------------------------------------------------------------
    foreign_admin_ctx = SecurityContext(
        user_id="user_admin_external",
        tenant_id="tenant_foreign_corp",
        role=Role.ADMIN,
        authorized_doc_ids={"doc_public_handbook", "doc_confidential_payroll"},
        permission_epoch=1
    )
    foreign_hit = secure_cache.get(foreign_admin_ctx, query)
    assert foreign_hit is None  # Different tenant namespace

    # --------------------------------------------------------------------------
    # Case 4: Epoch Invalidation on Permission Change
    # Admin revokes payroll document access or changes security policies
    # --------------------------------------------------------------------------
    secure_cache.invalidate_tenant_epoch("tenant_acme")
    invalidated_hit = secure_cache.get(admin_ctx, query)
    assert invalidated_hit is None  # Cache entry evicted after epoch rotation

    print("All permission-scoped semantic cache invariants verified successfully.")


if __name__ == "__main__":
    main()
