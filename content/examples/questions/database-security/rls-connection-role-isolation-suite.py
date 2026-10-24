"""
rls-connection-role-isolation-suite.py

Production-grade PostgreSQL Row-Level Security (RLS) Connection Role and Isolation Suite.
Demonstrates:
1. The Table Owner / Superuser Bypass Trap:
   - Why connecting as table_owner or superuser silently bypasses RLS policies by default
     unless FORCE ROW LEVEL SECURITY is set.
2. Connection Pool Context Bleeding (e.g. PgBouncer):
   - How unscoped session variables (SET app.current_tenant_id) bleed across requests on pooled
     TCP connections, exposing Tenant A data to Tenant B.
3. The Hardened Multi-Tenant Isolation Architecture:
   - Unprivileged application role (NOBYPASSRLS) + FORCE ROW LEVEL SECURITY + transaction-scoped
     set_config(..., is_local=True) ensuring fail-closed isolation.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class DatabaseRole:
    username: str
    is_superuser: bool = False
    is_table_owner: bool = False
    can_bypass_rls: bool = False


@dataclass
class DocumentRow:
    doc_id: str
    tenant_id: str
    title: str
    classification: str


class MockPostgresEngine:
    def __init__(self):
        self.rows: List[DocumentRow] = [
            DocumentRow("doc_1", "tenant_alpha", "Alpha Financial Strategy", "Confidential"),
            DocumentRow("doc_2", "tenant_alpha", "Alpha Customer PII", "Restricted"),
            DocumentRow("doc_3", "tenant_beta", "Beta Patent Submission", "Confidential"),
            DocumentRow("doc_4", "tenant_beta", "Beta Board Minutes", "Restricted"),
        ]
        self.rls_enabled: bool = True
        self.force_rls: bool = False
        # Session state on the physical database connection
        self.connection_session_vars: Dict[str, str] = {}
        self.transaction_local_vars: Dict[str, str] = {}
        self.in_transaction: bool = False

    def begin_transaction(self) -> None:
        self.in_transaction = True
        self.transaction_local_vars.clear()

    def set_config(self, key: str, value: str, is_local: bool) -> None:
        if is_local:
            if not self.in_transaction:
                raise RuntimeError("SET LOCAL cannot be executed outside a transaction block")
            self.transaction_local_vars[key] = value
        else:
            self.connection_session_vars[key] = value

    def commit_transaction(self) -> None:
        self.in_transaction = False
        # Transaction-scoped variables are wiped on commit/rollback
        self.transaction_local_vars.clear()

    def get_current_setting(self, key: str) -> Optional[str]:
        # Transaction-local variable overrides session-level variable
        if self.in_transaction and key in self.transaction_local_vars:
            return self.transaction_local_vars[key]
        return self.connection_session_vars.get(key)

    def execute_select_documents(self, role: DatabaseRole) -> List[DocumentRow]:
        """
        Simulates PostgreSQL query executor evaluating RLS predicates.
        """
        # Superuser and BYPASSRLS roles ALWAYS bypass RLS
        if role.is_superuser or role.can_bypass_rls:
            return list(self.rows)

        # Table owner bypasses RLS unless FORCE ROW LEVEL SECURITY is enabled
        if role.is_table_owner and not self.force_rls:
            return list(self.rows)

        # RLS Policy Evaluation: USING (tenant_id = current_setting('app.current_tenant_id'))
        current_tenant = self.get_current_setting("app.current_tenant_id")
        if not current_tenant:
            # Fails closed if session variable is not set
            return []

        return [r for r in self.rows if r.tenant_id == current_tenant]


def main() -> None:
    print("=== Testing PostgreSQL Row-Level Security Connection Role & Session Isolation ===")
    pg = MockPostgresEngine()

    superuser = DatabaseRole("postgres", is_superuser=True)
    table_owner = DatabaseRole("migration_admin", is_table_owner=True)
    app_user = DatabaseRole("app_runtime_user", is_superuser=False, is_table_owner=False, can_bypass_rls=False)

    # 1. Demonstrate The Table Owner / Superuser Bypass Trap
    # A web application connects as the table owner. It expects RLS to filter to tenant_alpha.
    pg.begin_transaction()
    pg.set_config("app.current_tenant_id", "tenant_alpha", is_local=True)

    # When querying as table_owner with default RLS (force_rls=False):
    bypassed_results = pg.execute_select_documents(role=table_owner)
    print(f"\n[Vulnerability] Querying as 'table_owner' returned {len(bypassed_results)} documents across ALL tenants:")
    for doc in bypassed_results:
        print(f"  {doc.doc_id} ({doc.tenant_id}): {doc.title}")
    # Critical security invariant: Table owner saw Tenant Beta's documents despite tenant_alpha setting!
    assert len(bypassed_results) == 4, "Table owner should bypass RLS when force_rls is False"
    pg.commit_transaction()

    # 2. Demonstrate Connection Pool Session Bleeding (PgBouncer without SET LOCAL)
    # Request 1 (Tenant Alpha) executes on Connection 1 without is_local=True
    pg.set_config("app.current_tenant_id", "tenant_alpha", is_local=False)  # Un-scoped SET!
    res_alpha = pg.execute_select_documents(role=app_user)
    assert len(res_alpha) == 2
    assert all(r.tenant_id == "tenant_alpha" for r in res_alpha)

    # Request 1 finishes and connection is returned to the pool with dirty state.
    # Request 2 (Tenant Beta) arrives on Connection 1, but due to a bug, fails to set its tenant ID.
    res_beta_leaked = pg.execute_select_documents(role=app_user)
    print(f"\n[Vulnerability] Request 2 on pooled connection without SET LOCAL retrieved {len(res_beta_leaked)} docs:")
    for doc in res_beta_leaked:
        print(f"  LEAKED -> {doc.doc_id} ({doc.tenant_id}): {doc.title}")
    # The second request inherited Tenant Alpha's data!
    assert all(r.tenant_id == "tenant_alpha" for r in res_beta_leaked), "Unscoped session variable caused bleeding!"

    # Clean the connection
    pg.connection_session_vars.clear()

    # 3. Demonstrate Hardened Production RLS (app_user + FORCE RLS + SET LOCAL)
    pg.force_rls = True

    # Proper transaction for Tenant Beta using is_local=True
    pg.begin_transaction()
    pg.set_config("app.current_tenant_id", "tenant_beta", is_local=True)
    res_beta = pg.execute_select_documents(role=app_user)
    print(f"\n[Hardened] Proper SET LOCAL query for Tenant Beta returned {len(res_beta)} documents:")
    for doc in res_beta:
        print(f"  {doc.doc_id} ({doc.tenant_id}): {doc.title}")
    assert len(res_beta) == 2
    assert all(r.tenant_id == "tenant_beta" for r in res_beta)
    pg.commit_transaction()

    # Verify that after commit, connection is automatically pristine
    res_after_commit = pg.execute_select_documents(role=app_user)
    print(f"\n[Hardened] After transaction commit, querying without tenant context returns {len(res_after_commit)} documents (fails closed).")
    assert len(res_after_commit) == 0

    print("\nAll PostgreSQL RLS connection role and session isolation invariants verified successfully.")


if __name__ == "__main__":
    main()
