"""Dynamic multi-tenant authorization filtering for vector search and RAG retrieval pipelines.

Demonstrates:
1. The failure mode of static vector metadata: Document ACLs and group memberships change dynamically while index metadata remains stale.
2. Two-tier retrieval authorization architecture:
   - Tier 1: Coarse pre-filtering on immutable isolation boundaries (tenant_id).
   - Tier 2: Authoritative real-time post-filtering against live database ACLs and revoked access lists.
3. Decoupling search candidates from source document lookup: Re-verifying permissions before returning full document text or citations.
"""
from typing import Any, Dict, List, Set, Tuple

class AuthoritativeAclService:
    def __init__(self):
        # Live relational authorization table: doc_id -> Set of authorized users
        self._doc_permissions: Dict[str, Set[str]] = {
            "doc_101": {"alice", "bob", "carol"},
            "doc_102": {"alice", "carol"},
            "doc_103": {"bob"}   # Alice's access was recently revoked in the database!
        }

    def has_access(self, user_id: str, doc_id: str) -> bool:
        return user_id in self._doc_permissions.get(doc_id, set())

    def revoke_access(self, user_id: str, doc_id: str) -> None:
        if doc_id in self._doc_permissions:
            self._doc_permissions[doc_id].discard(user_id)

class TwoTierVectorRetrievalEngine:
    def __init__(self, acl_service: AuthoritativeAclService):
        self.acl_service = acl_service
        # Simulated vector database with static metadata
        self._vector_records = [
            {"id": "doc_101", "tenant_id": "corp_a", "score": 0.95, "title": "Quarterly Strategy"},
            {"id": "doc_102", "tenant_id": "corp_a", "score": 0.91, "title": "Engineering Roadmap"},
            {"id": "doc_103", "tenant_id": "corp_a", "score": 0.88, "title": "Mergers & Acquisitions"},
            {"id": "doc_201", "tenant_id": "corp_b", "score": 0.99, "title": "Competitor Secret"}
        ]

    def search_authorized(self, caller_tenant: str, caller_user: str, top_k: int = 2) -> List[Dict[str, Any]]:
        # --- TIER 1: COARSE PRE-FILTER (IMMUTABLE TENANT BOUNDARY) ---
        # Never allow vectors from Corp B into Corp A's candidate pool!
        tenant_candidates = [
            rec for rec in self._vector_records
            if rec["tenant_id"] == caller_tenant
        ]

        # --- TIER 2: REAL-TIME AUTHORITATIVE POST-FILTER (LIVE ACL SERVICE) ---
        # Filter candidates against current live permissions (eliminating stale ACL leakage)
        authorized_results = []
        for candidate in tenant_candidates:
            doc_id = candidate["id"]
            if self.acl_service.has_access(caller_user, doc_id):
                authorized_results.append(candidate)
            if len(authorized_results) == top_k:
                break

        return authorized_results

    def view_document_source(self, caller_tenant: str, caller_user: str, doc_id: str) -> Dict[str, Any]:
        """Source lookup must re-evaluate authorization independently from search scores!"""
        # Re-check live permissions
        if not self.acl_service.has_access(caller_user, doc_id):
            raise PermissionError(f"Access Denied: User '{caller_user}' does not have read permissions for '{doc_id}'.")

        return {
            "doc_id": doc_id,
            "tenant_id": caller_tenant,
            "full_content": f"Authoritative full text for {doc_id} under live ACL verification."
        }

if __name__ == "__main__":
    acl = AuthoritativeAclService()
    engine = TwoTierVectorRetrievalEngine(acl)

    # 1. Initial search for Alice in corp_a
    results_alice = engine.search_authorized(caller_tenant="corp_a", caller_user="alice", top_k=5)
    doc_ids_alice = [r["id"] for r in results_alice]
    # Alice can see doc_101 and doc_102, but NOT doc_103 (access was not granted in ACL)
    assert "doc_101" in doc_ids_alice
    assert "doc_102" in doc_ids_alice
    assert "doc_103" not in doc_ids_alice
    # Tenant boundary strictly prevented doc_201 (corp_b) from ever leaking
    assert "doc_201" not in doc_ids_alice

    # 2. Dynamic Access Revocation in Real Time:
    # Alice's access to doc_102 is revoked in the live database
    acl.revoke_access("alice", "doc_102")

    # Immediate subsequent search reflects revocation without rebuilding vector index!
    results_after_revocation = engine.search_authorized(caller_tenant="corp_a", caller_user="alice", top_k=5)
    updated_ids = [r["id"] for r in results_after_revocation]
    assert "doc_102" not in updated_ids  # Revocation was instantly enforced!
    assert updated_ids == ["doc_101"]

    # 3. Source Lookup Re-Verification:
    # Attempting to fetch source for revoked doc_102 fails even if Alice cached the ID
    try:
        engine.view_document_source(caller_tenant="corp_a", caller_user="alice", doc_id="doc_102")
        assert False, "Should have blocked view of revoked document"
    except PermissionError as pe:
        assert "Access Denied" in str(pe)

    # Authorized source lookup succeeds
    valid_source = engine.view_document_source(caller_tenant="corp_a", caller_user="alice", doc_id="doc_101")
    assert "doc_101" in valid_source["doc_id"]

    print("Dynamic two-tier vector authorization and real-time revocation verified successfully.")
