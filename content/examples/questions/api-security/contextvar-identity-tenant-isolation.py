"""Request-scoped identity isolation via ContextVar, RBAC vs resource ownership, and model spoofing defense.

Demonstrates:
1. Concurrency isolation with contextvars: Ensuring concurrent asyncio tasks maintain isolated request identities without cross-talk.
2. The critical difference between RBAC (global role permissions) and Object-Level Resource Ownership (tenant + user ID matching).
3. Defeating model-injected identity spoofing: Tools strictly extract principal from ContextVar, ignoring model-suggested user or tenant IDs.
"""
from typing import Any, Dict, List, Optional
import asyncio
import contextvars

# Global request context variable
CURRENT_PRINCIPAL: contextvars.ContextVar[Optional[Dict[str, Any]]] = contextvars.ContextVar("current_principal", default=None)

class CaseRecord:
    def __init__(self, case_id: str, tenant_id: str, owner_id: str, title: str):
        self.case_id = case_id
        self.tenant_id = tenant_id
        self.owner_id = owner_id
        self.title = title

class SecureCaseService:
    def __init__(self):
        # Database table of cases
        self._cases: Dict[str, CaseRecord] = {
            "case_001": CaseRecord("case_001", "tenant_alpha", "user_alice", "Confidential Alpha Audit"),
            "case_002": CaseRecord("case_002", "tenant_alpha", "user_bob", "Alpha Marketing Plan"),
            "case_003": CaseRecord("case_003", "tenant_beta", "user_charlie", "Beta Proprietary IP")
        }

    def get_case(self, case_id: str) -> Dict[str, Any]:
        # 1. Retrieve verified principal from ContextVar
        principal = CURRENT_PRINCIPAL.get()
        if not principal:
            raise PermissionError("Unauthenticated: No request security context.")

        if case_id not in self._cases:
            raise KeyError(f"Case '{case_id}' not found.")

        record = self._cases[case_id]

        # 2. Multi-Tenant Boundary Check (Object-Level Authorization)
        if record.tenant_id != principal["tenant_id"]:
            # Defend against horizontal IDOR: Tenant Beta cannot see Tenant Alpha records!
            raise PermissionError(f"Access Denied: Case '{case_id}' belongs to another tenant.")

        # 3. RBAC vs Ownership Distinction:
        # - Admin in tenant_alpha can view any case in tenant_alpha
        # - Regular user can only view cases they own
        is_owner = (record.owner_id == principal["user_id"])
        is_tenant_admin = (principal["role"] == "admin")

        if not (is_owner or is_tenant_admin):
            raise PermissionError(f"Access Denied: User '{principal['user_id']}' does not own case '{case_id}'.")

        return {
            "case_id": record.case_id,
            "title": record.title,
            "owner": record.owner_id,
            "tenant": record.tenant_id
        }

    def tool_update_case(self, case_id: str, new_title: str, untrusted_model_user: Optional[str] = None) -> Dict[str, Any]:
        """Tool execution method invoked by LLM agent."""
        # CRITICAL DEFENSE: Ignore untrusted_model_user parameter completely!
        # Always derive authorization strictly from ContextVar.
        case_data = self.get_case(case_id)
        self._cases[case_id].title = new_title
        return {"status": "UPDATED", "case_id": case_id, "new_title": new_title}

async def simulate_concurrent_requests():
    service = SecureCaseService()

    async def handle_request(user_id: str, tenant_id: str, role: str, target_case_id: str) -> Dict[str, Any]:
        # Bind request-scoped principal in ContextVar
        token = CURRENT_PRINCIPAL.set({
            "user_id": user_id,
            "tenant_id": tenant_id,
            "role": role
        })
        try:
            # Yield control to event loop to simulate concurrent I/O
            await asyncio.sleep(0.01)
            # Principal in ContextVar is isolated to this async execution branch!
            return service.get_case(target_case_id)
        finally:
            CURRENT_PRINCIPAL.reset(token)

    # Launch concurrent tasks with different tenants and roles
    task1 = asyncio.create_task(handle_request("user_alice", "tenant_alpha", "member", "case_001"))
    task2 = asyncio.create_task(handle_request("user_charlie", "tenant_beta", "member", "case_003"))
    task3_admin = asyncio.create_task(handle_request("user_admin", "tenant_alpha", "admin", "case_002"))

    res1, res2, res3 = await asyncio.gather(task1, task2, task3_admin)

    assert res1["title"] == "Confidential Alpha Audit"
    assert res2["title"] == "Beta Proprietary IP"
    assert res3["title"] == "Alpha Marketing Plan"

    # Test Cross-Tenant Rejection (user_alice trying to access tenant_beta's case_003)
    try:
        await handle_request("user_alice", "tenant_alpha", "admin", "case_003")
        assert False, "Should have blocked cross-tenant access"
    except PermissionError as pe:
        assert "belongs to another tenant" in str(pe)

    # Test Model Spoofing Rejection: LLM suggests untrusted_model_user="user_alice"
    token = CURRENT_PRINCIPAL.set({"user_id": "user_bob", "tenant_id": "tenant_alpha", "role": "member"})
    try:
        # Bob cannot update Alice's case_001 even if model tries to claim it is Alice!
        service.tool_update_case("case_001", "Hacked Title", untrusted_model_user="user_alice")
        assert False, "Should have rejected spoofed user"
    except PermissionError as pe:
        assert "does not own case" in str(pe)
    finally:
        CURRENT_PRINCIPAL.reset(token)

if __name__ == "__main__":
    asyncio.run(simulate_concurrent_requests())
    print("ContextVar identity isolation, RBAC vs ownership, and model spoofing defenses verified successfully.")

